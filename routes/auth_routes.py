"""
Module : Auth + Chatbot API avec JWT
Description : Gestion inscription, connexion, déconnexion et chatbot
Compatible app mobile via JSON et JWT
"""

#================================Importation des modules/bibliotheques=======================================

# Flask et ses modules pour gérer les routes, requêtes et templates
from flask import Blueprint, request, jsonify, render_template, session, redirect, flash, url_for
# - Blueprint : permet d'organiser les routes en modules séparés
# - request : pour accéder aux données envoyées par l'utilisateur (GET, POST, headers…)
# - jsonify : pour renvoyer des réponses JSON
# - render_template : pour afficher des fichiers HTML avec Flask
# - session : pour gérer les sessions utilisateur
# - redirect : pour rediriger l'utilisateur vers une autre route
# - flash : pour afficher des messages temporaires à l'utilisateur
# - url_for : pour générer dynamiquement les URL de vos routes

# Pour sécuriser les mots de passe
from werkzeug.security import generate_password_hash, check_password_hash
# - generate_password_hash : permet de "hasher" un mot de passe avant de le stocker
# - check_password_hash : vérifie qu'un mot de passe correspond à son hash

# Connexion à la base de données PostgreSQL
from models.db_connect import get_db_connection
# - get_db_connection : fonction personnalisée pour obtenir une connexion à la base

# Pour travailler avec PostgreSQL de façon plus pratique (dictionnaires pour les résultats)
import psycopg2.extras


# Pour gérer les JSON Web Tokens (JWT)
import jwt
# - jwt.encode() : créer un token
# - jwt.decode() : décoder et vérifier un token

# Pour créer des décorateurs
from functools import wraps
# - wraps : permet de conserver les informations de la fonction originale quand on la décore

# Pour gérer les dates et durées (utile pour l'expiration des tokens)
from datetime import datetime, timedelta
# - datetime : pour récupérer la date et l'heure actuelles
# - timedelta : pour calculer des durées (ex: token valide pendant 1 heure)

#=============================================================================================================



# Clé secrète provisoire pour JWT 
SECRET_KEY = "ma_super_cle_secrete_pour_jwt"



# Création du blueprint avec préfixe API : # Le blueprint permet de regrouper les routes du chatbot dans un module distinct pour une meilleur organisation du code et facilite la maintenance et l'evolution du code
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')




# =========================
# DECORATEUR JWT : permettra au chatbot de reconnaître le user connecté sans session Flask.(pluatard..)
# =========================

