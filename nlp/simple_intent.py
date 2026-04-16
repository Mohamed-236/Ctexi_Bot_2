from rapidfuzz import fuzz
import random

SEUIL = 80  # tolérance fautes

INTENTS_LIGHT = {
    "salutation": {
        "patterns": [
            "salut",
            "bonjour",
            "bonsoir",
            "coucou",
            "hello",
            "cc",
            "ca va",
            "ça va"
        ],
        "responses": [
            "Bonjour 👋 Comment puis-je vous aider ?",
            "Salut 😊 Que puis-je faire pour vous ?",
            "Bonsoir 👋 Comment puis-je vous assister ?",
            "Hello 👋 Je suis là pour vous aider !"
        ]
    },

    "merci": {
        "patterns": [
            "merci",
            "merci beaucoup",
            "thanks",
            "thx"
        ],
        "responses": [
            "Avec plaisir 😊",
            "Je vous en prie 👍",
            "Toujours là pour vous aider 😉"
        ]
    },

    "au_revoir": {
        "patterns": [
            "au revoir",
            "bye",
            "a plus",
            "a bientot"
        ],
        "responses": [
            "Au revoir 👋 À bientôt !",
            "Bye 👋 Passez une excellente journée !",
            "À la prochaine 😊"
        ]
    }
}


def detecter_intent_light(message: str):
    best_intent = None
    best_score = 0

    for intent, data in INTENTS_LIGHT.items():
        for pattern in data["patterns"]:
            score = fuzz.ratio(message, pattern)

            if score > best_score:
                best_score = score
                best_intent = intent

    if best_score >= SEUIL:
        return best_intent

    return None


def repondre_intent_light(intent):
    if intent not in INTENTS_LIGHT:
        return None

    return random.choice(INTENTS_LIGHT[intent]["responses"])