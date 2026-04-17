# ==========================================================
# IMPORTS
# ==========================================================

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from models.db_connect import get_db_connection
from models.contact_agent import recuperer_agent_par_intention
from models.service import recuperer_service_par_intention

import numpy as np
import psycopg2.extras
import logging

from models.suivi_colis import recuperer_colis
from nlp.preprocess_colis import est_code_colis
from nlp.netoyage import nettoyer_message


from services.conversion_service import convertir_devise
from nlp.extraction_devise import extraire_donnees_conversion




#===============================================================
# Les operations

from router.operation_router import detecter_operation
from services.tracking_service import get_colis_info
from services.controler.conversion_controler import convertir_operation
from services.agent_service import get_agent
from services.service_info import get_services
#===============================================================
from nlp.simple_intent import detecter_intent_light, repondre_intent_light



# ==========================================================
# LOGGING
# ==========================================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# ==========================================================
# MODELE
# ==========================================================
modele_embedding = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

SEUIL_FAQ = 0.55
MARGE = 0.1


# ==========================================================
# CACHE
# ==========================================================
CACHE_FAQ = []


# ==========================================================
# CHARGEMENT FAQ
# ==========================================================
def charger_faq():
    global CACHE_FAQ

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cur.execute("""
        SELECT id_faq, id_intent, message_user, reponse_bot, embedding
        FROM chatbot.faq
        WHERE embedding IS NOT NULL
    """)

    CACHE_FAQ = cur.fetchall()

    cur.close()
    conn.close()

    logging.info(f"{len(CACHE_FAQ)} FAQ chargées")


# ==========================================================
# TOP-K FAQ
# ==========================================================
def rechercher_faq_top_k(embedding_message, top_k=5):
    global CACHE_FAQ

    if not CACHE_FAQ:
        charger_faq()

    embeddings = np.array([
        np.array(f["embedding"], dtype=float)
        for f in CACHE_FAQ
    ])

    scores = cosine_similarity(embedding_message, embeddings)[0]

    top_indices = np.argsort(scores)[-top_k:][::-1]

    top_faqs = [(CACHE_FAQ[i], scores[i]) for i in top_indices]

    best_faq, best_score = top_faqs[0]
    second_score = top_faqs[1][1] if len(top_faqs) > 1 else 0

    logging.info(f"BEST FAQ: {best_faq['message_user']} => {best_score:.4f}")

    # ==========================
    # 🔥 FIX IMPORTANT 1 : SCORE MIN
    # ==========================
    if best_score < SEUIL_FAQ:
        return None, best_score

    # ==========================
    # 🔥 FIX IMPORTANT 2 : ANTI-CONFUSION (TRÈS IMPORTANT)
    # ==========================

    gap = best_score - second_score

    # 🔥 CAS 1 : score très élevé → on accepte toujours
    if best_score >= 0.75:
        return {
            "type": "ok",
            "faq": best_faq
        }, best_score

    # 🔥 CAS 2 : score moyen → vérifier gap
    if gap < 0.03:
        logging.info("FAQ ambiguë détectée (score proche)")

        return {
            "type": "incertain",
            "faq": best_faq,
            "suggestions": [f[0]["message_user"] for f in top_faqs[1:3]]
        }, best_score

    # ==========================
    # ⚠️ CAS INCERTAIN
    # ==========================
    if SEUIL_FAQ <= best_score < (SEUIL_FAQ + MARGE):
        return {
            "type": "incertain",
            "faq": best_faq,
            "suggestions": [f[0]["message_user"] for f in top_faqs[1:3]]
        }, best_score

    # ==========================
    # ✅ CAS OK
    # ==========================
    return {
        "type": "ok",
        "faq": best_faq
    }, best_score

# ==========================================================
# MOTEUR PRINCIPAL
# ==========================================================

def trouver_meilleure_correspondance(message_utilisateur, id_user):

    logging.info(f"Message: {message_utilisateur}")

    # ==========================
    # ROUTER CENTRAL
    # ==========================
    # message_clean = nettoyer_message(message_utilisateur)


    # ==========================
    # INTENTS SIMPLES (PRIORITÉ MAX)
    # ==========================
    intent_light = detecter_intent_light(message_utilisateur)

    if intent_light:
        return {
            "type": intent_light,
            "reponse": repondre_intent_light(intent_light),
            "trouve": True
        }



    operation = detecter_operation(message_utilisateur)

    # ==========================
    # TRACKING
    # ==========================
    if operation == "suivi_colis":

        info = get_colis_info(message_utilisateur, id_user)

        if info:
            return {
                "type": "tracking",
                "reponse": "Voici les informations de votre colis",
                "data": info,
                "trouve": True
            }

        code = est_code_colis(message_utilisateur)

        if code:
            return {
                "type": "tracking_not_found",
                "reponse": "Aucun colis trouvé ou code non attribué a l'utilisateur connecté.",
                "trouve": False
            }

        return {
            "type": "tracking_request",
            "reponse": "Veuillez entrer votre code colis CTExI pour voir les informations:",
            "trouve": True
        }
    

    # ==========================
    # CONVERSION
    # ==========================
    if operation == "conversion":
        result = convertir_operation(message_utilisateur)

        # ✅ CAS 1 : conversion complète
        if result:
            return {
                "type": "conversion",
                "reponse": f"{result['montant']} {result['source']} ≈ {result['resultat']} {result['cible']}",
                "trouve": True
            }

        # ✅ CAS 2 : intention détectée MAIS données manquantes
        return {
            "type": "conversion_help",
            "reponse": "Veuillez préciser le montant et les devises.\nExemple : 5000 FCFA en EUR",
            "trouve": True
        }
    # ==========================
    # AGENT
    # ==========================
    if operation == "contact_agent":

        agent = get_agent()

        if agent:
            return {
                "type": "agent",
                "reponse": "Je vous mets en relation avec un agent",
                "agent": agent,
                "trouve": True
            }

        return {
            "type": "fallback",
            "reponse": "Aucun agent disponible.",
            "trouve": False
        }

    # ==========================
    # SERVICES
    # ==========================
    if operation == "service_info":

        services = get_services()

        return {
            "type": "service",
            "reponse": "Voici nos services disponibles",
            "services": services,
            "trouve": True
        }

    # ==========================
    # FAQ (IA)
    # ==========================
    embedding_message = modele_embedding.encode(
        [message_utilisateur],
        normalize_embeddings=True
    )

    faq, score = rechercher_faq_top_k(embedding_message)

    if faq:
        if faq["type"] == "incertain":
            return {
                "type": "faq_incertain",
                "reponse": faq["faq"]["reponse_bot"],
                "suggestions": faq["suggestions"],
                "trouve": True
            }

        return {
            "type": "faq",
            "reponse": faq["faq"]["reponse_bot"],
            "trouve": True
        }

    # ==========================
    # FALLBACK FINAL
    # ==========================
    agent = get_agent()

    if agent:
        return {
            "type": "agent",
            "reponse": "Je ne suis pas sûr de comprendre.Merci de contacter un agent pour plus d'eclaircissement.",
            "agent": agent,
            "trouve": False
        }

    return {
        "type": "fallback",
        "reponse": "Je ne comprends pas votre demande.",
        "trouve": False
    }