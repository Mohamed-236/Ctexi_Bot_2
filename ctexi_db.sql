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


SELECT * FROM chatbot.operation;

SELECT * FROM chatbot.operation_phrase;


-- Table des phrases utilisateur (patterns)
CREATE TABLE chatbot.operation_phrase (
    id_phrase SERIAL PRIMARY KEY,
    id_operation INT REFERENCES chatbot.operation(id_operation) ON DELETE CASCADE,
    id_intent INT REFERENCES chatbot.intention(id_intent) ON DELETE CASCADE,
    phrase TEXT NOT NULL,
    est_actif BOOLEAN DEFAULT TRUE,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


DROP TABLE chatbot.operation_phrase;

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
CREATE TABLE chatbot.conversations(
    id_conv SERIAL PRIMARY KEY,
    id_user INTEGER NOT NULL REFERENCES auth.users(id_user) ON DELETE CASCADE,
    id_intent INTEGER NOT NULL REFERENCES chatbot.intention(id_intent) ON DELETE CASCADE,
    message_user TEXT NOT NULL,
    reponse_bot TEXT,
    dates TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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


INSERT INTO chatbot.intention(nom, type_intent, descriptions)
VALUES
(
'salutation',
'social',
'Intentions de début de conversation et de salutation.'
);


----------------------------------------------aurevoir ==>2
INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'au_revoir',
'social',
'Intentions de fin de conversation ou de prise de congé.'

);


----------------------------------------------remerciement ==>3

INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'remerciement',
'social',
'Intentions exprimant la gratitude ou les remerciements.'
);


----------------------------------------------validation ==>4
INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'validation',
'social',
'Intentions de confirmation ou validation d’une information.'

);


----------------------------------------------buy(achat) ==>5

INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'faq_buy',
'information',
'Questions sur le service d’achat de produits en Chine (processus, commande, paiement, livraison).'

);


--------------------------------------------travel  ==> 6

INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'faq_travel',
'information',
'Questions liées au voyage en Chine (visa, billet, hébergement, procédures).'
);



-----------------------------------------academie  ==> 7

INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'faq_academie',
'information',
'Questions sur les formations proposées (inscription, contenu, durée, prix).'
);



--------------------------------------    cargo==> 8

INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'faq_cargo',
'information',
'Questions sur le transport de colis Chine–Burkina (délais, coûts, douane, suivi).'
);


-----------------------------------suivi_colis ==> 9

INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'suivi_colis',
'operation',
'Suivi et vérification du statut d’un colis ou d’une commande.'

);


----------------------------------contact_agent ==> 10
INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'contact_agent',
'operation',
'Demande de mise en relation avec un agent humain ou assistance directe.'

);

--------------------------------service_info ==> 11
INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'service_info',
'operation',
'Demande d’information générale sur les services proposés par l’entreprise.'
);



-----------------------------------taux_de_change ==> 12

INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'taux_change',
'operation',
'Conversion de devises et gestion des paiements internationaux.'
);




SELECT * FROM chatbot.intention;

------------------------------------------------Table Faq--------------------------------------------------------------



-- =======================
-- buy (id_intent = 5)
-- =======================


INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES

(5, 'comment fonctionne votre service ctexi buy', 'CTEXI Buy vous accompagne de la recherche du produit jusqu’à la livraison : sourcing, achat, contrôle qualité et expédition.'),
(5, 'comment fonctionne  ctexi buy', 'CTEXI Buy vous accompagne de la recherche du produit jusqu’à la livraison : sourcing, achat, contrôle qualité et expédition.'),
(5, 'comment fonctionne votre service d’achat', 'CTEXI Buy vous accompagne de la recherche du produit jusqu’à la livraison : sourcing, achat, contrôle qualité et expédition.'),


