# ==========================================================
# IMPORTS
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
_embedding_cache      = TTLCache(maxsize=500, ttl=3600)
_reponse_cache        = TTLCache(maxsize=200, ttl=60)
_domain_llm_cache     = TTLCache(maxsize=500, ttl=1800)

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
    _SESSION_CONTEXT[id_user] = {
        "intent": intent_nom,
        "ts": time.time()
    }
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
# VERIFICATION DOMAINE PAR LLM
# NOUVELLE COUCHE AVANT TOUT LE PIPELINE
# ==========================================================
def verifier_domaine_llm(message: str):

    cache_key = hashlib.md5(message.lower().encode()).hexdigest()

    if cache_key in _domain_llm_cache:
        return _domain_llm_cache[cache_key]

    prompt = f"""
Tu es un classificateur IA.

Ta mission :
Déterminer si le message utilisateur concerne
les services CTEXI.

CTEXI travaille dans :
- import/export Chine → Afrique
- cargo
- transport de colis
- suivi colis
- paiement international
- sourcing fournisseurs chinois
- voyage business Chine
- visa Chine
- formation import-export
- taux de change
- devises
- achats Chine

MESSAGE :
"{message}"

RÈGLES :
- Réponds UNIQUEMENT par :
OUI
ou
NON

- OUI si le message est lié directement ou indirectement
aux services CTEXI.
- NON si le sujet est hors domaine :
maths, médecine, football, politique, religion,
programmation générale, culture générale, etc.
"""

    try:
        resp = gemini_model.generate_content(prompt)

        if resp and resp.text:
            decision = resp.text.strip().upper()

            is_valid = "OUI" in decision

            _domain_llm_cache[cache_key] = is_valid

            logging.info(f"[DOMAIN LLM] {message} → {decision}")

            return is_valid

    except Exception as e:
        logging.error(f"[DOMAIN CHECK ERROR] {e}")

    return True

# ==========================================================
# REPONSE HORS DOMAINE
# ==========================================================
def reponse_hors_domaine_llm(message: str):

    prompt = f"""
Tu es CTEXI-BOT.

L'utilisateur a posé une question hors domaine.

MESSAGE :
{message}

RÈGLES :
- Ne réponds PAS à la question
- Explique poliment que tu es spécialisé
  uniquement dans les services CTEXI
- Ton chaleureux
- 2 phrases max
- Emojis modérés
- Même langue que le message
- Invite l'utilisateur à poser une question
  sur :
  cargo, achat Chine, paiement,
  suivi colis, visa ou formation

Retourne uniquement la réponse finale.
"""

    try:
        resp = gemini_model.generate_content(prompt)

        if resp and resp.text:
            return markdown.markdown(resp.text.strip())

    except Exception as e:
        logging.error(f"[OUT DOMAIN ERROR] {e}")

    return markdown.markdown(
        "Je suis spécialisé uniquement dans les services CTEXI 😊 "
        "Je peux vous aider concernant le cargo, le suivi de colis, "
        "les paiements internationaux, les achats Chine ou les formations."
    )

# ==========================================================
# PARSER EMBEDDING
# ==========================================================
def _parse_embedding(raw):

    if isinstance(raw, str):
        raw = raw.strip().lstrip("[").rstrip("]")
        return np.array(
            [float(x) for x in raw.split(",")],
            dtype=float
        )

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
        cur = conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        )

        cur.execute("""
            SELECT
                e.id,
                e.id_intent,
                i.nom AS intent_nom,
                i.type_intent,
                e.sous_intent,
                e.phrase,
                e.embedding
            FROM chatbot.intent_examples e
            JOIN chatbot.intention i
                ON i.id_intent = e.id_intent
            WHERE e.embedding IS NOT NULL
        """)

        CACHE_INTENTS      = cur.fetchall()
        _intents_last_load = now

        cur.close()

        logging.info(
            f"[INTENTS] {len(CACHE_INTENTS)} exemples chargés"
        )

    finally:
        release_conn(conn)

# ==========================================================
# ENCODE AVEC CACHE
# ==========================================================
def encode_avec_cache(message: str):

    key = hashlib.md5(message.encode()).hexdigest()

    if key in _embedding_cache:
        return _embedding_cache[key]

    emb = modele_embedding.encode(
        [message],
        normalize_embeddings=True
    )

    _embedding_cache[key] = emb

    return emb

