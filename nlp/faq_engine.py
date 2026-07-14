# ==========================================================
# nlp/faq_engine.py  — Pipeline hybride Embedding + Gemini
# v4 — Corrections dashboard + opérations fiables
#
# FLUX PRINCIPAL :
#  1.  Contexte opérationnel actif  → listes rapides → Gemini si ambigu
#  2.  Vérification domaine LLM
#  3.  Opérations fuzzy/regex
#  4.  Embedding type=operation     → gerer_operations_par_nom
#  5.  Score HAUT  (≥ 0.82)         → DB + reformulation Gemini
#  6.  Score MOYEN (≥ 0.65)         → Gemini vérifie → DB ou LLM
#  7.  Score BAS   (< 0.65)         → Gemini direct avec historique
#
# CORRECTIONS v4 :
#  [FIX 1] get_reponse_intention : cache hit retournait rows (liste)
#          au lieu de random.choice(rows)[0] → AttributeError corrigé.
#  [FIX 2] reformuler_avec_gemini : normalisation défensive du type
#          de reponse_brute (list/tuple → str).
#  [FIX 3] gemini_verifier_intent : même normalisation défensive.
#  [FIX 4] DASHBOARD — sauvegarder_conversation : toutes les
#          conversations sauvegardées avec type_intent et action_handler
#          explicites, y compris :
#            • annulation/confirmation de contexte → type_intent='operation'
#            • LLM direct (étape 7) → type_intent='llm'
#            • hors domaine → type_intent='hors_domaine'
#          Cela permet au dashboard de distinguer correctement les
#          3 catégories (DB / Opération / Fallback LLM).
# ==========================================================
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from concurrent.futures import ThreadPoolExecutor
from cachetools import TTLCache
from psycopg2 import pool as pg_pool

import numpy as np
import psycopg2.extras
import logging
import random
import hashlib
import time
import os
import markdown

from nlp.netoyage import nettoyer_message
from router.operation_router import detecter_operation
from services.controler.conversion_controler import convertir_operation
from services.agent_service import get_agent
from services.service_info import get_services
from services.tracking_service import get_colis_info
from nlp.preprocess_colis import est_code_colis

import google.generativeai as genai

# ==========================================================
# GEMINI CONFIG
# ==========================================================
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("models/gemini-flash-lite-latest")

logging.basicConfig(level=logging.INFO)
_executor = ThreadPoolExecutor(max_workers=4)

# ==========================================================
# CONNECTION POOL POSTGRES
# ==========================================================
_db_pool = None

def get_pool():
    global _db_pool
    if _db_pool is None:
        _db_pool = pg_pool.ThreadedConnectionPool(
            2, 10,
            host     = os.getenv("DB_HOST", "localhost"),
            port     = int(os.getenv("DB_PORT", "5432")),
            dbname   = os.getenv("DB_NAME"),
            user     = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
        )
        logging.info("[POOL] Connection pool initialisé")
    return _db_pool

def get_conn():       return get_pool().getconn()
def release_conn(c):  get_pool().putconn(c)

# ==========================================================
# EMBEDDING MODEL + PRÉCHAUFFAGE
# ==========================================================
modele_embedding = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)
logging.info("[WARMUP] Préchauffage du modèle embedding...")
modele_embedding.encode(["warmup"], normalize_embeddings=True)
logging.info("[WARMUP] Modèle prêt.")

# ==========================================================
# SEUILS
# ==========================================================
SEUIL_HAUT  = 0.82   # Très confiant  → DB + reformulation directe
SEUIL_MOYEN = 0.65   # Incertain      → Gemini vérifie avant de répondre
SEUIL_BAS   = 0.50   # Opérations     → seuil bas acceptable pour les ops

# ==========================================================
# CACHES
# ==========================================================
CACHE_INTENTS      = []
_intents_last_load = 0
_INTENTS_TTL       = 300

_embedding_cache   = TTLCache(maxsize=500, ttl=3600)
_reponse_cache     = TTLCache(maxsize=200, ttl=60)
_domain_llm_cache  = TTLCache(maxsize=500, ttl=1800)
_verify_cache      = TTLCache(maxsize=300, ttl=600)
_context_llm_cache = TTLCache(maxsize=300, ttl=120)

# ==========================================================
# MAPPING action_handler
# ==========================================================
_ACTION_HANDLER_MAP = {
    "taux_change":   "conversion_handler",
    "suivi_colis":   "suivi_handler",
    "contact_agent": "agent_handler",
    "service_info":  "service_handler",
}

