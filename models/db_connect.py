import psycopg2             # Pour se connecter a psgsl
from config import Config   # importer la classe config pour acceder  a la configuration de la bd

def get_db_connection():
    """Cette fonction etablit une connexion a la bd en utilisant les infos de configuration de la classe Config"""
    return psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            dbname=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )


