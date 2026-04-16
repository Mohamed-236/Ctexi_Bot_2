import re
import unicodedata

def nettoyer_message(message: str) -> str:
    # minuscule
    message = message.lower()

    # enlever accents
    message = ''.join(
        c for c in unicodedata.normalize('NFD', message)
        if unicodedata.category(c) != 'Mn'
    )

    # enlever ponctuation
    message = re.sub(r"[^\w\s]", " ", message)

    # enlever espaces multiples
    message = re.sub(r"\s+", " ", message).strip()


    # enlever répétitions ex: biennnn → bien
    message = re.sub(r"(.)\1{2,}", r"\1", message)

    return message