# token_required est un decorateur,Un décorateur est une fonction qui prend une autre fonction (f) en argument et lui ajoute du comportement avant ou après son exécution.
def token_required(f): # 
    """
    Vérifie que la requête contient un JWT valide
    """
    @wraps(f)  #@wraps(f) est utilisé pour préserver le nom et la documentation de la fonction originale f après l’avoir décorée.
    def decorated(*args, **kwargs):        # *args, **kwargs permet de transmettre tous les arguments que la fonction originale attend.
        token = None

        # Vérification dans header
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]

        if not token:
            return jsonify({"status": "error", "message": "Token manquant"}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            # On récupère l'id et le nom du user depuis le token
            request.user_id = data['id']
            request.user_name = data['nom']
        except Exception as e:
            return jsonify({"status": "error", "message": "Token invalide"}), 401

        return f(*args, **kwargs)
    return decorated


# ==================================================================
# ROUTE REGISTER  : Api : http://localhost:5000/api/auth/register
# ==================================================================
@auth_bp.route('/register', methods=["GET", "POST"])
def register():
    # GET → page HTML
    if request.method == "GET":
        return render_template("register.html")

    # JSON → récupération depuis body
    if request.is_json:
        data = request.get_json()
        nom = data.get("nom")
        prenom = data.get("prenom")
        email = data.get("email")
        telephone = data.get("telephone")
        mdp = data.get("mdp")
    else:
        # Formulaire HTML
        nom = request.form.get("nom")
        prenom = request.form.get("prenom")
        email = request.form.get("email")
        telephone = request.form.get("telephone")
        mdp = request.form.get("mdp")

    # Vérification champs obligatoires
    if not all([nom, prenom, email, mdp]):
        if request.is_json:
            return jsonify({"status": "error", "message": "Champs obligatoires manquants"}), 400
        flash("Veuillez remplir tous les champs obligatoires", "danger")
        return redirect(url_for("auth.register"))

    mdp_hash = generate_password_hash(mdp)

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO auth.users(nom, prenom, email, telephone, mdp_hash)
            VALUES (%s, %s, %s, %s, %s)
        """, (nom, prenom, email, telephone, mdp_hash))
        conn.commit()

        if request.is_json:
            return jsonify({"status": "success", "message": "Inscription réussie"}), 201

        flash("Inscription réussie ! Connectez-vous.", "success")
        return redirect(url_for("auth.login"))

    except Exception as e:
        if request.is_json:
            return jsonify({"status": "error", "message": str(e)}), 500
        flash(f"Erreur : {e}", "danger")
        return redirect(url_for("auth.register"))
    finally:
        conn.close()


# ==========================================================
# ROUTE LOGIN : Api: http://localhost:5000/api/auth/login
# ==========================================================
@auth_bp.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.is_json:
        data = request.get_json()
        email = data.get("email")
        mdp = data.get("mot")
    else:
        email = request.form.get("email")
        mdp = request.form.get("mdp")

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT * FROM auth.users WHERE email=%s", (email,))
    user = cur.fetchone()
    conn.close()

    if user and mdp and check_password_hash(user['mdp_hash'], mdp):
        # Création JWT pour app mobile
        token = jwt.encode({
            "id": user["id_user"],
            "nom": user["nom"],
            "exp": datetime.utcnow() + timedelta(hours=12)  # token valide 12h
        }, SECRET_KEY, algorithm="HS256")

        if request.is_json:
            return jsonify({
                "status": "success",
                "message": "Connexion réussie",
                "token": token,
                "user": {
                    "id": user["id_user"],
                    "nom": user["nom"]
                }
            }), 200

        # HTML → session + redirection
        session['user_id'] = user['id_user']
        session['user_name'] = user['nom']
        flash("Connexion réussie !!", "success")
        return redirect(url_for('auth.index'))

    if request.is_json:
        return jsonify({"status": "error", "message": "Email ou mot de passe incorrect"}), 401

    flash("Email ou mot de passe incorrect", "danger")
    return redirect(url_for('auth.login'))


# =============================================================
# ROUTE LOGOUT : Api : http://localhost:5000/api/auth/logout
# =============================================================
@auth_bp.route('/logout', methods=["POST"])
def logout():
    if 'user_id' in session:
        session.clear()

    if request.is_json:
        return jsonify({"status": "success", "message": "Déconnexion réussie"}), 200

    flash("Vous êtes déconnecté avec succès", "success")
    return redirect(url_for("auth.login"))






# =============================================================
# ROUTE INDEX : Api : http://localhost:5000/api/auth/index
# =============================================================

@auth_bp.route("/index", methods=["GET"]) 
def index():
    user_name = session.get('user_name', 'Utilisateur')
    return render_template('index.html', user_name=user_name)




# =============================================================
# ROUTE USER : API : http://localhost:5000/api/auth/user
# =============================================================

@auth_bp.route("/user", methods=["GET"])
def get_user():
    """
    Route API pour récupérer les infos de l'utilisateur connecté
    (mobile-ready, JSON)
    """
    user_id = session.get('user_id')
    user_name = session.get('user_name')

    if not user_id:
        return jsonify({"status": "error", "message": "Utilisateur non connecté"}), 401

    return jsonify({
        "status": "success",
        "user": {
            "id": user_id,
            "nom": user_name
        }
    })








