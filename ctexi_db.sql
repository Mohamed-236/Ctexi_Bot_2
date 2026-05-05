-- Active: 1774354264909@@127.0.0.1@5432@ctexi_db

-----------------------------------CREATION DES SCHEMA---------------------------------------------------


-- installation de  pgvector(extension de postgres) pour la creation des embedding
CREATE EXTENSION IF NOT EXISTS vector;

SET search_path TO public;

-- Mdp:postgres: Yakfis@226



-- ---------AUTH
CREATE SCHEMA IF NOT EXISTS auth;

-----------CHATBOT
CREATE SCHEMA IF NOT EXISTS chatbot;

------------CORE
CREATE SCHEMA IF NOT EXISTS core;

-----------SYSTEM
CREATE SCHEMA IF NOT EXISTS systems;




---------------------CREATION DES TABLES POUR LES SCHEMAS-------------------------------------------




--------------------------------------SCHEMA AUTH---------------------------------------------------


-- Table users
CREATE TABLE auth.users(
    id_user SERIAL PRIMARY KEY,
    nom VARCHAR(50) NOT NULL,
    prenom VARCHAR(50) NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    telephone VARCHAR(20) NOT NULL,
    mdp_hash TEXT NOT NULL,
    est_admin BOOLEAN DEFAULT FALSE,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    
); 