# ==========================================================
# LISTES RAPIDES
# ==========================================================
_MOTS_CONFIRMATION = {
    "oui", "yes", "ok", "okay", "d'accord", "daccord",
    "bien sur", "bien sûr", "absolument", "exactement",
    "affirmatif", "yep", "ouais", "ouep", "yop",
    "allez", "vas-y", "vas y", "go", "continue",
    "continuer", "proceed", "allons-y", "allons y",
    "je veux", "pret", "prêt", "je suis pret",
    "je suis prêt", "parfait", "super", "nickel",
    "pourquoi pas", "avec plaisir",
}

_MOTS_ANNULATION = {
    "non", "no", "nope", "annuler", "cancel", "stop",
    "laisse tomber", "pas maintenant", "plus tard",
    "ça va", "ca va", "c'est bon", "non merci",
    "pas besoin", "ça va merci",
}

# ==========================================================
# SESSION CONTEXT
# ==========================================================
_SESSION_CONTEXT = {}
_SESSION_TTL     = 300

def set_context(id_user, intent_nom: str):
    _SESSION_CONTEXT[id_user] = {"intent": intent_nom, "ts": time.time()}
    logging.info(f"[CONTEXT SET] user={id_user} → {intent_nom}")

def get_context(id_user):
    ctx = _SESSION_CONTEXT.get(id_user)
    if not ctx:
        return None
    if time.time() - ctx["ts"] > _SESSION_TTL:
        del _SESSION_CONTEXT[id_user]
        logging.info(f"[CONTEXT EXPIRED] user={id_user}")
        return None
    return ctx["intent"]

def clear_context(id_user):
    _SESSION_CONTEXT.pop(id_user, None)
    logging.info(f"[CONTEXT CLEARED] user={id_user}")

# ==========================================================
# ANALYSE CONTEXTUELLE PAR GEMINI
# ==========================================================
def analyser_intention_contextuelle(message: str, historique: list, intent_contexte: str) -> str:
    derniers  = "".join(h["content"] for h in historique[-4:])
    cache_key = hashlib.md5(f"{message}:{derniers}:{intent_contexte}".encode()).hexdigest()

    if cache_key in _context_llm_cache:
        result = _context_llm_cache[cache_key]
        logging.info(f"[CONTEXT LLM CACHE] → {result}")
        return result

    hist_str = ""
    for h in historique[-6:]:
        role = "Bot" if h["role"] == "assistant" else "Utilisateur"
        hist_str += f"{role}: {h['content']}\n"

    prompt = f"""Tu es un analyseur d'intention pour un chatbot CTEXI.

HISTORIQUE DE LA CONVERSATION :
{hist_str}

NOUVEAU MESSAGE DE L'UTILISATEUR : "{message}"
CONTEXTE ACTIF : le bot attend une réponse liée à "{intent_contexte}"

Réponds UNIQUEMENT par un de ces 4 mots (sans explication) :
- CONFIRME  → l'utilisateur accepte ou valide la proposition du bot
- ANNULE    → l'utilisateur refuse ou veut arrêter
- DONNEE    → l'utilisateur fournit une information attendue (code colis, montant, ville...)
- NOUVEAU   → question sans lien avec le contexte actif

RÉPONSE (1 seul mot) :"""

    try:
        resp = gemini_model.generate_content(prompt)
        if resp and resp.text:
            decision = resp.text.strip().upper().split()[0]
            if decision not in ("CONFIRME", "ANNULE", "DONNEE", "NOUVEAU"):
                decision = "DONNEE"
            _context_llm_cache[cache_key] = decision
            logging.info(f"[CONTEXT LLM] msg='{message[:40]}' ctx={intent_contexte} → {decision}")
            return decision
    except Exception as e:
        logging.error(f"[CONTEXT LLM ERROR] {e}")

    return "DONNEE"

# ==========================================================
# PARSER EMBEDDING
# ==========================================================
def _parse_embedding(raw):
    if isinstance(raw, str):
        raw = raw.strip().lstrip("[").rstrip("]")
        return np.array([float(x) for x in raw.split(",")], dtype=float)
    return np.array(raw, dtype=float)

