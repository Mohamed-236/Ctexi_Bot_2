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

model = SentenceTransformer("all-mpnet-base-v2")


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


# ================================
# POINT D’ENTRÉE DU SCRIPT
# ================================
if __name__ == "__main__":
    generate_intention_embeddings()

'''
def generate_intention_embeddings():
    """
    1. Se connecte à la base
    2. Récupère les intentions sans embedding
    3. Génère leur embedding (nom + description)
    4. Sauvegarde le vecteur en base
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Récupérer uniquement les intentions sans embedding
    cur.execute("""
        SELECT id_intent, nom, descriptions
        FROM chatbot.intention
        WHERE embedding IS NULL
    """)
    intentions = cur.fetchall()
    print(f"{len(intentions)} intentions à traiter...")

    for intent in intentions:
        # Concaténer nom + description
        texte_intention = f"{intent['nom']} {intent['descriptions']}"
        vec = model.encode(texte_intention)  # numpy array directement

        # ❌ Plus besoin de conversion Vector()
        cur.execute(
            "UPDATE chatbot.intention SET embedding = %s WHERE id_intent = %s",
            (vec, intent["id_intent"])
        )

    conn.commit()
    cur.close()
    conn.close()
    print("Embeddings des intentions générés avec succès ✅")

# ================================
# POINT D’ENTRÉE DU SCRIPT
# ================================
if __name__ == "__main__":
    generate_intention_embeddings()

'''