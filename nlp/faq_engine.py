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
# gemini_model = genai.GenerativeModel("models/gemini-2.5-flash")

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
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("""
        SELECT id, id_intent, sous_intent, phrase, mots_cles, embedding
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

    message = message.lower()
    score = 0

    for mot in mots_cles:
        if mot.lower() in message:
            score += 0.08

    return score


# ==========================================================
# INTENT DETECTION
# ==========================================================
def detecter_intention(message):

    if not CACHE_INTENTS:
        charger_intents()

    emb_msg = modele_embedding.encode([message], normalize_embeddings=True)

    embeddings = np.array([
        np.array(i["embedding"], dtype=float)
        for i in CACHE_INTENTS
    ])

    scores = cosine_similarity(emb_msg, embeddings)[0]

    final_scores = []

    for idx, score in enumerate(scores):

        item = CACHE_INTENTS[idx]
        boost = calculer_boost_keywords(message, item["mots_cles"])
        final_scores.append(score + boost)

    best_index = np.argmax(final_scores)
    best_score = final_scores[best_index]
    best = CACHE_INTENTS[best_index]

    logging.info(f"INTENT={best['id_intent']} SCORE={best_score}")

    return best["id_intent"], best["sous_intent"], best_score


# ==========================================================
# DB RESPONSE
# ==========================================================
def get_reponse_intention(id_intent, sous_intent):

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT reponse
        FROM chatbot.intent_responses
        WHERE id_intent = %s AND sous_intent = %s
    """, (id_intent, sous_intent))

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return random.choice(rows)[0] if rows else None


# ==========================================================
# GEMINI REFORMULATION (AMELIORATION STYLE)
# ==========================================================
# ==========================================================
# GEMINI REFORMULATION AVANCEE CTEXI
# ==========================================================
def reformuler_avec_gemini(
    message_user,
    reponse_brute,
    history=None
):

    try:

        # ==================================================
        # HISTORIQUE CONVERSATION
        # ==================================================
        historique = ""

        if history:

            for item in history[-5:]:

                role = item.get("role", "user")
                content = item.get("content", "")

                historique += f"{role}: {content}\n"

        # ==================================================
        # PROMPT CTEXI PREMIUM
        # ==================================================
        prompt = f"""
Tu es CTEXI-BOT,
l’assistant virtuel officiel de :

Cherif Trans Expert International (CTEXI)

Devise :
« Au cœur du Sahel, Au Service du Monde »

==================================================
🏢 A PROPOS DE CTEXI
==================================================

CTEXI est une entreprise spécialisée dans :

• l’achat de produits en Chine
• le sourcing fournisseurs
• le transport Chine → Afrique
• les paiements internationaux
• le voyage Chine
• les formations import-export

Services principaux :

1. CTEXI BUY
→ recherche fournisseurs
→ négociation
→ contrôle qualité

2. CTEXI CARGO
→ transport maritime
→ transport aérien
→ suivi colis

3. CTEXI PAY
→ paiements fournisseurs
→ Alipay
→ WeChat Pay
→ conversion devise

4. CTEXI TRAVEL
→ visa Chine
→ billet avion
→ hôtel

5. CTEXI ACADÉMIE
→ formation import-export
→ Alibaba
→ sourcing
→ e-commerce

==================================================
🎯 TON OBJECTIF
==================================================

Tu dois améliorer la réponse donnée afin qu’elle soit :

• naturelle
• humaine
• professionnelle
• moderne
• fluide
• agréable à lire

==================================================
💬 STYLE OBLIGATOIRE
==================================================

Tu peux utiliser naturellement des expressions comme :

• « Excellente question 😊 »
• « Très bon choix 👍 »
• « Avec plaisir »
• « Pas de souci 👌 »
• « Nous allons vous accompagner »

Tu peux utiliser des emojis MODÉRÉMENT.

Le ton doit être :
• chaleureux
• premium
• rassurant
• professionnel

==================================================
📌 STRUCTURE DES RÉPONSES
==================================================

Si la réponse est courte :
→ phrase simple améliorée

Si la réponse est moyenne :
→ paragraphes propres

Si la réponse est longue :
→ structure avec :

✅ titres
✅ listes à puces
✅ étapes
✅ emojis modérés

Exemple :

📦 Voici comment fonctionne notre service :

• Étape 1 : ...
• Étape 2 : ...
• Étape 3 : ...

==================================================
🧠 CONTEXTE CONVERSATIONNEL
==================================================

Tu dois tenir compte de l’historique conversationnel.

Historique récent :
{historique}

==================================================
❌ RÈGLES IMPORTANTES
==================================================

INTERDIT :
- inventer des prix
- inventer des délais
- inventer des services
- modifier les informations
- répondre hors sujet

Tu dois garder EXACTEMENT le même sens.

==================================================
📥 DONNÉES UTILISATEUR
==================================================

Utilisateur :
{message_user}

Réponse brute :
{reponse_brute}

==================================================
📤 RÉSULTAT FINAL
==================================================

Réécris uniquement la réponse finale améliorée.
"""

        # ==================================================
        # APPEL GEMINI
        # ==================================================
        response = gemini_model.generate_content(prompt)

        # ==================================================
        # VALIDATION
        # ==================================================
        if response and response.text:

            final_text = response.text.strip()

            # éviter réponses trop courtes
            if len(final_text) > 5:
                return final_text

        return reponse_brute

    except Exception as e:

        logging.error(f"GEMINI ERROR: {e}")

        return reponse_brute