# ==========================================================
# CHARGER INTENTS
# ==========================================================
def charger_intents():
    global CACHE_INTENTS, _intents_last_load
    now = time.time()
    if CACHE_INTENTS and (now - _intents_last_load) < _INTENTS_TTL:
        return
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT
                e.id, e.id_intent,
                i.nom            AS intent_nom,
                i.type_intent,
                i.action_handler,
                e.sous_intent,
                e.phrase,
                e.embedding
            FROM chatbot.intent_examples e
            JOIN chatbot.intention i ON i.id_intent = e.id_intent
            WHERE e.embedding IS NOT NULL
        """)
        CACHE_INTENTS      = cur.fetchall()
        _intents_last_load = now
        cur.close()
        logging.info(f"[INTENTS] {len(CACHE_INTENTS)} exemples chargés")
    finally:
        release_conn(conn)

# ==========================================================
# ENCODE AVEC CACHE
# ==========================================================
def encode_avec_cache(message: str):
    key = hashlib.md5(message.encode()).hexdigest()
    if key in _embedding_cache:
        return _embedding_cache[key]
    emb = modele_embedding.encode([message], normalize_embeddings=True)
    _embedding_cache[key] = emb
    return emb

# ==========================================================
# DETECTION INTENTION
# ==========================================================
def detecter_intention(message: str):
    charger_intents()
    emb_msg    = encode_avec_cache(message)
    embeddings = np.array([_parse_embedding(i["embedding"]) for i in CACHE_INTENTS])
    scores     = cosine_similarity(emb_msg, embeddings)[0]

    best_index = int(np.argmax(scores))
    best_score = float(scores[best_index])
    best       = CACHE_INTENTS[best_index]

    top3_idx = np.argsort(scores)[::-1][:3]
    top3_exemples = [
        {
            "intent": CACHE_INTENTS[i]["intent_nom"],
            "phrase": CACHE_INTENTS[i]["phrase"],
            "score":  round(float(scores[i]), 3),
        }
        for i in top3_idx
    ]

    vus = {}
    for i in np.argsort(scores)[::-1]:
        nom = CACHE_INTENTS[i]["intent_nom"]
        if nom not in vus:
            vus[nom] = {
                "id_intent":      CACHE_INTENTS[i]["id_intent"],
                "intent_nom":     nom,
                "sous_intent":    CACHE_INTENTS[i]["sous_intent"],
                "score":          round(float(scores[i]), 3),
                "type_intent":    CACHE_INTENTS[i]["type_intent"],
                "action_handler": CACHE_INTENTS[i]["action_handler"],
                "phrase":         CACHE_INTENTS[i]["phrase"],
            }
        if len(vus) >= 5:
            break
    top_candidats = list(vus.values())

    logging.info(
        f"[INTENT] nom={best['intent_nom']} sous={best['sous_intent']} "
        f"score={best_score:.3f} type={best['type_intent']}"
    )
    if len(top_candidats) > 1:
        alts = " | ".join(
            f"{c['intent_nom']}({c['score']:.3f})" for c in top_candidats[1:]
        )
        logging.info(f"[INTENT ALT] {alts}")

    return (
        best["id_intent"], best["intent_nom"], best["sous_intent"],
        best_score, best["type_intent"], best["action_handler"],
        top3_exemples, top_candidats,
    )

# ==========================================================
# VÉRIFICATION GEMINI
# ==========================================================
def gemini_verifier_intent(message: str, intent_nom: str, reponse_candidate, top3: list) -> bool:
    # ── [FIX 3] normalisation défensive ──────────────────────
    if isinstance(reponse_candidate, (list, tuple)):
        reponse_candidate = reponse_candidate[0] if reponse_candidate else ""
        if isinstance(reponse_candidate, (list, tuple)):
            reponse_candidate = reponse_candidate[0] if reponse_candidate else ""
    reponse_candidate = str(reponse_candidate) if reponse_candidate else ""
    # ─────────────────────────────────────────────────────────

    cache_key = hashlib.md5(f"{message}:{intent_nom}".encode()).hexdigest()
    if cache_key in _verify_cache:
        return _verify_cache[cache_key]

    top3_str = "\n".join(
        f"  - intent={c['intent']} score={c['score']} exemple='{c['phrase']}'"
        for c in top3
    )
    prompt = f"""Tu es un vérificateur d'intention pour un chatbot CTEXI.

QUESTION : "{message}"
INTENTION DÉTECTÉE : "{intent_nom}"
RÉPONSE CANDIDATE : "{reponse_candidate[:200]}..."
TOP 3 :
{top3_str}

Est-ce que "{intent_nom}" correspond VRAIMENT à la question ?
Réponds UNIQUEMENT par OUI ou NON."""
    try:
        resp = gemini_model.generate_content(prompt)
        if resp and resp.text:
            is_valid = "OUI" in resp.text.strip().upper()
            _verify_cache[cache_key] = is_valid
            logging.info(f"[VERIFY] intent={intent_nom} → {'OUI' if is_valid else 'NON'}")
            return is_valid
    except Exception as e:
        logging.error(f"[VERIFY ERROR] {e}")
    return True

# ==========================================================
# SÉLECTION GEMINI parmi les candidats
# ==========================================================
def gemini_choisir_meilleur_intent(message: str, candidats: list) -> dict | None:
    if not candidats:
        return None

    cache_key = hashlib.md5(
        f"choose:{message}:{'|'.join(c['intent_nom'] for c in candidats)}".encode()
    ).hexdigest()
    if cache_key in _verify_cache:
        nom_choisi = _verify_cache[cache_key]
        if nom_choisi == "AUCUN":
            return None
        return next((c for c in candidats if c["intent_nom"] == nom_choisi), None)

    liste_str = "\n".join(
        f"  {i+1}. intent={c['intent_nom']} score={c['score']:.3f} exemple='{c['phrase']}'"
        for i, c in enumerate(candidats)
    )
    prompt = f"""Tu es un sélecteur d'intention pour un chatbot CTEXI.

