# ==========================================================
# nlp/faq_engine.py
# ==========================================================
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from concurrent.futures import ThreadPoolExecutor
from cachetools import TTLCache
from psycopg2 import pool as pg_pool

from models.db_connect import get_db_connection

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

# ==========================================================
# LOGGING
# ==========================================================
logging.basicConfig(level=logging.INFO)

# ==========================================================
# THREAD POOL
# ==========================================================
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
            host     = os.getenv("DB_HOST",     "localhost"),
            port     = int(os.getenv("DB_PORT", "5432")),
            dbname   = os.getenv("DB_NAME"),
            user     = os.getenv("DB_USER"),
            password = os.getenv("DB_PASSWORD"),
        )
        logging.info("[POOL] Connection pool initialisé")
    return _db_pool

def get_conn():
    return get_pool().getconn()

def release_conn(conn):
    get_pool().putconn(conn)

# ==========================================================
# EMBEDDING MODEL + PRECHAUFFAGE
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
SEUIL_INTENT = 0.70
SEUIL_SIMPLE = 0.50

# ==========================================================
# CACHE INTENTS
# ==========================================================
CACHE_INTENTS      = []
_intents_last_load = 0
_INTENTS_TTL       = 300

# ==========================================================
# CACHES
# ==========================================================
_embedding_cache  = TTLCache(maxsize=500, ttl=3600)
_reponse_cache    = TTLCache(maxsize=200, ttl=60)
_domain_llm_cache = TTLCache(maxsize=500, ttl=1800)

# ==========================================================
# MAPPING action_handler pour les opérations
# Permet de sauvegarder l'action_handler sans requête DB extra
# ==========================================================
_ACTION_HANDLER_MAP = {
    "taux_change":   "conversion_handler",
    "suivi_colis":   "suivi_handler",
    "contact_agent": "agent_handler",
    "service_info":  "service_handler",
}

# ==========================================================
# SESSION CONTEXT
# ==========================================================
_SESSION_CONTEXT = {}
_SESSION_TTL     = 300

_MOTS_CONFIRMATION = {
    "oui", "yes", "ok", "okay", "d'accord", "daccord",
    "bien sur", "bien sûr", "absolument", "exactement",
    "affirmatif", "yep", "ouais", "ouep", "yop",
    "allez", "vas-y", "vas y", "go", "continue",
    "continuer", "proceed", "allons-y", "allons y",
    "je veux", "pret", "prêt", "je suis pret",
    "je suis prêt", "parfait", "super", "nickel",
}

_MOTS_ANNULATION = {
    "non", "no", "nope", "annuler", "cancel", "stop",
    "laisse tomber", "pas maintenant", "plus tard",
    "ça va", "ca va", "c'est bon",
}

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
    if id_user in _SESSION_CONTEXT:
        del _SESSION_CONTEXT[id_user]
        logging.info(f"[CONTEXT CLEARED] user={id_user}")

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
# Charge aussi action_handler depuis chatbot.intention
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
                e.id,
                e.id_intent,
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
# Retourne : (id_intent, intent_nom, sous_intent, score,
#             type_intent, action_handler)
# ==========================================================
def detecter_intention(message: str):
    charger_intents()

    emb_msg    = encode_avec_cache(message)
    embeddings = np.array([_parse_embedding(i["embedding"]) for i in CACHE_INTENTS])
    scores     = cosine_similarity(emb_msg, embeddings)[0]
    best_index = int(np.argmax(scores))
    best_score = float(scores[best_index])
    best       = CACHE_INTENTS[best_index]

    logging.info(
        f"[INTENT] nom={best['intent_nom']} "
        f"sous={best['sous_intent']} "
        f"score={best_score:.3f} "
        f"type={best['type_intent']}"
    )

    return (
        best["id_intent"],        # INT  — clé FK pour conversations
        best["intent_nom"],       # STR  — nom lisible
        best["sous_intent"],      # STR  — sous-catégorie
        best_score,               # FLOAT
        best["type_intent"],      # 'information' | 'operation'
        best["action_handler"],   # STR | None — ex: 'conversion_handler'
    )

