from nlp.extraction_devise import extraire_donnees_conversion
from services.conversion_service import convertir_devise

def convertir_operation(message: str):
    data = extraire_donnees_conversion(message)

    if not data:
        return None

    resultat = convertir_devise(
        data["montant"],
        data["devise_source"],
        data["devise_cible"]
    )

    if resultat is None:
        return None

    return {
        "montant": data["montant"],
        "source": data["devise_source"],
        "cible": data["devise_cible"],
        "resultat": round(resultat, 2)
    }



    