QUESTION DE L'UTILISATEUR : "{message}"

INTENTIONS CANDIDATES :
{liste_str}

Quelle intention correspond le mieux à la question ?
Réponds UNIQUEMENT avec le nom exact de l'intention ou "AUCUN"."""

    try:
        resp = gemini_model.generate_content(prompt)
        if resp and resp.text:
            choix = resp.text.strip().upper()
            if choix == "AUCUN":
                _verify_cache[cache_key] = "AUCUN"
                logging.info(f"[CHOOSE] → AUCUN pour '{message[:40]}'")
                return None
            for c in candidats:
                if c["intent_nom"].upper() == choix:
                    _verify_cache[cache_key] = c["intent_nom"]
                    logging.info(f"[CHOOSE] → {c['intent_nom']} score={c['score']:.3f}")
                    return c
            for c in candidats:
                if c["intent_nom"].upper() in choix or choix in c["intent_nom"].upper():
                    _verify_cache[cache_key] = c["intent_nom"]
                    logging.info(f"[CHOOSE fuzzy] → {c['intent_nom']}")
                    return c
    except Exception as e:
        logging.error(f"[CHOOSE ERROR] {e}")

    return None

# ==========================================================
# [FIX 1] GET REPONSE DB
# ==========================================================
def get_reponse_intention(id_intent: int, sous_intent: str):
    cache_key = f"{id_intent}:{sous_intent}"

    if cache_key in _reponse_cache:
        logging.info("[CACHE] réponse DB hit")
        rows = _reponse_cache[cache_key]
        if not rows:
            return None
        return random.choice(rows)[0]

    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT reponse FROM chatbot.intent_responses
            WHERE id_intent = %s AND sous_intent = %s
            ORDER BY priorite DESC
        """, (id_intent, sous_intent))
        rows = cur.fetchall()
        cur.close()
        _reponse_cache[cache_key] = rows
    finally:
        release_conn(conn)

    if not rows:
        return None
    return random.choice(rows)[0]

# ==========================================================
# HISTORIQUE
# ==========================================================
def get_conversation_history(id_user, limit=8):
    try:
        conn = get_conn()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("""
                SELECT message_user, reponse_bot
                FROM chatbot.conversations
                WHERE id_user = %s
                ORDER BY created_at DESC LIMIT %s
            """, (id_user, limit))
            rows = cur.fetchall()
            cur.close()
        finally:
            release_conn(conn)
        rows.reverse()
        history = []
        for row in rows:
            if row["message_user"]:
                history.append({"role": "user",      "content": row["message_user"]})
            if row["reponse_bot"]:
                history.append({"role": "assistant", "content": row["reponse_bot"]})
        return history
    except Exception as e:
        logging.error(f"[HISTORY ERROR] {e}")
        return []

# ==========================================================
# SAUVEGARDE
# ==========================================================
def sauvegarder_conversation(
    id_user, message_user, reponse_bot,
    id_intent=None, type_intent=None, action_handler=None, confidence=None
):
    try:
        if isinstance(id_intent, str):
            id_intent = None
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO chatbot.conversations
                    (id_user, id_intent, message_user, reponse_bot,
                     type_intent, action_handler, confidence)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (id_user, id_intent, message_user, reponse_bot,
                  type_intent, action_handler, confidence))
            conn.commit()
            cur.close()
        finally:
            release_conn(conn)
    except Exception as e:
        logging.error(f"[DB ERROR] {e}")

def sauvegarder_conversation_async(
    id_user, message_user, reponse_bot,
    id_intent=None, type_intent=None, action_handler=None, confidence=None
):
    _executor.submit(
        sauvegarder_conversation,
        id_user, message_user, reponse_bot,
        id_intent, type_intent, action_handler, confidence
    )

# ==========================================================
# DOMAINE
# ==========================================================
def verifier_domaine_llm(message: str) -> bool:
    cache_key = hashlib.md5(message.lower().encode()).hexdigest()
    if cache_key in _domain_llm_cache:
        return _domain_llm_cache[cache_key]

    prompt = f"""Tu es un classificateur IA.
