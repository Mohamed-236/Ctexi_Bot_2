import re

# ===========================
# MAPPING DES DEVISES
# ===========================

MAPPING_DEVISES = {
    "fcfa": "XOF",
    "cfa": "XOF",
    "xof": "XOF",
    "rmb": "CNY",
    "yuan": "CNY",
    "cny": "CNY"
}


# ===========================
# EXTRACTION DES INFOS
# ===========================
def extraire_donnees_conversion(message):
    message = message.lower()

    # montant
    match_montant = re.search(r"\d+(?:[\.,]\d+)?", message)
    if not match_montant:
        return None

    montant = float(match_montant.group().replace(",", "."))

    positions = []

    for mot, code in MAPPING_DEVISES.items():
        index = message.find(mot)
        if index != -1:
            positions.append((index, code))

    if len(positions) < 2:
        return None

    # trier selon position dans la phrase
    positions.sort()

    devise_source = positions[0][1]
    devise_cible = positions[1][1]

    return {
        "montant": montant,
        "devise_source": devise_source,
        "devise_cible": devise_cible
    }