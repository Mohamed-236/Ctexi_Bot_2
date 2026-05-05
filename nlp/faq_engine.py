# ==========================================================
# IMPORTS
# ==========================================================

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from models.db_connect import get_db_connection

import numpy as np
import psycopg2.extras
import logging

from models.suivi_colis import recuperer_colis
from nlp.preprocess_colis import est_code_colis
from nlp.netoyage import nettoyer_message

from services.controler.conversion_controler import convertir_operation
from services.agent_service import get_agent
from services.service_info import get_services

from router.operation_router import detecter_operation
from services.tracking_service import get_colis_info

from nlp.simple_intent import detecter_intent_light, repondre_intent_light

# ==========================================================
# LOGGING
# ==========================================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==========================================================
# MODELE
# ==========================================================
modele_embedding = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

SEUIL_INTENT = 0.6

# ==========================================================
# CACHE INTENT
# ==========================================================
CACHE_INTENTS = []

# ==========================================================
# CHARGEMENT INTENTS
# ==========================================================
def charger_intents():
    global CACHE_INTENTS

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("""
        SELECT id, id_intent, phrase, embedding
        FROM chatbot.intent_examples
        WHERE embedding IS NOT NULL
    """)

    CACHE_INTENTS = cur.fetchall()

    cur.close()
    conn.close()

    logging.info(f"{len(CACHE_INTENTS)} intents chargés")

# ==========================================================
# DETECTION INTENTION
# ==========================================================
def detecter_intention(message):

    global CACHE_INTENTS

    if not CACHE_INTENTS:
        charger_intents()

    embedding_message = modele_embedding.encode(
        [message],
        normalize_embeddings=True
    )

    embeddings = np.array([
        np.array(i["embedding"], dtype=float)
        for i in CACHE_INTENTS
    ])

    scores = cosine_similarity(embedding_message, embeddings)[0]

    best_index = np.argmax(scores)
    best_score = scores[best_index]

    best_intent = CACHE_INTENTS[best_index]["id_intent"]

    logging.info(f"Intent détecté: {best_intent} score={best_score:.4f}")

    return best_intent, best_score

# ==========================================================
# REPONSE INTENTION
# ==========================================================
def get_reponse_intention(id_intent):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT reponse
        FROM chatbot.intent_responses
        WHERE id_intent = %s
        LIMIT 1
    """, (id_intent,))

    row = cur.fetchone()

    cur.close()
    conn.close()

    return row[0] if row else None

# ==========================================================
# HELPERS
# ==========================================================
def safe_float(value, default=0.0):
    try:
        if isinstance(value, (list, tuple, np.ndarray)):
            value = value[0]
        return float(value)
    except:
        return default

def build_response(base: dict, confidence: float):
    base["confidence"] = safe_float(confidence)
    return base

def enlever_salutation(message: str):
    salutations = ["salut", "bonjour", "bonsoir", "hello", "cc", "coucou"]

    mots = message.lower().split()

    if mots and mots[0] in salutations:
        return " ".join(mots[1:]), mots[0]

    return message, None

# ==========================================================
# MOTEUR PRINCIPAL
# ==========================================================
def trouver_meilleure_correspondance(message_utilisateur, id_user):

    logging.info(f"Message: {message_utilisateur}")

    message_brut = message_utilisateur
    message_clean = nettoyer_message(message_utilisateur)

    # ==========================
    # INTENT SIMPLE
    # ==========================
    intent_light = detecter_intent_light(message_clean)

    if intent_light and len(message_clean.split()) <= 3:
        return build_response({
            "type": intent_light,
            "reponse": repondre_intent_light(intent_light),
            "trouve": True
        }, 0.95)

    # ==========================
    # SALUTATION
    # ==========================
    message_sans_salut, salutation_detectee = enlever_salutation(message_clean)

    salutation_response = None

    if salutation_detectee:
        intent_salut = detecter_intent_light(salutation_detectee)
        if intent_salut:
            salutation_response = repondre_intent_light(intent_salut)

    if not message_sans_salut.strip():
        if salutation_response:
            return build_response({
                "type": "salutation",
                "reponse": salutation_response,
                "trouve": True
            }, 0.95)

    message_utilisateur = message_sans_salut if message_sans_salut else message_clean

    # ==========================
    # OPERATIONS (prioritaire)
    # ==========================
    operation = detecter_operation(message_utilisateur)

    if operation == "suivi_colis":
        info = get_colis_info(message_brut, id_user)

        if info:
            reponse = "Voici les informations de votre colis"
        else:
            code = est_code_colis(message_brut)
            reponse = "Aucun colis trouvé ou code invalide." if code else "Veuillez entrer votre code colis."

        if salutation_response:
            reponse = f"{salutation_response}\n\n👉 {reponse}"

        return build_response({
            "type": "tracking",
            "reponse": reponse,
            "data": info,
            "trouve": bool(info)
        }, 1.0 if info else 0.8)

    if operation == "conversion":
        result = convertir_operation(message_brut)

        reponse = (
            f"{result['montant']} {result['source']} ≈ {result['resultat']} {result['cible']}"
            if result else "Exemple : 5000 FCFA en EUR"
        )

        if salutation_response:
            reponse = f"{salutation_response}\n\n👉 {reponse}"

        return build_response({
            "type": "conversion",
            "reponse": reponse,
            "trouve": bool(result)
        }, 1.0 if result else 0.7)

    if operation == "contact_agent":
        agent = get_agent()
        reponse = "Je vous mets en relation avec un agent" if agent else "Aucun agent disponible."

        if salutation_response:
            reponse = f"{salutation_response}\n\n👉 {reponse}"

        return build_response({
            "type": "agent",
            "reponse": reponse,
            "agent": agent,
            "trouve": bool(agent)
        }, 1.0 if agent else 0.6)

    if operation == "service_info":
        services = get_services()
        reponse = "Voici nos services disponibles"

        if salutation_response:
            reponse = f"{salutation_response}\n\n👉 {reponse}"

        return build_response({
            "type": "service",
            "reponse": reponse,
            "services": services,
            "trouve": True
        }, 1.0)

    # ==========================
    # INTENTION (NOUVEAU SYSTEME)
    # ==========================
    if len(message_utilisateur.split()) <= 2:
        return build_response({
            "type": "fallback",
            "reponse": "Pouvez-vous préciser votre demande ?",
            "trouve": False
        }, 0.4)

    intent_id, score = detecter_intention(message_utilisateur)

    if intent_id and score >= SEUIL_INTENT:
        reponse = get_reponse_intention(intent_id)

        if salutation_response:
            reponse = f"{salutation_response}\n\n👉 {reponse}"

        return build_response({
            "type": "intent",
            "reponse": reponse,
            "trouve": True
        }, score)

    # ==========================
    # FALLBACK FINAL
    # ==========================
    agent = get_agent()

    reponse = "Je ne comprends pas votre demande. Veuillez contacter un agent."

    if salutation_response:
        reponse = f"{salutation_response}\n\n👉 {reponse}"

    return build_response({
        "type": "agent" if agent else "fallback",
        "reponse": reponse,
        "agent": agent,
        "trouve": False
    }, 0.5) 