Détermine si le message concerne les services CTEXI.
CTEXI : fret maritime et aérien, cargo, colis, suivi colis, paiement international,
sourcing Chine, voyage business, visa Chine, formation import-export,
taux de change, devises, achats Chine.
MESSAGE : "{message}"
Salutations, remerciements et messages sociaux → OUI.
Réponds UNIQUEMENT par OUI ou NON."""
    try:
        resp = gemini_model.generate_content(prompt)
        if resp and resp.text:
            is_valid = "OUI" in resp.text.strip().upper()
            _domain_llm_cache[cache_key] = is_valid
            return is_valid
    except Exception as e:
        logging.error(f"[DOMAIN ERROR] {e}")
    return True

def reponse_hors_domaine_llm(message: str) -> str:
    prompt = f"""Tu es CTEXI-BOT l'assistant de Ctexi. 
    
- L'utilisateur pose une question hors domaine : "{message}"
- Dis lui poliment que tu es désolé mais cela ne releve pas de tes competances, tes competances se limite dans le domaine dans le domaine du fret maritime et aérien de CTEXI .
- Propose : Ctexi Buy, Ctexi Travel, Ctexi Pay, Ctexi Cargo, Ctexi Académie.
- Propose lui aussi de contacter nos agent pour plus d'eclaircissement
2 phrases max, chaleureux, emojis modérés. Même langue."""
    try:
        resp = gemini_model.generate_content(prompt)
        if resp and resp.text:
            return markdown.markdown(resp.text.strip())
    except Exception as e:
        logging.error(f"[OUT DOMAIN ERROR] {e}")
    return markdown.markdown(
        "Je suis CTEXI-BOT, spécialisé dans le fret maritime et aérien entre la Chine et le Burkina Faso 😊 "
        "Puis-je vous aider avec : cargo, achat, paiement, visa ou formation ?"
    )

# ==========================================================
# FORMATTER + REFORMULATION + FALLBACK
# ==========================================================
def formatter_operation_avec_llm(type_operation: str, message: str) -> str:
    if type_operation in ("service", "agent"):
        return markdown.markdown(message)
    prompt = f"Tu es CTEXI-BOT. TYPE: {type_operation}. MESSAGE: {message}\nAméliore uniquement le style. 2 phrases max. Même langue."
    try:
        resp = gemini_model.generate_content(prompt)
        if resp and resp.text:
            return markdown.markdown(resp.text.strip())
    except Exception as e:
        logging.error(f"[FORMATTER ERROR] {e}")
    return markdown.markdown(message)

# ==========================================================
# [FIX 2] REFORMULATION GEMINI
# ==========================================================
def reformuler_avec_gemini(message_user: str, reponse_brute, history=None) -> str:

    # ── [FIX 2] normalisation défensive du type ───────────────
    if isinstance(reponse_brute, (list, tuple)):
        reponse_brute = reponse_brute[0] if reponse_brute else ""
    if isinstance(reponse_brute, (list, tuple)):
        reponse_brute = reponse_brute[0] if reponse_brute else ""
    reponse_brute = str(reponse_brute).strip() if reponse_brute is not None else ""

    if not reponse_brute:
        logging.warning("[REFORMULATION] reponse_brute vide après normalisation")
        return markdown.markdown("Je n'ai pas pu trouver une réponse précise. Puis-je vous aider autrement ?")
    # ─────────────────────────────────────────────────────────

    if len(reponse_brute.split()) <= 8:
        logging.info("[OPT] reformulation court-circuitée (réponse courte)")
        return markdown.markdown(reponse_brute)

    historique = ""
    if history:
        for item in history[-4:]:
            historique += f"{item['role']}: {item['content']}\n"

    prompt = f"""Tu es CTEXI-BOT l'agent officiel de Ctexi (Cherif Trans Expert International —
fret maritime et aérien Chine → Burkina Faso).

HISTORIQUE : {historique}
QUESTION : {message_user}
RÉPONSE BRUTE : {reponse_brute}

- Améliore le style sans changer le sens.
- Utilise des listes à puces si la réponse est longue.
- Emojis modérés. Même langue. Sois bref (3-4 lignes max pour les réponses simples).
- INTERDIT : inventer prix/délais.
- Termine toujours par une proposition à l'utilisateur.

