import requests
import time

# ===========================
# CACHE DES TAUX
# ===========================

CACHE_TAUX = {
    "donnees": None,
    "timestamp": 0
}

DUREE_CACHE = 600  # 10 minutes


# ===========================
# RECUPERATION DES TAUX
# ===========================

def recuperer_taux(devise_base="USD"):
    """
    Récupère les taux de conversion depuis l'API
    avec gestion du cache pour éviter trop de requêtes
    """

    temps_actuel = time.time()

    # Vérifier si le cache est encore valide
    if (
        CACHE_TAUX["donnees"] and
        (temps_actuel - CACHE_TAUX["timestamp"] < DUREE_CACHE)
    ):
        return CACHE_TAUX["donnees"]

    # Appel API publique sans clé
    url = f"https://open.er-api.com/v6/latest/{devise_base}"

    try:
        reponse = requests.get(url)
        data = reponse.json()

        if data["result"] != "success":
            return None

        # Mise à jour du cache
        CACHE_TAUX["donnees"] = data["rates"]
        CACHE_TAUX["timestamp"] = temps_actuel

        return CACHE_TAUX["donnees"]

    except Exception:
        return None


# ===========================
# FONCTION DE CONVERSION
# ===========================
def convertir_devise(montant, devise_source, devise_cible):
    """
    Convertit un montant d'une devise vers une autre
    en passant par USD comme devise pivot
    """

    # 1. récupérer tous les taux avec USD comme base
    taux = recuperer_taux("USD")

    if not taux:
        return None

    # 2. vérifier que les devises existent
    if devise_source not in taux or devise_cible not in taux:
        return None

    # 3. convertir source → USD
    montant_usd = montant / taux[devise_source]

    # 4. convertir USD → cible
    montant_final = montant_usd * taux[devise_cible]

    return montant_final