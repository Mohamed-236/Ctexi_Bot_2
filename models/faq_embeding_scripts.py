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
model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# ==========================
# GENERATION EMBEDDINGS
# ==========================
def generate_intent_embeddings():

    conn = get_db_connection()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("""
        SELECT id, phrase
        FROM chatbot.intent_examples
        WHERE embedding IS NULL
          AND phrase IS NOT NULL
    """)

    rows = cur.fetchall()
    print(f"{len(rows)} phrases à traiter...")

    if not rows:
        print("Rien à encoder — tous les embeddings existent déjà.")
        cur.close()
        conn.close()
        return

    for i, row in enumerate(rows):
        phrase = row["phrase"].strip().lower()

        # normalize_embeddings=True — OBLIGATOIRE
        # pour que cosine_similarity soit cohérente dans faq_engine
        vec = model.encode(phrase, normalize_embeddings=True)

        # tolist() — OBLIGATOIRE
        # psycopg2 ne sait pas sérialiser un np.ndarray directement
        cur.execute("""
            UPDATE chatbot.intent_examples
            SET embedding = %s::vector
            WHERE id = %s
        """, (vec.tolist(), row["id"]))

        if (i + 1) % 20 == 0:
            print(f"  {i+1}/{len(rows)} traités...")

    conn.commit()
    cur.close()
    conn.close()

    print(f"Embeddings générés avec succès ({len(rows)} phrases) ✅")

# ==========================
# MAIN
# ==========================
if __name__ == "__main__":
    generate_intent_embeddings()