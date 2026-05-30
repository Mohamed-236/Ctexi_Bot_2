# ================================================================
#  dashboard_routes.py
#  Blueprint Flask — Dashboard Admin Ctexi-Bot
#  Toutes les routes utilisent get_db_connection() (psycopg2)
# ================================================================

from flask import Blueprint, render_template, jsonify, session, redirect, url_for
import psycopg2.extras
from models.db_connect import get_db_connection   # adapte le chemin si besoin

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


# ----------------------------------------------------------------
#  HELPER — exécute une requête et retourne des dicts
# ----------------------------------------------------------------
def query(sql, params=None, one=False):
    conn = get_db_connection()
    if not conn:
        return None if one else []
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params or ())
            result = cur.fetchone() if one else cur.fetchall()
            return dict(result) if (one and result) else [dict(r) for r in (result or [])]
    except Exception as e:
        print(f"[DB ERROR] {e}")
        return None if one else []
    finally:
        conn.close()


def scalar(sql, params=None, default=0):
    """Retourne une seule valeur numérique (COUNT, AVG…)"""
    conn = get_db_connection()
    if not conn:
        return default
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            row = cur.fetchone()
            val = row[0] if row else default
            return float(val) if val is not None else default
    except Exception as e:
        print(f"[DB ERROR] {e}")
        return default
    finally:
        conn.close()