# ==========================================================
# DETECTION INTENTION
# ==========================================================
def detecter_intention(message: str):

    charger_intents()

    emb_msg = encode_avec_cache(message)

    embeddings = np.array([
        _parse_embedding(i["embedding"])
        for i in CACHE_INTENTS
    ])

    scores = cosine_similarity(
        emb_msg,
        embeddings
    )[0]

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
        best["id_intent"],
        best["intent_nom"],
        best["sous_intent"],
        best_score,
        best["type_intent"]
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
            cur = conn.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            )

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
                history.append({
                    "role": "user",
                    "content": row["message_user"]
                })

            if row["reponse_bot"]:
                history.append({
                    "role": "assistant",
                    "content": row["reponse_bot"]
                })

        return history

    except Exception as e:
        logging.error(f"[HISTORY ERROR] {e}")
        return []

# ==========================================================
# SAUVEGARDE CONVERSATION
# ==========================================================
def sauvegarder_conversation(
    id_user,
    message_user,
    reponse_bot,
    id_intent=None,
    confidence=None
):

    try:

        if isinstance(id_intent, str):
            logging.warning(
                f"[WARN] id_intent string '{id_intent}' → None"
            )
            id_intent = None

        conn = get_conn()

        try:
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO chatbot.conversations
                (
                    id_user,
                    message_user,
                    reponse_bot,
                    id_intent,
                    confidence
                )
                VALUES (%s, %s, %s, %s, %s)
            """, (
                id_user,
                message_user,
                reponse_bot,
                id_intent,
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
    id_intent=None,
    confidence=None
):

    _executor.submit(
        sauvegarder_conversation,
        id_user,
        message_user,
        reponse_bot,
        id_intent,
        confidence
    )

# ==========================================================
# FORMATTER OPERATION
# ==========================================================
def formatter_operation_avec_llm(
    type_operation: str,
    message: str
):

    if type_operation in ("service", "agent"):
        return markdown.markdown(message)

    prompt = f"""
Tu es CTEXI-BOT.

TYPE : {type_operation}

MESSAGE :
{message}

Améliore uniquement le style.
Maximum 2 phrases.
Ton chaleureux.
Même langue que le message.

Retourne uniquement la réponse finale.
"""

    try:
        resp = gemini_model.generate_content(prompt)

        if resp and resp.text:
            return markdown.markdown(resp.text.strip())

    except Exception as e:
        logging.error(f"[FORMATTER ERROR] {e}")

    return markdown.markdown(message)

# ==========================================================
# REFORMULATION GEMINI
# ==========================================================
def reformuler_avec_gemini(
    message_user: str,
    reponse_brute: str,
    history=None
):

    if len(reponse_brute.split()) <= 8:
        return markdown.markdown(reponse_brute)

    historique = ""

    if history:
        for item in history[-4:]:
            historique += (
                f"{item['role']}: {item['content']}\n"
            )

    prompt = f"""
Tu es CTEXI-BOT.

HISTORIQUE :
{historique}

QUESTION :
{message_user}

RÉPONSE BRUTE :
{reponse_brute}

RÈGLES :
- garde exactement le même sens
- n'invente rien
- style moderne et professionnel
- emojis modérés
- même langue que la question
- termine par une ouverture utilisateur

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
def gemini_direct_answer(message: str, history=None):

    historique = ""

    if history:
        for item in history[-4:]:
            historique += (
                f"{item['role']}: {item['content']}\n"
            )

    prompt = f"""
Tu es CTEXI-BOT l'agent officiel de Ctexi une entreprise evoluant dans le fret maritime et aérien de la chine vers le Burkina faso.

CTEXI propose :
- cargo Chine → Burkina Faso
- achat fournisseurs chinois
- paiement international
- suivi colis
- voyage Chine
- visa
- formation import-export

HISTORIQUE :
{historique}

QUESTION :
{message}

RÈGLES :
- ne jamais inventer
- ton professionnel
- emojis modérés
- même langue
- si information inconnue :
  proposer contact agent

Retourne uniquement la réponse finale.
"""

    try:
        resp = gemini_model.generate_content(prompt)

        if resp and resp.text:
            return markdown.markdown(resp.text.strip())

    except Exception as e:
        logging.error(f"[LLM FALLBACK ERROR] {e}")

    return "<p>Assistant momentanément indisponible 😊</p>"

