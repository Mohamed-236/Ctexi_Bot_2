import re

# ===========================
# MAPPING DES DEVISES
# ===========================

MAPPING_DEVISES = {
    # FCFA
    "fcfa": "XOF",
    "cfa": "XOF",
    "xof": "XOF",

    # EURO
    "euro": "EUR",
    "euros": "EUR",
    "eur": "EUR",

    # USD
    "usd": "USD",
    "dollar": "USD",
    "dollars": "USD",

    # YUAN
    "rmb": "CNY",
    "rnb": "CNY",   
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
        # 🔥 mot complet uniquement
        pattern = r"\b" + re.escape(mot) + r"\b"
        match = re.search(pattern, message)

        if match:
            positions.append((match.start(), code))

    if len(positions) < 2:
        return None

    # trier
    positions.sort()

    # 🔥 éviter doublon (XOF, XOF)
    codes_uniques = []
    for _, code in positions:
        if code not in codes_uniques:
            codes_uniques.append(code)

    if len(codes_uniques) < 2:
        return None

    return {
        "montant": montant,
        "devise_source": codes_uniques[0],
        "devise_cible": codes_uniques[1]
    }