from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import random

# Chargement modèle une seule fois
model = SentenceTransformer("all-MiniLM-L6-v2")

SEUIL_CONFIANCE = 0.60

FAQ_CACHE = []
FAQ_EMBEDDINGS = None


def charger_faq_embeddings(faq_data):
    global FAQ_CACHE, FAQ_EMBEDDINGS

    FAQ_CACHE = faq_data
    questions = [item["message_user"] for item in faq_data]

    FAQ_EMBEDDINGS = model.encode(questions)


def trouver_meilleure_correspondance(message_utilisateur, faq_data):
    global FAQ_CACHE, FAQ_EMBEDDINGS

    # Charger embeddings une seule fois
    if not FAQ_CACHE:
        charger_faq_embeddings(faq_data)

    # Embedding utilisateur
    user_embedding = model.encode([message_utilisateur])

    # Similarité cosine
    scores = cosine_similarity(user_embedding, FAQ_EMBEDDINGS)[0]

    meilleur_index = np.argmax(scores)
    meilleure_confiance = scores[meilleur_index]

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


