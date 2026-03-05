# ==========================================================
# IMPORTS
# ==========================================================

# Permet de charger un modèle de génération d'embeddings
from sentence_transformers import SentenceTransformer

# Permet de calculer la similarité cosinus entre deux vecteurs
from sklearn.metrics.pairwise import cosine_similarity

# Fonction personnalisée pour se connecter à la base de données
from models.db_connect import get_db_connection

# Manipulation mathématique des tableaux
import numpy as np

# Permet de récupérer les résultats SQL sous forme de dictionnaire
import psycopg2.extras

# Pour afficher des logs propres dans la console
import logging


# ==========================================================
# CONFIGURATION DU LOGGING
# ==========================================================

# Format des messages affichés dans la console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# ==========================================================
# CONFIGURATION DU MODELE D'EMBEDDING
# ==========================================================

# Chargement du modèle multilingue
# Il comprend le français courant, familier et soutenu
modele_embedding = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# Seuil minimum pour accepter une intention
SEUIL_INTENTION = 0.45

# Seuil minimum pour accepter une FAQ
SEUIL_FAQ = 0.60

# Petite marge pour ajuster dynamiquement le seuil
MARGE_ADAPTATIVE = 0.1


# ==========================================================
# CACHES (Mémoire temporaire)
# ==========================================================

# Liste des intentions chargées en mémoire
CACHE_INTENTIONS = []

# Liste des FAQ chargées en mémoire
CACHE_FAQ = []


# ==========================================================
# CHARGEMENT DES INTENTIONS DEPUIS LA BASE
# ==========================================================

def charger_intentions():
    """
    Charge toutes les intentions qui possèdent un embedding
    et les stocke en mémoire pour éviter les requêtes répétées.
    """
    global CACHE_INTENTIONS

    connexion = get_db_connection()
    curseur = connexion.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    # On récupère uniquement les intentions déjà vectorisées
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
    """
    Charge toutes les FAQ ayant un embedding
    et les stocke en mémoire.
    """
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
    """
    Compare le message utilisateur avec toutes les intentions
    et retourne la plus proche si le score dépasse le seuil.
    """

    global CACHE_INTENTIONS

    # Si les intentions ne sont pas encore en mémoire
    if not CACHE_INTENTIONS:
        charger_intentions()

    # On transforme les embeddings stockés en tableau numpy
    embeddings_intentions = np.array([
        np.array(intention["embedding"], dtype=float)
        for intention in CACHE_INTENTIONS
    ])

    # Calcul de similarité entre message utilisateur et intentions
    scores = cosine_similarity(
        embedding_message,
        embeddings_intentions
    )[0]

    # Affichage des scores pour debug
    for index, score in enumerate(scores):
        nom_intention = CACHE_INTENTIONS[index]["nom"]
        logging.info(f"Intention '{nom_intention}' score: {score:.4f}")

    # On récupère l’index du score le plus élevé
    index_max = np.argmax(scores)
    score_max = scores[index_max]

    seuil_utilise = SEUIL_INTENTION

    # Si le score est proche du seuil, on adapte légèrement
    if (
        score_max < SEUIL_INTENTION
        and score_max > SEUIL_INTENTION - MARGE_ADAPTATIVE
    ):
        seuil_utilise = score_max - 0.01
        logging.info(f"Seuil adaptatif appliqué : {seuil_utilise:.4f}")

    intention_selectionnee = CACHE_INTENTIONS[index_max]

    logging.info(
        f"Intention choisie : '{intention_selectionnee['nom']}' "
        f"avec score {score_max:.4f}"
    )

    # Si le score est insuffisant → rejet
    if score_max < seuil_utilise:
        logging.info("Intention rejetée (score insuffisant)")
        return None, score_max

    return intention_selectionnee, score_max


# ==========================================================
# RECHERCHE DE LA MEILLEURE FAQ
# ==========================================================

def rechercher_faq(embedding_message, id_intention):
    """
    Recherche la FAQ la plus proche à l'intérieur
    d'une intention déjà détectée.
    """

    global CACHE_FAQ

    if not CACHE_FAQ:
        charger_faq()

    # Filtrer les FAQ appartenant à l'intention détectée
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

    for index, faq in enumerate(faq_correspondantes):
        logging.info(
            f"FAQ '{faq['message_user']}' score: {scores[index]:.4f}"
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
    """
    Fonction principale appelée par ton chatbot.
    """

    logging.info(f"Message utilisateur : {message_utilisateur}")

    # Encodage du message UNE SEULE FOIS
    embedding_message = modele_embedding.encode(
        [message_utilisateur],
        normalize_embeddings=True
    )

    # Étape 1 : détecter intention
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

    # Étape 2 : chercher FAQ
    faq, score_faq = rechercher_faq(
        embedding_message,
        intention["id_intent"]
    )

    if not faq:
        return {
            "reponse": "Je comprends votre demande, mais je n'ai pas encore assez d'informations. Souhaitez-vous contacter un agent CTEXI ?",
            "confiance": float(score_faq),
            "trouve": False
        }

    # Étape 3 : réponse finale
    return {
        "reponse": faq["reponse_bot"],
        "confiance": float(score_faq),
        "trouve": True,
        "intention": intention["nom"]
    }
