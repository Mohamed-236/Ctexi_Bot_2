import unicodedata
import re
import spacy

# Chargement du modèle français
nlp = spacy.load("fr_core_news_md")  # md pour meilleure sim


def text_normaliser(text: str) -> str:
    """
    Normalise le texte :
    - minuscule
    - suppression accents
    - gestion des apostrophes et contractions
    - suppression ponctuation
    - suppression espaces inutiles
    """

    text = text.lower()

    # Remplacer les apostrophes par un espace pour séparer correctement les mots
    text = text.replace("’", "'").replace("'", " ")

    # Supprimer accents
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore").decode("utf-8")

    # Supprimer ponctuation (sauf les lettres et chiffres)
    text = re.sub(r"[^\w\s]", "", text)

    # Supprimer espaces multiples
    text = re.sub(r"\s+", " ", text).strip()

    return text


def text_lematiser(text: str) -> str:
    """
    Retourne le texte lemmatisé (en ignorant les mots vides)
    """
    doc = nlp(text)
    lemmas = [token.lemma_ for token in doc if not token.is_stop]
    return " ".join(lemmas)