Retourne uniquement la réponse finale."""
    try:
        resp = gemini_model.generate_content(prompt)
        if resp and resp.text:
            return markdown.markdown(resp.text.strip())
    except Exception as e:
        logging.error(f"[REFORMULATION ERROR] {e}")
    return markdown.markdown(reponse_brute)

def gemini_direct_answer(message: str, history=None) -> str:
    historique = ""
    if history:
        for item in history[-6:]:
            role = "Bot" if item["role"] == "assistant" else "Utilisateur"
            historique += f"{role}: {item['content']}\n"
    prompt = f"""Tu es CTEXI-BOT, agent officiel de CTEXI (Cherif Trans Expert International —
devise : Au cœur du Sahel, au service du monde).
Services : Cargo, Buy (achat et sourcing), Pay (paiement RMB),
Travel (visa et réservation d'hôtel), Académie (formations sourcing et achat en Chine).

HISTORIQUE : {historique}

RÈGLES : ton professionnel et chaleureux. N'invente jamais prix/délais.
Si inconnu → invite à contacter un agent. Même langue. Tiens compte de l'historique.

NOUVEAU MESSAGE : {message}
RÉPONSE :"""
    try:
        resp = gemini_model.generate_content(prompt)
        if resp and resp.text:
            return markdown.markdown(resp.text.strip())
    except Exception as e:
        logging.error(f"[LLM FALLBACK ERROR] {e}")
    return "<p>Notre assistant est momentanément indisponible 😊</p>"

# ==========================================================
# OPÉRATIONS
# ==========================================================
def gerer_operations_par_nom(intent_nom: str, message: str, id_user) -> dict | None:
    action_handler = _ACTION_HANDLER_MAP.get(intent_nom)

    if intent_nom == "taux_change":
        result = convertir_operation(message)
        if not result:
            set_context(id_user, "taux_change")
            return {
                "type": "conversion",
                "reponse": "<p>💱 Veuillez préciser le montant et les devises.<br>Exemple : <b>100 USD en FCFA</b></p>",
                "trouve": False,
                # [FIX 4] type_intent et action_handler explicites pour dashboard
                "_type_intent": "operation",
                "_action_handler": action_handler,
                "_id_intent": None,
            }
        clear_context(id_user)
        msg = f"💱 {result['montant']} {result['source']} = {result['resultat']:.2f} {result['cible']}"
        return {
            "type": "conversion",
            "reponse": formatter_operation_avec_llm("conversion", msg),
            "trouve": True,
            "_type_intent": "operation",
            "_action_handler": action_handler,
            "_id_intent": None,
        }

    if intent_nom == "suivi_colis":
        code = est_code_colis(message)
        if not code:
            set_context(id_user, "suivi_colis")
            return {
                "type": "tracking",
                "reponse": "<p>📦 Veuillez envoyer votre code de suivi.<br>Exemple : <b>CTX10001</b></p>",
                "trouve": False,
                "_type_intent": "operation",
                "_action_handler": action_handler,
                "_id_intent": None,
            }
        clear_context(id_user)
        result = get_colis_info(code, id_user)
        if not result:
            return {
                "type": "tracking",
                "reponse": f"<p>❌ Aucun colis trouvé pour le code <b>{code}</b>.</p>",
                "trouve": False,
                "_type_intent": "operation",
                "_action_handler": action_handler,
                "_id_intent": None,
            }
        msg = f"📦 Colis {result['code']} — Statut : {result['statut']}"
        return {
            "type": "tracking",
            "reponse": formatter_operation_avec_llm("tracking", msg),
            "data": result, "trouve": True,
            "_type_intent": "operation",
            "_action_handler": action_handler,
            "_id_intent": None,
        }

    if intent_nom == "contact_agent":
        clear_context(id_user)
        return {
            "type": "agent",
            "reponse": "<p>👨‍💼 Choisissez un moyen de contact ci-dessous :</p>",
            "agent": get_agent(), "trouve": True,
            "_type_intent": "operation",
            "_action_handler": action_handler,
            "_id_intent": None,
        }

    if intent_nom == "service_info":
        clear_context(id_user)
        return {
            "type": "service",
            "reponse": "<p>📌 Voici les services disponibles chez CTEXI.</p>",
            "services": get_services(), "trouve": True,
            "_type_intent": "operation",
            "_action_handler": action_handler,
            "_id_intent": None,
        }

    return None

def gerer_operations(message: str, id_user) -> dict | None:
    op = detecter_operation(message)
    if not op:
        return None
    return gerer_operations_par_nom(op, message, id_user)

def _sauvegarder_op(id_user, message_original, op: dict, confidence=None):
    sauvegarder_conversation_async(
        id_user=id_user,
        message_user=message_original,
        reponse_bot=op.get("reponse", ""),
        id_intent=op.get("_id_intent"),
        type_intent=op.get("_type_intent"),     # toujours 'operation'
        action_handler=op.get("_action_handler"),
        confidence=confidence
    )

# ==========================================================
# MAIN ENGINE
# ==========================================================
def trouver_meilleure_correspondance(message: str, id_user):

    logging.info(f"[MSG] {message}")
    t_start          = time.time()
    message_original = message
    message          = nettoyer_message(message)
    msg_lower        = message.strip().lower().rstrip("!?.,;:")

    future_history = _executor.submit(get_conversation_history, id_user, 8)

    # --------------------------------------------------
    # ÉTAPE 1 — CONTEXTE OPÉRATIONNEL ACTIF
    # --------------------------------------------------
    ctx = get_context(id_user)
    if ctx:
        ctx_handler = _ACTION_HANDLER_MAP.get(ctx)

        # a) Annulation rapide
        if msg_lower in _MOTS_ANNULATION:
            clear_context(id_user)
            reponse = "<p>D'accord, pas de problème 👍 Comment puis-je vous aider ?</p>"
            # [FIX 4] type_intent='operation' explicite → pas compté en fallback
            sauvegarder_conversation_async(
                id_user=id_user,
                message_user=message_original,
                reponse_bot=reponse,
                type_intent="operation",
                action_handler=ctx_handler,
            )
            logging.info(f"[SOURCE] ANNULATION rapide ctx={ctx}")
            return {
                "type": "annulation",
                "reponse": reponse,
                "debug": {"source": "annulation_liste", "intent": ctx},
            }

        # b) Confirmation rapide
        if msg_lower in _MOTS_CONFIRMATION:
            logging.info(f"[SOURCE] CONFIRMATION rapide ctx={ctx}")
            op = gerer_operations_par_nom(ctx, message, id_user)
            if op:
                _sauvegarder_op(id_user, message_original, op)
                op["debug"] = {"source": f"confirmation_liste:{ctx}"}
                return op

        # c) Cas ambigu → Gemini décide
        history_for_ctx = future_history.result()
        decision = analyser_intention_contextuelle(message, history_for_ctx, ctx)
        logging.info(f"[CONTEXTE LLM] ctx={ctx} decision={decision}")

        if decision == "ANNULE":
            clear_context(id_user)
            reponse = "<p>D'accord, pas de problème 👍 Comment puis-je vous aider ?</p>"
            # [FIX 4] type_intent='operation' explicite
            sauvegarder_conversation_async(
                id_user=id_user,
                message_user=message_original,
                reponse_bot=reponse,
                type_intent="operation",
                action_handler=ctx_handler,
            )
            return {
                "type": "annulation",
                "reponse": reponse,
                "debug": {"source": "annulation_llm", "intent": ctx},
            }

        if decision in ("CONFIRME", "DONNEE"):
            op = gerer_operations_par_nom(ctx, message, id_user)
            if op:
                _sauvegarder_op(id_user, message_original, op)
                op["debug"] = {"source": f"contexte_llm:{ctx}", "decision": decision}
                return op

        if decision == "NOUVEAU":
            clear_context(id_user)
            logging.info("[CONTEXTE LLM] Nouvelle question → contexte effacé, pipeline normal")

    # --------------------------------------------------
    # ÉTAPE 2 — VÉRIFICATION DOMAINE
    # --------------------------------------------------
    if not verifier_domaine_llm(message):
        reponse = reponse_hors_domaine_llm(message)
        # [FIX 4] type_intent='hors_domaine' → pas compté en fallback LLM
        sauvegarder_conversation_async(
            id_user=id_user,
            message_user=message_original,
            reponse_bot=reponse,
            type_intent="hors_domaine",
            action_handler=None,
            confidence=0.0,
        )
        logging.info("[SOURCE] HORS DOMAINE")
        return {
            "type": "hors_domaine",
            "reponse": reponse,
            "debug": {"source": "domain_filter"},
        }

    # --------------------------------------------------
    # ÉTAPE 3 — OPÉRATIONS FUZZY/REGEX
    # --------------------------------------------------
    op = gerer_operations(message, id_user)
    if op:
        _sauvegarder_op(id_user, message_original, op)
        op["debug"] = {"source": "operation_fuzzy"}
        logging.info(f"[SOURCE] OPERATION FUZZY type={op['type']} durée={time.time()-t_start:.2f}s")
        return op

    # --------------------------------------------------
    # ÉTAPES 4-7 — EMBEDDING + PIPELINE HYBRIDE
    # --------------------------------------------------
    id_intent, intent_nom, sous_intent, score, type_intent, action_handler, \
        top3_exemples, top_candidats = detecter_intention(message)

    logging.info(f"[SCORE] intent={intent_nom} score={score:.3f} type={type_intent}")

    # ÉTAPE 4 — Opération via embedding
    if type_intent == "operation" and score >= SEUIL_BAS:
        op = gerer_operations_par_nom(intent_nom, message, id_user)
        if op:
            _sauvegarder_op(id_user, message_original, op, confidence=float(score))
            op["debug"] = {"source": "operation_embedding", "score": score}
            logging.info(f"[SOURCE] OPERATION EMBEDDING type={op['type']} score={score:.3f}")
            return op

    history = future_history.result()

    # ÉTAPE 5 — Score HAUT → DB + reformulation directe
    if score >= SEUIL_HAUT:
        reponse_brute = get_reponse_intention(id_intent, sous_intent)
        if reponse_brute:
            reponse_finale = reformuler_avec_gemini(message, reponse_brute, history)
            sauvegarder_conversation_async(
                id_user=id_user,
                message_user=message_original,
                reponse_bot=reponse_finale,
                id_intent=id_intent,
                type_intent=type_intent,
                action_handler=action_handler,
                confidence=float(score),
            )
            logging.info(f"[SOURCE] DB HAUT SCORE score={score:.3f} durée={time.time()-t_start:.2f}s")
            return {
                "type": "intent",
                "reponse": reponse_finale,
                "confidence": float(score),
                "debug": {"source": "db_haut_score", "intent": intent_nom, "score": score},
            }

    # ÉTAPE 6 — Score MOYEN → Gemini vérifie
    if score >= SEUIL_MOYEN:
        reponse_brute = get_reponse_intention(id_intent, sous_intent)
        if reponse_brute:
            if gemini_verifier_intent(message, intent_nom, reponse_brute, top3_exemples):
                reponse_finale = reformuler_avec_gemini(message, reponse_brute, history)
                sauvegarder_conversation_async(
                    id_user=id_user,
                    message_user=message_original,
                    reponse_bot=reponse_finale,
                    id_intent=id_intent,
                    type_intent=type_intent,
                    action_handler=action_handler,
                    confidence=float(score),
                )
                logging.info(f"[SOURCE] DB MOYEN SCORE vérifié score={score:.3f} durée={time.time()-t_start:.2f}s")
                return {
                    "type": "intent",
                    "reponse": reponse_finale,
                    "confidence": float(score),
                    "debug": {"source": "db_verifie", "intent": intent_nom, "score": score},
                }

            # 1er intent rejeté → candidats alternatifs
            logging.info(f"[RETRY] '{intent_nom}' rejeté → {len(top_candidats)-1} candidats alternatifs")
            candidats_alternatifs = [
                c for c in top_candidats[1:] if c["score"] >= SEUIL_MOYEN - 0.10
            ]

            if candidats_alternatifs:
                meilleur = gemini_choisir_meilleur_intent(message, candidats_alternatifs)
                if meilleur:
                    reponse_alt = get_reponse_intention(meilleur["id_intent"], meilleur["sous_intent"])
                    if reponse_alt:
                        reponse_finale = reformuler_avec_gemini(message, reponse_alt, history)
                        sauvegarder_conversation_async(
                            id_user=id_user,
                            message_user=message_original,
                            reponse_bot=reponse_finale,
                            id_intent=meilleur["id_intent"],
                            type_intent=meilleur["type_intent"],
                            action_handler=meilleur["action_handler"],
                            confidence=float(meilleur["score"]),
                        )
                        logging.info(
                            f"[SOURCE] DB CANDIDAT ALTERNATIF intent={meilleur['intent_nom']} "
                            f"score={meilleur['score']:.3f} durée={time.time()-t_start:.2f}s"
                        )
                        return {
                            "type": "intent",
                            "reponse": reponse_finale,
                            "confidence": float(meilleur["score"]),
                            "debug": {
                                "source": "db_candidat_alternatif",
                                "intent": meilleur["intent_nom"],
                                "score": meilleur["score"],
                            },
                        }

            logging.info("[RETRY] aucun candidat alternatif valide → LLM direct")

    # --------------------------------------------------
    # ÉTAPE 7 — Score BAS ou tous rejetés → Gemini direct
    # [FIX 4] type_intent='llm' explicite → identifiable en dashboard
    # --------------------------------------------------
    reponse_finale = gemini_direct_answer(message, history)
    sauvegarder_conversation_async(
        id_user=id_user,
        message_user=message_original,
        reponse_bot=reponse_finale,
        id_intent=None,
        type_intent="llm",           # 'llm' et non NULL → lisible en dashboard
        action_handler=None,
        confidence=float(score),
    )
    logging.info(f"[SOURCE] LLM DIRECT score={score:.3f} durée={time.time()-t_start:.2f}s")
    return {
        "type": "llm",
        "reponse": reponse_finale,
        "confidence": float(score),
        "debug": {"source": "llm_direct", "score": score},
    }