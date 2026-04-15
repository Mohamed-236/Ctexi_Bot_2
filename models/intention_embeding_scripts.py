from sentence_transformers import SentenceTransformer
import psycopg2
import psycopg2.extras
from models.db_connect import get_db_connection

model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')



def generate_intention_embeddings():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("""
        SELECT id_intent, descriptions 
        FROM chatbot.intention
        WHERE descriptions IS NOT NULL
    """)
    intentions = cur.fetchall()

    for intent in intentions:
        # ✅ On encode la description directement, pas la moyenne des FAQ
        vec = model.encode(intent["descriptions"], normalize_embeddings=True)
        
        cur.execute("""
            UPDATE chatbot.intention
            SET embedding = %s
            WHERE id_intent = %s
        """, (vec, intent["id_intent"]))

    conn.commit()
    cur.close()
    conn.close()
    print("Embeddings intention recalculés ✅")

if __name__ == "__main__":
    generate_intention_embeddings()