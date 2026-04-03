# ==========================
# IMPORTS
# ==========================
from sentence_transformers import SentenceTransformer
import psycopg2
import psycopg2.extras
from models.db_connect import get_db_connection  # register_vector déjà appelé dedans
import numpy as np
# ================================
# CHARGEMENT DU MODELE
# ================================
# model = SentenceTransformer("all-MiniLM-L6-v2")

# model = SentenceTransformer("all-mpnet-base-v2")

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
# ================================
# FONCTION PRINCIPALE
# ================================



def generate_intention_embeddings():

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Récupérer toutes les intentions
    cur.execute("SELECT id_intent FROM chatbot.intention")
    intentions = cur.fetchall()

    for intent in intentions:
        id_intent = intent["id_intent"]

        # récupérer les FAQ liées
        cur.execute("""
            SELECT embedding
            FROM chatbot.faq
            WHERE id_intent = %s AND embedding IS NOT NULL
        """, (id_intent,))
        faq_embeddings = cur.fetchall()

        if not faq_embeddings:
            continue

        vectors = [f["embedding"] for f in faq_embeddings]
        moyenne = np.mean(vectors, axis=0)

        cur.execute("""
            UPDATE chatbot.intention
            SET embedding = %s
            WHERE id_intent = %s
        """, (moyenne, id_intent))

    conn.commit()
    cur.close()
    conn.close()

    print("Embeddings intention recalculés intelligemment ✅")

if __name__== "__main__":
    generate_intention_embeddings()
