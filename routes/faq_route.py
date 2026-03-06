from flask import Blueprint, jsonify, request
from token_nize import token_required
from models.sauvergarde import sauvegarder_conversation


# Module NLP
from nlp.faq_engine import trouver_meilleure_correspondance

faq_bp = Blueprint("faq", __name__, url_prefix="/api/faq")


@faq_bp.route("/message", methods=["POST"])
@token_required
def chatbot_response():
    """
    Endpoint principal du chatbot.
    Analyse le message, retourne réponse ou contact agent si nécessaire.
    """

    data = request.get_json()
    message = data.get("message")

    if not message:
        return jsonify({"status": "error", "message": "Message manquant"}), 400

    # 🔹 Appel moteur NLP
    result = trouver_meilleure_correspondance(message)

    response_payload = {
        "status": "success",
        "user": request.user_name,
        "reponse": result["reponse"],
        "confidence_score": round(result["confiance"], 2),
        "matched": result["trouve"]
        
    }

    if result.get("agent"):
      response_payload["agent"] = result["agent"]

    # 🔹 Sauvegarde automatique dans la DB
    try:
        sauvegarder_conversation(
            id_user=request.user_id,
            message_utilisateur=message,
            reponse_bot=result["reponse"],
            intention=result.get("intention")
        )
    except Exception as e:
        print("Erreur lors de la sauvegarde:", e)

    return jsonify(response_payload), 200

