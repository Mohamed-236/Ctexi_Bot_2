from nlp.preprocess_colis import est_code_colis
from nlp.extraction_devise import extraire_donnees_conversion

def detecter_operation(message: str):
    message_low = message.lower()

    # =========================
    # COLIS
    # =========================
    if est_code_colis(message):
        return "suivi_colis"

    # =========================
    # CONVERSION
    # =========================
    if extraire_donnees_conversion(message):
        return "conversion"

    # =========================
    # CONTACT AGENT
    # =========================
    if any(x in message_low for x in ["agent", "contact", "service client", "humain"]):
        return "contact_agent"

    # =========================
    # SERVICE INFO
    # =========================
    if any(x in message_low for x in ["service", "services", "proposez", "offres"]):
        return "service_info"

    return None