from models.db_connect import get_db_connection
import psycopg2.extras
import logging




def recuperer_service(id_intent):


    conn = get_db_connection()
    cur = conn.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    cur.execute("""



            """)
