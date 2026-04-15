from models.suivi_colis import recuperer_colis

def get_colis_info(code_colis, user_id):
    """
    Aujourd'hui: DB simulée
    Demain: API mobile
    """

    colis = recuperer_colis(code_colis, user_id)

    if not colis:
        return None

    code, statut, type_colis, modes, derniere_maj = colis

    return {
        "code": code,
        "statut": statut,
        "type": type_colis,
        "transport": modes,
        "derniere_maj": derniere_maj.strftime("%Y-%m-%d %H:%M")
    }