(5, 'comment acheter en chine ', 'Vous nous envoyez le produit souhaité, nous recherchons le fournisseur, achetons et livrons le produit.'),
(5, 'comment acheter un produit en chine ', 'Vous nous envoyez le produit souhaité, nous recherchons le fournisseur, achetons et livrons le produit.'),
(5, 'comment acheter un produit en chine  avec vous', 'Vous nous envoyez le produit souhaité, nous recherchons le fournisseur, achetons et livrons le produit.'),


(5, 'quelles sont les étapes d’achat', 'Les étapes sont : demande client, recherche fournisseur, achat, contrôle qualité, expédition et livraison.'),
(5, 'les étapes d’achat', 'Les étapes sont : demande client, recherche fournisseur, achat, contrôle qualité, expédition et livraison.'),
(5, 'les étapes pour acheter', 'Les étapes sont : demande client, recherche fournisseur, achat, contrôle qualité, expédition et livraison.'),
(5, 'les étapes pour un achat', 'Les étapes sont : demande client, recherche fournisseur, achat, contrôle qualité, expédition et livraison.'),
(5, 'cite moi les étapes pour un acheter un produit', 'Les étapes sont : demande client, recherche fournisseur, achat, contrôle qualité, expédition et livraison.'),


(5, 'c’est possible d’acheter pour moi', 'Oui, nous achetons directement pour vous auprès de fournisseurs en Chine.'),
(5, 'est ce que vous achetez pour moi', 'Oui, nous achetons directement pour vous auprès de fournisseurs en Chine.'),
(5, 'vous achetez pour moi', 'Oui, nous achetons directement pour vous auprès de fournisseurs en Chine.'),
(5, 'je veux que vous achetez pour moi', 'Oui, nous achetons directement pour vous auprès de fournisseurs en Chine.'),


(5, 'comment passer une commande', 'Vous envoyez les détails du produit, nous nous occupons du reste jusqu’à la livraison.'),
(5, 'comment faire une commande', 'Vous envoyez les détails du produit, nous nous occupons du reste jusqu’à la livraison.'),
(5, 'comment effectuer une commande', 'Vous envoyez les détails du produit, nous nous occupons du reste jusqu’à la livraison.'),
(5, 'comment effectuer une commande avec vous', 'Vous envoyez les détails du produit, nous nous occupons du reste jusqu’à la livraison.'),
(5, 'comment effectuer une commande chez vous', 'Vous envoyez les détails du produit, nous nous occupons du reste jusqu’à la livraison.'),
(5, 'comment effectuer une commande en chine', 'Vous envoyez les détails du produit, nous nous occupons du reste jusqu’à la livraison.'),
(5, 'comment faire une commande en chine', 'Vous envoyez les détails du produit, nous nous occupons du reste jusqu’à la livraison.'),


(5, 'combien de temps prend une commande', 'Le délai est généralement de 7 à 45 jours selon le mode de transport.'),
(5, 'combien de temps prend une commande en chine', 'Le délai est généralement de 7 à 45 jours selon le mode de transport.'),
(5, 'combien de temps dure une commande', 'Le délai est généralement de 7 à 45 jours selon le mode de transport.'),
(5, 'une commande peut durer combien temps', 'Le délai est généralement de 7 à 45 jours selon le mode de transport.'),
(5, 'une commande dure combien temps', 'Le délai est généralement de 7 à 45 jours selon le mode de transport.'),
(5, 'une commande dure combien de jour', 'Le délai est généralement de 7 à 45 jours selon le mode de transport.'),


(5, 'est ce que vous verifiez les produits', 'Oui, nous faisons un contrôle qualité avant l’expédition pour vérifier la conformité.'),
(5, 'vous verifiez les produits', 'Oui, nous faisons un contrôle qualité avant l’expédition pour vérifier la conformité.'),
(5, 'est ce que vous faites une verification des produits', 'Oui, nous faisons un contrôle qualité avant l’expédition pour vérifier la conformité.'),
(5, 'vous faites une verification des produits', 'Oui, nous faisons un contrôle qualité avant l’expédition pour vérifier la conformité.'),



