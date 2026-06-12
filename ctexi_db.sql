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







-- Sauvegarde des conversations
CREATE TABLE chatbot.conversations(
    id_conv SERIAL PRIMARY KEY,
    id_user INTEGER NOT NULL REFERENCES auth.users(id_user) ON DELETE CASCADE,
    id_intent INT REFERENCES chatbot.intention(id_intent) ON DELETE CASCADE,

    
    message_user TEXT NOT NULL,
    reponse_bot TEXT,


    type_intent VARCHAR(50),  -- 'information' | 'operation'
    action_handler VARCHAR(100), -- ex: conversion_handler, agent_handler

    confidence FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



TRUNCATE chatbot.conversations         RESTART IDENTITY;


SELECT * FROM chatbot.conversations;



DROP TABLE chatbot.conversations CASCADE;



--Table intention


SELECT * FROM chatbot.intention;

CREATE TABLE chatbot.intention (
    id_intent SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL,
    type_intent VARCHAR(50) NOT NULL,
    action_handler VARCHAR(100), 
    descriptions TEXT,
    dates TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



DROP TABLE chatbot.intention CASCADE;

SELECT * FROM chatbot.intention;


--Table services
CREATE TABLE core.service(
    id_service SERIAL PRIMARY KEY,
    nom_service VARCHAR (255),
    descriptions TEXT,
    menu JSONB,
    icone VARCHAR(255)

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




-- Table pour les intention users(question users)
CREATE TABLE chatbot.intent_examples(
    id SERIAL PRIMARY KEY,
    id_intent INT REFERENCES chatbot.intention(id_intent)ON DELETE CASCADE,
    sous_intent VARCHAR(100),
    phrase TEXT,
    mots_cles TEXT[],
    embedding vector(384)
);




-- Table pour les reponses possible (reponse_bot)
CREATE TABLE chatbot.intent_responses(
    id SERIAL PRIMARY KEY,
    id_intent INT REFERENCES chatbot.intention(id_intent)ON DELETE CASCADE,
    sous_intent VARCHAR(100),
    reponse TEXT,
    type_reponse VARCHAR(50) DEFAULT 'text',
    priorite INT DEFAULT 1
);


SELECT * FROM chatbot.intent_responses


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

------------------------------Insertion dans les tables operations--------------------------------------






-------------------------------------SCHEMA CORE--------------------------------------------------------------


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


INSERT INTO core.colis (code_colis, id_user, statut, type_colis, modes) VALUES
('CTX10001', 1, 'En préparation', 'Electronique', 'Aérien'),
('CTX10002', 1, 'Expédié', 'Vêtements', 'Maritime'),
('CTX10003', 6, 'En transit', 'Accessoires', 'Aérien'),
('CTX10004', 7, 'Arrivé au centre de tri', 'Téléphone', 'Aérien'),
('CTX10005', 9, 'Livré', 'Chaussures', 'Maritime');




-------------------------------------SCHEMA SYSTEMS--------------------------------------------------------------


------------------------------------------Table Intention---------------------------------------------------------------

-- ==========================================================
-- FAQ (INFORMATIONS - PAS D'ACTION DIRECTE)
-- ==========================================================

INSERT INTO chatbot.intention (nom, type_intent, descriptions, action_handler)
VALUES
(
'faq_buy',
'information',
'Service d’achat de produits en Chine incluant la recherche de fournisseurs, négociation, commande, paiement, contrôle qualité, importation et livraison internationale de marchandises.',
NULL
);

INSERT INTO chatbot.intention (nom, type_intent, descriptions, action_handler)
VALUES
(
'faq_travel',
'information',
'Service d’accompagnement pour voyager en Chine incluant visa, passeport, billet d’avion, réservation d’hôtel, procédures administratives et assistance de voyage.',
NULL
);

INSERT INTO chatbot.intention (nom, type_intent, descriptions, action_handler)
VALUES
(
'faq_academie',
'information',
'Formations professionnelles en import-export, commerce international, achat en Chine, marketing digital, entrepreneuriat, avec inscription, certification, durée et accompagnement pédagogique.',
NULL
);

INSERT INTO chatbot.intention (nom, type_intent, descriptions, action_handler)
VALUES
(
'faq_cargo',
'information',
'Service de transport et expédition de colis et marchandises entre la Chine et le Burkina Faso incluant expédition, envoi de colis, fret aérien et maritime, délais de livraison, suivi de colis, douane, prix de transport et gestion logistique.',
NULL
);


-- ==========================================================
-- OPERATIONS (EXECUTABLES)
-- ==========================================================

INSERT INTO chatbot.intention (nom, type_intent, descriptions, action_handler)
VALUES
(
'contact_agent',
'operation',
'Demande d’assistance humaine, contact avec un agent, support client direct ou transfert vers un conseiller.',
'agent_handler'
);

INSERT INTO chatbot.intention (nom, type_intent, descriptions, action_handler)
VALUES
(
'service_info',
'operation',
'Informations générales sur les services de l’entreprise, présentation des offres et explication des activités.',
'service_handler'
);


INSERT INTO chatbot.intention (nom, type_intent, descriptions, action_handler)
VALUES
(
'suivi_colis',
'operation',
'Service de suivi de colis ou commande',
'suivi_handler'
);





INSERT INTO chatbot.intention (nom, type_intent, descriptions, action_handler)
VALUES
(
'taux_change',
'operation',
'Conversion de devises, calcul de prix en FCFA ou yuan, transfert d’argent, paiement international et assistance financière.',
'conversion_handler'
);



TRUNCATE TABLE chatbot.intent_responses RESTART IDENTITY;

SELECT * FROM chatbot.intent_responses;

-- ==========================================================
-- INTENT EXAMPLES
-- ==========================================================






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




TRUNCATE TABLE chatbot.intent_responses RESTART IDENTITY;

DROP TABLE chatbot.intent_examples CASCADE;

DROP TABLE chatbot.intent_responses CASCADE;

TRUNCATE TABLE chatbot.intent_examples RESTART IDENTITY;


SELECT * FROM chatbot.intent_responses;



SELECT * FROM chatbot.intention;









SELECT * FROM chatbot.intention;

------------------------------------------------Table Faq--------------------------------------------------------------

DROP TABLE chatbot.faq CASCADE;

-- =======================
-- buy (id_intent = 5)
-- =======================


SELECT * FROM chatbot.faq;




========================Question=================================


-- ===========================================================
-- CTEXI CHATBOT — SEED DATA COMPLET
-- Tables: intention, intent_examples, intent_responses
-- ===========================================================

-- ===========================================================
-- 0. NETTOYAGE (optionnel — commenter si déjà en prod)
-- ===========================================================
TRUNCATE chatbot.intent_responses  RESTART IDENTITY CASCADE;
TRUNCATE chatbot.intent_examples   RESTART IDENTITY CASCADE;
TRUNCATE chatbot.intention         RESTART IDENTITY CASCADE;



SELECT * FROM chatbot.intent_responses;

-- ===========================================================
-- 1. INTENTIONS
-- ===========================================================
INSERT INTO chatbot.intention (id_intent, nom, type_intent, action_handler, descriptions) VALUES
(1,  'faq_buy',        'information', NULL,                'Questions sur le service CTEXI BUY (achat, sourcing, fournisseurs Chine)'),
(2,  'faq_travel',     'information', NULL,                'Questions sur le service CTEXI TRAVEL (visa, billets, hôtels Chine)'),
(3,  'faq_academie',   'information', NULL,                'Questions sur CTEXI ACADÉMIE (formations import-export, e-commerce)'),
(4,  'faq_cargo',      'information', NULL,                'Questions sur CTEXI CARGO (transport marchandises Chine → Afrique)'),
(5,  'contact_agent',  'operation',   'agent_handler',     'Mise en relation avec un agent CTEXI'),
(6,  'service_info',   'operation',   'service_handler',   'Affichage des services CTEXI sous forme de boutons'),
(7,  'suivi_colis',    'operation',   'suivi_handler',     'Suivi de colis/commande via code de suivi'),
(8,  'taux_change',    'operation',   'conversion_handler','Conversion de devises (FCFA, USD, EUR, RMB)'),
(9,  'faq_general',    'information', NULL,                'Questions générales sur CTEXI (présentation, localisation, contact...)'),
(10, 'salutation',     'information', NULL,                'Salutations et messages d''accueil'),
(11, 'remerciement',   'information', NULL,                'Remerciements et messages de fin de conversation');



-- -----------------------------------------------------------
-- SALUTATION (10)
-- -----------------------------------------------------------
INSERT INTO chatbot.intent_examples (id_intent, sous_intent, phrase, mots_cles) VALUES
(10, 'salutation_generale', 'Bonjour', ARRAY['bonjour']),
(10, 'salutation_generale', 'Salut', ARRAY['salut']),
(10, 'salutation_generale', 'Bonsoir', ARRAY['bonsoir']),
(10, 'salutation_generale', 'Hello', ARRAY['hello']),
(10, 'salutation_generale', 'Hi', ARRAY['hi']),
(10, 'salutation_generale', 'Hey', ARRAY['hey']),
(10, 'salutation_generale', 'Bonjour, je voudrais des informations', ARRAY['bonjour','information']),
(10, 'salutation_generale', 'Salut, comment ça marche ici ?', ARRAY['salut','marche']),
(10, 'salutation_generale', 'Bonsoir, je suis nouveau client', ARRAY['bonsoir','nouveau','client']),
(10, 'salutation_generale', 'Bonjour CTEXI', ARRAY['bonjour','ctexi']),
(10, 'salutation_generale', 'Good morning', ARRAY['good','morning']),
(10, 'salutation_generale', 'Good evening', ARRAY['good','evening']),
(10, 'salutation_generale', 'Coucou', ARRAY['coucou']),
(10, 'salutation_generale', 'Bjr', ARRAY['bjr']),
(10, 'salutation_generale', 'Slt', ARRAY['slt']);

-- -----------------------------------------------------------
-- REMERCIEMENT (11)
-- -----------------------------------------------------------
INSERT INTO chatbot.intent_examples (id_intent, sous_intent, phrase, mots_cles) VALUES
(11, 'remerciement_general', 'Merci', ARRAY['merci']),
(11, 'remerciement_general', 'Merci beaucoup', ARRAY['merci','beaucoup']),
(11, 'remerciement_general', 'Thanks', ARRAY['thanks']),
(11, 'remerciement_general', 'Thank you', ARRAY['thank','you']),
(11, 'remerciement_general', 'Super merci', ARRAY['super','merci']),
(11, 'remerciement_general', 'Ok merci', ARRAY['ok','merci']),
(11, 'remerciement_general', 'Parfait merci', ARRAY['parfait','merci']),
(11, 'remerciement_general', 'C est bon merci', ARRAY['bon','merci']),
(11, 'remerciement_general', 'Au revoir', ARRAY['au revoir']),
(11, 'remerciement_general', 'Bonne journée', ARRAY['bonne','journée']),
(11, 'remerciement_general', 'Bye', ARRAY['bye']),
(11, 'remerciement_general', 'A bientôt', ARRAY['bientôt']),
(11, 'remerciement_general', 'Nickel merci', ARRAY['nickel','merci']),
(11, 'remerciement_general', 'Très bien merci', ARRAY['très','bien','merci']);

-- -----------------------------------------------------------
-- FAQ GÉNÉRAL CTEXI (9)
-- -----------------------------------------------------------
INSERT INTO chatbot.intent_examples (id_intent, sous_intent, phrase, mots_cles) VALUES
-- présentation
(9, 'presentation', 'C est quoi CTEXI ?', ARRAY['ctexi','quoi']),
(9, 'presentation', 'Parlez-moi de votre entreprise', ARRAY['entreprise','parler']),
(9, 'presentation', 'Que fait CTEXI ?', ARRAY['ctexi','fait']),
(9, 'presentation', 'Qui êtes-vous ?', ARRAY['qui','vous']),
(9, 'presentation', 'CTEXI c est quoi exactement ?', ARRAY['ctexi','exactement']),
(9, 'presentation', 'Présentez-moi CTEXI', ARRAY['présenter','ctexi']),
(9, 'presentation', 'Qu est-ce que CTEXI ?', ARRAY['qu','est','ctexi']),
(9, 'presentation', 'Tell me about CTEXI', ARRAY['tell','about','ctexi']),
(9, 'presentation', 'What is CTEXI ?', ARRAY['what','is','ctexi']),
(9, 'presentation', 'CTEXI est une entreprise de quoi ?', ARRAY['ctexi','entreprise']),
 (9, 'localisation', 'Où êtes-vous situés ?', ARRAY['où','situé']),
(9, 'localisation', 'Vous êtes basés où ?', ARRAY['basé','où']),
(9, 'localisation', 'Quelle est votre adresse ?', ARRAY['adresse']),
(9, 'localisation', 'Vous opérez dans quels pays ?', ARRAY['pays','opérez']),
(9, 'localisation', 'Est-ce que vous êtes au Burkina Faso ?', ARRAY['burkina','faso']),
(9, 'localisation', 'Vous êtes en Chine ou en Afrique ?', ARRAY['chine','afrique']),
(9, 'localisation', 'CTEXI est basé à Ouagadougou ?', ARRAY['ouagadougou','ctexi']),
-- contact
(9, 'contact_info', 'Comment vous contacter ?', ARRAY['contacter']),
(9, 'contact_info', 'Quel est votre numéro de téléphone ?', ARRAY['téléphone','numéro']),
(9, 'contact_info', 'Vous avez un WhatsApp ?', ARRAY['whatsapp']),
(9, 'contact_info', 'Quel est votre email ?', ARRAY['email']),
(9, 'contact_info', 'Comment joindre CTEXI ?', ARRAY['joindre','ctexi']),
(9, 'contact_info', 'Votre numéro svp', ARRAY['numéro','svp']),
-- horaires
(9, 'horaires', 'Quels sont vos horaires ?', ARRAY['horaires']),
(9, 'horaires', 'Vous êtes ouverts le weekend ?', ARRAY['ouverts','weekend']),
(9, 'horaires', 'A quelle heure vous ouvrez ?', ARRAY['heure','ouvrez']),
(9, 'horaires', 'Vous travaillez le dimanche ?', ARRAY['dimanche','travaillez']),
(9, 'horaires', 'Vos heures d ouverture svp', ARRAY['heures','ouverture']),
-- confiance
(9, 'confiance', 'CTEXI est fiable ?', ARRAY['fiable','ctexi']),
(9, 'confiance', 'Est-ce que je peux vous faire confiance ?', ARRAY['confiance']),
(9, 'confiance', 'Vous êtes sérieux ?', ARRAY['sérieux']),
(9, 'confiance', 'CTEXI est légal ?', ARRAY['légal','ctexi']),
(9, 'confiance', 'Comment savoir que c est pas une arnaque ?', ARRAY['arnaque']),
(9, 'confiance', 'Vous avez des références clients ?', ARRAY['références','clients']),
(9, 'confiance', 'Combien d années d expérience avez-vous ?', ARRAY['années','expérience']),
(9, 'confiance', 'Est-ce que CTEXI est enregistré légalement ?', ARRAY['enregistré','légalement']),
-- paiement
(9, 'paiement_general', 'Quels modes de paiement acceptez-vous ?', ARRAY['paiement','modes']),
(9, 'paiement_general', 'Je peux payer en FCFA ?', ARRAY['fcfa','payer']),
(9, 'paiement_general', 'Vous acceptez le mobile money ?', ARRAY['mobile','money']),
(9, 'paiement_general', 'Paiement en ligne possible ?', ARRAY['paiement','ligne']),
(9, 'paiement_general', 'Vous prenez Orange Money ?', ARRAY['orange','money']),
(9, 'paiement_general', 'Comment payer mes commandes ?', ARRAY['payer','commandes']);

-- -----------------------------------------------------------
-- CONTACT AGENT (5) — exemples uniquement, réponse dynamique
-- -----------------------------------------------------------
INSERT INTO chatbot.intent_examples (id_intent, sous_intent, phrase, mots_cles) VALUES
(5, 'contact_agent', 'Je veux parler à un agent', ARRAY['parler','agent']),
(5, 'contact_agent', 'Mettre en relation avec un conseiller', ARRAY['relation','conseiller']),
(5, 'contact_agent', 'Je veux contacter un humain', ARRAY['contacter','humain']),
(5, 'contact_agent', 'Parler à quelqu un', ARRAY['parler','quelquun']),
(5, 'contact_agent', 'J ai besoin d un agent', ARRAY['besoin','agent']),
(5, 'contact_agent', 'Mettre moi en contact avec un agent', ARRAY['contact','agent']),
(5, 'contact_agent', 'Je veux discuter avec un conseiller', ARRAY['discuter','conseiller']),
(5, 'contact_agent', 'Un agent svp', ARRAY['agent','svp']),
(5, 'contact_agent', 'Pouvez-vous me passer un agent ?', ARRAY['passer','agent']),
(5, 'contact_agent', 'Je voudrais parler à une personne réelle', ARRAY['personne','réelle']),
(5, 'contact_agent', 'Contact a human agent', ARRAY['contact','human','agent']),
(5, 'contact_agent', 'I want to speak to someone', ARRAY['speak','someone']),
(5, 'contact_agent', 'Besoin d aide d un agent', ARRAY['aide','agent']),
(5, 'contact_agent', 'Votre numéro WhatsApp ?', ARRAY['numéro','whatsapp']),
(5, 'contact_agent', 'Comment joindre un responsable ?', ARRAY['joindre','responsable']);

-- -----------------------------------------------------------
-- SERVICE INFO (6) — exemples uniquement, réponse dynamique
-- -----------------------------------------------------------
INSERT INTO chatbot.intent_examples (id_intent, sous_intent, phrase, mots_cles) VALUES
(6, 'service_info', 'Quels sont vos services ?', ARRAY['services']),
(6, 'service_info', 'Qu est-ce que vous proposez ?', ARRAY['proposez']),
(6, 'service_info', 'Liste de vos services', ARRAY['liste','services']),
(6, 'service_info', 'Vous faites quoi exactement ?', ARRAY['faites','exactement']),
(6, 'service_info', 'Vos offres disponibles', ARRAY['offres','disponibles']),
(6, 'service_info', 'Quels services offrez-vous ?', ARRAY['services','offrez']),
(6, 'service_info', 'Qu avez-vous comme services ?', ARRAY['avez','services']),
(6, 'service_info', 'What services do you offer ?', ARRAY['services','offer']),
(6, 'service_info', 'Dites-moi ce que vous faites', ARRAY['dites','faites']),
(6, 'service_info', 'Montrez-moi vos services', ARRAY['montrez','services']),
(6, 'service_info', 'Vos domaines d activité', ARRAY['domaines','activité']),
(6, 'service_info', 'C est quoi vos activités ?', ARRAY['activités']),
(6, 'service_info', 'Qu est-ce que CTEXI propose ?', ARRAY['ctexi','propose']);

-- -----------------------------------------------------------
-- SUIVI COLIS (7) — exemples uniquement, réponse dynamique
-- -----------------------------------------------------------
INSERT INTO chatbot.intent_examples (id_intent, sous_intent, phrase, mots_cles) VALUES
(7, 'suivi_colis', 'Je veux suivre mon colis', ARRAY['suivre','colis']),
(7, 'suivi_colis', 'Où est ma commande ?', ARRAY['où','commande']),
(7, 'suivi_colis', 'Suivi de mon colis', ARRAY['suivi','colis']),
(7, 'suivi_colis', 'Mon colis est où ?', ARRAY['colis','où']),
(7, 'suivi_colis', 'Tracking de ma commande', ARRAY['tracking','commande']),
(7, 'suivi_colis', 'Où en est ma livraison ?', ARRAY['livraison','où']),
(7, 'suivi_colis', 'Je veux savoir où est mon colis', ARRAY['savoir','colis']),
(7, 'suivi_colis', 'CTX10023', ARRAY['code','colis']),
(7, 'suivi_colis', 'Mon code de suivi est CTX10045', ARRAY['code','suivi']),
(7, 'suivi_colis', 'Suivre ma marchandise', ARRAY['suivre','marchandise']),
(7, 'suivi_colis', 'Statut de ma commande', ARRAY['statut','commande']),
(7, 'suivi_colis', 'Track my parcel', ARRAY['track','parcel']),
(7, 'suivi_colis', 'Where is my package ?', ARRAY['where','package']),
(7, 'suivi_colis', 'Ma livraison est arrivée ?', ARRAY['livraison','arrivée']),
(7, 'suivi_colis', 'Est-ce que mon colis est parti de Chine ?', ARRAY['colis','parti','chine']);

-- -----------------------------------------------------------
-- TAUX DE CHANGE (8) — exemples uniquement, réponse dynamique
-- -----------------------------------------------------------
INSERT INTO chatbot.intent_examples (id_intent, sous_intent, phrase, mots_cles) VALUES
(8, 'conversion', 'Convertir 100 USD en FCFA', ARRAY['convertir','usd','fcfa']),
(8, 'conversion', 'Taux de change EUR FCFA', ARRAY['taux','change','eur','fcfa']),
(8, 'conversion', 'Combien vaut 1 dollar en francs ?', ARRAY['dollar','francs']),
(8, 'conversion', 'Conversion de devises', ARRAY['conversion','devises']),
(8, 'conversion', 'Convertir yuan en FCFA', ARRAY['yuan','fcfa']),
(8, 'conversion', '500 euros en francs CFA', ARRAY['euros','francs','cfa']),
(8, 'conversion', 'Quel est le taux du dollar ?', ARRAY['taux','dollar']),
(8, 'conversion', 'RMB en FCFA', ARRAY['rmb','fcfa']),
(8, 'conversion', 'Je veux convertir de l argent', ARRAY['convertir','argent']),
(8, 'conversion', '1000 CNY en XOF', ARRAY['cny','xof']),
(8, 'conversion', 'Taux euro aujourd hui', ARRAY['taux','euro']),
(8, 'conversion', 'Currency exchange rate', ARRAY['currency','exchange','rate']),
(8, 'conversion', 'How much is 100 USD in FCFA ?', ARRAY['usd','fcfa']),
(8, 'conversion', 'Taux de change RMB', ARRAY['taux','rmb']),
(8, 'conversion', 'Combien fait 200 dollars en FCFA ?', ARRAY['dollars','fcfa']);

-- -----------------------------------------------------------
-- FAQ CARGO (4)
-- -----------------------------------------------------------
INSERT INTO chatbot.intent_examples (id_intent, sous_intent, phrase, mots_cles) VALUES
-- general
(4, 'cargo_general', 'C est quoi CTEXI Cargo ?', ARRAY['ctexi','cargo']),
(4, 'cargo_general', 'Comment fonctionne le transport ?', ARRAY['transport','fonctionne']),
(4, 'cargo_general', 'Vous faites le transport de marchandises ?', ARRAY['transport','marchandises']),
(4, 'cargo_general', 'Comment expédier mes marchandises depuis la Chine ?', ARRAY['expédier','chine']),
(4, 'cargo_general', 'Je veux envoyer des marchandises de Chine au Burkina', ARRAY['envoyer','chine','burkina']),
(4, 'cargo_general', 'Transport de produits depuis la Chine', ARRAY['transport','produits','chine']),
(4, 'cargo_general', 'Livraison Chine Afrique', ARRAY['livraison','chine','afrique']),
-- delais
(4, 'cargo_delais', 'Quel est le délai de livraison ?', ARRAY['délai','livraison']),
(4, 'cargo_delais', 'Combien de temps pour recevoir ma commande ?', ARRAY['temps','commande']),
(4, 'cargo_delais', 'La livraison prend combien de jours ?', ARRAY['livraison','jours']),
(4, 'cargo_delais', 'Délai moyen Chine Burkina ?', ARRAY['délai','chine','burkina']),
(4, 'cargo_delais', 'C est long pour recevoir ?', ARRAY['long','recevoir']),
-- tarifs
(4, 'cargo_tarif', 'Quel est le prix du transport ?', ARRAY['prix','transport']),
(4, 'cargo_tarif', 'Combien coûte l expédition ?', ARRAY['coûte','expédition']),
(4, 'cargo_tarif', 'Tarif par kilo ?', ARRAY['tarif','kilo']),
(4, 'cargo_tarif', 'C est combien pour envoyer 50kg ?', ARRAY['kg','envoyer']),
(4, 'cargo_tarif', 'Le fret c est à quel prix ?', ARRAY['fret','prix']),
(4, 'cargo_tarif', 'Vos frais de port ?', ARRAY['frais','port']),
-- processus
(4, 'cargo_processus', 'Comment ça marche pour envoyer un colis ?', ARRAY['marche','colis']),
(4, 'cargo_processus', 'Quelles sont les étapes pour expédier ?', ARRAY['étapes','expédier']),
(4, 'cargo_processus', 'Comment commander avec vous ?', ARRAY['commander']),
(4, 'cargo_processus', 'Processus de commande CTEXI', ARRAY['processus','commande']),
(4, 'cargo_processus', 'Comment démarrer avec CTEXI Cargo ?', ARRAY['démarrer','cargo']),
-- produits
(4, 'cargo_produits', 'Quels types de produits transportez-vous ?', ARRAY['types','produits']),
(4, 'cargo_produits', 'Vous transportez des électroniques ?', ARRAY['électroniques']),
(4, 'cargo_produits', 'Les vêtements peuvent être transportés ?', ARRAY['vêtements']),
(4, 'cargo_produits', 'Y a des produits interdits ?', ARRAY['interdits','produits']),
(4, 'cargo_produits', 'Vous faites les gros volumes ?', ARRAY['gros','volumes']),
-- assurance
(4, 'cargo_assurance', 'Mes marchandises sont assurées ?', ARRAY['assurées','marchandises']),
(4, 'cargo_assurance', 'Que se passe-t-il si le colis est perdu ?', ARRAY['perdu','colis']),
(4, 'cargo_assurance', 'Et si mes produits sont endommagés ?', ARRAY['endommagés','produits']),
(4, 'cargo_assurance', 'Vous garantissez la livraison ?', ARRAY['garantissez','livraison']);

-- -----------------------------------------------------------
-- FAQ BUY (1)
-- -----------------------------------------------------------
INSERT INTO chatbot.intent_examples (id_intent, sous_intent, phrase, mots_cles) VALUES
-- general
(1, 'buy_general', 'C est quoi CTEXI Buy ?', ARRAY['ctexi','buy']),
(1, 'buy_general', 'Vous faites le sourcing ?', ARRAY['sourcing']),
(1, 'buy_general', 'Je veux acheter des produits en Chine', ARRAY['acheter','produits','chine']),
(1, 'buy_general', 'Comment vous aider à acheter ?', ARRAY['aider','acheter']),
(1, 'buy_general', 'Vous achetez à ma place en Chine ?', ARRAY['achetez','place','chine']),
(1, 'buy_general', 'Assistance achat Chine', ARRAY['assistance','achat','chine']),
(1, 'buy_general', 'Agent d achat en Chine', ARRAY['agent','achat','chine']),
-- fournisseurs
(1, 'buy_fournisseurs', 'Vous trouvez des fournisseurs ?', ARRAY['fournisseurs','trouvez']),
(1, 'buy_fournisseurs', 'Comment trouver un bon fournisseur chinois ?', ARRAY['fournisseur','chinois']),
(1, 'buy_fournisseurs', 'Vous vérifiez les fournisseurs ?', ARRAY['vérifiez','fournisseurs']),
(1, 'buy_fournisseurs', 'Fournisseur fiable en Chine', ARRAY['fiable','fournisseur','chine']),
(1, 'buy_fournisseurs', 'Vous négociez avec les fournisseurs ?', ARRAY['négociez','fournisseurs']),
(1, 'buy_fournisseurs', 'Comment vérifier la qualité des produits ?', ARRAY['qualité','produits']),
-- controle qualite
(1, 'buy_qualite', 'Vous contrôlez la qualité ?', ARRAY['contrôlez','qualité']),
(1, 'buy_qualite', 'Inspection des produits avant expédition', ARRAY['inspection','produits']),
(1, 'buy_qualite', 'Comment vous assurez la qualité ?', ARRAY['assurez','qualité']),
(1, 'buy_qualite', 'Les produits sont vérifiés avant envoi ?', ARRAY['vérifiés','envoi']),
-- tarifs
(1, 'buy_tarif', 'Combien coûtent vos services d achat ?', ARRAY['coûtent','services','achat']),
(1, 'buy_tarif', 'Quel est votre commission ?', ARRAY['commission']),
(1, 'buy_tarif', 'Vous prenez combien sur les achats ?', ARRAY['combien','achats']),
(1, 'buy_tarif', 'Frais d agent d achat ?', ARRAY['frais','agent','achat']),
-- plateformes
(1, 'buy_plateformes', 'Vous travaillez avec Alibaba ?', ARRAY['alibaba']),
(1, 'buy_plateformes', '1688 vous connaissez ?', ARRAY['1688']),
(1, 'buy_plateformes', 'Taobao c est possible ?', ARRAY['taobao']),
(1, 'buy_plateformes', 'Vous achetez sur Pinduoduo ?', ARRAY['pinduoduo']),
(1, 'buy_plateformes', 'AliExpress c est possible avec vous ?', ARRAY['aliexpress']),
(1, 'buy_plateformes', 'Quelles plateformes chinoises utilisez-vous ?', ARRAY['plateformes','chinoises']);

-- -----------------------------------------------------------
-- FAQ TRAVEL (2)
-- -----------------------------------------------------------
INSERT INTO chatbot.intent_examples (id_intent, sous_intent, phrase, mots_cles) VALUES
-- general
(2, 'travel_general', 'C est quoi CTEXI Travel ?', ARRAY['ctexi','travel']),
(2, 'travel_general', 'Vous aidez pour les voyages en Chine ?', ARRAY['voyages','chine']),
(2, 'travel_general', 'Je veux aller en Chine, vous pouvez aider ?', ARRAY['aller','chine','aider']),
(2, 'travel_general', 'Services de voyage CTEXI', ARRAY['voyage','ctexi']),
-- visa
(2, 'travel_visa', 'Comment obtenir un visa pour la Chine ?', ARRAY['visa','chine']),
(2, 'travel_visa', 'Vous aidez pour le visa chinois ?', ARRAY['aidez','visa','chinois']),
(2, 'travel_visa', 'Délai pour obtenir un visa Chine ?', ARRAY['délai','visa','chine']),
(2, 'travel_visa', 'Documents nécessaires pour le visa Chine ?', ARRAY['documents','visa','chine']),
(2, 'travel_visa', 'Prix du visa pour la Chine ?', ARRAY['prix','visa','chine']),
(2, 'travel_visa', 'Visa chinois c est compliqué ?', ARRAY['visa','chinois','compliqué']),
(2, 'travel_visa', 'Vous faites les démarches visa à ma place ?', ARRAY['démarches','visa']),
(2, 'travel_visa', 'J ai besoin d un visa d affaires pour la Chine', ARRAY['visa','affaires','chine']),
-- billet avion
(2, 'travel_billet', 'Vous réservez les billets d avion ?', ARRAY['billets','avion']),
(2, 'travel_billet', 'Billet Ouagadougou Chine ?', ARRAY['billet','ouagadougou','chine']),
(2, 'travel_billet', 'Prix d un billet pour la Chine ?', ARRAY['prix','billet','chine']),
(2, 'travel_billet', 'Comment réserver un vol pour la Chine ?', ARRAY['réserver','vol','chine']),
(2, 'travel_billet', 'Vous avez des tarifs pour les vols ?', ARRAY['tarifs','vols']),
-- hotel
(2, 'travel_hotel', 'Vous réservez les hôtels en Chine ?', ARRAY['hôtels','chine']),
(2, 'travel_hotel', 'Hébergement à Guangzhou ?', ARRAY['hébergement','guangzhou']),
(2, 'travel_hotel', 'Hôtel à Shanghai disponible ?', ARRAY['hôtel','shanghai']),
(2, 'travel_hotel', 'Trouver un bon hôtel à Yiwu ?', ARRAY['hôtel','yiwu']),
(2, 'travel_hotel', 'Vous aidez pour l hébergement en Chine ?', ARRAY['hébergement','chine']),
-- accompagnement
(2, 'travel_accompagnement', 'Vous accompagnez pendant le voyage ?', ARRAY['accompagnez','voyage']),
(2, 'travel_accompagnement', 'Guide en Chine disponible ?', ARRAY['guide','chine']),
(2, 'travel_accompagnement', 'Interprète chinois pour les affaires ?', ARRAY['interprète','chinois']),
(2, 'travel_accompagnement', 'Assistance en Chine pendant mon séjour ?', ARRAY['assistance','chine','séjour']);

-- -----------------------------------------------------------
-- FAQ ACADEMIE (3)
-- -----------------------------------------------------------
INSERT INTO chatbot.intent_examples (id_intent, sous_intent, phrase, mots_cles) VALUES
-- general
(3, 'academie_general', 'C est quoi CTEXI Académie ?', ARRAY['ctexi','académie']),
(3, 'academie_general', 'Vous faites des formations ?', ARRAY['formations']),
(3, 'academie_general', 'Je veux me former à l import-export', ARRAY['former','import','export']),
(3, 'academie_general', 'Formation commerce international', ARRAY['formation','commerce','international']),
(3, 'academie_general', 'Vous proposez des cours ?', ARRAY['cours']),
(3, 'academie_general', 'CTEXI Académie c est pour qui ?', ARRAY['académie','pour','qui']),
-- contenu formations
(3, 'academie_contenu', 'Qu est-ce qu on apprend dans vos formations ?', ARRAY['apprend','formations']),
(3, 'academie_contenu', 'Formation Alibaba disponible ?', ARRAY['formation','alibaba']),
(3, 'academie_contenu', 'Vous enseignez le sourcing ?', ARRAY['enseignez','sourcing']),
(3, 'academie_contenu', 'Formation e-commerce ?', ARRAY['formation','ecommerce']),
(3, 'academie_contenu', 'Comment apprendre à acheter en Chine ?', ARRAY['apprendre','acheter','chine']),
(3, 'academie_contenu', 'Formation import depuis la Chine ?', ARRAY['formation','import','chine']),
(3, 'academie_contenu', 'Vous apprenez la négociation avec fournisseurs ?', ARRAY['négociation','fournisseurs']),
-- modalites
(3, 'academie_modalites', 'Les formations sont en ligne ou présentiel ?', ARRAY['ligne','présentiel']),
(3, 'academie_modalites', 'Durée de vos formations ?', ARRAY['durée','formations']),
(3, 'academie_modalites', 'Formation disponible à distance ?', ARRAY['distance','formation']),
(3, 'academie_modalites', 'Vous avez des formations en groupe ?', ARRAY['groupe','formations']),
(3, 'academie_modalites', 'Formation individuelle possible ?', ARRAY['individuelle','formation']),
-- tarifs
(3, 'academie_tarif', 'Combien coûte la formation ?', ARRAY['coûte','formation']),
(3, 'academie_tarif', 'Prix de vos formations ?', ARRAY['prix','formations']),
(3, 'academie_tarif', 'La formation est payante ?', ARRAY['payante','formation']),
(3, 'academie_tarif', 'Vous avez des formations gratuites ?', ARRAY['gratuites','formations']),
-- certification
(3, 'academie_certification', 'On reçoit un certificat après la formation ?', ARRAY['certificat','formation']),
(3, 'academie_certification', 'La formation est certifiante ?', ARRAY['certifiante','formation']),
(3, 'academie_certification', 'Vous délivrez des diplômes ?', ARRAY['diplômes']);

-- ===========================================================
-- 3. INTENT RESPONSES
-- (uniquement pour les intents de type information)
-- ===========================================================

-- -----------------------------------------------------------
-- SALUTATION (10)
-- -----------------------------------------------------------
INSERT INTO chatbot.intent_responses (id_intent, sous_intent, reponse, type_reponse, priorite) VALUES
(10, 'salutation_generale', 'Bonjour ! 👋 Bienvenue chez CTEXI. Je suis votre assistant virtuel, comment puis-je vous aider aujourd hui ?', 'text', 1),
(10, 'salutation_generale', 'Bonjour et bienvenue ! 😊 Je suis CTEXI-BOT, prêt à répondre à toutes vos questions. Que puis-je faire pour vous ?', 'text', 1),
(10, 'salutation_generale', 'Salut ! 👋 Vous êtes chez CTEXI, votre partenaire import-export Chine-Afrique. Comment puis-je vous aider ?', 'text', 1),
(10, 'salutation_generale', 'Hello ! 😊 Bienvenue chez CTEXI. Je suis là pour vous accompagner, n hésitez pas à me poser vos questions !', 'text', 1),
(10, 'salutation_generale', 'Bonsoir ! 🌙 Bienvenue chez CTEXI. Comment puis-je vous aider ce soir ?', 'text', 1);

-- -----------------------------------------------------------
-- REMERCIEMENT (11)
-- -----------------------------------------------------------
INSERT INTO chatbot.intent_responses (id_intent, sous_intent, reponse, type_reponse, priorite) VALUES
(11, 'remerciement_general', 'Avec plaisir ! 😊 N hésitez pas si vous avez d autres questions.', 'text', 1),
(11, 'remerciement_general', 'De rien ! 🙏 Je suis là si vous avez besoin d autre chose.', 'text', 1),
(11, 'remerciement_general', 'C est un plaisir de vous aider ! 😊 Bonne continuation chez CTEXI.', 'text', 1),
(11, 'remerciement_general', 'Merci à vous de nous faire confiance ! 🙏 À bientôt.', 'text', 1),
(11, 'remerciement_general', 'Tout le plaisir est pour nous ! N hésitez pas à revenir. 😊', 'text', 1);

-- -----------------------------------------------------------
-- FAQ GÉNÉRAL (9)
-- -----------------------------------------------------------
INSERT INTO chatbot.intent_responses (id_intent, sous_intent, reponse, type_reponse, priorite) VALUES
-- presentation
(9, 'presentation',
'CTEXI (Cherif Trans Expert International) est une entreprise spécialisée dans le commerce international entre la Chine et l Afrique, basée au Burkina Faso. Notre devise : « Au cœur du Sahel, Au Service du Monde ». Nous proposons 5 services : CTEXI Cargo (transport), CTEXI Buy (sourcing & achat), CTEXI Pay (paiement international), CTEXI Travel (visa & voyages) et CTEXI Académie (formations). 🌍',
'text', 1),
(9, 'presentation',
'CTEXI est votre partenaire de confiance pour l import-export Chine-Afrique. 🤝 Nous accompagnons les entrepreneurs et commerçants africains dans leurs achats en Chine, le transport de leurs marchandises, les paiements internationaux, les voyages d affaires et la formation.',
'text', 1),
-- localisation
(9, 'localisation',
'CTEXI est basée au Burkina Faso 🇧🇫 avec des opérations en Chine. Nous intervenons principalement sur l axe Chine → Burkina Faso, mais nous couvrons également d autres pays d Afrique de l Ouest. Contactez un agent pour plus de détails sur votre zone.',
'text', 1),
-- contact_info
(9, 'contact_info',
'Pour nous contacter directement, je vous invite à cliquer sur "Contacter un agent" 📞. Nos agents sont disponibles pour vous répondre par WhatsApp, téléphone ou email dans les meilleurs délais.',
'text', 1),
-- horaires
(9, 'horaires',
'Nos agents sont disponibles du lundi au samedi 🕐. Pour une réponse rapide en dehors des heures ouvrables, vous pouvez laisser un message et nous vous recontacterons dès que possible. Je reste disponible 24h/24 pour répondre à vos questions !',
'text', 1),
-- confiance
(9, 'confiance',
'CTEXI est une entreprise sérieuse et enregistrée légalement au Burkina Faso ✅. Nous accompagnons de nombreux clients dans leurs opérations d import depuis la Chine. Notre priorité : votre satisfaction et la sécurité de vos transactions. N hésitez pas à contacter un agent pour en savoir plus sur nos références.',
'text', 1),
-- paiement_general
(9, 'paiement_general',
'Nous acceptons plusieurs modes de paiement selon le service concerné 💳 : paiement en FCFA, mobile money, virement bancaire et paiements en RMB (yuan chinois) via Alipay ou WeChat Pay pour les fournisseurs. Contactez un agent pour plus de détails selon votre besoin spécifique.',
'text', 1);

-- -----------------------------------------------------------
-- FAQ CARGO (4)
-- -----------------------------------------------------------
INSERT INTO chatbot.intent_responses (id_intent, sous_intent, reponse, type_reponse, priorite) VALUES
(4, 'cargo_general',
'CTEXI Cargo gère le transport de vos marchandises depuis la Chine vers le Burkina Faso et le reste de l Afrique 🚢✈️. Nous prenons en charge toute la logistique : enlèvement chez le fournisseur, groupage, expédition maritime ou aérienne, dédouanement et livraison finale.',
'text', 1),
(4, 'cargo_general',
'Avec CTEXI Cargo, importez vos marchandises depuis la Chine en toute sérénité 📦. Nous gérons le transport de A à Z : collecte, expédition, dédouanement et livraison. Service disponible par voie maritime (économique) ou aérienne (rapide).',
'text', 1),
(4, 'cargo_delais',
'Les délais varient selon le mode de transport choisi ⏱️ : par voie maritime comptez généralement plusieurs semaines, et par voie aérienne le délai est plus court. Pour une estimation précise selon votre type de marchandise et destination, je vous invite à contacter un de nos agents.',
'text', 1),
(4, 'cargo_tarif',
'Nos tarifs cargo dépendent du poids, du volume et du mode de transport (maritime ou aérien) 💰. Pour obtenir un devis personnalisé selon votre marchandise, contactez un de nos agents qui vous préparera une offre adaptée.',
'text', 1),
(4, 'cargo_processus',
'Le processus est simple avec CTEXI Cargo 📋 : 1️⃣ Vous nous communiquez les détails de votre commande, 2️⃣ Nous collectons chez votre fournisseur, 3️⃣ Nous expédions et gérons le dédouanement, 4️⃣ Vous recevez vos marchandises. Contactez un agent pour démarrer !',
'text', 1),
(4, 'cargo_produits',
'Nous transportons une large gamme de produits : vêtements, électroniques, équipements, cosmétiques, accessoires, pièces détachées et bien plus 📦. Certains produits sont soumis à des réglementations douanières spécifiques. Contactez un agent pour vérifier votre type de marchandise.',
'text', 1),
(4, 'cargo_assurance',
'Nous prenons soin de vos marchandises tout au long du transport 🛡️. En cas de problème, nos agents sont là pour vous accompagner dans les démarches. Pour les détails sur les garanties et assurances disponibles, je vous invite à contacter directement un agent CTEXI.',
'text', 1);

-- -----------------------------------------------------------
-- FAQ BUY (1)
-- -----------------------------------------------------------
INSERT INTO chatbot.intent_responses (id_intent, sous_intent, reponse, type_reponse, priorite) VALUES
(1, 'buy_general',
'CTEXI Buy est votre agent d achat en Chine 🛒. Nous nous occupons de tout : recherche de produits, identification de fournisseurs fiables, négociation des prix, contrôle qualité et coordination avec CTEXI Cargo pour l expédition. Vous achetez mieux, sans vous déplacer !',
'text', 1),
(1, 'buy_general',
'Avec CTEXI Buy, importez depuis la Chine sans stress ! 🇨🇳 Nos équipes sur place trouvent vos produits, vérifient la qualité et négocient les meilleurs prix pour vous. Idéal pour les commerçants et entrepreneurs africains.',
'text', 1),
(1, 'buy_fournisseurs',
'Oui, nous trouvons et vérifions les fournisseurs pour vous ✅. Notre équipe en Chine identifie des partenaires fiables, visite les usines si nécessaire et vérifie la conformité des produits avant tout paiement. Fini les arnaques et les mauvaises surprises !',
'text', 1),
(1, 'buy_qualite',
'Le contrôle qualité est au cœur de notre service 🔍. Avant chaque expédition, nos équipes inspectent les produits : conformité, quantité, emballage. Vous ne payez que pour ce que vous avez commandé, dans la qualité attendue.',
'text', 1),
(1, 'buy_tarif',
'Nos frais de service Buy sont calculés selon le volume et la complexité de la commande 💼. Pour obtenir une estimation, contactez un de nos agents qui étudiera votre besoin et vous proposera une offre transparente sans frais cachés.',
'text', 1),
(1, 'buy_plateformes',
'Nous travaillons avec toutes les grandes plateformes chinoises 🛍️ : Alibaba, 1688, Taobao, Pinduoduo, AliExpress et d autres. Vous nous donnez la référence produit ou la description, et nous trouvons la meilleure source pour vous.',
'text', 1);

-- -----------------------------------------------------------
-- FAQ TRAVEL (2)
-- -----------------------------------------------------------
INSERT INTO chatbot.intent_responses (id_intent, sous_intent, reponse, type_reponse, priorite) VALUES
(2, 'travel_general',
'CTEXI Travel vous accompagne dans tous vos voyages d affaires en Chine ✈️ : obtention du visa, réservation de billets d avion, hébergement et assistance sur place. Voyagez sereinement, nous gérons la logistique !',
'text', 1),
(2, 'travel_visa',
'Nous vous assistons dans toutes vos démarches de visa pour la Chine 🇨🇳📄. Nous vous guidons sur les documents à préparer, les démarches à suivre et nous vous aidons à optimiser les chances d obtention. Pour les délais et tarifs, contactez un agent.',
'text', 1),
(2, 'travel_visa',
'L obtention d un visa chinois nécessite plusieurs documents (passeport, photos, justificatifs...) 📋. CTEXI Travel vous accompagne étape par étape pour constituer votre dossier et maximiser vos chances d acceptation. Contactez un agent pour démarrer.',
'text', 1),
(2, 'travel_billet',
'Oui, nous réservons vos billets d avion pour la Chine ✈️ ! Nous cherchons les meilleures options selon vos dates et votre budget. Pour un devis, contactez un agent CTEXI Travel.',
'text', 1),
(2, 'travel_hotel',
'Nous réservons vos hôtels dans les principales villes d affaires chinoises 🏨 : Guangzhou, Shanghai, Yiwu, Shenzhen, Beijing... Selon votre budget et vos préférences. Contactez un agent pour vos réservations.',
'text', 1),
(2, 'travel_accompagnement',
'Nous pouvons vous accompagner avec des services d assistance sur place en Chine 🤝 : interprète, guide pour les marchés et usines, accompagnement lors des négociations. Une présence locale pour sécuriser vos achats d affaires. Demandez à un agent !',
'text', 1);

-- -----------------------------------------------------------
-- FAQ ACADEMIE (3)
-- -----------------------------------------------------------
INSERT INTO chatbot.intent_responses (id_intent, sous_intent, reponse, type_reponse, priorite) VALUES
(3, 'academie_general',
'CTEXI Académie est notre centre de formation spécialisé dans le commerce international 🎓. Nous formons les entrepreneurs et commerçants africains aux techniques d achat en Chine, au e-commerce, au sourcing et à l import-export en général.',
'text', 1),
(3, 'academie_general',
'Avec CTEXI Académie, devenez un expert de l import depuis la Chine ! 📚 Nos formations pratiques vous donnent toutes les clés pour acheter intelligemment, éviter les arnaques et développer votre business.',
'text', 1),
(3, 'academie_contenu',
'Nos formations couvrent : l utilisation des plateformes chinoises (Alibaba, 1688, Pinduoduo) 🛒, la négociation avec les fournisseurs, le contrôle qualité, la logistique import, le e-commerce et le sourcing commercial. Formation complète et pratique !',
'text', 1),
(3, 'academie_modalites',
'Nous proposons des formations en présentiel et à distance 💻. Les sessions peuvent être individuelles ou en groupe, selon vos disponibilités. Pour connaître le planning des prochaines formations, contactez un agent CTEXI Académie.',
'text', 1),
(3, 'academie_tarif',
'Les tarifs de nos formations varient selon le type et la durée du programme 💰. Pour obtenir le programme détaillé et les tarifs, je vous invite à contacter un de nos agents qui vous présentera nos offres de formation disponibles.',
'text', 1),
(3, 'academie_certification',
'À l issue de nos formations, vous recevez une attestation de participation CTEXI Académie 🎓. Nos formations sont conçues pour être immédiatement opérationnelles. Pour les détails sur la certification, contactez un agent.',
'text', 1);