# ==========================================================
# GESTION OPERATIONS
# ==========================================================
def gerer_operations_par_nom(
    intent_nom: str,
    message: str,
    id_user
):

    if intent_nom == "taux_change":

        result = convertir_operation(message)

        if not result:

            set_context(id_user, "taux_change")

            return {
                "type": "conversion",
                "reponse":
                    "<p>💱 Veuillez préciser le montant "
                    "et les devises.<br>"
                    "Exemple : <b>100 USD en FCFA</b></p>",
                "trouve": False
            }

        clear_context(id_user)

        msg = (
            f"💱 {result['montant']} "
            f"{result['source']} "
            f"= {result['resultat']:.2f} "
            f"{result['cible']}"
        )

        return {
            "type": "conversion",
            "reponse":
                formatter_operation_avec_llm(
                    "conversion",
                    msg
                ),
            "trouve": True
        }

    if intent_nom == "suivi_colis":

        code = est_code_colis(message)

        if not code:

            set_context(id_user, "suivi_colis")

            return {
                "type": "tracking",
                "reponse":
                    "<p>📦 Veuillez envoyer votre "
                    "code de suivi.<br>"
                    "Exemple : <b>CTX10001</b></p>",
                "trouve": False
            }

        clear_context(id_user)

        result = get_colis_info(code, id_user)

        if not result:
            return {
                "type": "tracking",
                "reponse":
                    f"<p>❌ Aucun colis trouvé "
                    f"pour le code <b>{code}</b>.</p>",
                "trouve": False
            }

        msg = (
            f"📦 Colis {result['code']} "
            f"— Statut : {result['statut']}"
        )

        return {
            "type": "tracking",
            "reponse":
                formatter_operation_avec_llm(
                    "tracking",
                    msg
                ),
            "data": result,
            "trouve": True
        }

    if intent_nom == "contact_agent":

        clear_context(id_user)

        return {
            "type": "agent",
            "reponse":
                "<p>👨‍💼 Choisissez un moyen "
                "de contact ci-dessous :</p>",
            "agent": get_agent(),
            "trouve": True
        }

    if intent_nom == "service_info":

        clear_context(id_user)

        return {
            "type": "service",
            "reponse":
                "<p>📌 Voici les services "
                "disponibles chez CTEXI.</p>",
            "services": get_services(),
            "trouve": True
        }

    return None

# ==========================================================
# ROUTER OPERATIONS
# ==========================================================
def gerer_operations(message: str, id_user):

    op = detecter_operation(message)

    if not op:
        return None

    return gerer_operations_par_nom(
        op,
        message,
        id_user
    )

