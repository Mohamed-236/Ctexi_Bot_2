# ==========================================================
# IMPORTS
# ==========================================================

# SentenceTransformer : pour transformer des phrases en vecteurs numériques (embeddings)
from sentence_transformers import SentenceTransformer

# cosine_similarity : pour calculer la similarité entre deux vecteurs
from sklearn.metrics.pairwise import cosine_similarity

# Connexion à la base de données
from models.db_connect import get_db_connection

# Fonction pour récupérer un agent selon l'intention détectée
from models.contact_agent import recuperer_agent_par_intention
from models.service import recuperer_service_par_intention

# NumPy : pour manipuler des vecteurs et tableaux numériques
import numpy as np

# psycopg2.extras : permet d’obtenir des résultats de requêtes sous forme de dictionnaires
import psycopg2.extras

# logging : pour suivre l’exécution du code et déboguer
import logging


# ==========================================================
# CONFIGURATION DU LOGGING
# ==========================================================

# Configuration de base pour les logs
# level=logging.INFO : on veut voir les messages d'information et supérieurs
# format : indique comment le message sera affiché (date, niveau, message)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# ==========================================================
# CONFIGURATION DU MODELE D'EMBEDDING
# ==========================================================

# Chargement du modèle multilingue pour transformer les phrases en vecteurs
# Le modèle "paraphrase-multilingual-MiniLM-L12-v2" est rapide et efficace pour la similarité sémantique
modele_embedding = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# Seuil de confiance pour décider si une intention est suffisamment proche
SEUIL_INTENTION = 0.55

# Seuil de confiance pour décider si une FAQ correspond bien à l'intention
SEUIL_FAQ = 0.65

# Marge adaptative : ajustement léger du seuil si le score est proche mais légèrement inférieur
MARGE_ADAPTATIVE = 0.1


# ==========================================================
# CACHES (Mémoire temporaire)
# ==========================================================

# On garde les intentions et FAQ en mémoire pour ne pas interroger la DB à chaque requête
CACHE_INTENTIONS = []
CACHE_FAQ = []


# ==========================================================
# CHARGEMENT DES INTENTIONS
# ==========================================================

def charger_intentions():
    """
    Charge toutes les intentions depuis la base de données
    et les stocke dans CACHE_INTENTIONS.
    Chaque intention contient : id, nom, type et embedding.
    """
    global CACHE_INTENTIONS

    # Connexion à la base de données
    connexion = get_db_connection()
    curseur = connexion.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor  # résultats sous forme de dict
    )

    # Récupération des intentions qui ont un embedding
    curseur.execute("""
        SELECT id_intent, nom, type_intent, embedding
        FROM chatbot.intention
        WHERE embedding IS NOT NULL
    """)

    # Stockage en mémoire
    CACHE_INTENTIONS = curseur.fetchall()

    # Fermeture du curseur et de la connexion
    curseur.close()
    connexion.close()

    # Log du nombre d'intentions chargées
    logging.info(f"{len(CACHE_INTENTIONS)} intentions chargées en mémoire")


# ==========================================================
# CHARGEMENT DES FAQ
# ==========================================================

