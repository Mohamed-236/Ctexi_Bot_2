from flask import Blueprint, jsonify, request, render_template
from models.db_connect import get_db_connection


dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")



# ===========================================================================
# ROUTE REGISTER  : Api : http://localhost:5000/api/dashboard/dashboard_index
# ===========================================================================
@dashboard_bp.route("/dashboard_index", methods=["GET"])
def dashboard_index():
    return render_template("dashboard_index.html")




# Conversation
@dashboard_bp.route("/conversations", methods=["GET"])
def conversations_page():
    return render_template("conversation.html")


# Discussion
@dashboard_bp.route("/discussion", methods=["GET"])
def get_conversations():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id_conv, id_user, message_user, reponse_bot,
               id_operation, confidence, created_at
        FROM chatbot.conversations
        ORDER BY created_at DESC
        LIMIT 100
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    data = []

    for r in rows:
        data.append({
            "id": r[0],
            "user_id": r[1],
            "message": r[2],
            "response": r[3],
            "operation": r[4],
            "confidence": float(r[5]) if r[5] else 0,
            "date": r[6].strftime("%Y-%m-%d %H:%M")
        })

    return jsonify(data)


# Route faq

@dashboard_bp.route("/faq", methods=["GET"])
def faq_page():
    return render_template("faq.html")


# Route users
@dashboard_bp.route("/users", methods=["GET"])
def users_page():
    return render_template("users.html")