--Table agents
CREATE TABLE auth.agents(
    id_agent SERIAL PRIMARY KEY,
    id_intent INTEGER REFERENCES chatbot.intention(id_intent) ON DELETE CASCADE,
    whatsapp VARCHAR(20) NOT NULL,
    telephone VARCHAR(20) NOT NULL,
    email VARCHAR(50) NOT NULL,
    actif BOOLEAN DEFAULT TRUE,
    dates TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

----------------------------------NSERTION DES AGENTS EXEMPLE--------------------------------------


INSERT INTO auth.agents ( id_intent, whatsapp, telephone, email)
VALUES
(1, '22674381094', '+22669090991',  'yakfismokonzi@gmail.com'),
(2, '22674381094', '+22669090991',  'yakfismokonzi@gmail.com'),
(3, '22674381094', '+22669090991',  'yakfismokonzi@gmail.com'),
(4, '22674381094', '+22669090991',  'yakfismokonzi@gmail.com'),
(5, '22674381094', '+22669090991',  'yakfismokonzi@gmail.com'),
(6, '22674381094', '+22669090991',  'yakfismokonzi@gmail.com'),
(7, '22674381094', '+22669090991',  'yakfismokonzi@gmail.com'),
(8, '22674381094', '+22669090991',  'yakfismokonzi@gmail.com'),
(9, '22674381094', '+22669090991',  'yakfismokonzi@gmail.com'),
(10,'22674381094', '+22669090991',  'yakfismokonzi@gmail.com'),
(11,'22674381094', '+22669090991',  'yakfismokonzi@gmail.com'),
(12,'22674381094', '+22669090991',  'yakfismokonzi@gmail.com');




-------------------------------------SCHEMA CHATBOT--------------------------------------------------------------


--table faq

CREATE TABLE chatbot.faq(
    id_faq SERIAL PRIMARY KEY,
    id_intent INT REFERENCES chatbot.intention(id_intent) ON DELETE CASCADE,
    message_user TEXT,
    reponse_bot TEXT,
    embedding vector(384),
    dates TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);




-- Table des opérations
CREATE TABLE chatbot.operation (
    id_operation SERIAL PRIMARY KEY,
    nom_operation VARCHAR(100) UNIQUE NOT NULL,
    descriptions TEXT,
    est_actif BOOLEAN DEFAULT TRUE,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



-- Table des phrases utilisateur (patterns)
CREATE TABLE chatbot.operation_phrase (
    id_phrase SERIAL PRIMARY KEY,
    id_operation INT REFERENCES chatbot.operation(id_operation) ON DELETE CASCADE,
    id_intent INT REFERENCES chatbot.intention(id_intent) ON DELETE CASCADE,
    phrase TEXT NOT NULL,
    est_actif BOOLEAN DEFAULT TRUE,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);




------------------------------Insertion dans les tables operations--------------------------------------


INSERT INTO chatbot.operation (nom_operation) VALUES
('suivi_colis'),
('conversion'),
('contact_agent'),
('service_info');



INSERT INTO chatbot.operation_phrase (id_operation, id_intent, phrase) VALUES
(1, 9, 'je veux suivre mon colis'),
(1, 9, 'ou est mon colis'),
(1, 9, 'je veux localiser mon colis'),
(1, 9, 'suivi de colis'),
(1, 9, 'voir statut de mon colis');

-------------------
INSERT INTO chatbot.operation_phrase (id_operation, id_intent, phrase) VALUES
(2, 12, 'je veux convertir de l argent'),
(2, 12, 'convertir devise'),
(2, 12, 'faire une conversion de monnaie'),
(2, 12, 'je veux connaitre le taux de change'),
(2, 12, 'convertir montant en devise');

------------------
INSERT INTO chatbot.operation_phrase (id_operation, id_intent, phrase) VALUES
(3, 10, 'je veux parler a un agent'),
(3, 10, 'je veux contacter le support'),
(3, 10, 'je veux parler a quelqu un'),
(3, 10, 'je veux assistance humaine'),
(3, 10, 'contacter un conseiller');

----------------
INSERT INTO chatbot.operation_phrase (id_operation, id_intent, phrase) VALUES
(4, 11, 'je veux voir vos services'),
(4, 11, 'quels sont vos services'),
(4, 11, 'liste de vos services'),
(4, 11, 'montre moi vos services'),
(4, 11, 'je veux connaitre vos offres');





TRUNCATE TABLE chatbot.operation_phrase RESTART IDENTITY;






--Table convesation


SELECT * FROM chatbot.conversations;

DROP TABLE chatbot.conversations CASCADE;

-- version numero 2:

CREATE TABLE chatbot.conversations (
    id_conv SERIAL PRIMARY KEY,
    id_user INTEGER NOT NULL REFERENCES auth.users(id_user) ON DELETE CASCADE,

    message_user TEXT NOT NULL,
    reponse_bot TEXT,

    id_intent INT REFERENCES chatbot.intention(id_intent),
    id_operation INT REFERENCES chatbot.operation(id_operation),

    confidence FLOAT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);




--Table intention

CREATE TABLE chatbot.intention(
    id_intent SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL,
    type_intent VARCHAR(50) NOT NULL,
    descriptions TEXT,
    dates TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



-------------------------------------SCHEMA CORE--------------------------------------------------------------


--Table services
CREATE TABLE core.service(
    id_service SERIAL PRIMARY KEY,
    nom_service VARCHAR (255),
    descriptions TEXT,
    menu JSONB,
    icone VARCHAR(255)

);


INSERT INTO core.service (nom_service, descriptions, menu, icone) VALUES
(
    'CTEXI Buy',
    'CTEXI Buy est le service d’achat de produits en Chine, sécurisé et fiable. Il accompagne le client de la recherche à la livraison.',
    '{
        "description": "CTEXI Buy vous permet d’acheter facilement des produits en Chine. L’entreprise se charge de trouver les fournisseurs fiables, d’acheter, vérifier, conditionner et expédier les produits vers le Burkina Faso.",
        "fonctionnalites": [
            "Recherche des produits selon les besoins du client",
            "Sourcing de fournisseurs fiables",
            "Achat des produits",
            "Vérification qualité et conformité",
            "Conditionnement sécurisé",
            "Expédition vers le Burkina Faso"
        ],
        "avantages": [
            "Sécurité maximale des transactions",
            "Expertise locale et connaissance du marché chinois",
            "Réduction des risques d’erreur",
            "Processus transparent étape par étape"
        ],
        "processus": [
            {"etape": 1, "titre": "Recherche produit"},
            {"etape": 2, "titre": "Sourcing fournisseurs"},
            {"etape": 3, "titre": "Achat"},
            {"etape": 4, "titre": "Vérification qualité"},
            {"etape": 5, "titre": "Conditionnement"},
            {"etape": 6, "titre": "Expédition"}
        ]
    }',
    'ctexi_buy.png'
),
(
    'CTEXI Cargo',
    'CTEXI Cargo vous permet de suivre l’expédition de vos colis depuis la Chine vers le Burkina Faso avec un suivi en temps réel.',
    '{
        "description": "CTEXI Cargo permet aux clients de suivre leurs colis depuis l’enregistrement en Chine jusqu’à la livraison finale au Burkina Faso. Chaque colis reçoit un code unique et des notifications automatiques sont envoyées à chaque étape.",
        "fonctionnalites": [
            "Enregistrement de colis avec code unique",
            "Suivi en temps réel des colis",
            "Notifications automatiques par WhatsApp ou SMS",
            "Gestion des changements de téléphone et des colis multiples"
        ],
        "avantages": [
            "Suivi précis et transparent",
            "Notifications instantanées pour chaque mise à jour",
            "Possibilité de suivre plusieurs colis simultanément",
            "Réduction des erreurs de suivi"
        ],
        "processus": [
            {"etape": 1, "titre": "Réception et enregistrement en Chine"},
            {"etape": 2, "titre": "Préparation du colis"},
            {"etape": 3, "titre": "Expédition"},
            {"etape": 4, "titre": "Transit vers le Burkina Faso"},
            {"etape": 5, "titre": "Arrivée à l’entrepôt"},
            {"etape": 6, "titre": "Dédouanement et livraison"}
        ]
    }',
    'ctexi_cargo.png'
),
(
    'CTEXI Pay',
    'CTEXI Pay facilite les transferts d’argent entre le Burkina Faso et la Chine avec simulation de paiement et contact direct.',
    '{
        "description": "CTEXI Pay permet aux clients de connaître le taux de change du jour, de simuler le montant à payer en FCFA et de contacter directement le service via WhatsApp pour finaliser la transaction.",
        "fonctionnalites": [
            "Affichage du taux de change RMB ↔ FCFA",
            "Simulation du montant à payer",
            "Envoi automatique d’un message pré-rempli au service",
            "Historique des taux et gestion par l’admin"
        ],
        "avantages": [
            "Transferts sécurisés",
            "Calcul automatique du montant à payer",
            "Communication directe avec le service",
            "Taux mis à jour et fiables"
        ],
        "processus": [
            {"etape": 1, "titre": "Consultation du taux de change"},
            {"etape": 2, "titre": "Simulation du paiement"},
            {"etape": 3, "titre": "Validation et contact via WhatsApp"},
            {"etape": 4, "titre": "Confirmation et suivi de la transaction"}
        ]
    }',
    'ctexi_pay.png'
),
(
    'CTEXI Travel',
    'CTEXI Travel s’occupe de tout ce qui concerne les voyages en Chine : visas, billets d’avion et hôtels.',
    '{
        "description": "CTEXI Travel fournit toutes les informations nécessaires pour voyager en Chine et permet de contacter facilement un agent pour chaque service.",
        "fonctionnalites": [
            "Assistance pour l’obtention de visas",
            "Réservation de billets d’avion",
            "Réservation d’hôtels",
            "Contact direct avec un agent CTEXI"
        ],
        "avantages": [
            "Facilite toutes les démarches de voyage",
            "Informations claires et à jour",
            "Assistance personnalisée",
            "Gain de temps et sécurité"
        ],
        "processus": [
            {"etape": 1, "titre": "Visa"},
            {"etape": 2, "titre": "Billet d’avion"},
            {"etape": 3, "titre": "Réservation hôtel"},
            {"etape": 4, "titre": "Contact agent pour confirmation"}
        ]
    }',
    'ctexi_travel.png'
),
(
    'CTEXI Académie',
    'CTEXI Académie propose des formations et du coaching sur l’import-export, l’achat en ligne et le marketing digital.',
    '{
        "description": "CTEXI Académie offre aux clients et partenaires des formations complètes sur l’achat en Chine, l’import-export et le marketing digital, ainsi que du coaching personnalisé.",
        "fonctionnalites": [
            "Formations sur achats en ligne",
            "Formations sur marketing digital",
            "Coaching personnalisé",
            "Inscription et contact via WhatsApp, mail ou formulaire"
        ],
        "avantages": [
            "Amélioration des compétences professionnelles",
            "Accompagnement personnalisé",
            "Programmes adaptés au public cible",
            "Accès facile aux informations et inscriptions"
        ],
        "processus": [
            {"etape": 1, "titre": "Consultation des formations disponibles"},
            {"etape": 2, "titre": "Sélection du programme"},
            {"etape": 3, "titre": "Inscription ou demande d’informations"},
            {"etape": 4, "titre": "Suivi et coaching"}
        ]
    }',
    'ctexi_academie.png'
);



