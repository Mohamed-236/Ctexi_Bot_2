# ==========================
# IMPORTS
# ==========================
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from models.db_connect import get_db_connection
import numpy as np
import psycopg2.extras
import logging

# ==========================
# CONFIG LOGGING
# ==========================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==========================
# CONFIG
# ==========================
model = SentenceTransformer("all-mpnet-base-v2")  # 768 dims
SEUIL_INTENTION_FIXE = 0.45
SEUIL_FAQ = 0.60
SEUIL_ADAPTATIF_MARGIN = 0.1  # tolérance pour intention

INTENTION_CACHE = []
FAQ_CACHE = []

# ==========================
# CHARGEMENT DES INTENTIONS
# ==========================
def charger_intentions():
    global INTENTION_CACHE
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT id_intent, nom, type_intent, embedding
        FROM chatbot.intention
        WHERE embedding IS NOT NULL
    """)
    INTENTION_CACHE = cur.fetchall()
    cur.close()
    conn.close()
    logging.info(f"{len(INTENTION_CACHE)} intentions chargées en mémoire")

# ==========================
# CHARGEMENT DES FAQ
# ==========================
def charger_faq():
    global FAQ_CACHE
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT id_faq, id_intent, message_user, reponse_bot, embedding
        FROM chatbot.faq
        WHERE embedding IS NOT NULL
    """)
    FAQ_CACHE = cur.fetchall()
    cur.close()
    conn.close()
    logging.info(f"{len(FAQ_CACHE)} FAQ chargées en mémoire")

# ==========================
# DETECTION D’INTENTION (avec logging)
# ==========================
def detecter_intention(message):
    global INTENTION_CACHE
    if not INTENTION_CACHE:
        charger_intentions()

    user_embedding = model.encode([message])
    intention_embeddings = np.array([np.array(i["embedding"], dtype=float) for i in INTENTION_CACHE])

    scores = cosine_similarity(user_embedding, intention_embeddings)[0]
    for i, s in enumerate(scores):
        logging.info(f"Intention '{INTENTION_CACHE[i]['nom']}' score: {s:.4f}")

    idx = np.argmax(scores)
    score_max = scores[idx]

    seuil_adaptatif = SEUIL_INTENTION_FIXE
    if score_max < SEUIL_INTENTION_FIXE and score_max > SEUIL_INTENTION_FIXE - SEUIL_ADAPTATIF_MARGIN:
        seuil_adaptatif = score_max - 0.01
        logging.info(f"Score proche du seuil, seuil adaptatif appliqué: {seuil_adaptatif:.4f}")

    logging.info(f"Intention choisie: '{INTENTION_CACHE[idx]['nom']}' avec score {score_max:.4f}")

    if score_max < seuil_adaptatif:
        logging.info("Score inférieur au seuil, intention rejetée")
        return None, score_max

    return INTENTION_CACHE[idx], score_max

# ==========================
# RECHERCHE DANS FAQ PAR INTENTION (avec logging)
# ==========================
def chercher_dans_faq(message, id_intent):
    global FAQ_CACHE
    if not FAQ_CACHE:
        charger_faq()

    faq_filtrees = [f for f in FAQ_CACHE if f["id_intent"] == id_intent]
    if not faq_filtrees:
        logging.info(f"Aucune FAQ pour l'intention id {id_intent}")
        return None, 0

    user_embedding = model.encode([message])
    faq_embeddings = np.array([np.array(f["embedding"], dtype=float) for f in faq_filtrees])

    scores = cosine_similarity(user_embedding, faq_embeddings)[0]
    for i, f in enumerate(faq_filtrees):
        logging.info(f"FAQ '{f['message_user']}' score: {scores[i]:.4f}")

    idx = np.argmax(scores)
    score_max = scores[idx]

    if score_max < SEUIL_FAQ:
        logging.info(f"Score FAQ max {score_max:.4f} inférieur au seuil {SEUIL_FAQ}")
        return None, score_max

    logging.info(f"FAQ choisie: '{faq_filtrees[idx]['message_user']}' avec score {score_max:.4f}")
    return faq_filtrees[idx], score_max

# ==========================
# MOTEUR PRINCIPAL
# ==========================
def trouver_meilleure_correspondance(message_utilisateur):
    logging.info(f"Message utilisateur: {message_utilisateur}")

    intention, score_intention = detecter_intention(message_utilisateur)
    if not intention:
        return {
            "reponse": "Je ne comprends pas bien votre demande. Pouvez-vous reformuler ?",
            "confiance": float(score_intention),
            "trouve": False
        }

    faq, score_faq = chercher_dans_faq(message_utilisateur, intention["id_intent"])
    if not faq:
        return {
            "reponse": "Je comprends votre demande, mais je n'ai pas encore assez d'informations. Souhaitez-vous contacter un agent CTEXI ?",
            "confiance": float(score_faq),
            "trouve": False
        }

    return {
        "reponse": faq["reponse_bot"],
        "confiance": float(score_faq),
        "trouve": True,
        "intention": intention["nom"],
        "type": intention["type_intent"]
    }



