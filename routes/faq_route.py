from flask import Blueprint, jsonify, request
from token_nize import token_required
from models.sauvergarde import sauvegarder_conversation
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

    # Appel moteur NLP
    result = trouver_meilleure_correspondance(message)


    response_payload = {
    "status": "success",
    "user": request.user_name,
    "type": result.get("type"),
    "reponse": result.get("reponse"),
    "services": result.get("services"),
    "agent": result.get("agent"),
    "confidence_score": round(result.get("confiance", 0), 2),
    "matched": result.get("trouve")
}

    

    if result.get("agent"):
       response_payload["agent"] = result["agent"]

    # Sauvegarde automatique dans la DB
    try:
        sauvegarder_conversation(
            id_user=request.user_id,
            message_utilisateur=message,
            reponse_bot=result["reponse"],
            intention=result.get("intention")
        )
    except Exception as e:
            print(f" Erreur lors de la sauvegarde pour user_id={request.user_id} : {e}")
        # Optionnel : inclure l'erreur dans la réponse pour debug
            response_payload["sauvegarde_error"] = str(e)

    return jsonify(response_payload), 200




