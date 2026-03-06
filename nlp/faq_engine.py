# ==========================================================
# IMPORTS
# ==========================================================

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from models.db_connect import get_db_connection
from models.contact_agent import recuperer_agent_par_intention
import numpy as np
import psycopg2.extras
import logging


# ==========================================================
# CONFIGURATION DU LOGGING
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# ==========================================================
# CONFIGURATION DU MODELE D'EMBEDDING
# ==========================================================

modele_embedding = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

SEUIL_INTENTION = 0.55
SEUIL_FAQ = 0.65
MARGE_ADAPTATIVE = 0.1


# ==========================================================
# CACHES (Mémoire temporaire)
# ==========================================================

CACHE_INTENTIONS = []
CACHE_FAQ = []


# ==========================================================
# CHARGEMENT DES INTENTIONS
# ==========================================================

def charger_intentions():
    global CACHE_INTENTIONS

    connexion = get_db_connection()
    curseur = connexion.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    curseur.execute("""
        SELECT id_intent, nom, type_intent, embedding
        FROM chatbot.intention
        WHERE embedding IS NOT NULL
    """)

    CACHE_INTENTIONS = curseur.fetchall()

    curseur.close()
    connexion.close()

    logging.info(f"{len(CACHE_INTENTIONS)} intentions chargées en mémoire")


# ==========================================================
# CHARGEMENT DES FAQ
# ==========================================================

def charger_faq():
    global CACHE_FAQ

    connexion = get_db_connection()
    curseur = connexion.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    curseur.execute("""
        SELECT id_faq, id_intent, message_user, reponse_bot, embedding
        FROM chatbot.faq
        WHERE embedding IS NOT NULL
    """)

    CACHE_FAQ = curseur.fetchall()

    curseur.close()
    connexion.close()

    logging.info(f"{len(CACHE_FAQ)} FAQ chargées en mémoire")


# ==========================================================
# DETECTION D'INTENTION
# ==========================================================

def detecter_intention(message_utilisateur, embedding_message):
    global CACHE_INTENTIONS

    if not CACHE_INTENTIONS:
        charger_intentions()

    embeddings_intentions = np.array([
        np.array(intention["embedding"], dtype=float)
        for intention in CACHE_INTENTIONS
    ])

    scores = cosine_similarity(
        embedding_message,
        embeddings_intentions
    )[0]

    # Logs des scores
    for idx, score in enumerate(scores):
        logging.info(
            f"Intention '{CACHE_INTENTIONS[idx]['nom']}' score: {score:.4f}"
        )

    index_max = np.argmax(scores)
    score_max = scores[index_max]

    seuil_utilise = SEUIL_INTENTION

    # Seuil adaptatif léger
    if SEUIL_INTENTION - MARGE_ADAPTATIVE < score_max < SEUIL_INTENTION:
        seuil_utilise = score_max - 0.01
        logging.info(f"Seuil adaptatif appliqué : {seuil_utilise:.4f}")

    if score_max < seuil_utilise:
        logging.info("Intention rejetée (score insuffisant)")
        return None, score_max

    intention_selectionnee = CACHE_INTENTIONS[index_max]

    logging.info(
        f"Intention choisie : '{intention_selectionnee['nom']}' "
        f"avec score {score_max:.4f}"
    )

    return intention_selectionnee, score_max


# ==========================================================
# RECHERCHE DE LA MEILLEURE FAQ
# ==========================================================

def rechercher_faq(embedding_message, id_intention):
    global CACHE_FAQ

    if not CACHE_FAQ:
        charger_faq()

    faq_correspondantes = [
        faq for faq in CACHE_FAQ
        if faq["id_intent"] == id_intention
    ]

    if not faq_correspondantes:
        logging.info("Aucune FAQ associée à cette intention")
        return None, 0

    embeddings_faq = np.array([
        np.array(faq["embedding"], dtype=float)
        for faq in faq_correspondantes
    ])

    scores = cosine_similarity(
        embedding_message,
        embeddings_faq
    )[0]

    for idx, faq in enumerate(faq_correspondantes):
        logging.info(
            f"FAQ '{faq['message_user']}' score: {scores[idx]:.4f}"
        )

    index_max = np.argmax(scores)
    score_max = scores[index_max]

    if score_max < SEUIL_FAQ:
        logging.info("Score FAQ insuffisant")
        return None, score_max

    faq_selectionnee = faq_correspondantes[index_max]

    logging.info(
        f"FAQ choisie : '{faq_selectionnee['message_user']}' "
        f"avec score {score_max:.4f}"
    )

    return faq_selectionnee, score_max


# ==========================================================
# MOTEUR PRINCIPAL
# ==========================================================

def trouver_meilleure_correspondance(message_utilisateur):

    logging.info(f"Message utilisateur : {message_utilisateur}")
    

    # Encodage UNE SEULE FOIS
    embedding_message = modele_embedding.encode(
        [message_utilisateur],
        normalize_embeddings=True
    )

    # 1️⃣ Détection intention
    intention, score_intention = detecter_intention(
        message_utilisateur,
        embedding_message
    )

    if not intention:
        return {
            "reponse": "Je ne comprends pas bien votre demande. Pouvez-vous reformuler ?",
            "confiance": float(score_intention),
            "trouve": False
        }

    # 2️⃣ Recherche FAQ
    faq, score_faq = rechercher_faq(
        embedding_message,
        intention["id_intent"]
    )

    if faq:
        return {
            "reponse": faq["reponse_bot"],
            "confiance": float(score_faq),
            "trouve": True,
            "intention": intention["nom"]
        }
    
        # 3️⃣ Aucun FAQ → proposer agent
    agent = recuperer_agent_par_intention(intention["id_intent"])

    if agent:
        return {
            "reponse": "Je comprends votre demande mais je n'ai pas encore la réponse exacte. Vous pouvez contacter un agent CTEXI.",
            "confiance": float(score_intention),
            "trouve": False,
            "intention": intention["nom"],
            "agent": {
                "whatsapp": agent["whatsapp"],
                "telephone": agent["telephone"],
                "email": agent["email"]
            }
        }

    # 4️⃣ Aucun agent trouvé
    return {
        "reponse": "Je ne trouve pas de réponse et aucun agent n'est disponible pour le moment.",
        "confiance": float(score_intention),
        "trouve": False,
        "intention": intention["nom"]
    }


'''
    # 3️⃣ Aucun FAQ → chercher agent via id_intent
    agent = recuperer_agent_par_intention(intention["id_intent"])

    if agent:
        return {
            "reponse": (
                "Je comprends votre demande, mais je n'ai pas encore assez d'informations.Vous pouvez contacter un agent CTEXI \n\n"
                f"📱 WhatsApp : {agent['whatsapp']}\n"
                f"📞 Téléphone : {agent['telephone']}\n"
                f"📧 Email : {agent['email']}"
            ),
            "confiance": float(score_intention),
            "trouve": False,
            "intention": intention["nom"],
            "agent": agent
        }

    # 4️⃣ Aucun agent trouvé
    logging.info(
        f"Aucun agent actif pour intention {intention['id_intent']}"
    )

    return {
        "reponse": "Je ne trouve pas de réponse et aucun agent n'est disponible pour le moment.",
        "confiance": float(score_intention),
        "trouve": False,
        "intention": intention["nom"]
    }

'''

