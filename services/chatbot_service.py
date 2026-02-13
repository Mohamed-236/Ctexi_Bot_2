from nlp.logic_nlp import comprendre

def traiter_message(message):
    mots = comprendre(message)

    if "colis" in mots:
        return "Veuillez entrer votre code colis CTEXI"
    elif "visa" in mots:
        return "Voici les informations pour le visa Chine..."
    else:
        return "Je n'ai pas bien compris. Pouvez-vous reformuler ?"
