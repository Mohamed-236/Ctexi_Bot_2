from flask import Blueprint, jsonify, request, redirect
from models.db_connect import get_db_connection
from token_nize import token_required
import psycopg2

# Module NLP (traitement du langage naturel) personnalisé
from nlp.faq_engine import find_best_match
# - comprehension : fonction personnalisée pour analyser ou comprendre du texte



# =====================================================================
# ROUTE CHATBOT MESSAGE Api : http://localhost:5000/api/chatbot/message
# ====================================================================

faq_bp = Blueprint("faq", __name__, url_prefix="/api/faq")




@faq_bp.route("/message", methods=["POST"])

@token_required
def chatbot_response():

    data = request.get_json()
    message = data.get("message")

    if not message:
        return jsonify({"status": "error", "message": "Message manquant"}), 400

    # Récupération FAQ depuis base
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT message_user, reponse_bot FROM chatbot.faq")
    faq_data = cur.fetchall()
    conn.close()

    # Appel moteur NLP
    result = find_best_match(message, faq_data)

    return jsonify({
        "status": "success",
        "user": request.user_name,
        "response": result["response"],
        "confidence_score": round(result["confidence"], 2),
        "matched": result["matched"]
    }), 200
