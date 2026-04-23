
from rapidfuzz import fuzz
from models.db_connect import get_db_connection
from nlp.preprocess_colis import est_code_colis
from nlp.extraction_devise import extraire_donnees_conversion

SEUIL = 90


def detecter_operation(message: str):
    message_normalise = message.lower()

    # =========================
    # PRIORITE STRUCTURE
    # =========================

    if est_code_colis(message):
        return "suivi_colis"

    if extraire_donnees_conversion(message):
        return "conversion"

    # =========================
    # RECUPERATION DES PHRASES DEPUIS LA BD
    # =========================

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT o.nom_operation, p.phrase
        FROM chatbot.operation_phrase p
        JOIN chatbot.operation o ON o.id_operation = p.id_operation
        WHERE p.est_actif = TRUE AND o.est_actif = TRUE
    """)

    resultats = cur.fetchall()
  
    cur.close()
    conn.close()

    # =========================
    # FUZZY MATCHING
    # =========================

    meilleure_operation = None
    meilleur_score = 0

    for nom_operation, phrase in resultats:
        score = fuzz.partial_ratio(message_normalise, phrase.lower())

        if score > meilleur_score:
            meilleur_score = score
            meilleure_operation = nom_operation

    if meilleur_score >= SEUIL:
        return meilleure_operation

    return None


