from models.db_connect import get_db_connection
import psycopg2.extras
import logging



def recuperer_service_par_intention(id_service=None):

    conn = get_db_connection()
    cur = conn.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor    # recuperer les donnees sous forme de dictionnaire
    )

    if id_service:
        cur.execute("""
            SELECT * FROM core.service WHERE id_service = %s
        """, (id_service,))
    else:
        cur.execute("""
            SELECT id_service, nom_service FROM core.service
             """)
    services = cur.fetchall()
    cur.close()
    conn.close()

    if services:
        logging.info("servive trouve")
    else:
        logging.info("pas de services")

    return services
