import os                              # permet de manipuler les fichiers et variables d'environnement
from dotenv import load_dotenv         # pour charger les variables d'environnement depuis le fichier .env



#Classe de configuration pour l'application Flask,Charge les variables d'environnement et fourni des attibuts de configuration."""

class Config:
    SECRET_KEY   = os.getenv("SECRET_KEY")
    DB_HOST      = os.getenv("DB_HOST")
    DB_USER      = os.getenv("DB_USER")
    DB_PASSWORD  = os.getenv("DB_PASSWORD")
    DB_NAME      = os.getenv("DB_NAME")

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    )

    

