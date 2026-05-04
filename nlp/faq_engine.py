# ==========================================================
# IMPORTS
# ==========================================================

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from models.db_connect import get_db_connection
from models.contact_agent import recuperer_agent_par_intention
from models.service import recuperer_service_par_intention

import numpy as np
import psycopg2.extras
import logging

from models.suivi_colis import recuperer_colis
from nlp.preprocess_colis import est_code_colis
from nlp.netoyage import nettoyer_message

from services.conversion_service import convertir_devise
from nlp.extraction_devise import extraire_donnees_conversion

# ==========================================================
# OPERATIONS
# ==========================================================

from router.operation_router import detecter_operation
from services.tracking_service import get_colis_info
from services.controler.conversion_controler import convertir_operation
from services.agent_service import get_agent
from services.service_info import get_services

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

SEUIL_FAQ = 0.55
MARGE = 0.1

# ==========================================================
# CACHE
# ==========================================================
CACHE_FAQ = []

# ==========================================================
# CHARGEMENT FAQ
# ==========================================================
def charger_faq():
    global CACHE_FAQ

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("""
        SELECT id_faq, id_intent, message_user, reponse_bot, embedding
        FROM chatbot.faq
        WHERE embedding IS NOT NULL
    """)

    CACHE_FAQ = cur.fetchall()

    cur.close()
    conn.close()

    logging.info(f"{len(CACHE_FAQ)} FAQ chargées")

# ==========================================================
# TOP-K FAQ
# ==========================================================
def rechercher_faq_top_k(embedding_message, top_k=5):
    global CACHE_FAQ

    if not CACHE_FAQ:
        charger_faq()

    embeddings = np.array([
        np.array(f["embedding"], dtype=float)
        for f in CACHE_FAQ
    ])

    scores = cosine_similarity(embedding_message, embeddings)[0]

    top_indices = np.argsort(scores)[-top_k:][::-1]
    top_faqs = [(CACHE_FAQ[i], scores[i]) for i in top_indices]

    best_faq, best_score = top_faqs[0]
    second_score = top_faqs[1][1] if len(top_faqs) > 1 else 0

    logging.info(f"BEST FAQ: {best_faq['message_user']} => {best_score:.4f}")

    if best_score < SEUIL_FAQ:
        return None, best_score

    gap = best_score - second_score

    if best_score >= 0.85:
        return {"type": "ok", "faq": best_faq}, best_score

    if gap < 0.03:
        return {
            "type": "incertain",
            "faq": best_faq,
            "suggestions": [f[0]["message_user"] for f in top_faqs[1:3]]
        }, best_score

    if SEUIL_FAQ <= best_score < (SEUIL_FAQ + MARGE):
        return {
            "type": "incertain",
            "faq": best_faq,
            "suggestions": [f[0]["message_user"] for f in top_faqs[1:3]]
        }, best_score

    return {"type": "ok", "faq": best_faq}, best_score

# ==========================================================
# HELPER CONFIDENCE
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

# ==========================================================
# MOTEUR PRINCIPAL
# ==========================================================
def enlever_salutation(message: str):
    salutations = ["salut", "bonjour", "bonsoir", "hello", "cc", "coucou"]

    mots = message.lower().split()

    if mots and mots[0] in salutations:
        return " ".join(mots[1:]), mots[0]

    return message, None

