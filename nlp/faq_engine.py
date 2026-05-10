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

# ==========================================================
# GEMINI
# ==========================================================
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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

    logging.info(f"INTENTS CHARGÉS: {len(CACHE_INTENTS)}")


# ==========================================================
# BOOST MOTS CLES
# ==========================================================
def calculer_boost_keywords(message, mots_cles):

    if not mots_cles:
        return 0

    score = 0
    message = message.lower()

    for mot in mots_cles:

        if mot.lower() in message:
            score += 0.08

    return score


# ==========================================================
# DETECTION INTENTION
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

    final_scores = []

    for idx, score in enumerate(scores):

        item = CACHE_INTENTS[idx]

        boost = calculer_boost_keywords(
            message,
            item["mots_cles"]
        )

        final_scores.append(score + boost)

    best_index = np.argmax(final_scores)

    best_score = final_scores[best_index]
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
# RECUPERER REPONSE DB
# ==========================================================
def get_reponse_intention(id_intent, sous_intent):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT reponse
        FROM chatbot.intent_responses
        WHERE id_intent = %s
        AND sous_intent = %s
    """, (id_intent, sous_intent))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    if not rows:
        return None

    return random.choice(rows)[0]


# ==========================================================
# MEMOIRE CONVERSATIONNELLE
# ==========================================================
def get_conversation_history(id_user, limit=6):

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
        """, (id_user, limit))

        rows = cur.fetchall()

        cur.close()
        conn.close()

        history = []

        rows.reverse()

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

        logging.error(f"HISTORY ERROR: {e}")

        return []


