from flask import Blueprint, request, jsonify ,render_template# blueprint pour organiser les routes, request pour acceder aux donnees de la requete, jsonify pour formater les reponses en json
from nlp.logic_nlp import comprehension
from models.db_connect import get_db_connection



chatbot_bp = Blueprint('chatbot',__name__, url_prefix='/api/chatbot') # Le blueprint permet de regrouper les routes du chatbot dans un module distinct pour une meilleur organisation du code et facilite la maintenance et l'evolution du code




@chatbot_bp.route('/login', methods = ["GET", "POST"])
def login():
    return render_template('login.html')



@chatbot_bp.route('/register', methods=["GET", "POST"] )
def register():
    return render_template('register.html')




# route pour l'affichage de mon acceuil
@chatbot_bp.route("/acceuil", methods=["GET"]) 
def index():
    return render_template('index.html')







# Cette route est accessible via une requete Post a l'url /api/chatbot en traiter les messages du user et retourner une reponse du chatbot
@chatbot_bp.route("/message", methods=["POST"]) 

def chatbot_reponse():
    data = request.get_json()     # Recuperer les donnees de la requete au format json
    message = data.get("message") # Extraire le message du user a partir des donnees de la requete
    if not message:               # verifier si le message est present, sinon retourner une reponse d'erreur
        return jsonify({"erreur": "Message manquant"})
    
    reponse = comprehension(message)
    return jsonify({"reponse": reponse}) # retourner la reponse du chatbot au format json
    