def trouver_meilleure_correspondance(message_utilisateur, id_user):

    logging.info(f"Message: {message_utilisateur}")

    # ==========================
    # 🔥 MESSAGE ORIGINAL
    # ==========================
    message_brut = message_utilisateur

    # ==========================
    # 🔥 NETTOYAGE NLP
    # ==========================
    message_clean = nettoyer_message(message_utilisateur)

    # ==========================
    # 🔥 INTENT SIMPLE (PRIORITAIRE)
    # ==========================
    intent_light = detecter_intent_light(message_clean)

    if intent_light and len(message_clean.split()) <= 3:
        return build_response({
            "type": intent_light,
            "reponse": repondre_intent_light(intent_light),
            "trouve": True
        }, 0.95)

    # ==========================
    # 🔥 SUPPRIMER SALUTATION
    # ==========================
    message_sans_salut, salutation_detectee = enlever_salutation(message_clean)

    salutation_response = None

    if salutation_detectee:
        intent_salut = detecter_intent_light(salutation_detectee)
        if intent_salut:
            salutation_response = repondre_intent_light(intent_salut)

    # si rien après salut → répondre juste salut
    if not message_sans_salut.strip():
        if salutation_response:
            return build_response({
                "type": "salutation",
                "reponse": salutation_response,
                "trouve": True
            }, 0.95)

    # message final à traiter
    message_utilisateur = message_sans_salut if message_sans_salut else message_clean

    # ==========================
    # 🔥 OPERATION DETECTION
    # ==========================
    operation = detecter_operation(message_utilisateur)

    # ==========================
    # TRACKING
    # ==========================
    if operation == "suivi_colis":

        info = get_colis_info(message_brut, id_user)

        if info:
            reponse = "Voici les informations de votre colis"

        else:
            code = est_code_colis(message_brut)

            if code:
                reponse = "Aucun colis trouvé ou code non attribué."

            else:
                reponse = "Veuillez entrer votre code colis CTExI."

        if salutation_response:
            reponse = f"{salutation_response}\n\n👉 {reponse}"

        return build_response({
            "type": "tracking",
            "reponse": reponse,
            "data": info if info else None,
            "trouve": bool(info)
        }, 1.0 if info else 0.8)

    # ==========================
    # CONVERSION
    # ==========================
    if operation == "conversion":

        result = convertir_operation(message_brut)

        if result:
            reponse = f"{result['montant']} {result['source']} ≈ {result['resultat']} {result['cible']}"
        else:
            reponse = "Exemple : 5000 FCFA en EUR"

        if salutation_response:
            reponse = f"{salutation_response}\n\n👉 {reponse}"

        return build_response({
            "type": "conversion",
            "reponse": reponse,
            "trouve": bool(result)
        }, 1.0 if result else 0.7)

    # ==========================
    # AGENT
    # ==========================
    if operation == "contact_agent":

        agent = get_agent()

        reponse = "Je vous mets en relation avec un agent" if agent else "Aucun agent disponible."

        if salutation_response:
            reponse = f"{salutation_response}\n\n👉 {reponse}"

        return build_response({
            "type": "agent" if agent else "fallback",
            "reponse": reponse,
            "agent": agent,
            "trouve": bool(agent)
        }, 1.0 if agent else 0.6)

    # ==========================
    # SERVICES
    # ==========================
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
    # 🔥 BLOQUER FAQ SI MESSAGE TROP COURT
    # ==========================
    if len(message_utilisateur.split()) <= 2:
        reponse = "Pouvez-vous préciser votre demande ?"

        if salutation_response:
            reponse = f"{salutation_response}\n\n👉 {reponse}"

        return build_response({
            "type": "fallback",
            "reponse": reponse,
            "trouve": False
        }, 0.4)

    # ==========================
    # FAQ (embedding)
    # ==========================
    embedding_message = modele_embedding.encode(
        [message_utilisateur],
        normalize_embeddings=True
    )

    faq, score = rechercher_faq_top_k(embedding_message)

    if faq and score >= 0.7:

        reponse = faq["faq"]["reponse_bot"]

        if salutation_response:
            reponse = f"{salutation_response}\n\n👉 {reponse}"

        return build_response({
            "type": "faq",
            "reponse": reponse,
            "trouve": True
        }, score)

    # ==========================
    # FALLBACK FINAL
    # ==========================
    agent = get_agent()

    reponse = "Je ne comprends pas votre demande.Merci de contacter un agent pour vous assiter."

    if salutation_response:
        reponse = f"{salutation_response}\n\n👉 {reponse}"

    if agent:
        return build_response({
            "type": "agent",
            "reponse": reponse,
            "agent": agent,
            "trouve": False
        }, 0.5)

    return build_response({
        "type": "fallback",
        "reponse": reponse,
        "trouve": False
    }, 0.3)