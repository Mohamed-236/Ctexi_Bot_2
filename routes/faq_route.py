# ==========================================================
# routes/faq_route.py
# ==========================================================
from flask import Blueprint, jsonify, request
from token_nize import token_required
from nlp.faq_engine import trouver_meilleure_correspondance

faq_bp = Blueprint("faq", __name__, url_prefix="/api/faq")


@faq_bp.route("/message", methods=["POST"])
@token_required
def chatbot_response():
    """
    Endpoint principal du chatbot.
    La sauvegarde est gérée UNIQUEMENT dans faq_engine
    via sauvegarder_conversation_async — pas de double save.
    """
    data    = request.get_json()
    message = data.get("message", "").strip()
    id_user = request.user_id

    if not message:
        return jsonify({
            "status":  "error",
            "message": "Message manquant"
        }), 400

    # Appel moteur NLP — la sauvegarde est faite à l'intérieur
    result = trouver_meilleure_correspondance(message, id_user)

    response_payload = {
        "status":           "success",
        "user":             request.user_name,
        "type":             result.get("type"),
        "reponse":          result.get("reponse"),
        "services":         result.get("services"),
        "agent":            result.get("agent"),
        "data":             result.get("data"),
        "confidence_score": round(result.get("confidence", 0), 2),
        "matched":          result.get("trouve"),
    }

    return jsonify(response_payload), 200
