
from rapidfuzz import fuzz
from nlp.preprocess_colis import est_code_colis
from nlp.extraction_devise import extraire_donnees_conversion

SEUIL = 70

INTENTIONS = {
    "suivi_colis": [
        "suivre mon colis",
        "ou est mon colis",
        "localiser mon colis",
        "tracking colis",
        "suivi colis",
        "mon colis est ou"
    ],
    "conversion": [
        "conversion",
        "convertir",
        "converti",
        "taux de change",
        "changer argent",
        "convertir devise"
    ],
    "contact_agent": [
        "parler a un agent",
        "contacter support",
        "service client",
        "assistance",
        "humain",
        "agent"
    ],
    "service_info": [
        "vos services",
        "quels services",
        "offres",
        "que proposez vous",
        "services disponibles"
    ]
}

def detecter_operation(message: str):
    message_low = message.lower()

    # =========================
    # PRIORITE STRUCTURE
    # =========================

    if est_code_colis(message):
        return "suivi_colis"

    # 🔥 IMPORTANT : conversion même si incomplète
    if extraire_donnees_conversion(message):
        return "conversion"

    # =========================
    # FUZZY MATCHING
    # =========================

    best_intent = None
    best_score = 0

    for intent, phrases in INTENTIONS.items():
        for phrase in phrases:
            score = fuzz.partial_ratio(message_low, phrase)

            if score > best_score:
                best_score = score
                best_intent = intent

    if best_score >= SEUIL:
        return best_intent

    return None