# ----------------------------------------------------------------
#  GUARD — vérifie que l'utilisateur est admin
# ----------------------------------------------------------------
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('est_admin'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated


# ================================================================
#  PAGE PRINCIPALE
# ================================================================
@dashboard_bp.route('/dashboard_index')
@admin_required
def dashboard_index():
    nom = session.get('nom', 'Admin')
    initials = ''.join(w[0] for w in nom.split()[:2]).upper()
    return render_template('dashboard_index.html', user_name=nom, user_initials=initials)


# ================================================================
#  API — KPI GLOBAUX
# ================================================================
@dashboard_bp.route('/stats')
@admin_required
def stats():
    total_users   = scalar("SELECT COUNT(*) FROM auth.users")
    total_convs   = scalar("SELECT COUNT(*) FROM chatbot.conversations")
    agents_actifs = scalar("SELECT COUNT(*) FROM auth.agents WHERE actif = true")
    agents_total  = scalar("SELECT COUNT(*) FROM auth.agents")
    intents_count = scalar("SELECT COUNT(*) FROM chatbot.intention")
    colis_count   = scalar("SELECT COUNT(*) FROM core.colis")
    confiance_moy = scalar("SELECT AVG(confidence) FROM chatbot.conversations WHERE confidence IS NOT NULL")

    # Taux FAQ vs Fallback
    total_avec_intent = scalar(
        "SELECT COUNT(*) FROM chatbot.conversations WHERE id_intent IS NOT NULL"
    )
    fallback_count = scalar(
        "SELECT COUNT(*) FROM chatbot.conversations WHERE action_handler = 'fallback_handler' OR id_intent IS NULL"
    )
    faq_rate     = round((1 - fallback_count / total_convs) * 100, 1) if total_convs > 0 else 0
    fallback_rate = round((fallback_count / total_convs) * 100, 1) if total_convs > 0 else 0

    return jsonify({
        "total_users":    int(total_users),
        "total_convs":    int(total_convs),
        "agents_actifs":  int(agents_actifs),
        "agents_total":   int(agents_total),
        "intents_count":  int(intents_count),
        "colis_count":    int(colis_count),
        "confiance_moy":  round(confiance_moy, 1),
        "faq_rate":       faq_rate,
        "fallback_rate":  fallback_rate,
        "uptime":         99.7   # statique ou à brancher sur ton monitoring
    })


# ================================================================
#  API — ACTIVITÉ 7 DERNIERS JOURS (graphique bar+line)
# ================================================================
@dashboard_bp.route('/activity')
@admin_required
def activity():
    rows_convs = query("""
        SELECT TO_CHAR(created_at, 'Dy') AS jour,
               DATE(created_at)          AS d,
               COUNT(*)                  AS total
        FROM chatbot.conversations
        WHERE created_at >= NOW() - INTERVAL '7 days'
        GROUP BY DATE(created_at), TO_CHAR(created_at, 'Dy')
        ORDER BY d
    """)

    rows_users = query("""
        SELECT TO_CHAR(date_creation, 'Dy') AS jour,
               DATE(date_creation)          AS d,
               COUNT(*)                     AS total
        FROM auth.users
        WHERE date_creation >= NOW() - INTERVAL '7 days'
        GROUP BY DATE(date_creation), TO_CHAR(date_creation, 'Dy')
        ORDER BY d
    """)

    # Aligne les deux séries sur les mêmes labels
    labels     = [r['jour'] for r in rows_convs]
    convs_data = [int(r['total']) for r in rows_convs]
    users_map  = {r['jour']: int(r['total']) for r in rows_users}
    users_data = [users_map.get(l, 0) for l in labels]

    return jsonify({"labels": labels, "convs": convs_data, "users": users_data})


# ================================================================
#  API — RÉPARTITION DES INTENTIONS (donut)
# ================================================================
@dashboard_bp.route('/intent_dist')
@admin_required
def intent_dist():
    rows = query("""
        SELECT i.nom, COUNT(c.id_conv) AS count
        FROM chatbot.intention i
        LEFT JOIN chatbot.conversations c ON c.id_intent = i.id_intent
        GROUP BY i.nom
        ORDER BY count DESC
        LIMIT 8
    """)
    return jsonify([{"nom": r['nom'], "count": int(r['count'])} for r in rows])


# ================================================================
#  API — CONVERSATIONS (table + recherche)
# ================================================================
@dashboard_bp.route('/conversations')
@admin_required
def conversations():
    rows = query("""
        SELECT
            c.id_conv,
            u.nom || ' ' || u.prenom        AS user_nom,
            c.message_user,
            c.reponse_bot,
            i.nom                            AS nom_intent,
            c.type_intent,
            c.action_handler,
            c.confidence,
            TO_CHAR(c.created_at, 'DD/MM HH24:MI') AS created_at
        FROM chatbot.conversations c
        JOIN  auth.users           u ON c.id_user  = u.id_user
        LEFT JOIN chatbot.intention i ON c.id_intent = i.id_intent
        ORDER BY c.created_at DESC
        LIMIT 100
    """)
    return jsonify(rows)


# ================================================================
#  API — INTENTIONS
# ================================================================
@dashboard_bp.route('/intentions')
@admin_required
def intentions():
    rows = query("""
        SELECT
            i.id_intent,
            i.nom,
            i.type_intent,
            i.action_handler,
            i.descriptions,
            COUNT(DISTINCT e.id) AS nb_exemples,
            COUNT(DISTINCT r.id) AS nb_reponses
        FROM chatbot.intention i
        LEFT JOIN chatbot.intent_examples  e ON e.id_intent = i.id_intent
        LEFT JOIN chatbot.intent_responses r ON r.id_intent = i.id_intent
        GROUP BY i.id_intent, i.nom, i.type_intent, i.action_handler, i.descriptions
        ORDER BY i.id_intent
    """)
    return jsonify(rows)


# ================================================================
#  API — UTILISATEURS
# ================================================================
@dashboard_bp.route('/users')
@admin_required
def users():
    rows = query("""
        SELECT
            u.id_user,
            u.nom,
            u.prenom,
            u.email,
            u.telephone,
            u.est_admin,
            TO_CHAR(u.date_creation, 'DD/MM/YYYY') AS date_creation,
            COUNT(c.id_conv) AS nb_convs
        FROM auth.users u
        LEFT JOIN chatbot.conversations c ON c.id_user = u.id_user
        GROUP BY u.id_user, u.nom, u.prenom, u.email, u.telephone, u.est_admin, u.date_creation
        ORDER BY u.date_creation DESC
    """)
    return jsonify(rows)


# ================================================================
#  API — AGENTS
# ================================================================
@dashboard_bp.route('/agents')
@admin_required
def agents():
    rows = query("""
        SELECT
            a.id_agent,
            a.email,
            a.whatsapp,
            a.telephone,
            a.actif,
            TO_CHAR(a.dates, 'DD/MM/YYYY') AS dates,
            i.nom AS nom_intent
        FROM auth.agents a
        LEFT JOIN chatbot.intention i ON i.id_intent = a.id_intent
        ORDER BY a.actif DESC, a.id_agent
    """)
    return jsonify(rows)


# ================================================================
#  API — COLIS
# ================================================================
@dashboard_bp.route('/colis')
@admin_required
def colis():
    rows = query("""
        SELECT
            c.id_colis,
            c.code_colis,
            u.nom || ' ' || u.prenom AS user_nom,
            c.statut,
            c.type_colis,
            c.modes,
            TO_CHAR(c.derniere_maj, 'DD/MM HH24:MI') AS derniere_maj
        FROM core.colis c
        LEFT JOIN auth.users u ON u.id_user = c.id_user
        ORDER BY c.derniere_maj DESC
        LIMIT 100
    """)
    return jsonify(rows)
