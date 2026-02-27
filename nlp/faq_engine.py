from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from models.db_connect import get_db_connection
from nlp.preprocessing import text_normaliser, text_lematiser
from difflib import get_close_matches
import numpy as np
import psycopg2
import psycopg2.extras
import random

# ==============================
# CONFIG
# ==============================

model = SentenceTransformer("all-mpnet-base-v2")
SEUIL_CONFIANCE = 0.65
FAQ_CACHE = []

# ==============================
# SALUTATIONS GROUPÉES (PRO)
# ==============================

SALUTATION_GROUPS = {
    ("bonjour", "salut", "hello", "hi"): [
        "Bonjour ! Comment puis-je vous aider aujourd'hui ?",
        "Salut ! Ravi de vous voir !",
        "Hello 👋 Que puis-je faire pour vous ?"
    ],
    ("ca va", "cava", "ça va"): [
        "Je vais bien merci 😊 Et vous ?",
        "Tout va bien de mon côté ! Et vous ?"
    ],
    ("au revoir", "bye"): [
        "Au revoir ! À bientôt 👋",
        "Bye ! Passez une excellente journée !"
    ],
    ("ok", "cool","yfy","d'accord"): [
        "Bien.Avez-vous d'autres question?",
        "Super!!! Si vous avez d'autres choses a me demander, n'hesitez pas!"
    ]
}

# ==============================
# CHARGEMENT FAQ
# ==============================

def charger_faq_depuis_db():
    global FAQ_CACHE
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT id_faq, message_user, reponse_bot, embedding FROM chatbot.faq")
    FAQ_CACHE = cur.fetchall()
    cur.close()
    conn.close()

# ==============================
# DETECTION SALUTATIONS
# ==============================
def detecter_salutation(message):
    """Cherche si le message correspond à un groupe de salutations/au revoir"""
    msg = text_normaliser(message)
    msg = text_lematiser(msg)
    
    for keys, reponses in SALUTATION_GROUPS.items():
        # Normaliser chaque clé
        normalized_keys = [text_normaliser(text_lematiser(k)) for k in keys]
        for key in normalized_keys:
            if get_close_matches(msg, [key], cutoff=0.6):
                return random.choice(reponses)
    return None

# ==============================
# MOTEUR PRINCIPAL
# ==============================

def trouver_meilleure_correspondance(message_utilisateur):
    global FAQ_CACHE

    #  Vérifier salutations
    reponse_salutation = detecter_salutation(message_utilisateur)
    if reponse_salutation:
        return {
            "reponse": reponse_salutation,
            "confiance": 1.0,
            "trouve": True
        }

    #  Charger FAQ si vide
    if not FAQ_CACHE:
        charger_faq_depuis_db()

    #  Embedding sur texte BRUT (important)
    user_embedding = model.encode([message_utilisateur])
    embeddings = np.array([faq["embedding"] for faq in FAQ_CACHE])

    scores = cosine_similarity(user_embedding, embeddings)[0]
    meilleur_index = np.argmax(scores)
    meilleure_confiance = scores[meilleur_index]

    print("Score max :", meilleure_confiance)  # DEBUG 

    # Vérifier seuil
    if meilleure_confiance < SEUIL_CONFIANCE:
        return {
            "reponse": "Je ne comprends pas bien votre demande. Pouvez-vous reformuler ?",
            "confiance": float(meilleure_confiance),
            "trouve": False
        }

    return {
        "reponse": FAQ_CACHE[meilleur_index]["reponse_bot"],
        "confiance": float(meilleure_confiance),
        "trouve": True
    }



'''from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from models.db_connect import get_db_connection
from nlp.preprocessing import text_normaliser, text_lematiser
import numpy as np
import psycopg2
import psycopg2.extras
import random
from difflib import get_close_matches

# Modèle d'embeddings
model = SentenceTransformer("all-mpnet-base-v2")
#model = SentenceTransformer("all-MiniLM-L6-v2")
SEUIL_CONFIANCE = 0.65
FAQ_CACHE = []

# Dictionnaire des salutations / au revoir
SALUTATIONS = {
    "bonjour": [
        "Bonjour ! Comment puis-je vous aider aujourd'hui ?",
        "Salut ! Ravi de vous voir !",
        "Bonjour 👋 Que puis-je faire pour vous ?"
    ],
    "salut": [
        "Salut ! Comment ça va ?",
        "Hey ! Que puis-je faire pour vous ?"
    ],
    "cava": [
        "Ça va bien, merci ! Et vous ?",
        "Je vais bien, merci ! Et toi ?"
    ],
    "ca va": [
        "Ça va bien, merci ! Et vous ?",
        "Je vais bien, merci ! Et toi ?"
    ],
    "hello": [
        "Hello ! Comment puis-je vous aider ?",
        "Salut ! Ravi de vous voir !"
    ],
    "hi": [
        "Hi there ! Que puis-je faire pour vous ?"
    ],
    "au revoir": [
        "Au revoir ! À bientôt 👋",
        "Bye ! Passez une bonne journée !",
        "À bientôt ! Prenez soin de vous !"
    ],
    "bye": [
        "Bye ! À la prochaine !",
        "Au revoir ! 👋"
    ],
    
}

def charger_faq_depuis_db():
    """Charge les FAQ depuis la base de données"""
    global FAQ_CACHE
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT id_faq, message_user, reponse_bot, embedding FROM chatbot.faq")
    FAQ_CACHE = cur.fetchall()
    cur.close()
    conn.close()

def trouver_salutation_fuzzy(message):
    """Cherche si le message correspond à une salutation / au revoir avec tolérance aux fautes"""
    msg = text_normaliser(message)
    msg = text_lematiser(message)
   
    for key in SALUTATIONS.keys():
        if get_close_matches(msg, [key], cutoff=0.6):
            return random.choice(SALUTATIONS[key])
    return None

def trouver_meilleure_correspondance(message_utilisateur):
    """Retourne la réponse la plus appropriée (FAQ ou salutation)"""
    global FAQ_CACHE


    #  Vérifier salutations / bye
    reponse_salutation = trouver_salutation_fuzzy(message_utilisateur)
    if reponse_salutation:
        return {
            "reponse": reponse_salutation,
            "confiance": 1.0,
            "trouve": True
        }

    # Charger la FAQ si nécessaire
    if not FAQ_CACHE:
        charger_faq_depuis_db()

        # Normaliser + lemmatiser avant d'embeddings
    #message_utilisateur = text_normaliser(message_utilisateur)
    #message_utilisateur = text_lematiser(message_utilisateur)

    # Calcul embeddings et similarité
    user_embedding = model.encode([message_utilisateur])
    embeddings = np.array([faq["embedding"] for faq in FAQ_CACHE])
    scores = cosine_similarity(user_embedding, embeddings)[0]

    # Trouver la meilleure correspondance
    meilleur_index = np.argmax(scores)
    meilleure_confiance = scores[meilleur_index]

    # Vérifier seuil de confiance
    if meilleure_confiance < SEUIL_CONFIANCE:
        return {
            "reponse": "Je ne comprends pas bien votre demande. Pouvez-vous reformuler ?",
            "confiance": float(meilleure_confiance),
            "trouve": False
        }

    #  Retourner la meilleure correspondance FAQ
    return {
        "reponse": FAQ_CACHE[meilleur_index]["reponse_bot"],
        "confiance": float(meilleure_confiance),
        "trouve": True
    }

'''