# ==========================================================
# MAIN ENGINE
# ==========================================================
def trouver_meilleure_correspondance(
    message: str,
    id_user
):

    logging.info(f"[MSG] {message}")

    t_start = time.time()

    message_original = message

    message = nettoyer_message(message)

    msg_lower = (
        message
        .strip()
        .lower()
        .rstrip("!?.,;:")
    )

    future_history = _executor.submit(
        get_conversation_history,
        id_user
    )

    # ======================================================
    # ETAPE -1
    # VERIFICATION DOMAINE PAR LLM
    # ======================================================
    is_ctexi_related = verifier_domaine_llm(message)

    if not is_ctexi_related:

        logging.info("[SOURCE] REFUS HORS DOMAINE LLM")

        reponse = reponse_hors_domaine_llm(message)

        sauvegarder_conversation_async(
            id_user,
            message_original,
            reponse
        )

        return {
            "type": "hors_domaine",
            "reponse": reponse,
            "debug": {
                "source": "llm_domain_filter",
                "llm_used": True
            }
        }

    # ======================================================
    # ETAPE 0a — ANNULATION
    # ======================================================
    if msg_lower in _MOTS_ANNULATION:

        ctx = get_context(id_user)

        if ctx:

            clear_context(id_user)

            reponse = (
                "<p>D'accord, opération annulée 👍 "
                "Comment puis-je vous aider ?</p>"
            )

            sauvegarder_conversation_async(
                id_user,
                message_original,
                reponse
            )

            return {
                "type": "annulation",
                "reponse": reponse,
                "debug": {
                    "source": "annulation"
                }
            }

    # ======================================================
    # ETAPE 0b — CONTEXTE ACTIF
    # ======================================================
    ctx = get_context(id_user)

    if ctx and msg_lower not in _MOTS_CONFIRMATION:

        logging.info(
            f"[CONTEXT ACTIVE] "
            f"user={id_user} intent={ctx}"
        )

        op = gerer_operations_par_nom(
            ctx,
            message,
            id_user
        )

        if op:

            sauvegarder_conversation_async(
                id_user,
                message_original,
                op["reponse"]
            )

            op["debug"] = {
                "source": f"context:{ctx}",
                "llm_used": False
            }

            return op

    # ======================================================
    # ETAPE 0c — CONFIRMATION
    # ======================================================
    if msg_lower in _MOTS_CONFIRMATION:

        ctx = get_context(id_user)

        if ctx:

            logging.info(
                f"[CONFIRMATION] "
                f"user={id_user} → {ctx}"
            )

            op = gerer_operations_par_nom(
                ctx,
                message,
                id_user
            )

            if op:

                sauvegarder_conversation_async(
                    id_user,
                    message_original,
                    op["reponse"]
                )

                op["debug"] = {
                    "source": f"confirmation:{ctx}",
                    "llm_used": False
                }

                return op

    # ======================================================
    # ETAPE 1 — OPERATIONS
    # ======================================================
    op = gerer_operations(message, id_user)

    if op:

        logging.info(
            f"[SOURCE] OPERATION={op['type']} "
            f"duree={time.time()-t_start:.2f}s"
        )

        sauvegarder_conversation_async(
            id_user,
            message_original,
            op["reponse"]
        )

        op["debug"] = {
            "source": "operation",
            "llm_used": False
        }

        return op

    # ======================================================
    # ETAPE 2 — EMBEDDINGS
    # ======================================================
    (
        id_intent,
        intent_nom,
        sous_intent,
        score,
        type_intent
    ) = detecter_intention(message)

    logging.info(
        f"[SCORE] intent={intent_nom} "
        f"score={score:.3f}"
    )

    # ======================================================
    # OPERATION VIA EMBEDDING
    # ======================================================
    if (
        type_intent == "operation"
        and score >= SEUIL_SIMPLE
    ):

        op = gerer_operations_par_nom(
            intent_nom,
            message,
            id_user
        )

        if op:

            sauvegarder_conversation_async(
                id_user,
                message_original,
                op["reponse"],
                id_intent,
                float(score)
            )

            op["debug"] = {
                "source": "operation_embedding",
                "llm_used": False
            }

            return op

    # ======================================================
    # DATABASE + GEMINI
    # ======================================================
    if score >= SEUIL_INTENT:

        reponse_brute = get_reponse_intention(
            id_intent,
            sous_intent
        )

        if reponse_brute:

            history = future_history.result()

            reponse_finale = reformuler_avec_gemini(
                message,
                reponse_brute,
                history
            )

            sauvegarder_conversation_async(
                id_user,
                message_original,
                reponse_finale,
                id_intent,
                float(score)
            )

            return {
                "type": "intent",
                "reponse": reponse_finale,
                "confidence": float(score),
                "debug": {
                    "source": "database_gemini",
                    "intent": intent_nom,
                    "llm_used": True
                }
            }

    # ======================================================
    # DATABASE DIRECT
    # ======================================================
    if score >= SEUIL_SIMPLE:

        reponse_brute = get_reponse_intention(
            id_intent,
            sous_intent
        )

        if reponse_brute:

            reponse_finale = markdown.markdown(
                reponse_brute
            )

            sauvegarder_conversation_async(
                id_user,
                message_original,
                reponse_finale,
                id_intent,
                float(score)
            )

            return {
                "type": "intent_direct",
                "reponse": reponse_finale,
                "confidence": float(score),
                "debug": {
                    "source": "database_direct",
                    "intent": intent_nom,
                    "llm_used": False
                }
            }

    # ======================================================
    # ETAPE FINALE — LLM FALLBACK
    # ======================================================
    logging.info("[SOURCE] LLM FALLBACK")

    history = future_history.result()

    reponse_llm = gemini_direct_answer(
        message,
        history
    )

    sauvegarder_conversation_async(
        id_user,
        message_original,
        reponse_llm,
        confidence=float(score)
    )

    logging.info(
        f"[DUREE] {time.time()-t_start:.2f}s"
    )

    return {
        "type": "llm",
        "reponse": reponse_llm,
        "confidence": float(score),
        "debug": {
            "source": "llm_only",
            "llm_used": True
        }
    }