(5, 'proposez vous une assurance', 'Oui, une assurance transport peut être ajoutée pour couvrir pertes ou dommages.'),
(5, 'est ce que vous proposez une assurance', 'Oui, une assurance transport peut être ajoutée pour couvrir pertes ou dommages.'),
(5, 'vous avez une assurance', 'Oui, une assurance transport peut être ajoutée pour couvrir pertes ou dommages.'),
(5, 'votre service dispose d’une assurance', 'Oui, une assurance transport peut être ajoutée pour couvrir pertes ou dommages.'),



(5, 'comment se passe la livraison du produit', 'La livraison se fait par avion ou bateau selon votre choix et votre budget.'),
(5, 'comment se fait la livraison', 'La livraison se fait par avion ou bateau selon votre choix et votre budget.'),
(5, 'la livraison se passe comment', 'La livraison se fait par avion ou bateau selon votre choix et votre budget.'),
(5, 'la livraison se fait comment', 'La livraison se fait par avion ou bateau selon votre choix et votre budget.'),
(5, 'comment se fait la livraison', 'La livraison se fait par avion ou bateau selon votre choix et votre budget.'),
(5, 'parle moi de la livraison', 'La livraison se fait par avion ou bateau selon votre choix et votre budget.'),
(5, 'parle moi du procedure de la livraison', 'La livraison se fait par avion ou bateau selon votre choix et votre budget.'),

