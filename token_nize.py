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
from config import Config


# Clé secrète provisoire pour JWT 
SECRET_KEY = Config.SECRET_KEY



def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Pour test : on simule un user connecté
        request.user_id = 1
        request.user_name = "TestUser"
        return f(*args, **kwargs)
    return decorated






'''
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
'''