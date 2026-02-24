from .db_connect import get_db_connection



def sauvegarder_conversation(id_user, message_utilisateur, reponse_bot):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO chatbot.conversations(id_user, message_user, reponse_bot)
            VALUES (%s, %s, %s)
        """, (id_user, message_utilisateur, reponse_bot))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("Erreur sauvegarde conversation:", e)