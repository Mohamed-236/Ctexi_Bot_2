from locust import HttpUser, task, between
import random

class ChatbotUser(HttpUser):
    wait_time = between(1, 3)

    messages = [
        "Bonjour",
        "Quels sont vos services ?",
        "Je veux suivre mon colis",
        "Comment obtenir un visa Chine ?",
        "Quel est le taux de change USD FCFA ?",
        "Comment contacter un agent ?"
    ]

    @task
    def envoyer_message(self):

        payload = {
            "message": random.choice(self.messages),
            "id_user": random.randint(1, 10000)
        }

        self.client.post(
            "/api/faq/message",
            json=payload
        )