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

    user_id = request.args.get("user_id")

    conn = get_db_connection()
    cur = conn.cursor()

    if user_id:
        cur.execute("""
            SELECT c.id_conv, c.id_user, u.nom,
                   c.message_user, c.reponse_bot,
                   c.id_operation, c.confidence, c.created_at
            FROM chatbot.conversations c
            JOIN auth.users u ON c.id_user = u.id_user
            WHERE c.id_user = %s
            ORDER BY c.created_at DESC
        """, (user_id,))
    else:
        cur.execute("""
            SELECT c.id_conv, c.id_user, u.nom,
                   c.message_user, c.reponse_bot,
                   c.id_operation, c.confidence, c.created_at
            FROM chatbot.conversations c
            JOIN auth.users u ON c.id_user = u.id_user
            ORDER BY c.created_at DESC
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
            "username": r[2],
            "message": r[3],
            "response": r[4],
            "operation": r[5],
            "confidence": float(r[6]) if r[6] else 0,
            "date": r[7].strftime("%Y-%m-%d %H:%M")
        })

    return jsonify(data)


@dashboard_bp.route("/delete/<int:id_conv>", methods=["DELETE"])
def delete_conversation(id_conv):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM chatbot.conversations WHERE id_conv = %s", (id_conv,))
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"status": "success"})


# Route faq

@dashboard_bp.route("/faq", methods=["GET"])
def faq_page():
    return render_template("faq.html")


# Route users
@dashboard_bp.route("/users", methods=["GET"])
def users_page():
    return render_template("users.html")



#================================== faq interface===========================

@dashboard_bp.route("/faq/list", methods=["GET"])
def get_faq():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id_faq, id_intent, message_user, reponse_bot, dates
        FROM chatbot.faq
        ORDER BY id_faq DESC
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    data = []

    for r in rows:
        data.append({
            "id": r[0],
            "intent": r[1],
            "question": r[2],
            "response": r[3],
            "date": r[4].strftime("%Y-%m-%d %H:%M")
        })

    return jsonify(data)




@dashboard_bp.route("/faq/add", methods=["POST"])
def add_faq():

    data = request.get_json()

    intent = data.get("intent")
    question = data.get("question")
    response = data.get("response")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot)
        VALUES (%s, %s, %s)
    """, (intent, question, response))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "success"})



@dashboard_bp.route("/faq/update/<int:id_faq>", methods=["PUT"])
def update_faq(id_faq):

    data = request.get_json()

    intent = data.get("intent")
    question = data.get("question")
    response = data.get("response")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE chatbot.faq
        SET id_intent = %s,
            message_user = %s,
            reponse_bot = %s
        WHERE id_faq = %s
    """, (intent, question, response, id_faq))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "updated"})




@dashboard_bp.route("/faq/delete/<int:id_faq>", methods=["DELETE"])
def delete_faq(id_faq):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM chatbot.faq WHERE id_faq = %s
    """, (id_faq,))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "deleted"})



@dashboard_bp.route("/faq/search", methods=["GET"])
def search_faq():

    q = request.args.get("q", "")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id_faq, message_user, reponse_bot
        FROM chatbot.faq
        WHERE message_user ILIKE %s
        ORDER BY id_faq DESC
    """, (f"%{q}%",))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify(rows)



#=======================suivi user et agent=========================

@dashboard_bp.route("/admin/users-agents", methods=["GET"])
def get_users_agents():

    conn = get_db_connection()
    cur = conn.cursor()

    # USERS
    cur.execute("""
        SELECT id_user, nom, prenom, email, telephone, est_admin, date_creation
        FROM auth.users
        ORDER BY id_user DESC
    """)
    users = cur.fetchall()

    # AGENTS
    cur.execute("""
        SELECT id_agent, id_intent, whatsapp, telephone, email, actif, dates
        FROM auth.agents
        ORDER BY id_agent DESC
    """)
    agents = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify({
        "users": [
            {
                "id": u[0],
                "nom": u[1],
                "prenom": u[2],
                "email": u[3],
                "telephone": u[4],
                "is_admin": u[5],
                "date": u[6].strftime("%Y-%m-%d")
            } for u in users
        ],
        "agents": [
            {
                "id": a[0],
                "intent": a[1],
                "whatsapp": a[2],
                "telephone": a[3],
                "email": a[4],
                "actif": a[5],
                "date": a[6].strftime("%Y-%m-%d")
            } for a in agents
        ]
    })





@dashboard_bp.route("/user/delete/<int:id_user>", methods=["DELETE"])
def delete_user(id_user):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM auth.users WHERE id_user=%s", (id_user,))
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"status": "deleted"})



@dashboard_bp.route("/agent/delete/<int:id_agent>", methods=["DELETE"])
def delete_agent(id_agent):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM auth.agents WHERE id_agent=%s", (id_agent,))
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"status": "deleted"})




@dashboard_bp.route("/agent/toggle/<int:id_agent>", methods=["PUT"])
def toggle_agent(id_agent):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE auth.agents
        SET actif = NOT actif
        WHERE id_agent = %s
    """, (id_agent,))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "updated"})






import csv
from flask import Response

@dashboard_bp.route("/conversations/export", methods=["GET"])
def export_conversations_csv():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id_conv, id_user, message_user, reponse_bot,
               confidence, created_at
        FROM chatbot.conversations
        ORDER BY created_at DESC
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    def generate():
        yield "id_conv,id_user,message,reponse,confidence,date\n"

        for r in rows:
            yield f"{r[0]},{r[1]},\"{r[2]}\",\"{r[3]}\",{r[4]},{r[5]}\n"

    return Response(generate(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=conversations.csv"})




# Gestion des operations

# =========================
# PAGE HTML
# =========================
@dashboard_bp.route("/operations", methods=["GET"])
def operations_page():
    return render_template("operations.html")


# =========================
# LIST OPERATIONS
# =========================
@dashboard_bp.route("/operations/list", methods=["GET"])
def get_operations():

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id_operation, nom_operation, descriptions, est_actif, date_creation
        FROM chatbot.operation
        ORDER BY id_operation DESC
    """)

    rows = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify([
        {
            "id": r[0],
            "name": r[1],
            "description": r[2],
            "active": r[3],
            "date": r[4].strftime("%Y-%m-%d")
        }
        for r in rows
    ])


# =========================
# ADD OPERATION
# =========================
@dashboard_bp.route("/operations/add", methods=["POST"])
def add_operation():

    data = request.get_json()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO chatbot.operation (nom_operation, descriptions)
        VALUES (%s, %s)
    """, (data["name"], data["description"]))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "created"})


# =========================
# DELETE OPERATION
# =========================
@dashboard_bp.route("/operations/delete/<int:id_op>", methods=["DELETE"])
def delete_operation(id_op):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM chatbot.operation WHERE id_operation=%s", (id_op,))
    conn.commit()

    cur.close()
    conn.close()

    return jsonify({"status": "deleted"})


# =========================
# TOGGLE OPERATION
# =========================
@dashboard_bp.route("/operations/toggle/<int:id_op>", methods=["PUT"])
def toggle_operation(id_op):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE chatbot.operation
        SET est_actif = NOT est_actif
        WHERE id_operation = %s
    """, (id_op,))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "updated"})