# ==========================================================
# GET REPONSE DB
# ==========================================================
def get_reponse_intention(id_intent: int, sous_intent: str):
    cache_key = f"{id_intent}:{sous_intent}"

    if cache_key in _reponse_cache:
        logging.info("[CACHE] réponse DB hit")
        rows = _reponse_cache[cache_key]
    else:
        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT reponse
                FROM chatbot.intent_responses
                WHERE id_intent   = %s
                  AND sous_intent = %s
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
def get_conversation_history(id_user, limit=6):
    try:
        conn = get_conn()
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("""
                SELECT message_user, reponse_bot
                FROM chatbot.conversations
                WHERE id_user = %s
                ORDER BY created_at DESC
                LIMIT %s
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
# SAUVEGARDE CONVERSATION
# Toutes les colonnes de la nouvelle table sont renseignées :
#   id_user, id_intent, message_user, reponse_bot,
#   type_intent, action_handler, confidence
# ==========================================================
def sauvegarder_conversation(
    id_user,
    message_user,
    reponse_bot,
    id_intent      = None,   # INT
    type_intent    = None,   # 'information' | 'operation'
    action_handler = None,   # ex: 'conversion_handler'
    confidence     = None    # FLOAT
):
    try:
        if isinstance(id_intent, str):
            logging.warning(f"[WARN] id_intent string '{id_intent}' → None")
            id_intent = None

        conn = get_conn()
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO chatbot.conversations (
                    id_user,
                    id_intent,
                    message_user,
                    reponse_bot,
                    type_intent,
                    action_handler,
                    confidence
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                id_user,
                id_intent,
                message_user,
                reponse_bot,
                type_intent,
                action_handler,
                confidence
            ))
            conn.commit()
            cur.close()
        finally:
            release_conn(conn)

    except Exception as e:
        logging.error(f"[DB ERROR] {e}")

def sauvegarder_conversation_async(
    id_user,
    message_user,
    reponse_bot,
    id_intent      = None,
    type_intent    = None,
    action_handler = None,
    confidence     = None
):
    """Fire & forget — ne bloque pas la réponse."""
    _executor.submit(
        sauvegarder_conversation,
        id_user,
        message_user,
        reponse_bot,
        id_intent,
        type_intent,
        action_handler,
        confidence
    )

# ==========================================================
# VÉRIFICATION DOMAINE PAR LLM
# ==========================================================
def verifier_domaine_llm(message: str) -> bool:
    cache_key = hashlib.md5(message.lower().encode()).hexdigest()

    if cache_key in _domain_llm_cache:
        return _domain_llm_cache[cache_key]

    prompt = f"""
Tu es un classificateur IA.

Détermine si le message concerne les services CTEXI.

CTEXI travaille dans :
import/export, cargo, colis, suivi colis, paiement international,
sourcing Chine, voyage business, visa Chine, formation import-export,
taux de change, devises, achats Chine.

MESSAGE : "{message}"

Réponds UNIQUEMENT par OUI ou NON.
OUI = lié directement ou indirectement aux services CTEXI.
NON = hors domaine (médecine, sport, politique, maths...).


- Les message social tel que les salutation, aurevoir, remerciement etc..ne font pas partie des hors domaine
"""
    try:
        resp = gemini_model.generate_content(prompt)
        if resp and resp.text:
            decision = resp.text.strip().upper()
            is_valid = "OUI" in decision
            _domain_llm_cache[cache_key] = is_valid
            logging.info(f"[DOMAIN] {message[:40]} → {decision}")
            return is_valid
    except Exception as e:
        logging.error(f"[DOMAIN CHECK ERROR] {e}")

    return True  # En cas d'erreur, on laisse passer

# ==========================================================
# RÉPONSE HORS DOMAINE
# ==========================================================
def reponse_hors_domaine_llm(message: str) -> str:
    prompt = f"""
Tu es CTEXI-BOT, assistant officiel de CTEXI.

L'utilisateur a posé une question hors de ton domaine.

Message : {message}

Règles :
- Ne réponds PAS à la question
- Explique poliment que tu es spécialisé CTEXI uniquement
- Propose d'aider sur : cargo, achat Chine, paiement,
  suivi colis, visa, formation
- 2 phrases max, ton chaleureux, emojis modérés
- Même langue que le message (FR ou EN)

Retourne uniquement la réponse finale.
"""
    try:
        resp = gemini_model.generate_content(prompt)
        if resp and resp.text:
            return markdown.markdown(resp.text.strip())
    except Exception as e:
        logging.error(f"[OUT DOMAIN ERROR] {e}")

    return markdown.markdown(
        "Je suis CTEXI-BOT, spécialisé dans l'import-export Chine → Afrique 😊 "
        "Je ne peux pas répondre à cette question, mais je suis là pour vous aider "
        "avec nos services : cargo, achat, paiement, visa ou formation !"
    )

# ==========================================================
# FORMATTER OPERATION
# ==========================================================
def formatter_operation_avec_llm(type_operation: str, message: str) -> str:
    if type_operation in ("service", "agent"):
        return markdown.markdown(message)

    prompt = f"""
Tu es CTEXI-BOT.
TYPE : {type_operation}
MESSAGE : {message}
Améliore uniquement le style. Maximum 2 phrases.
Ton chaleureux, emojis modérés. Même langue.
Retourne uniquement le message final.
"""
    try:
        resp = gemini_model.generate_content(prompt)
        if resp and resp.text:
            return markdown.markdown(resp.text.strip())
    except Exception as e:
        logging.error(f"[FORMATTER ERROR] {e}")
    return markdown.markdown(message)

# ==========================================================
# REFORMULATION AVEC GEMINI
# ==========================================================
def reformuler_avec_gemini(message_user: str, reponse_brute: str, history=None) -> str:
    if len(reponse_brute.split()) <= 8:
        logging.info("[OPT] reformulation court-circuitée")
        return markdown.markdown(reponse_brute)

    historique = ""
    if history:
        for item in history[-4:]:
            historique += f"{item['role']}: {item['content']}\n"

    prompt = f"""
Tu es CTEXI-BOT, assistant officiel de CTEXI (import-export Chine → Afrique).

HISTORIQUE : {historique}
QUESTION : {message_user}
RÉPONSE BRUTE : {reponse_brute}

RÈGLES :
- garde exactement le même sens, n'invente rien
- style naturel, moderne, professionnel, chaleureux
- emojis modérés
- réponse courte → 1 phrase fluide
- réponse longue → listes à puces structurées
- INTERDIT : inventer prix, délais ou services
- si besoin de prix/délai → propose de contacter un agent
- termine par une proposition à l'utilisateur
- même langue que la question (FR ou EN)

Retourne uniquement la réponse finale.
"""
    try:
        resp = gemini_model.generate_content(prompt)
        if resp and resp.text:
            return markdown.markdown(resp.text.strip())
    except Exception as e:
        logging.error(f"[REFORMULATION ERROR] {e}")
    return markdown.markdown(reponse_brute)

# ==========================================================
# GEMINI FALLBACK
# ==========================================================
def gemini_direct_answer(message: str, history=None) -> str:
    historique = ""
    if history:
        for item in history[-4:]:
            historique += f"{item['role']}: {item['content']}\n"

    prompt = f"""
Tu es CTEXI-BOT, agent officiel de CTEXI
(fret maritime et aérien Chine → Burkina Faso).

CTEXI propose :
- CTEXI Cargo    : transport marchandises Chine → Burkina & Afrique
- CTEXI Buy      : achat & sourcing fournisseurs chinois
- CTEXI Pay      : paiement international en RMB
- CTEXI Travel   : visa & voyages d'affaires Chine
- CTEXI Académie : formations import-export & e-commerce

HISTORIQUE : {historique}

RÈGLES :
- ton professionnel, chaleureux, emojis modérés
- n'invente jamais prix, délais ou services
- si inconnu → invite à contacter un agent
- INTERDIT : phrases d'intro inutiles
- même langue que la question (FR ou EN)

QUESTION : {message}
RÉPONSE :
"""
    try:
        resp = gemini_model.generate_content(prompt)
        if resp and resp.text:
            return markdown.markdown(resp.text.strip())
    except Exception as e:
        logging.error(f"[LLM FALLBACK ERROR] {e}")
    return "<p>Notre assistant est momentanément indisponible 😊</p>"

# ==========================================================
# GESTION DES OPÉRATIONS PAR NOM
# Source unique — fuzzy, embedding ET contexte utilisent cette fonction
# Chaque branche save son propre type_intent + action_handler
# ==========================================================
def gerer_operations_par_nom(intent_nom: str, message: str, id_user) -> dict | None:

    action_handler = _ACTION_HANDLER_MAP.get(intent_nom)

    if intent_nom == "taux_change":
        result = convertir_operation(message)
        if not result:
            set_context(id_user, "taux_change")
            return {
                "type":           "conversion",
                "reponse":        "<p>💱 Veuillez préciser le montant et les devises.<br>Exemple : <b>100 USD en FCFA</b></p>",
                "trouve":         False,
                "_type_intent":   "operation",
                "_action_handler": action_handler,
                "_id_intent":     None,
            }
        clear_context(id_user)
        msg = (
            f"💱 {result['montant']} {result['source']} "
            f"= {result['resultat']:.2f} {result['cible']}"
        )
        return {
            "type":           "conversion",
            "reponse":        formatter_operation_avec_llm("conversion", msg),
            "trouve":         True,
            "_type_intent":   "operation",
            "_action_handler": action_handler,
            "_id_intent":     None,
        }

    if intent_nom == "suivi_colis":
        code = est_code_colis(message)
        if not code:
            set_context(id_user, "suivi_colis")
            return {
                "type":           "tracking",
                "reponse":        "<p>📦 Veuillez envoyer votre code de suivi.<br>Exemple : <b>CTX10001</b></p>",
                "trouve":         False,
                "_type_intent":   "operation",
                "_action_handler": action_handler,
                "_id_intent":     None,
            }
        clear_context(id_user)
        result = get_colis_info(code, id_user)
        if not result:
            return {
                "type":           "tracking",
                "reponse":        f"<p>❌ Aucun colis trouvé pour le code <b>{code}</b>.</p>",
                "trouve":         False,
                "_type_intent":   "operation",
                "_action_handler": action_handler,
                "_id_intent":     None,
            }
        msg = f"📦 Colis {result['code']} — Statut : {result['statut']}"
        return {
            "type":           "tracking",
            "reponse":        formatter_operation_avec_llm("tracking", msg),
            "data":           result,
            "trouve":         True,
            "_type_intent":   "operation",
            "_action_handler": action_handler,
            "_id_intent":     None,
        }

    if intent_nom == "contact_agent":
        clear_context(id_user)
        return {
            "type":           "agent",
            "reponse":        "<p>👨‍💼 Choisissez un moyen de contact ci-dessous :</p>",
            "agent":          get_agent(),
            "trouve":         True,
            "_type_intent":   "operation",
            "_action_handler": action_handler,
            "_id_intent":     None,
        }

    if intent_nom == "service_info":
        clear_context(id_user)
        return {
            "type":           "service",
            "reponse":        "<p>📌 Voici les services disponibles chez CTEXI.</p>",
            "services":       get_services(),
            "trouve":         True,
            "_type_intent":   "operation",
            "_action_handler": action_handler,
            "_id_intent":     None,
        }

    return None

# Alias pour l'étape fuzzy/regex
def gerer_operations(message: str, id_user) -> dict | None:
    op = detecter_operation(message)
    if not op:
        return None
    return gerer_operations_par_nom(op, message, id_user)

# ==========================================================
# HELPER — sauvegarde depuis un dict résultat d'opération
# Lit les champs privés _type_intent / _action_handler / _id_intent
# puis appelle sauvegarder_conversation_async
# ==========================================================
def _sauvegarder_op(id_user, message_original, op: dict, confidence=None):
    sauvegarder_conversation_async(
        id_user        = id_user,
        message_user   = message_original,
        reponse_bot    = op.get("reponse", ""),
        id_intent      = op.get("_id_intent"),        # None pour les opérations
        type_intent    = op.get("_type_intent"),      # 'operation'
        action_handler = op.get("_action_handler"),   # ex: 'agent_handler'
        confidence     = confidence
    )

# ==========================================================
# MAIN ENGINE
#
# Flux :
#  -1. Vérification domaine LLM
#   0a. Annulation ("non/stop")
#   0b. Contexte actif + donnée utilisateur
#   0c. Confirmation ("oui/ok")
#   1.  Operation router (fuzzy + regex)
#   2.  Embedding type=operation
#   3.  score >= SEUIL_INTENT → DB + Gemini reformule
#   4.  score >= SEUIL_SIMPLE → DB directe
#   5.  LLM fallback
# ==========================================================
def trouver_meilleure_correspondance(message: str, id_user):

    logging.info(f"[MSG] {message}")
    t_start          = time.time()
    message_original = message
    message          = nettoyer_message(message)
    msg_lower        = message.strip().lower().rstrip("!?.,;:")

    future_history = _executor.submit(get_conversation_history, id_user)

    # --------------------------------------------------
    # ÉTAPE -1 — VÉRIFICATION DOMAINE
    # --------------------------------------------------
    is_ctexi = verifier_domaine_llm(message)
    if not is_ctexi:
        logging.info("[SOURCE] HORS DOMAINE")
        reponse = reponse_hors_domaine_llm(message)
        sauvegarder_conversation_async(
            id_user        = id_user,
            message_user   = message_original,
            reponse_bot    = reponse,
            id_intent      = None,
            type_intent    = None,
            action_handler = None,
            confidence     = 0.0
        )
        return {
            "type":    "hors_domaine",
            "reponse": reponse,
            "debug":   {"source": "domain_filter", "llm_used": True}
        }

    # --------------------------------------------------
    # ÉTAPE 0a — ANNULATION
    # --------------------------------------------------
    if msg_lower in _MOTS_ANNULATION:
        ctx = get_context(id_user)
        if ctx:
            clear_context(id_user)
            reponse = "<p>D'accord, opération annulée 👍 Comment puis-je vous aider ?</p>"
            sauvegarder_conversation_async(
                id_user        = id_user,
                message_user   = message_original,
                reponse_bot    = reponse,
                type_intent    = "operation",
                action_handler = _ACTION_HANDLER_MAP.get(ctx)
            )
            return {"type": "annulation", "reponse": reponse,
                    "debug": {"source": "annulation"}}

    # --------------------------------------------------
    # ÉTAPE 0b — CONTEXTE ACTIF (donnée attendue)
    # --------------------------------------------------
    ctx = get_context(id_user)
    if ctx and msg_lower not in _MOTS_CONFIRMATION:
        logging.info(f"[CONTEXT ACTIVE] user={id_user} intent={ctx}")
        op = gerer_operations_par_nom(ctx, message, id_user)
        if op:
            _sauvegarder_op(id_user, message_original, op)
            op["debug"] = {"source": f"contexte:{ctx}", "llm_used": False}
            return op

    # --------------------------------------------------
    # ÉTAPE 0c — CONFIRMATION "oui/ok/d'accord"
    # --------------------------------------------------
    if msg_lower in _MOTS_CONFIRMATION:
        ctx = get_context(id_user)
        if ctx:
            logging.info(f"[CONFIRMATION] user={id_user} → {ctx}")
            op = gerer_operations_par_nom(ctx, message, id_user)
            if op:
                _sauvegarder_op(id_user, message_original, op)
                op["debug"] = {"source": f"confirmation:{ctx}", "llm_used": False}
                return op

    # --------------------------------------------------
    # ÉTAPE 1 — OPÉRATIONS (fuzzy + regex)
    # --------------------------------------------------
    op = gerer_operations(message, id_user)
    if op:
        logging.info(f"[SOURCE] OPERATION={op['type']} durée={time.time()-t_start:.2f}s")
        _sauvegarder_op(id_user, message_original, op)
        op["debug"] = {"source": "operation", "llm_used": False}
        return op

    # --------------------------------------------------
    # ÉTAPE 2 — EMBEDDING INTENT MATCHING
    # --------------------------------------------------
    id_intent, intent_nom, sous_intent, score, type_intent, action_handler = \
        detecter_intention(message)

    logging.info(
        f"[SCORE] intent={intent_nom} sous={sous_intent} "
        f"score={score:.3f} type={type_intent}"
    )

    # Intent opération détecté par embedding
    if type_intent == "operation" and score >= SEUIL_SIMPLE:
        logging.info(f"[SOURCE] OPERATION VIA EMBEDDING → {intent_nom}")
        op = gerer_operations_par_nom(intent_nom, message, id_user)
        if op:
            _sauvegarder_op(id_user, message_original, op, confidence=float(score))
            op["debug"] = {"source": "operation_embedding", "llm_used": False}
            return op

    # Score fort → DB + Gemini reformule
    if score >= SEUIL_INTENT:
        reponse_brute = get_reponse_intention(id_intent, sous_intent)
        if reponse_brute:
            logging.info("[SOURCE] DATABASE + REFORMULATION GEMINI")
            history        = future_history.result()
            reponse_finale = reformuler_avec_gemini(message, reponse_brute, history)

            sauvegarder_conversation_async(
                id_user        = id_user,
                message_user   = message_original,
                reponse_bot    = reponse_finale,
                id_intent      = id_intent,        # INT 
                type_intent    = type_intent,       # 'information'
                action_handler = action_handler,    # None pour information
                confidence     = float(score)
            )
            logging.info(f"[DURÉE] {time.time()-t_start:.2f}s")
            return {
                "type":       "intent",
                "reponse":    reponse_finale,
                "confidence": float(score),
                "debug": {
                    "source":      "database_gemini",
                    "intent":      intent_nom,
                    "sous_intent": sous_intent,
                    "llm_used":    True
                }
            }

    # Score moyen → DB directe sans Gemini
    if score >= SEUIL_SIMPLE:
        reponse_brute = get_reponse_intention(id_intent, sous_intent)
        if reponse_brute:
            logging.info(f"[SOURCE] DATABASE DIRECT (score={score:.3f})")
            reponse_finale = markdown.markdown(reponse_brute)

            sauvegarder_conversation_async(
                id_user        = id_user,
                message_user   = message_original,
                reponse_bot    = reponse_finale,
                id_intent      = id_intent,
                type_intent    = type_intent,
                action_handler = action_handler,
                confidence     = float(score)
            )
            logging.info(f"[DURÉE] {time.time()-t_start:.2f}s")
            return {
                "type":       "intent_direct",
                "reponse":    reponse_finale,
                "confidence": float(score),
                "debug": {
                    "source":      "database_direct",
                    "intent":      intent_nom,
                    "sous_intent": sous_intent,
                    "llm_used":    False
                }
            }

    # --------------------------------------------------
    # ÉTAPE 5 — LLM FALLBACK
    # --------------------------------------------------
    logging.info(f"[SOURCE] LLM FALLBACK (score={score:.3f})")
    history     = future_history.result()
    reponse_llm = gemini_direct_answer(message, history)

    sauvegarder_conversation_async(
        id_user        = id_user,
        message_user   = message_original,
        reponse_bot    = reponse_llm,
        id_intent      = None,
        type_intent    = None,
        action_handler = None,
        confidence     = float(score)
    )
    logging.info(f"[DURÉE] {time.time()-t_start:.2f}s")
    return {
        "type":       "llm",
        "reponse":    reponse_llm,
        "confidence": float(score),
        "debug":      {"source": "llm_only", "llm_used": True}
    }
