import psycopg2             # Pour se connecter a psgsl
import psycopg2.extras
from config import Config   # importer la classe config pour acceder  a la configuration de la bd
from psycopg2 import OperationalError
from pgvector.psycopg2 import register_vector

def get_db_connection():
    """Cette fonction etablit une connexion a la bd en utilisant les infos de configuration de la classe Config"""
    try:
        conn=psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            dbname=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        print("Bravo!!! Connexion reusssie")
        register_vector(conn)
        return conn
    
    except OperationalError as e :
        print(f"erreur de connexion{e}")
        return None


if __name__ == "__main__":
    connection = get_db_connection()
    if connection:
       connection.close()