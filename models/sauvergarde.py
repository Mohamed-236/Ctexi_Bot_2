from .db_connect import get_db_connection



def sauvegarder_conversation(id_user, message_user, reponse_bot, id_intent, id_operation, confidence):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO chatbot.conversations(id_user, message_user, reponse_bot, id_intent, id_operation, confidence)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (id_user, message_user, reponse_bot, id_intent, id_operation, confidence))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print("Erreur sauvegarde conversation:", e)




