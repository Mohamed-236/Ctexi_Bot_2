# ==========================================================
# SERVICE AGENT - GESTION DES AGENTS HUMAINS
# ==========================================================

from models.db_connect import get_db_connection
import psycopg2.extras
import logging


def recuperer_agent_par_intention(id_intent):
    """
    Récupère un agent actif correspondant à l'intention détectée.
    On utilise id_intent (clé étrangère) et non plus le nom.
    """

    conn = get_db_connection()
    cur = conn.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    cur.execute("""
        SELECT id_agent, whatsapp, telephone, email
        FROM auth.agents
        WHERE id_intent = %s
        AND actif = TRUE
        LIMIT 1
    """, (id_intent,))

    agent = cur.fetchone()

    cur.close()
    conn.close()

    if agent:
        logging.info(f"Agent trouvé pour intention {id_intent}")
    else:
        logging.info(f"Aucun agent actif trouvé pour intention {id_intent}")

    return agent