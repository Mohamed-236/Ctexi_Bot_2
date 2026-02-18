#blueprint pour organiser les routes, request pour acceder aux donnees de la requete, jsonify pour formater les reponses en json
from flask import Blueprint, request, jsonify, render_template, session, redirect, flash,url_for
from nlp.logic_nlp import comprehension
from werkzeug.security import generate_password_hash, check_password_hash
from models.db_connect import get_db_connection
import psycopg2.extras


chatbot_bp = Blueprint('chatbot',__name__, url_prefix='/api/chatbot') # Le blueprint permet de regrouper les routes du chatbot dans un module distinct pour une meilleur organisation du code et facilite la maintenance et l'evolution du code




# Page de connexion  : Api : http://localhost:5000/api/chatbot/login
@chatbot_bp.route('/login', methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        mdp = request.form.get("mdp")

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
                    SELECT * FROM auth.users WHERE email=%s 
                """,(email,))
        user = cur.fetchone()
        conn.close()

    
        if user and mdp and check_password_hash(user['mdp_hash'],mdp):
            session['user_id'] = user['id_user']
            session['user_name'] = user['nom']
            flash("Connexion reussie!!", "success")
            return redirect(url_for('chatbot.index'))
        else:
            flash("Email ou mot de passe incorrect", "danger")

    return render_template('login.html')



# Page d'inscription : Api : http://localhost:5000/api/chatbot/register
@chatbot_bp.route('/register', methods=["GET", "POST"] )
def register():
    if request.method =='POST':
        nom = request.form.get('nom')
        prenom = request.form.get('prenom')
        email = request.form.get('email')
        telephone = request.form.get('telephone')
        mdp = request.form.get('mdp')
        mdp_hash = generate_password_hash(mdp)

#Connexion ajout a la base de donnees

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("""
                
               INSERT INTO auth.users(nom, prenom, email, telephone, mdp_hash)
               VALUES(%s, %s, %s, %s, %s)
            """, (nom, prenom, email, telephone, mdp_hash))
            conn.commit()
            flash("Inscription reussie! Connectez-vous avec vos information de connexion.", "succes")
            return redirect(url_for('chatbot.login'))
        
        except Exception as e:
              flash(f"Erreur : {e}", "danger")
        finally:
            conn.close()
    
    return render_template('register.html')


# Page de deconnexion: api: http://localhost:5000/api/logout
@chatbot_bp.route("/logout", methods=["POST"])
def logout():
    if 'user_id' in session:
       session.clear()
       flash("Vous etes de donnectez avec succes!!")
    return redirect(url_for("chatbot.login"))





# Page du chatbot :  Api  :   http://localhost:5000/api/index
@chatbot_bp.route("/index", methods=["GET"]) 
def index():
    user_name = session.get('user_name', 'Utilisateur')
    return render_template('index.html', user_name=user_name)





# Cette route est accessible via une requete Post a l'url /api/chatbot en traiter les messages du user et retourner une reponse du chatbot
@chatbot_bp.route("/message", methods=["POST"]) 

def chatbot_reponse():
    data = request.get_json()     # Recuperer les donnees de la requete au format json
    message = data.get("message") # Extraire le message du user a partir des donnees de la requete
    if not message:               # verifier si le message est present, sinon retourner une reponse d'erreur
        return jsonify({"erreur": "Message manquant"})
    
    reponse = comprehension(message)
    return jsonify({"reponse": reponse}) # retourner la reponse du chatbot au format json
    








