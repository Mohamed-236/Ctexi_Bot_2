
"""
ctexi_bot/
│
├── app.py                  # Point d’entrée Flask
├── config.py               # Configuration (DB, clés, etc.)
├── .env                    # Variables d’environnement (secret)
├── requirements.txt        # Dépendances
│
├── /routes/                # Endpoints API
│   ├── chatbot_routes.py   # /api/chatbot/message
│   ├── colis_routes.py     # /api/colis/{code}
│   ├── taux_routes.py      # /api/taux
│   └── contact_routes.py   # /api/contact
│
├── /services/              # Logique métier
│   ├── chatbot_service.py  # NLP, intents, réponses
│   ├── colis_service.py
│   ├── taux_service.py
│   └── faq_service.py
│
├── /models/                # Accès BD
│   ├── db.py               # Connexion PostgreSQL
│   ├── message_model.py
│   ├── colis_model.py
│   ├── faq_model.py
│   └── user_model.py
│
├── /nlp/
│   └── spacy_nlp.py        # Chargement spaCy + intents
│
├── /utils/
│   └── helpers.py
│
└── /tests/
    └── test_api.py
"""