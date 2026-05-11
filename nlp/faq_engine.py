# ==========================================================
# IMPORTS
# ==========================================================
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from models.db_connect import get_db_connection

import numpy as np
import psycopg2.extras
import logging
import random
import os
import markdown

from nlp.netoyage import nettoyer_message
from router.operation_router import detecter_operation

from services.controler.conversion_controler import convertir_operation
from services.agent_service import get_agent
from services.service_info import get_services
from services.tracking_service import get_colis_info
from nlp.preprocess_colis import est_code_colis

import google.generativeai as genai

# ==========================================================
# GEMINI CONFIG
# ==========================================================
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

gemini_model = genai.GenerativeModel(
    "models/gemini-flash-lite-latest"
)

# ==========================================================
# LOGGING
# ==========================================================
logging.basicConfig(level=logging.INFO)

# ==========================================================
# EMBEDDING MODEL
# ==========================================================
modele_embedding = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

SEUIL_INTENT = 0.60
CACHE_INTENTS = []

# ==========================================================
# CHARGER INTENTS
# ==========================================================
def charger_intents():

    global CACHE_INTENTS

    conn = get_db_connection()

    cur = conn.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor
    )

    cur.execute("""
        SELECT
            id,
            id_intent,
            sous_intent,
            phrase,
            mots_cles,
            embedding
        FROM chatbot.intent_examples
        WHERE embedding IS NOT NULL
    """)

    CACHE_INTENTS = cur.fetchall()

    cur.close()
    conn.close()

    logging.info(
        f"INTENTS CHARGÉS: {len(CACHE_INTENTS)}"
    )

# ==========================================================
# DETECTION INTENT
# ==========================================================
def detecter_intention(message):

    if not CACHE_INTENTS:
        charger_intents()

    emb_msg = modele_embedding.encode(
        [message],
        normalize_embeddings=True
    )

    embeddings = np.array([
        np.array(i["embedding"], dtype=float)
        for i in CACHE_INTENTS
    ])

    scores = cosine_similarity(
        emb_msg,
        embeddings
    )[0]

    best_index = np.argmax(scores)

    best_score = float(scores[best_index])

    best_data = CACHE_INTENTS[best_index]

    logging.info(
        f"INTENT={best_data['id_intent']} SCORE={best_score}"
    )

    return (
        best_data["id_intent"],
        best_data["sous_intent"],
        best_score
    )

# ==========================================================
# GET REPONSE DB
# ==========================================================
def get_reponse_intention(id_intent, sous_intent):

    conn = get_db_connection()

    cur = conn.cursor()

    cur.execute("""
        SELECT reponse
        FROM chatbot.intent_responses
        WHERE id_intent = %s
        AND sous_intent = %s
    """, (
        id_intent,
        sous_intent
    ))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    if not rows:
        return None

    return random.choice(rows)[0]