(5, 'puis je annuler ma commande', 'Oui, uniquement si la commande n’a pas encore été payée au fournisseur.'),
(5, 'on peut annuler une commande', 'Oui, uniquement si la commande n’a pas encore été payée au fournisseur.'),
(5, 'est ce que c’est possible d’annuler ma commande', 'Oui, uniquement si la commande n’a pas encore été payée au fournisseur.'),
(5, 'puis je annuler ma commande', 'Oui, uniquement 'si la commande n’a pas encore été payée au fournisseur.'),
(5, 'c’est possible d’annuler ma commande', 'Oui, uniquement si la commande n’a pas encore été payée au fournisseur.'),

(5, 'quels produits pouvez vous acheter', 'Nous pouvons acheter presque tous les produits disponibles en Chine selon la légalité.'),
(5, 'quel type de produits pouvez vous acheter', 'Nous pouvons acheter presque tous les produits disponibles en Chine selon la légalité.'),
(5, 'c’est quel produit vous pouvez acheter', 'Nous pouvons acheter presque tous les produits disponibles en Chine selon la légalité.'),
(5, 'quels produits pouvez vous acheter', 'Nous pouvons acheter presque tous les produits disponibles en Chine selon la légalité.'),
(5, 'vous acheter quel genre de produit', 'Nous pouvons acheter presque tous les produits disponibles en Chine selon la légalité.'),


(5, 'comment payer la commande', 'Le paiement se fait après validation du devis et du produit choisi.'),
(5, 'on fait comment pour payer une commande', 'Le paiement se fait après validation du devis et du produit choisi.'),
(5, 'comment se fait le paiement', 'Le paiement se fait après validation du devis et du produit choisi.'),
(5, 'comment payer une commande', 'Le paiement se fait après validation du devis et du produit choisi.'),

(5, 'est ce fiable d’acheter avec vous', 'Oui, nous sécurisons l’achat, vérifions les produits et réduisons les risques liés aux fournisseurs chinois.'),
(5, 'c’est garanti d’acheter avec vous', 'Oui, nous sécurisons l’achat, vérifions les produits et réduisons les risques liés aux fournisseurs chinois.'),
(5, 'est ce fiable d’acheter avec vous', 'Oui, nous sécurisons l’achat, vérifions les produits et réduisons les risques liés aux fournisseurs chinois.'),
(5, 'l’achat chez vous est garanti', 'Oui, nous sécurisons l’achat, vérifions les produits et réduisons les risques liés aux fournisseurs chinois.'),
(5, 'c’est sure d’acheter chez vous', 'Oui, nous sécurisons l’achat, vérifions les produits et réduisons les risques liés aux fournisseurs chinois.');



-- =======================
-- travel (id_intent = 6)
-- =======================

INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES

(6, 'comment obtenir un visa pour la chine', 'CTEXI Travel vous accompagne dans l’obtention de votre visa chinois avec les documents, délais et assistance.'),
(6, 'comment obtenir un visa chinois', 'CTEXI Travel vous accompagne dans l’obtention de votre visa chinois avec les documents, délais et assistance.'),
(6, 'comment faire un visa pour la chine', 'CTEXI Travel vous accompagne dans l’obtention de votre visa chinois avec les documents, délais et assistance.'),
(6, 'quel est la procedure de visa pour la chine', 'CTEXI Travel vous accompagne dans l’obtention de votre visa chinois avec les documents, délais et assistance.'),
(6, 'je veux aller en chine comment obtenir le visa', 'CTEXI Travel vous accompagne dans l’obtention de votre visa chinois avec les documents, délais et assistance.'),
(6, 'comment voyager en chine', 'CTEXI Travel vous accompagne dans l’obtention de votre visa chinois avec les documents, délais et assistance.'),

(6, 'quels sont les documents pour  le visa chinois', 'Vous devez fournir un passeport valide, des photos, un formulaire rempli, une preuve d’hébergement et un billet aller-retour.'),
(6, 'quels sont les documents necessaires pour le visa en chine', 'Vous devez fournir un passeport valide, des photos, un formulaire rempli, une preuve d’hébergement et un billet aller-retour.'),
(6, 'quel est le dossier a fournir pour le visa en chine', 'Vous devez fournir un passeport valide, des photos, un formulaire rempli, une preuve d’hébergement et un billet aller-retour.'),
(6, 'quels sont les pieces a fournir pour le visa chinois', 'Vous devez fournir un passeport valide, des photos, un formulaire rempli, une preuve d’hébergement et un billet aller-retour.'),

(6, 'il faut combien de temps pour obtenir le visa pour la chine', 'Le délai est généralement de 5 à 15 jours ouvrables selon le type de visa.'),
(6, 'quel est le delai pour obtenir le visa pour la chine', 'Le délai est généralement de 5 à 15 jours ouvrables selon le type de visa.'),
(6, 'le visa pour la chine prend combien de jours', 'Le délai est généralement de 5 à 15 jours ouvrables selon le type de visa.'),
(6, 'quel est le temps de traitement pour le visa chinois', 'Le délai est généralement de 5 à 15 jours ouvrables selon le type de visa.'),

(6, 'vous faites la reservation de billet d’avion pour la chine', 'Nous pouvons vous aider à réserver vos billets d’avion et hôtels en Chine.'),
(6, 'quel est le prix de billet d’avion pour la chine', 'Nous pouvons vous aider à réserver vos billets d’avion et hôtels en Chine.Pour le prix merci de contacter un agent'),
(6, 'je veux acheter un billet pour la chine', 'Nous pouvons vous aider à réserver vos billets d’avion et hôtels en Chine.'),
(6, 'aidez moi a reserver un billet d’avion pour la chine', 'Nous pouvons vous aider à réserver vos billets d’avion et hôtels en Chine.'),

(6, 'vous faites la reservation d’hotel en chine', 'Nous pouvons vous aider à réserver vos hôtels en Chine.'),
(6, 'je veux prendre un hotel en chine', 'Nous pouvons vous aider à réserver vos hôtels en Chine.'),
(6, 'ou je vais me loger une fois en chine', 'Nous pouvons vous aider à réserver vos hôtels en Chine.'),
(6, 'comment se passe le logement une fois en chine', 'Nous pouvons vous aider à réserver vos hôtels en Chine.'),


(6, 'vous avez une assistance a l’aeroport en chine', 'Oui, une assistance peut être organisée à votre arrivée en Chine.'),
(6, 'vous faites un accueil a l’aeroport en chine', 'Oui, une assistance peut être organisée à votre arrivée en Chine.'),
(6, 'est ce que quelqu’un peut me recuperer a l’aeroport en chine', 'Oui, une assistance peut être organisée à votre arrivée en Chine.'),
(6, 'est ce que quelqu’un me croisera a l’aeroport en chine', 'Oui, une assistance peut être organisée à votre arrivée en Chine.'),

(6, 'est ce que c’est possible de modifier une reservation', 'Les modifications dépendent des conditions du billet ou de l’hôtel.'),
(6, 'c’est possible de changer un billet d’avion', 'Les modifications dépendent des conditions du billet ou de l’hôtel.'),
(6, 'c’est possible de modifier ou changer un hotel', 'Les modifications dépendent des conditions du billet ou de l’hôtel.'),
(6, 'est ce que que c’est possible d’annuler une reservation', 'Les modifications dépendent des conditions du billet ou de l’hôtel.');


-- =======================
-- academie (id_intent = 7)
-- =======================

INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES

(7, 'quelles sont les formations que vous proposez', 'CTEXI Académie propose des formations en import-export, achats en Chine, marketing digital et coaching.'),
(7, 'vous faites des formations', 'CTEXI Académie propose des formations en import-export, achats en Chine, marketing digital et coaching.'),
(7, 'je veux me former chez vous', 'CTEXI Académie propose des formations en import-export, achats en Chine, marketing digital et coaching.'),
(7, 'c’est quoi vos formations', 'CTEXI Académie propose des formations en import-export, achats en Chine, marketing digital et coaching.'),
(7, 'je veux apprendre import export', 'CTEXI Académie propose des formations en import-export, achats en Chine, marketing digital et coaching.'),

(7, 'comment je peux m’inscrire a une formation', 'Vous pouvez vous inscrire en nous contactant via WhatsApp, email ou en remplissant le formulaire.'),
(7, 'je veux m’inscrire a une formation', 'Vous pouvez vous inscrire en nous contactant via WhatsApp, email ou en remplissant le formulaire.'),
(7, 'comment faire pour s’inscrire a une formation', 'Vous pouvez vous inscrire en nous contactant via WhatsApp, email ou en remplissant le formulaire.'),
(7, 'inscription formation comment ca se passe', 'Vous pouvez vous inscrire en nous contactant via WhatsApp, email ou en remplissant le formulaire.'),

(7, 'les formations sont en ligne ou en salle ou presentielle', 'Nos formations sont disponibles en ligne et aussi en présentiel.'),
(7, 'je peux suivre la formation a distance', 'Oui, vous pouvez suivre nos formations en ligne ou en présentiel.'),
(7, 'est ce que c’est en ligne', 'Oui, vous pouvez suivre nos formations en ligne ou en présentiel.'),
(7, 'vous faites des cours en ligne', 'Oui, vous pouvez suivre nos formations en ligne ou en présentiel.'),

(7, 'est ce que vous donnez un certificat', 'Oui, un certificat est délivré à la fin de la formation.'),
(7, 'je vais avoir une attestation apres la formation', 'Oui, un certificat est délivré à la fin de la formation.'),
(7, 'il y a certificat a la fin', 'Oui, un certificat est délivré à la fin de la formation.'),

(7, 'est ce que vous accompagnez les apprenants', 'Oui, certaines formations incluent un accompagnement pratique personnalisé.'),
(7, 'vous aidez apres la formation', 'Oui, certaines formations incluent un accompagnement pratique personnalisé.'),
(7, 'est ce que vous suivez les etudiants', 'Oui, certaines formations incluent un accompagnement pratique personnalisé.'),
(7, 'il y a un suivi apres formation', 'Oui, certaines formations incluent un accompagnement pratique personnalisé.'),

(7, 'formation coute combien', 'Le prix dépend de la formation choisie. Contactez-nous pour plus de détails.'),
(7, 'formation dure combien de temps', 'La durée varie selon la formation, contactez-nous pour plus de précisions.'),
(7, 'formation commence quand', 'Les sessions sont programmées régulièrement, contactez-nous pour connaître les prochaines dates.');


-- =======================
-- cargo (id_intent = 8)
-- =======================

INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES
(8, 'est ce que vous pouvez expedier mes colis de chine au burkina', 'Nous assurons l’expédition de vos marchandises de la Chine vers le Burkina Faso.'),
(8, 'est ce que vous pouvez envoyer mes colis de chine au burkina', 'Nous assurons l’expédition de vos marchandises de la Chine vers le Burkina Faso.'),
(8, 'comment envoyer de la marchandise de la chine vers le burkina', 'Nous assurons l’expédition de vos marchandises de la Chine vers le Burkina Faso.'),
(8, 'vous faites transport de la chine vers le burkina', 'Nous assurons l’expédition de vos marchandises de la Chine vers le Burkina Faso.'),
(8, 'je veux faire venir des produits de chine', 'Nous assurons l’expédition de vos marchandises de la Chine vers le Burkina Faso.'),
(8, 'vous pouvez livrer mes colis depuis la chine', 'Nous assurons l’expédition de vos marchandises de la Chine vers le Burkina Faso.'),
(8, 'je veux faire une expedition', 'Nous assurons l’expédition de vos marchandises de la Chine vers le Burkina Faso.'),

(8, 'combien de temps prend le transport', 'Le délai dépend du mode : environ 7 à 15 jours par avion et 30 à 45 jours par bateau.'),
(8, 'le colis va arriver en combien de jours', 'Le délai dépend du mode : environ 7 à 15 jours par avion et 30 à 45 jours par bateau.'),
(8, 'quel est le delai de livraison de la chine vers le burkina', 'Le délai dépend du mode : environ 7 à 15 jours par avion et 30 à 45 jours par bateau.'),
(8, 'le transport depuis la chine dure combien de temps', 'Le délai dépend du mode : environ 7 à 15 jours par avion et 30 à 45 jours par bateau.'),

(8, 'combien ca coute le transport', 'Les frais dépendent du poids, du volume, du mode de transport et de la destination.'),
(8, 'je veux connaitre le prix de transport de chine vers le burkina', 'Les frais dépendent du poids, du volume, du mode de transport et de la destination.'),
(8, 'je vais payer combien pour transporter mes colis', 'Les frais dépendent du poids, du volume, du mode de transport et de la destination.'),
(8, 'quel est le tarif d’expedition depuis la chine', 'Les frais dépendent du poids, du volume, du mode de transport et de la destination.'),

(8, 'est ce qu’il y a des produits interdits', 'Certains produits sont interdits comme les marchandises dangereuses ou contrefaites.'),
(8, 'quels produits je ne peux pas envoyer', 'Certains produits sont interdits comme les marchandises dangereuses ou contrefaites.'),
(8, 'est ce que je peux envoyer tout type de marchandise', 'Certains produits sont interdits comme les marchandises dangereuses ou contrefaites.'),

(8, 'est ce que je dois payer les frais de la douane', 'Des frais de douane peuvent s’appliquer selon la nature du produit.'),
(8, 'les frais de douane comment ca marche', 'Des frais de douane peuvent s’appliquer selon la nature du produit.'),
(8, 'douane burkina colis chine', 'Des frais de douane peuvent s’appliquer selon la nature du produit.'),

(8, 'pourquoi mon colis est en retard', 'Les retards peuvent être causés par la douane ou le transport.'),
(8, 'mon colis tarde a arriver', 'Les retards peuvent être causés par la douane ou le transport.'),
(8, 'quel est la cause de retard de livraison', 'Les retards peuvent être causés par la douane ou le transport.'),


(8, 'mon colis est en transit ca veut dire quoi', 'Votre colis est en cours d’acheminement vers le Burkina Faso.'),
(8, 'colis en route', 'Votre colis est en cours d’acheminement vers le Burkina Faso.'),
(8, 'mon colis est en chemin', 'Votre colis est en cours d’acheminement vers le Burkina Faso.'),


(8, 'mon code colis ne marche pas', 'Vérifiez votre code ou contactez le support.'),
(8, 'code colis invalide', 'Vérifiez votre code ou contactez le support.'),
(8, 'je n’arrive pas a suivre mon colis', 'Vérifiez votre code ou contactez le support.'),

(8, 'j’ai plusieurs colis comment faire', 'Vous pouvez suivre plusieurs colis en même temps.'),
(8, 'je veux suivre plusieurs colis', 'Vous pouvez suivre plusieurs colis en même temps.'),
(8, 'est ce que je peux suivre plusieurs colis', 'Vous pouvez suivre plusieurs colis en même temps.'),

(8, 'mon colis est gate', 'Signalez le problème avec des preuves pour lancer une procédure d’indemnisation.'),
(8, 'colis endommage', 'Signalez le problème avec des preuves pour lancer une procédure d’indemnisation.'),
(8, 'j’ai recu mon colis abime', 'Signalez le problème avec des preuves pour lancer une procédure d’indemnisation.'),
(8, 'mon colis est casse', 'Signalez le problème avec des preuves pour lancer une procédure d’indemnisation.');



-- =======================
-- taux_change (id_intent = 12)
-- =======================

INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES

(12, 'combien de temps prend un transfert', 'Un transfert prend généralement entre 24 et 72 heures.'),
(12, 'un transfert dure combien de jours', 'Un transfert prend généralement entre 24 et 72 heures.'),
(12, 'je vais attendre combien de temps pour mon paiement', 'Un transfert prend généralement entre 24 et 72 heures.'),
(12, 'delai paiement chine combien de temps', 'Un transfert prend généralement entre 24 et 72 heures.'),

(12, 'comment calculer le paiement', 'Entrez le montant en yuan (RMB) et vous aurez le montant total en FCFA.'),
(12, 'je veux calculer combien je vais payer', 'Entrez le montant en yuan (RMB) et vous aurez le montant total en FCFA.'),
(12, 'comment convertir yuan en fcfa', 'Entrez le montant en yuan (RMB) et vous aurez le montant total en FCFA.'),
(12, 'je veux connaitre le prix en fcfa', 'Entrez le montant en yuan (RMB) et vous aurez le montant total en FCFA.'),

(12, 'comment faire une demande de paiement', 'Cliquez pour contacter CTEXI Pay via WhatsApp et un agent va vous accompagner.'),
(12, 'je veux faire un paiement', 'Cliquez pour contacter CTEXI Pay via WhatsApp et un agent va vous accompagner.'),
(12, 'comment payer un fournisseur en chine', 'Cliquez pour contacter CTEXI Pay via WhatsApp et un agent va vous accompagner.'),
(12, 'vous pouvez payer pour moi en chine', 'Cliquez pour contacter CTEXI Pay via WhatsApp et un agent va vous accompagner.'),

(12, 'est ce que le paiement est securise', 'Oui, toutes les transactions sont sécurisées.'),
(12, 'votre paiement est fiable', 'Oui, toutes les transactions sont sécurisées.'),
(12, 'je peux vous faire confiance pour payer', 'Oui, toutes les transactions sont sécurisées.'),

(12, 'est ce que je vais recevoir une preuve de paiement', 'Oui, une preuve est fournie après chaque transaction.'),
(12, 'vous donnez recu paiement', 'Oui, une preuve est fournie après chaque transaction.'),
(12, 'je vais avoir un justificatif', 'Oui, une preuve est fournie après chaque transaction.');


SELECT * FROM chatbot.faq;