# ==========================================================
# SAUVEGARDE CONVERSATION
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
            INSERT INTO chatbot.conversations(
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

        logging.error(f"SAVE CONVERSATION ERROR: {e}")


# ==========================================================
# GEMINI REFORMULATION
# ==========================================================
def reformuler_avec_gemini(
    message_user,
    reponse_brute,
    history=None
):

    try:

        historique = ""

        if history:

            for item in history[-6:]:

                role = item.get("role", "user")
                content = item.get("content", "")

                historique += f"{role}: {content}\n"

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

• import-export Chine → Afrique
• sourcing fournisseurs
• transport colis
• paiement international
• visa Chine
• réservation hôtel
• formation import-export

==================================================
🧠 CONTEXTE CONVERSATIONNEL
==================================================

Historique récent :
{historique}

==================================================
🎯 OBJECTIF
==================================================

Tu dois améliorer la réponse donnée afin qu’elle soit :

• naturelle
• humaine
• professionnelle
• moderne
• fluide

==================================================
💬 STYLE
==================================================

Tu peux utiliser :

• "Excellente question 😊"
• "Très bon choix 👍"
• "Avec plaisir"
• "Pas de souci 👌"

Utilise des emojis modérément.

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
- inventer des prix
- inventer des délais
- inventer des services

Tu dois garder EXACTEMENT le sens.

==================================================
👤 UTILISATEUR
==================================================

Question :
{message_user}

Réponse brute :
{reponse_brute}

==================================================
📤 REPONSE FINALE
==================================================
"""

        response = gemini_model.generate_content(prompt)

        if response and response.text:

            final_text = response.text.strip()

            if len(final_text) > 5:

                html = markdown.markdown(final_text)

                return html

        return reponse_brute

    except Exception as e:

        logging.error(f"GEMINI ERROR: {e}")

        return reponse_brute


# ==========================================================
# GEMINI DIRECT ANSWER
# ==========================================================
def gemini_direct_answer(message, history=None):

    try:

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
🏢 ENTREPRISE
==================================================

CTEXI aide les clients dans :

• achat Chine
• sourcing fournisseur
• transport colis
• paiement Chine
• visa Chine
• réservation hôtel
• formation import-export

==================================================
🧠 HISTORIQUE CONVERSATION
==================================================

{historique}

==================================================
🎯 OBJECTIF
==================================================

Réponds naturellement,
professionnellement
et intelligemment.

==================================================
💬 STYLE
==================================================

Le ton doit être :

• humain
• premium
• rassurant
• chaleureux

Tu peux utiliser des emojis modérés 😊

==================================================
❌ INTERDIT
==================================================

- ne pas inventer de prix
- ne pas inventer de délais
- si info inconnue :
  inviter le client à contacter un agent

==================================================
👤 QUESTION CLIENT
==================================================

{message}

==================================================
📤 REPONSE
==================================================
"""

        response = gemini_model.generate_content(prompt)

        if response and response.text:

            html = markdown.markdown(
                response.text.strip()
            )

            return html

        return "Je ne peux pas répondre pour le moment."

    except Exception as e:

        logging.error(f"GEMINI FALLBACK ERROR: {e}")

        return """
<p>
Merci pour votre message 😊<br><br>
Notre assistant est momentanément indisponible.
Veuillez réessayer dans quelques instants.
</p>
"""


# ==========================================================
# OPERATIONS
# ==========================================================
def gerer_operations(message, id_user):

    op = detecter_operation(message)

    if op == "suivi_colis":

        info = get_colis_info(message, id_user)

        return {
            "type": "tracking",
            "reponse": "Colis trouvé" if info else "Introuvable",
            "data": info,
            "trouve": bool(info)
        }

    if op == "conversion":

        result = convertir_operation(message)

        return {
            "type": "conversion",
            "reponse": "Conversion OK" if result else "Erreur",
            "trouve": bool(result)
        }

    if op == "contact_agent":

        agent = get_agent()

        return {
            "type": "agent",
            "reponse": "Agent disponible" if agent else "Aucun agent",
            "agent": agent,
            "trouve": bool(agent)
        }

    if op == "service_info":

        services = get_services()

        return {
            "type": "service",
            "reponse": "Services disponibles",
            "services": services,
            "trouve": True
        }

    return None


# ==========================================================
# MAIN ENGINE FINAL
# ==========================================================
def trouver_meilleure_correspondance(
    message,
    id_user
):

    logging.info(f"MESSAGE: {message}")

    message_original = message

    message = nettoyer_message(message)

    # ======================================================
    # MEMOIRE CONVERSATIONNELLE
    # ======================================================
    history = get_conversation_history(id_user)

    # ======================================================
    # OPERATIONS
    # ======================================================
    op = gerer_operations(message, id_user)

    if op:

        sauvegarder_conversation(
            id_user=id_user,
            message_user=message_original,
            reponse_bot=op["reponse"]
        )

        return op

    # ======================================================
    # INTENT DETECTION
    # ======================================================
    intent_id, sous_intent, score = detecter_intention(message)

    # ======================================================
    # SI MATCH TROUVE
    # ======================================================
    if score >= SEUIL_INTENT:

        reponse_brute = get_reponse_intention(
            intent_id,
            sous_intent
        )

        if reponse_brute:

            reponse_finale = reformuler_avec_gemini(
                message_user=message,
                reponse_brute=reponse_brute,
                history=history
            )

            sauvegarder_conversation(
                id_user=id_user,
                message_user=message_original,
                reponse_bot=reponse_finale,
                id_intent=intent_id,
                confidence=score
            )

            return {
                "type": "intent",
                "intent_id": intent_id,
                "sous_intent": sous_intent,
                "reponse": reponse_finale,
                "trouve": True,
                "confidence": float(score)
            }

    # ======================================================
    # FALLBACK GEMINI
    # ======================================================
    reponse_llm = gemini_direct_answer(
        message,
        history
    )

    sauvegarder_conversation(
        id_user=id_user,
        message_user=message_original,
        reponse_bot=reponse_llm,
        confidence=score
    )

    return {
        "type": "llm_fallback",
        "reponse": reponse_llm,
        "trouve": True,
        "confidence": float(score)
    }