--table colis
CREATE TABLE core.colis(
    id_colis SERIAL PRIMARY KEY,
    code_colis VARCHAR(50) UNIQUE NOT NULL,
    id_user INTEGER REFERENCES auth.users(id_user) ON DELETE CASCADE,
    statut VARCHAR(100),
    type_colis VARCHAR(100),
    modes VARCHAR(100),
    derniere_maj TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



INSERT INTO core.colis (code_colis, id_user, statut, type_colis, modes) VALUES
('CTX10001', 1, 'En préparation', 'Electronique', 'Aérien'),
('CTX10002', 1, 'Expédié', 'Vêtements', 'Maritime'),
('CTX10003', 6, 'En transit', 'Accessoires', 'Aérien'),
('CTX10004', 7, 'Arrivé au centre de tri', 'Téléphone', 'Aérien'),
('CTX10005', 9, 'Livré', 'Chaussures', 'Maritime');




-------------------------------------SCHEMA SYSTEMS--------------------------------------------------------------


-- Pour chatbot.faq
UPDATE chatbot.faq SET embedding = NULL;

-- Pour chatbot.intention
UPDATE chatbot.intention SET embedding = NULL;



SET search_path TO chatbot, public;


SELECT extname FROM pg_extension;


SELECT * FROM auth.agents;


--Ajout d'embeding dans intention
SET search_path TO chatbot, public;


ALTER TABLE chatbot.intention 
ADD COLUMN embedding vector(384);



------------------------------------------Table Intention---------------------------------------------------------------


INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES (
'faq_buy',
'information',
'Service d’achat de produits en Chine incluant la recherche de fournisseurs, négociation, commande, paiement, contrôle qualité, importation et livraison internationale de marchandises.'
);


INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES (
'faq_travel',
'information',
'Service d’accompagnement pour voyager en Chine incluant visa, passeport, billet d’avion, réservation d’hôtel, procédures administratives et assistance de voyage.'
);


INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES (
'faq_academie',
'information',
'Formations professionnelles en import-export, commerce international, achat en Chine, marketing digital, entrepreneuriat, avec inscription, certification, durée et accompagnement pédagogique.'
);



INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES (
'faq_cargo',
'information',
'Service de transport et expédition de colis et marchandises entre la Chine et le Burkina Faso incluant expédition, envoi de colis, fret aérien et maritime, délais de livraison, suivi de colis, douane, prix de transport et gestion logistique.'
);


INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES (
'contact_agent',
'operation',
'Demande d’assistance humaine, contact avec un agent, support client direct ou transfert vers un conseiller.'
);



INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES (
'service_info',
'operation',
'Informations générales sur les services de l’entreprise, présentation des offres et explication des activités.'
);


INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES (
'taux_change',
'operation',
'Conversion de devises, calcul de prix en FCFA ou yuan, transfert d’argent, paiement international et assistance financière.'
);




SELECT * FROM chatbot.intention;




CREATE TABLE chatbot.intent_examples(
    id SERIAL PRIMARY KEY,
    id_intent INT REFERENCES chatbot.intention(id_intent) ON DELETE CASCADE,
    phrase TEXT,
    embedding vector(384)
);


CREATE TABLE chatbot.intent_responses(
    id SERIAL PRIMARY KEY,
    id_intent INT REFERENCES chatbot.intention(id_intent) ON DELETE CASCADE,
    reponse TEXT
);




SELECT * FROM chatbot.intention;

------------------------------------------------Table Faq--------------------------------------------------------------

DROP TABLE chatbot.faq CASCADE;

-- =======================
-- buy (id_intent = 5)
-- =======================


SELECT * FROM chatbot.faq;




INSERT INTO chatbot.intent_examples (id_intent, phrase) VALUES

(5, 'comment fonctionne votre service ctexi buy'),
(5, 'comment acheter un produit en chine'),
(5, 'je veux acheter en chine'),
(5, 'vous pouvez acheter pour moi'),
(5, 'comment passer une commande'),
(5, 'quelles sont les étapes d’achat'),
(5, 'comment payer une commande'),
(5, 'est ce fiable d’acheter avec vous'),
(5, 'comment se fait la livraison'),
(5, 'puis je annuler ma commande'),


(6, 'comment obtenir un visa pour la chine'),
(6, 'je veux voyager en chine'),
(6, 'quels documents pour visa chine'),
(6, 'delai visa chine'),
(6, 'reservation billet avion chine'),
(6, 'reservation hotel chine'),
(6, 'assistance aeroport chine'),
(6, 'modifier reservation voyage'),


(7, 'quelles formations proposez vous'),
(7, 'je veux me former chez vous'),
(7, 'comment sinscrire a une formation'),
(7, 'formation en ligne ou presentiel'),
(7, 'certificat formation'),
(7, 'accompagnement apres formation'),
(7, 'prix formation'),
(7, 'duree formation'),


(8, 'expedier colis chine burkina'),
(8, 'envoyer marchandise chine burkina'),
(8, 'transport chine burkina comment ca marche'),
(8, 'delai livraison chine burkina'),
(8, 'prix transport chine burkina'),
(8, 'produits interdits transport'),
(8, 'frais de douane colis'),
(8, 'colis en retard'),
(8, 'mon colis est en transit'),
(8, 'code colis invalide'),


(12, 'combien de temps prend un transfert'),
(12, 'convertir yuan en fcfa'),
(12, 'comment payer fournisseur chine'),
(12, 'faire une demande de paiement'),
(12, 'paiement securise'),
(12, 'preuve de paiement');

================================Response=============================

INSERT INTO chatbot.intent_responses (id_intent, reponse) VALUES


(5, 'CTEXI Buy est un service complet d’accompagnement à l’achat de produits en Chine. Nous vous aidons depuis la recherche du fournisseur jusqu’à la livraison finale au Burkina Faso. Concrètement, vous nous envoyez le produit ou l’idée du produit que vous souhaitez, nous analysons la demande, nous recherchons les meilleurs fournisseurs fiables en Chine, nous négocions le prix, nous effectuons l’achat, nous vérifions la qualité du produit avant expédition et nous organisons la livraison sécurisée. Le processus est transparent et vous êtes accompagné à chaque étape pour éviter les risques liés aux achats internationaux.'),


(6, 'CTEXI Travel vous accompagne dans toutes vos démarches de voyage vers la Chine. Nous vous aidons à obtenir votre visa en vous guidant sur les documents nécessaires, les délais et les procédures administratives. Nous pouvons également vous assister pour la réservation de vos billets d’avion, la réservation d’hôtel, ainsi que l’organisation de votre accueil à l’aéroport en Chine. Notre objectif est de simplifier votre voyage et de vous éviter les complications administratives afin que vous puissiez voyager sereinement.'),


(7, 'CTEXI Académie propose des formations pratiques et professionnelles dans plusieurs domaines comme l’import-export, l’achat de produits en Chine, le marketing digital et l’entrepreneuriat. Nos formations sont accessibles en ligne ou en présentiel selon votre disponibilité. Chaque formation est structurée avec des modules clairs, un accompagnement personnalisé et un suivi après formation pour vous aider à appliquer concrètement ce que vous apprenez. Un certificat est délivré à la fin de la formation selon le programme suivi.'),

(8, 'Nous assurons l’expédition de marchandises et colis depuis la Chine vers le Burkina Faso avec un service complet incluant le transport, le suivi et l’assistance. Nous proposons plusieurs options de livraison (avion ou bateau) selon votre budget et votre urgence. Les délais varient généralement entre 7 et 45 jours. Nous gérons également les aspects logistiques comme le suivi du colis, la gestion des retards éventuels et les formalités douanières. Notre objectif est de garantir un transport sécurisé et fiable pour vos marchandises.'),


(12, 'CTEXI Pay facilite vos paiements internationaux vers la Chine en assurant la conversion de devises, la sécurisation des transactions et l’accompagnement complet. Nous vous aidons à comprendre le montant exact à payer en FCFA ou en yuan, nous effectuons les transferts vers les fournisseurs et nous vous fournissons une preuve de paiement après chaque transaction. Notre service est conçu pour sécuriser vos achats et réduire les risques liés aux paiements internationaux.');


TRUNCATE TABLE chatbot.intent_responses RESTART IDENTITY;



TRUNCATE TABLE chatbot.intent_examples RESTART IDENTITY;


SELECT * FROM chatbot.intent_responses;