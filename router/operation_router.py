from rapidfuzz import fuzz
from models.db_connect import get_db_connection
from nlp.preprocess_colis import est_code_colis
from nlp.extraction_devise import extraire_donnees_conversion

# ==========================================================
# SEUIL FUZZY MATCHING
# ==========================================================
SEUIL = 80

# ==========================================================
# MAPPING action_handler → nom retourné au moteur
# Doit correspondre aux clés vérifiées dans gerer_operations()
# ==========================================================
ACTION_HANDLER_MAP = {
    "agent_handler":      "contact_agent",
    "service_handler":    "service_info",
    "suivi_handler":      "suivi_colis",
    "conversion_handler": "taux_change",
}

# ==========================================================
# CACHE PHRASES — chargé une seule fois au démarrage
# Source : intent_examples JOIN intention WHERE type_intent='operation'
# ==========================================================
_CACHE_OP = []       # liste de (action_handler, phrase)
_OP_LOADED = False

def _charger_phrases_operation():
    global _CACHE_OP, _OP_LOADED

    if _OP_LOADED:
        return

    conn = get_db_connection()
    cur  = conn.cursor()

    cur.execute("""
        SELECT i.action_handler, e.phrase
        FROM chatbot.intent_examples e
        JOIN chatbot.intention i ON i.id_intent = e.id_intent
        WHERE i.type_intent  = 'operation'
          AND i.action_handler IS NOT NULL
          AND e.phrase         IS NOT NULL
    """)

    _CACHE_OP  = cur.fetchall()
    _OP_LOADED = True

    cur.close()
    conn.close()

# ==========================================================
# DETECTER OPERATION
#
# Priorité :
#   1. Code colis  (regex, priorité absolue)
#   2. Conversion  (regex montant + 2 devises)
#   3. Fuzzy match sur les phrases d'opération
#      → retourne le nom via ACTION_HANDLER_MAP
# ==========================================================
def detecter_operation(message: str):

    message_norm = message.lower().strip()

    # -------------------------------------------------------
    # 1. Code colis — regex prioritaire
    # -------------------------------------------------------
    if est_code_colis(message):
        return "suivi_colis"

    # -------------------------------------------------------
    # 2. Conversion devise — regex montant + devises
    # -------------------------------------------------------
    if extraire_donnees_conversion(message):
        return "taux_change"

    # -------------------------------------------------------
    # 3. Fuzzy matching sur les phrases d'opération en DB
    # -------------------------------------------------------
    _charger_phrases_operation()

    meilleur_handler = None
    meilleur_score   = 0

    for action_handler, phrase in _CACHE_OP:
        score = fuzz.partial_ratio(message_norm, phrase.lower())

        if score > meilleur_score:
            meilleur_score   = score
            meilleur_handler = action_handler

    if meilleur_score >= SEUIL and meilleur_handler:
        return ACTION_HANDLER_MAP.get(meilleur_handler)

    return None