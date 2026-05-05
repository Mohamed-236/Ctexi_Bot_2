# ==========================
# IMPORTS
# ==========================
from sentence_transformers import SentenceTransformer
import psycopg2
import psycopg2.extras
from models.db_connect import get_db_connection

# ==========================
# MODELE
# ==========================
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

# ==========================
# GENERATION EMBEDDINGS
# ==========================
def generate_intent_embeddings():
    """
    Génère les embeddings pour intent_examples
    """

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # 🔥 IMPORTANT : nouvelle table
    cur.execute("""
        SELECT id, phrase
        FROM chatbot.intent_examples
        WHERE embedding IS NULL
    """)

    rows = cur.fetchall()
    print(f"{len(rows)} phrases à traiter...")

    for row in rows:
        # 🔥 Nettoyage léger (important)
        phrase = row["phrase"].strip().lower()

        # Génération embedding
        vec = model.encode(phrase)

        # Sauvegarde
        cur.execute("""
            UPDATE chatbot.intent_examples
            SET embedding = %s
            WHERE id = %s
        """, (vec, row["id"]))

    conn.commit()
    cur.close()
    conn.close()

    print("Embeddings générés avec succès ✅")

# ==========================
# MAIN
# ==========================
if __name__ == "__main__":
    generate_intent_embeddings()