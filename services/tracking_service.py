from models.suivi_colis import recuperer_colis
from nlp.preprocess_colis import est_code_colis

def get_colis_info(message, user_id):
    code = est_code_colis(message)

    if not code:
        return None

    colis = recuperer_colis(code, user_id)

    if not colis:
        return None

    code, statut, type_colis, modes, derniere_maj = colis

    return {
        "code": code,
        "statut": statut,
        "type_colis": type_colis,
        "transport": modes,
        "derniere_maj": derniere_maj.strftime("%Y-%m-%d %H:%M")
    }

