# ==========================
# IMPORTS
# ==========================
from sentence_transformers import SentenceTransformer
import psycopg2
import psycopg2.extras
from models.db_connect import get_db_connection

# ================================
# CHARGEMENT DU MODELE
# ================================
# model = SentenceTransformer("all-MiniLM-L6-v2")
model = SentenceTransformer("all-mpnet-base-v2")

# ================================
# FONCTION PRINCIPALE
# ================================
def generate_faq_embeddings():
    """
    1. Se connecte à la base de données
    2. Récupère les FAQ sans embedding
    3. Génère leur embedding
    4. Sauvegarde le vecteur en base
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Récupérer uniquement les FAQ sans embedding
    cur.execute("""
        SELECT id_faq, message_user
        FROM chatbot.faq
        WHERE embedding IS NULL
    """)
    faq_list = cur.fetchall()
    print(f"{len(faq_list)} FAQ à traiter...")

    for faq in faq_list:
        # Génération embedding (numpy array)
        vec = model.encode(faq["message_user"])

        # ❌ Plus besoin de conversion pgvector(), on passe directement le numpy array
        cur.execute(
            "UPDATE chatbot.faq SET embedding = %s WHERE id_faq = %s",
            (vec, faq["id_faq"])
        )

    conn.commit()
    cur.close()
    conn.close()
    print("Embeddings FAQ générés avec succès ✅")

# ================================
# POINT D’ENTRÉE DU SCRIPT
# ================================
if __name__ == "__main__":
    generate_faq_embeddings()