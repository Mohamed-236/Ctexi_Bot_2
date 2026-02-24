import unicodedata
import re
import spacy

# Chargement du modèle français
nlp = spacy.load("fr_core_news_md")  # md pour meilleure sim


def normalize_text(text):
    """
    Normalise le texte :
    - minuscule
    - suppression accents
    - suppression ponctuation
    - suppression espaces inutiles
    """

    text = text.lower()

    # Supprimer accents
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore").decode("utf-8")

    # Supprimer ponctuation
    text = re.sub(r"[^\w\s]", "", text)

    # Supprimer espaces multiples
    text = re.sub(r"\s+", " ", text).strip()

    return text


def lemmatize_text(text):
    """
    Retourne le texte lemmatisé
    """
    doc = nlp(text)
    lemmas = [token.lemma_ for token in doc if not token.is_stop]
    return " ".join(lemmas)
