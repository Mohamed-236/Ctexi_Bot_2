import requests

def generer_reponse_llm(message, contexte=""):
    """
    Génère une réponse intelligente avec Phi
    """

    prompt = f"""
Tu es un assistant professionnel de CTEXI (import-export, voyage, formation, logistique).

Règles:
- Réponds clairement et de façon détaillée
- Utilise des sous-points si nécessaire
- Sois structuré
- Ne sois pas trop court
- Si possible, ajoute des étapes

Contexte entreprise:
{contexte}

Question utilisateur:
{message}

Réponse:
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "phi",
            "prompt": prompt,
            "stream": False
        }
    )

    if response.status_code == 200:
        return response.json()["response"]
    
    return "Désolé, une erreur est survenue."