import os                              # permet de manipuler les fichiers et variables d'environnement
from dotenv import load_dotenv         # pour charger les variables d'environnement depuis le fichier .env

# appele la variable load_dotenv() pour pouvoir l'utiliser
load_dotenv()


#Classe de configuration pour l'application Flask,Charge les variables d'environnement et fourni des attibuts de configuration."""

class Config:
    SECRET_KEY   = os.getenv("SECRET_KEY")
    DB_NAME      = os.getenv("DB_NAME")
    DB_HOST      = os.getenv("DB_HOST")
    DB_USER      = os.getenv("DB_USER")
    DB_PASSWORD  = os.getenv("DB_PASSWORD")
    DB_PORT      = os.getenv("DB_PORT")


    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    )



# sql alachemy permet de manipuler les base de donnes coe des objets python

