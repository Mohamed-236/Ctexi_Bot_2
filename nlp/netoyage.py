import re
import unicodedata

def nettoyer_message(message: str) -> str:
    message = message.lower()

    # enlever accents
    message = ''.join(
        c for c in unicodedata.normalize('NFD', message)
        if unicodedata.category(c) != 'Mn'
    )

    # garder lettres + chiffres + espaces
    message = re.sub(r"[^a-z0-9\s]", " ", message)

    # espaces multiples
    message = re.sub(r"\s+", " ", message).strip()

    # repetition seulement sur lettres (PAS chiffres)
    message = re.sub(r"([a-z])\1{2,}", r"\1", message)

    return message