# ==========================================================
# GEMINI DIRECT ANSWER (FALLBACK INTELLIGENT)
# ==========================================================
def gemini_direct_answer(message):

    try:

        prompt = f"""
Tu es CTEXI-BOT, l'assistant officiel de l'entreprise CTEXI
(Cherif Trans Expert International).

==================================================
🏢 A PROPOS DE CTEXI
==================================================

Devise :
"Au cœur du Sahel, Au Service du Monde."

CTEXI accompagne les clients du Burkina Faso et d'Afrique
dans leurs opérations avec la Chine.

Services principaux :

1. CTEXI BUY
- recherche fournisseurs
- achat produits Chine
- négociation prix
- contrôle qualité

2. CTEXI CARGO
- transport colis Chine → Burkina Faso
- fret aérien et maritime
- suivi colis

3. CTEXI PAY
- paiement fournisseurs chinois
- Alipay
- WeChat Pay
- conversion devises

4. CTEXI TRAVEL
- visa Chine
- réservation hôtel
- billet avion

5. CTEXI ACADÉMIE
- formations import-export
- Alibaba
- sourcing
- e-commerce

==================================================
🎯 TON OBJECTIF
==================================================

Tu dois répondre comme un véritable assistant premium.

Tu aides le client :
- clairement
- rapidement
- naturellement
- professionnellement

==================================================
💬 STYLE OBLIGATOIRE
==================================================

Le ton doit être :
- humain
- chaleureux
- professionnel
- moderne
- intelligent

Tu peux utiliser :
- emojis modérés 😊
- expressions naturelles :
  "Très bon choix 👍"
  "Avec plaisir"
  "Bonne question 😊"

==================================================
📌 FORMAT DES RÉPONSES
==================================================

Si réponse courte :
→ phrase fluide naturelle

Si réponse moyenne :
→ paragraphes clairs

Si réponse longue :
→ structure avec :
• listes
• titres
• étapes

==================================================
❌ INTERDIT
==================================================

- ne jamais inventer de faux prix
- ne jamais inventer de faux délais
- ne jamais inventer de faux services
- si information inconnue :
  inviter le client à contacter un agent

==================================================
📌 IMPORTANT
==================================================

Tu représentes une vraie entreprise professionnelle.

Tu dois donner l'impression :
- d'un assistant haut de gamme
- intelligent
- rassurant
- utile

==================================================
👤 QUESTION CLIENT
==================================================

{message}

==================================================
📤 RÉPONSE
==================================================
"""

        response = gemini_model.generate_content(prompt)

        if response and response.text:
            return response.text.strip()

        return "Je ne peux pas répondre pour le moment."

    except Exception as e:

        logging.error(f"GEMINI FALLBACK ERROR: {e}")

        return (
            "Merci pour votre message.Notre assistant est momentanément indisponible. "
            "Veuillez réessayer dans quelques instants 😊"
        )
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
# MAIN ENGINE (HYBRIDE FINAL)
# ==========================================================
def trouver_meilleure_correspondance(message, id_user):

    logging.info(f"MESSAGE: {message}")

    message = nettoyer_message(message)

    # 1. OPERATIONS
    op = gerer_operations(message, id_user)
    if op:
        return op

    # 2. INTENT DETECTION
    intent_id, sous_intent, score = detecter_intention(message)

    # 3. SI BON MATCH DB
    if score >= SEUIL_INTENT:

        reponse_brute = get_reponse_intention(intent_id, sous_intent)

        if reponse_brute:

            reponse_finale = reformuler_avec_gemini(
                message,
                reponse_brute
            )

            return {
                "type": "intent",
                "intent_id": intent_id,
                "reponse": reponse_finale,
                "trouve": True,
                "confidence": float(score)
            }

    # 4. FALLBACK INTELLIGENT (IMPORTANT)
    reponse_llm = gemini_direct_answer(message)

    return {
        "type": "llm_fallback",
        "reponse": reponse_llm,
        "trouve": True,
        "confidence": float(score)
    }