# ==========================================================
# HISTORY
# ==========================================================
def get_conversation_history(
    id_user,
    limit=6
):

    try:

        conn = get_db_connection()

        cur = conn.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
        )

        cur.execute("""
            SELECT
                message_user,
                reponse_bot
            FROM chatbot.conversations
            WHERE id_user = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (
            id_user,
            limit
        ))

        rows = cur.fetchall()

        cur.close()
        conn.close()

        rows.reverse()

        history = []

        for row in rows:

            if row["message_user"]:

                history.append({
                    "role": "user",
                    "content": row["message_user"]
                })

            if row["reponse_bot"]:

                history.append({
                    "role": "assistant",
                    "content": row["reponse_bot"]
                })

        return history

    except Exception as e:

        logging.error(
            f"HISTORY ERROR: {e}"
        )

        return []

# ==========================================================
# SAVE CONVERSATION
# ==========================================================
def sauvegarder_conversation(
    id_user,
    message_user,
    reponse_bot,
    id_intent=None,
    confidence=None
):

    try:

        conn = get_db_connection()

        cur = conn.cursor()

        cur.execute("""
            INSERT INTO chatbot.conversations
            (
                id_user,
                message_user,
                reponse_bot,
                id_intent,
                confidence
            )
            VALUES(%s,%s,%s,%s,%s)
        """, (
            id_user,
            message_user,
            reponse_bot,
            id_intent,
            confidence
        ))

        conn.commit()

        cur.close()
        conn.close()

    except Exception as e:

        logging.error(
            f"DB ERROR: {e}"
        )

# ==========================================================
# LLM FORMATTER
# UTILISÉ UNIQUEMENT POUR LES OPERATIONS
# ==========================================================
def formatter_operation_avec_llm(
    type_operation,
    message
):

    prompt = f"""
Tu es CTEXI-BOT,
l’assistant virtuel officiel de :

Cherif Trans Expert International (CTEXI)

Devise :
« Au cœur du Sahel, Au Service du Monde »

==================================================
🏢 A PROPOS DE CTEXI
==================================================

CTEXI est spécialisée dans :

• import-export Chine → Burkina Faso , sourcing fournisseurs (Ctexi buy)
• transport colis et marchandises (Ctexi cargo)
• paiement international          (Ctexi pay)
• réservation hôtel et visa Chine (Ctexi Travel)
• formation import-export (Ctexi academie)


==================================================
OBJECTIF
==================================================

Tu dois UNIQUEMENT améliorer le style du message.

==================================================
REGLES STRICTES
==================================================

- ne jamais changer le sens
- ne jamais ajouter des informations
- ne jamais inventer
- réponse courte
- maximum 2 phrases
- ton chaleureux
- ton professionnel
- emojis modérés

==================================================
TYPE OPERATION
==================================================

{type_operation}

==================================================
MESSAGE ORIGINAL
==================================================

{message}

==================================================
SORTIE
==================================================

Retourne uniquement le message final.
"""

    try:

        response = gemini_model.generate_content(prompt)

        if response and response.text:

            return markdown.markdown(
                response.text.strip()
            )

    except Exception as e:

        logging.error(
            f"FORMATTER ERROR: {e}"
        )

    return markdown.markdown(message)

# ==========================================================
# REFORMULATION INTENT DB
# ==========================================================
def reformuler_avec_gemini(
    message_user,
    reponse_brute,
    history=None
):

    historique = ""

    if history:

        for item in history[-6:]:

            historique += (
                f"{item['role']}: "
                f"{item['content']}\n"
            )

    prompt = f"""
Tu es CTEXI-BOT,
l’assistant virtuel officiel de :

Cherif Trans Expert International (CTEXI)

Devise :
« Au cœur du Sahel, Au Service du Monde »

==================================================
🏢 A PROPOS DE CTEXI
==================================================

CTEXI est spécialisée dans :

• import-export Chine → Burkina Faso , sourcing fournisseurs (Ctexi buy)
• transport colis et marchandises (Ctexi cargo)
• paiement international          (Ctexi pay)
• réservation hôtel et visa Chine (Ctexi Travel)
• formation import-export (Ctexi academie)

==================================================
HISTORIQUE
==================================================

{historique}

==================================================
MISSION
==================================================

Tu dois reformuler la réponse
pour qu'elle soit :

- naturelle
- moderne
- fluide
- professionnelle
- humaine

==================================================
REGLES STRICTES
==================================================

- garder EXACTEMENT le même sens
- ne rien inventer
- ne pas ajouter de prix, si besoin de prix propose une redirection vers un agent
- ne pas ajouter de délais
- ne pas ajouter de services

==================================================
STYLE
==================================================

Tu peux utiliser :

- emojis modérés
- listes
- ton premium
- ton rassurant



==================================================
📌 FORMAT
==================================================

Si réponse courte :
→ phrase naturelle

Si réponse longue :
→ listes
→ titres
→ étapes


==================================================
❌ IMPORTANT
==================================================

INTERDIT :
- inventer des prix propose plutot une redirection vers un agent
- inventer des délais
- inventer des services

Tu dois garder EXACTEMENT le sens.

==================================================
QUESTION UTILISATEUR
==================================================

{message_user}

==================================================
REPONSE BRUTE
==================================================

{reponse_brute}

==================================================
REPONSE FINALE
==================================================
"""

    try:

        response = gemini_model.generate_content(prompt)

        if response and response.text:

            return markdown.markdown(
                response.text.strip()
            )

    except Exception as e:

        logging.error(
            f"REFORMULATION ERROR: {e}"
        )

    return markdown.markdown(reponse_brute)

# ==========================================================
# GEMINI FALLBACK
# ==========================================================
def gemini_direct_answer(
    message,
    history=None
):

    historique = ""

    if history:

        for item in history[-6:]:

            historique += (
                f"{item['role']}: "
                f"{item['content']}\n"
            )

    prompt = f"""
Tu es CTEXI-BOT,
assistant officiel de CTEXI.

==================================================
A PROPOS DE CTEXI
==================================================

CTEXI est spécialisée dans :

- import-export Chine
- achat fournisseur
- transport colis
- paiement international
- visa Chine
- réservation hôtel
- formation import-export

==================================================
HISTORIQUE
==================================================

{historique}

==================================================
STYLE
==================================================

Le ton doit être :

- professionnel
- chaleureux
- moderne
- humain

Tu peux utiliser des emojis modérés 😊

==================================================
REGLES IMPORTANTES
==================================================

- ne jamais inventer des prix propose plutot une redirection vers un agent
- ne jamais dire (Nous ne proposons pas la vente d'un truc donné) dis plutot que tu n'a pas acces aux prix et propose plutot une redirection vers un agent
- ne jamais inventer des délais
- ne jamais inventer des services

Si l'information n'est pas connue :
invite le client à contacter un agent.

==================================================
REGLES DE SORTIE
==================================================

INTERDIT :

- "voici la réponse"
- "voici la reformulation"
- "je vais reformuler"
- phrases inutiles


Réponds directement.




==================================================
QUESTION CLIENT
==================================================

{message}

==================================================
REPONSE
==================================================
"""

    try:

        response = gemini_model.generate_content(prompt)

        if response and response.text:

            return markdown.markdown(
                response.text.strip()
            )

    except Exception as e:

        logging.error(
            f"LLM FALLBACK ERROR: {e}"
        )

    return """
<p>
Notre assistant est momentanément indisponible 😊
</p>
"""

# ==========================================================
# OPERATIONS
# ==========================================================
def gerer_operations(
    message,
    id_user
):

    op = detecter_operation(message)

    if not op:
        return None

    # ======================================================
    # CONVERSION
    # ======================================================
    if op == "conversion":

        result = convertir_operation(message)

        # ----------------------------------------------
        # PAS ASSEZ D'INFOS
        # ----------------------------------------------
        if not result:

            msg = """
💱 Veuillez entrer le montant
ainsi que les devises.

Exemple :
100 USD en EUR
"""

            return {
                "type": "conversion",
                "reponse": formatter_operation_avec_llm(
                    "conversion",
                    msg
                ),
                "trouve": False
            }

        # ----------------------------------------------
        # RESULTAT CONVERSION
        # ----------------------------------------------
        msg = f"""
💱 {result['montant']} {result['source']}
=
{result['resultat']} {result['cible']}
"""

        return {
            "type": "conversion",
            "reponse": formatter_operation_avec_llm(
                "conversion",
                msg
            ),
            "trouve": True
        }

    # ======================================================
    # TRACKING
    # ======================================================
    if op == "suivi_colis":

        code = est_code_colis(message)

        # ----------------------------------------------
        # PAS DE CODE
        # ----------------------------------------------
        if not code:

            msg = """
📦 Veuillez envoyer votre code de suivi.

Exemple :
CTX10001
"""

            return {
                "type": "tracking",
                "reponse": formatter_operation_avec_llm(
                    "tracking",
                    msg
                ),
                "trouve": False
            }

        # ----------------------------------------------
        # RECHERCHE COLIS
        # ----------------------------------------------
        result = get_colis_info(
            code,
            id_user
        )

        # ----------------------------------------------
        # COLIS INTROUVABLE
        # ----------------------------------------------
        if not result:

            msg = f"""
❌ Aucun colis trouvé
pour le code {code}
"""

            return {
                "type": "tracking",
                "reponse": formatter_operation_avec_llm(
                    "tracking",
                    msg
                ),
                "trouve": False
            }

        # ----------------------------------------------
        # COLIS TROUVÉ
        # ----------------------------------------------
        msg = f"""
📦 Colis {result['code']}

Statut :
{result['statut']}
"""

        return {
            "type": "tracking",
            "reponse": formatter_operation_avec_llm(
                "tracking",
                msg
            ),
            "data": result,
            "trouve": True
        }

    # ======================================================
    # CONTACT AGENT
    # ======================================================
    if op == "contact_agent":

        msg = """
👨‍💼 Merci de choisir
un moyen de contact disponible.
"""

        return {
            "type": "agent",
            "reponse": formatter_operation_avec_llm(
                "agent",
                msg
            ),
            "agent": get_agent(),
            "trouve": True
        }

    # ======================================================
    # SERVICES
    # ======================================================
    if op == "service_info":

        msg = """
📌 Voici les services
disponibles chez CTEXI.
"""

        return {
            "type": "service",
            "reponse": formatter_operation_avec_llm(
                "service",
                msg
            ),
            "services": get_services(),
            "trouve": True
        }

    return None

# ==========================================================
# MAIN ENGINE
# ==========================================================
def trouver_meilleure_correspondance(
    message,
    id_user
):

    logging.info(f"MESSAGE: {message}")

    message_original = message

    message = nettoyer_message(message)

    history = get_conversation_history(id_user)

    # ======================================================
    # 1. OPERATIONS
    # ======================================================
    op = gerer_operations(
        message,
        id_user
    )

    if op:

        logging.info(
            "[DEBUG] SOURCE = OPERATION"
        )

        sauvegarder_conversation(
            id_user,
            message_original,
            op["reponse"]
        )

        op["debug"] = {
            "source": "operation",
            "llm_used": True
        }

        return op

    # ======================================================
    # 2. INTENT MATCHING
    # ======================================================
    intent_id, sous_intent, score = detecter_intention(message)

    logging.info(
        f"[DEBUG] INTENT SCORE = {score}"
    )

    if score >= SEUIL_INTENT:

        reponse_brute = get_reponse_intention(
            intent_id,
            sous_intent
        )

        if reponse_brute:

            logging.info(
                "[DEBUG] SOURCE = DATABASE"
            )

            reponse_finale = reformuler_avec_gemini(
                message,
                reponse_brute,
                history
            )

            sauvegarder_conversation(
                id_user,
                message_original,
                reponse_finale,
                intent_id,
                float(score)
            )

            return {
                "type": "intent",
                "reponse": reponse_finale,
                "confidence": float(score),

                "debug": {
                    "source": "database + reformulation",
                    "llm_used": True,
                    "intent_match": True
                }
            }

    # ======================================================
    # 3. LLM FALLBACK
    # ======================================================
    logging.info(
        "[DEBUG] SOURCE = LLM FALLBACK"
    )

    reponse_llm = gemini_direct_answer(
        message,
        history
    )

    sauvegarder_conversation(
        id_user,
        message_original,
        reponse_llm,
        confidence=float(score)
    )

    return {
        "type": "llm",
        "reponse": reponse_llm,
        "confidence": float(score),

        "debug": {
            "source": "llm_only",
            "llm_used": True,
            "intent_match": False
        }
    }