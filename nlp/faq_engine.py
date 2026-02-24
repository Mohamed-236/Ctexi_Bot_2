from .preprocessing import normalize_text, lemmatize_text, nlp

# Seuil de confiance minimum pour considérer une réponse comme pertinente
CONFIDENCE_THRESHOLD = 0.65  # Seuil professionnel


def find_best_match(user_message, faq_data):
    """
    Trouve la meilleure correspondance entre le message de l'utilisateur
    et les questions de la FAQ, en utilisant la similarité sémantique de spaCy.
    
    Arguments :
    - user_message : str, le texte envoyé par l'utilisateur
    - faq_data : list de dicts, chaque dict contient :
        - "message_user" : question de la FAQ
        - "reponse_bot" : réponse associée à la question
    
    Retour :
    - dict contenant :
        - "response" : texte de la réponse
        - "confidence" : score de similarité
        - "matched" : True si la correspondance est supérieure au seuil
    """

    # 1. Normalisation + lemmatisation du message utilisateur
    normalized = normalize_text(user_message)         # nettoyage du texte (minuscules, ponctuation, etc.)
    lemmatized_user = lemmatize_text(normalized)     # réduction des mots à leur forme de base
    doc_user = nlp(lemmatized_user)                 # création d'un objet spaCy pour calculer la similarité

    # Initialisation des variables pour la meilleure correspondance
    best_score = 0
    best_answer = None

    # 2. Parcours de toutes les questions de la FAQ
    for faq in faq_data:
        # Normalisation et lemmatisation de la question de la FAQ
        question = normalize_text(faq["message_user"])
        lemmatized_question = lemmatize_text(question)
        doc_faq = nlp(lemmatized_question)

        # Calcul du score de similarité sémantique entre message utilisateur et question FAQ
        score = doc_user.similarity(doc_faq)

        # Mise à jour de la meilleure correspondance si le score est plus élevé
        if score > best_score:
            best_score = score
            best_answer = faq["reponse_bot"]

    # 3. Vérification si le score dépasse le seuil de confiance
    if best_score < CONFIDENCE_THRESHOLD:
        return {
            "response": "Je ne comprends pas bien votre demande. Pouvez-vous reformuler ?",
            "confidence": best_score,
            "matched": False
        }

    # 4. Retour de la réponse correspondante si seuil atteint
    return {
        "response": best_answer,
        "confidence": best_score,
        "matched": True
    }





