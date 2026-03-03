from .db_connect import get_db_connection



def sauvegarder_conversation(id_user, message_utilisateur, reponse_bot, intention, type_intent):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO chatbot.conversations(id_user, message_user, reponse_bot, intention, type_intent)
            VALUES (%s, %s, %s, %s, %s)
        """, (id_user, message_utilisateur, reponse_bot, intention, type_intent))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("Erreur sauvegarde conversation:", e)