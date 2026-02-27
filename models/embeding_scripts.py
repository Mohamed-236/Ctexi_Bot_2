
# ==========================
# IMPORTS
# ==========================

# Permet de transformer du texte en vecteur (embedding)
from sentence_transformers import SentenceTransformer

# Bibliothèque pour se connecter à PostgreSQL
import psycopg2
import psycopg2.extras

# On importe la configuration centrale du  projet 
# (les variables viennent du fichier .env via config.py)
from models.db_connect import get_db_connection

# ================================
# CHARGEMENT DU MODELE
# ================================

# On charge le modèle d'embedding UNE SEULE FOIS.
# all-MiniLM-L6-v2 produit des vecteurs de 384 dimensions.
# model = SentenceTransformer("all-MiniLM-L6-v2")
model = SentenceTransformer("all-mpnet-base-v2")

# ================================
# FONCTION PRINCIPALE
# ================================

def generate_embeddings():
    """
    Cette fonction :
    1. Se connecte à la base de données
    2. Récupère les FAQ sans embedding
    3. Génère leur embedding
    4. Sauvegarde le vecteur en base
    """

    # -------------------------------
    # Connexion à PostgreSQL
    # -------------------------------

    # On utilise les informations définies dans  .env
    conn = get_db_connection()

    # RealDictCursor permet de récupérer les résultats
    # sous forme de dictionnaire (plus pratique)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


    # -------------------------------
    # Récupérer uniquement les FAQ
    # qui n'ont PAS encore d'embedding
    # -------------------------------

    cur.execute("""
        SELECT id_faq, message_user
        FROM chatbot.faq
        WHERE embedding IS NULL
    """)

    # On stocke toutes les FAQ concernées
    faq_list = cur.fetchall()

    print(f"{len(faq_list)} FAQ à traiter...")


    # -------------------------------
    # Génération des embeddings
    # -------------------------------

    for faq in faq_list:

        # Transformer le texte de la question en vecteur numérique
        # Le modèle retourne un tableau numpy
        vector = model.encode(faq["message_user"])

        # On convertit en liste Python
        # PostgreSQL ne peut pas stocker directement un numpy array
        vector = vector.tolist()

        # -------------------------------
        # Mise à jour de la ligne
        # -------------------------------

        cur.execute(
            """
            UPDATE chatbot.faq
            SET embedding = %s
            WHERE id_faq = %s
            """,
            (vector, faq["id_faq"])
        )


    # -------------------------------
    # Sauvegarde définitive
    # -------------------------------

    # On valide les modifications
    conn.commit()

    # On ferme proprement la connexion
    cur.close()
    conn.close()

    print("Embeddings générés avec succès ✅")


# ================================
# POINT D’ENTRÉE DU SCRIPT
# ================================

# Cette condition signifie :
# "Exécute la fonction uniquement si ce fichier est lancé directement"
# Donc Flask ne lancera JAMAIS ce script automatiquement.
if __name__ == "__main__":
    generate_embeddings()

    