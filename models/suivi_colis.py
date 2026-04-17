from models.db_connect import get_db_connection
import re



def recuperer_colis(code_colis, id_user):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT code_colis, statut,type_colis, modes, derniere_maj
        FROM core.colis
        WHERE code_colis = %s
        AND id_user = %s
    """, (code_colis, id_user))
    
    colis = cur.fetchone()


    # 🔥 DEBUG ICI
    print("DEBUG SQL → code:", code_colis)
    print("DEBUG SQL → user:", id_user)
    print("DEBUG SQL → resultat:", colis)
    
    cur.close()
    conn.close()
    return colis