def charger_faq():
    """
    Charge toutes les FAQ depuis la base de données
    et les stocke dans CACHE_FAQ.
    Chaque FAQ contient : id, id_intent associé, message utilisateur, réponse du bot, embedding.
    """
    #global sert à indiquer qu’on veut utiliser la variable globale définie en dehors de la fonction, plutôt que de créer une nouvelle variable locale à l’intérieur de la fonction.
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
    Détecte l'intention la plus probable pour un message utilisateur.
    Retourne l'intention sélectionnée et le score de similarité.
    """
    global CACHE_INTENTIONS

    # Si les intentions ne sont pas encore chargées, on les charge
    if not CACHE_INTENTIONS:
        charger_intentions()

    # Transformation des embeddings des intentions en tableau NumPy
    # NumPy est optimisé pour faire des calculs vectoriels et matriciels très rapidement grâce à du code compilé.
    embeddings_intentions = np.array([
        np.array(intention["embedding"], dtype=float)
        for intention in CACHE_INTENTIONS
    ])

    # Calcul de la similarité cosinus entre le message utilisateur et toutes les intentions
    scores = cosine_similarity(
        embedding_message,
        embeddings_intentions
    )[0]

    # Logs détaillés des scores pour chaque intention
    for idx, score in enumerate(scores):
        logging.info(
            f"Intention '{CACHE_INTENTIONS[idx]['nom']}' score: {score:.4f}"
        )

    # Trouver l'indice de l'intention ayant le score maximum
    index_max = np.argmax(scores)
    score_max = scores[index_max]

    # Seuil à utiliser pour accepter l'intention
    seuil_utilise = SEUIL_INTENTION

    # Ajustement léger du seuil si le score est juste en dessous du seuil principal
    if SEUIL_INTENTION - MARGE_ADAPTATIVE < score_max < SEUIL_INTENTION:
        seuil_utilise = score_max - 0.01
        logging.info(f"Seuil adaptatif appliqué : {seuil_utilise:.4f}")

    # Si le score est trop faible, on rejette l'intention
    if score_max < seuil_utilise:
        logging.info("Intention rejetée (score insuffisant)")
        return None, score_max

    # Sélection de l'intention correspondante
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
    """
    Recherche la FAQ la plus pertinente pour une intention donnée.
    Retourne la FAQ sélectionnée et le score de similarité.
    """
    global CACHE_FAQ

    if not CACHE_FAQ:
        charger_faq()

    # Filtrer les FAQ associées à l'intention détectée
    faq_correspondantes = [
        faq for faq in CACHE_FAQ
        if faq["id_intent"] == id_intention
    ]

    if not faq_correspondantes:
        logging.info("Aucune FAQ associée à cette intention")
        return None, 0

    # Transformation des embeddings des FAQ en tableau NumPy
    embeddings_faq = np.array([
        np.array(faq["embedding"], dtype=float)
        for faq in faq_correspondantes
    ])

    # Calcul de la similarité cosinus entre le message utilisateur et les FAQ
    scores = cosine_similarity(
        embedding_message,
        embeddings_faq
    )[0]

    # Log des scores pour chaque FAQ
    for idx, faq in enumerate(faq_correspondantes):
        logging.info(
            f"FAQ '{faq['message_user']}' score: {scores[idx]:.4f}"
        )

    # Sélection de la FAQ ayant le score maximum
    index_max = np.argmax(scores)
    score_max = scores[index_max]

    # Si le score est trop faible, on ne renvoie rien
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
    Fonction principale pour trouver la meilleure réponse à un message utilisateur.
    - Détecte l'intention
    - Cherche la FAQ correspondante
    - Si l'intention est 'contact_agent', propose directement les boutons
    - Si aucune FAQ et agent dispo, propose contact agent
    - Sinon message fallback
    """

    logging.info(f"Message utilisateur : {message_utilisateur}")
    
    # Encodage du message utilisateur en vecteur (embedding)
    embedding_message = modele_embedding.encode(
        [message_utilisateur],
        normalize_embeddings=True
    )

    # Détection de l'intention
    intention, score_intention = detecter_intention(
        message_utilisateur,
        embedding_message
    )

    # Si aucune intention détectée
    if not intention:
        return {
            "type":"fallback",
            "reponse": "Je ne comprends pas bien votre demande. Pouvez-vous reformuler ?",
            "confiance": float(score_intention),
            "trouve": False
        }

    # ===========================
    # LOGIQUE CONTACT_AGENT
    # ===========================
    if intention["nom"] == "contact_agent":
        agent = recuperer_agent_par_intention(intention["id_intent"])
        if agent:
            return {
                "type": "agent",
                "reponse": "Je peux vous mettre en relation avec un agent. Choisissez un moyen de contact ci-dessous.",
                "confiance": float(score_intention),
                "trouve": True,
                "intention": intention["nom"],
                "agent": {
                    "whatsapp": agent["whatsapp"],
                    "telephone": agent["telephone"],
                    "email": agent["email"]
                }
            }
        else:
            return {
                "type": "fallback2",
                "reponse": "Aucun agent n'est disponible pour le moment.",
                "confiance": float(score_intention),
                "trouve": False,
                "intention": intention["nom"]
            }

    # ===========================
    # LOGIQUE SERVICE
    # ===========================
    if intention["nom"] == "service_info":

        services = recuperer_service_par_intention()

        return {
            "type": "service",
            "reponse": "Voici nos services disponible",
            "confiance": float(score_intention),
            "services" : services,
            "trouve": True,
            "intention": intention["nom"]
        }
    
    
        

    # ===========================
    # LOGIQUE FAQ (pour les autres intentions)
    # ===========================
    faq, score_faq = rechercher_faq(embedding_message, intention["id_intent"])
    if faq:
        return {
            "type":"faq",
            "reponse": faq["reponse_bot"],
            "confiance": float(score_faq),
            "trouve": True,
            "intention": intention["nom"]
        }

    # ===========================
    # LOGIQUE AGENT (si aucune FAQ trouvée)
    # ===========================
    agent = recuperer_agent_par_intention(intention["id_intent"])
    if agent:
        return {
            "type":"agent",
            "reponse": "Je ne connais pas encore la réponse exacte. Vous pouvez contacter un agent ci-dessous.",
            "confiance": float(score_intention),
            "trouve": False,
            "intention": intention["nom"],
            "agent": {
                "whatsapp": agent["whatsapp"],
                "telephone": agent["telephone"],
                "email": agent["email"]
            }
        }
    

    # ===========================
    # FALLBACK GENERIQUE
    # ===========================
    return {
        "type":"fallback2",
        "reponse": "Je ne trouve pas de réponse et aucun agent n'est disponible pour le moment.",
        "confiance": float(score_intention),
        "trouve": False,
        "intention": intention["nom"]
    }



