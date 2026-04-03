-- Active: 1774354264909@@127.0.0.1@5432@ctexi_db

-----------------------------------CREATION DES SCHEMA---------------------------------------------------


-- installation de  pgvector(extension de postgres) pour la creation des embedding
CREATE EXTENSION IF NOT EXISTS vector;

SET search_path TO public;

-- Mdp:postgres: Yakfis@226

SELECT * FROM chatbot.faq;


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

SELECT * FROM auth.users;

--Table agents
DROP TABLE auth.agents CASCADE;

CREATE TABLE auth.agents(
    id_agent SERIAL PRIMARY KEY,
    id_intent INTEGER REFERENCES chatbot.intention(id_intent) ON DELETE CASCADE,
    whatsapp VARCHAR(20) NOT NULL,
    telephone VARCHAR(20) NOT NULL,
    email VARCHAR(50) NOT NULL,
    actif BOOLEAN DEFAULT TRUE,
    dates TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

SELECT * FROM auth.agents;
----------------------------------NSERTION DES AGENTS EXEMPLE--------------------------------------

TRUNCATE TABLE auth.agents RESTART IDENTITY;

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


SELECT * FROM auth.agents;


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




--Table convesation
CREATE TABLE chatbot.conversations(
    id_conv SERIAL PRIMARY KEY,
    id_user INTEGER NOT NULL REFERENCES auth.users(id_user) ON DELETE CASCADE,
    message_user TEXT NOT NULL,
    reponse_bot TEXT,
    intention VARCHAR(255),
    dates TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


DROP TABLE chatbot.conversations CASCADE;

TRUNCATE TABLE chatbot.conversations RESTART IDENTITY CASCADE;




--Table sessions
CREATE TABLE chatbot.sessions(
    id_sess SERIAL PRIMARY KEY,
    id_user INTEGER REFERENCES auth.users(id_user) ON DELETE CASCADE,
    heure_debut TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    heure_fin TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statut VARCHAR(50) NOT NULL
);




--Table intention

CREATE TABLE chatbot.intention(
    id_intent SERIAL PRIMARY KEY,
    nom VARCHAR(100) UNIQUE NOT NULL,
    type_intent VARCHAR(50) NOT NULL,
    descriptions TEXT,
    embedding vector(384),
    dates TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE chatbot.intention CASCADE;




SELECT * FROM chatbot.intention;



SELECT * FROM chatbot.intention;

-- Table reponse_intention

CREATE TABLE chatbot.reponse_intention(
    id_rep_intent SERIAL PRIMARY KEY,
    id_intent INTEGER NOT NULL REFERENCES chatbot.intention(id_intent) ON DELETE CASCADE,
    reponse TEXT NOT NULL
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

SELECT * FROM core.service;

TRUNCATE TABLE core.service RESTART IDENTITY CASCADE;


--Table formations
CREATE TABLE core.formation(
    id_formation SERIAL PRIMARY KEY,
    titre VARCHAR(150) NOT NULL,
    descriptions TEXT,
    date_debut DATE,
    date_fin DATE
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


SELECT * FROM core.colis;

--Table taux_change
CREATE TABLE core.taux_change(
    id_taux SERIAL PRIMARY KEY,
    taux NUMERIC(10, 2) NOT NULL,
    dates TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-------------------------------------SCHEMA SYSTEMS--------------------------------------------------------------


--Table logs 
CREATE TABLE systems.log(
    id_log SERIAL PRIMARY KEY,
    id_sess INTEGER REFERENCES chatbot.sessions(id_sess) ON DELETE SET NULL,
    actions VARCHAR(100),
    levels VARCHAR(20),
    dates TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);




--table notification

CREATE TABLE systems.notification(
    id_notif SERIAL PRIMARY KEY,
    id_user INTEGER REFERENCES auth.users(id_user) ON DELETE CASCADE,
    contenu TEXT NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


----------------------------------------------Suppression et mise a jour-------------------------------------------


-- Pour chatbot.faq
UPDATE chatbot.faq SET embedding = NULL;

-- Pour chatbot.intention
UPDATE chatbot.intention SET embedding = NULL;



DROP TABLE chatbot.faq CASCADE;
DROP TABLE chatbot.intention CASCADE;


-- Supprime toutes les lignes de la table FAQ
DELETE FROM chatbot.faq;

-- Supprime toutes les lignes de la table intention
DELETE FROM chatbot.intention;


SELECT * FROM chatbot.conversations;

SET search_path TO chatbot, public;


SELECT extname FROM pg_extension;


SELECT * FROM auth.agents;



--Ajout d'embeding dans intention
SET search_path TO chatbot, public;



-- Supprime toutes les lignes et réinitialise les séquences
TRUNCATE TABLE chatbot.faq RESTART IDENTITY CASCADE;
TRUNCATE TABLE chatbot.intention RESTART IDENTITY CASCADE;


-- Supprimer la colonne embedding
ALTER TABLE chatbot.faq DROP COLUMN embedding;
ALTER TABLE chatbot.intention DROP COLUMN embedding;

ALTER TABLE chatbot.intention 
ADD COLUMN embedding vector(384);


SELECT * FROM chatbot.intention;


-------------------------------Insertion des donnees dans les tables faq et intention----------------------------------





------------------------------------------Table Intention---------------------------------------------------------------



---------------------------------------------salutation ==> 1
INSERT INTO chatbot.intention(nom, type_intent, descriptions)
VALUES
(
'salutation',
'social',

'Intentions de salutation et interaction sociale initiale. L''utilisateur cherche à dire bonjour, saluer, engager une conversation ou établir un contact poli.'
);


----------------------------------------------aurevoir ==>2
INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'au_revoir',
'social',
'Intentions de fin de conversation : l’utilisateur souhaite quitter la discussion, dire au revoir, prendre congé ou terminer l’échange.'
);


----------------------------------------------remerciement ==>3

INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'remerciement',
'social',
'Intentions où l’utilisateur exprime sa gratitude, remercie ou montre de la reconnaissance après une aide ou une information reçue.'
);


----------------------------------------------validation ==>4
INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'validation',
'social',
'Intentions où l’utilisateur confirme une information, valide une réponse, accepte ou montre son accord.'
);




----------------------------------------------buy(achat) ==>5
INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'faq_buy',
'information',
'Intentions liées au service CTEXI Buy : achat de produits en Chine pour le client. Inclut la recherche de fournisseurs, la commande, le contrôle qualité, la négociation, l''expédition, le suivi de commande, les délais de livraison et la gestion des problèmes liés aux achats.'
);


-------------------------------------------travel  ==>6

INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'faq_travel',
'information',
'Intentions liées au service CTEXI Travel : voyage en Chine, obtention de visa, réservation de billets d''avion, réservation d''hôtels, assistance aéroport et modification de réservation.'
);


-----------------------------------------academie ==>7

INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'faq_academie',
'information',
'Intentions liées aux formations CTEXI Académie : inscription, types de formations, formation en ligne ou présentiel, certification et accompagnement pratique.'
);


--------------------------------------cargo  ==>8

INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'faq_cargo',
'information',
'Intentions liées au transport et à la logistique CTEXI Cargo : expédition Chine vers Burkina Faso, frais de transport, douane, délais, produits interdits et service client.'
);




-----------------------------------suivi_colis ==>9

INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'suivi_colis',
'operation',
'Intentions liées au suivi de colis : consulter le statut, vérifier la position, comprendre les statuts, gérer les problèmes de colis et suivi des expéditions.'
);




----------------------------------contact_agent ==>10

INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'contact_agent',
'operation',
'Intentions où L''utilisateur veut parler à un agent humain, contacter le support,obtenir une assistance directe, 
discuter avec un conseiller,
demander un contact WhatsApp, email ou téléphone,
parler à une vraie personne, aide humaine urgente.'
);





--------------------------------service_info ==> 11

INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'service_info',
'operation',
'Intentions où l’utilisateur souhaite découvrir les services proposés par CTEXI : Buy, Cargo, Pay, Travel et Académie.'
);



-----------------------------------taux_de_change ==> 12

INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'taux_change',
'operation',
'Intentions liées aux paiements et taux de change : conversion RMB FCFA, transfert d''argent, délais de paiement, preuve de transaction et sécurité.'
);




------------------------------------------------Table Faq--------------------------------------------------------------


-- =======================
-- salutation (id_intent = 1)
-- =======================

INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES
(1, 'salut', 'Salut 👋 Comment puis-je vous aider ?'),
(1, 'bonjour', 'Bonjour 👋 Comment puis-je vous aider ?'),
(1, 'ca va', 'Je vais bien merci 😊  Comment puis-je vous aider ?'),
(1, 'bonsoir', 'Bonsoir 👋 Comment puis-je vous aider ?');



-- =======================
-- aurevoir (id_intent = 2)
-- =======================

INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES

(2, 'au revoir', 'Au revoir 👋 À bientôt !'),
(2, 'bye', 'Bye 👋 Passez une excellente journée !'),
(2, 'a plus', 'À la prochaine 👋'),
(2, 'je pars', 'D’accord 😊 À bientôt !'),
(2, 'bonne journee', 'Merci 😊 Bonne journée à vous aussi !');



-- =======================
-- remerciement (id_intent = 3)
-- =======================


INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES

(3, 'merci', 'Je vous en prie 😊 N’hésitez pas si vous avez d’autres questions.'),
(3, 'merci beaucoup', 'Je vous en prie 😊'),
(3, 'thanks', 'You are welcome 😊'),
(3, 'grand merci', 'Avec plaisir 😊'),
(3, 'c est gentil', 'Merci à vous 😊 Si vous avez d’autres questions n’hesitez pas.');



-- =======================
-- validation (id_intent = 4)
-- =======================

INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES

(4, 'ok', 'Parfait 👍 Avez-vous d’autres questions ?'),
(4, 'd accord', 'Très bien 👍 N’hésitez pas si besoin !'),
(4, 'cool', 'Super 😄 Autres choses a me demander ?'),
(4, 'ca marche', 'Parfait 👍Si vous avez d’autres questions n’hesitez pas.'),
(4, 'c est bon', 'Très bien 👍Si vous avez d’autres questions n’hesitez pas.');



-- =======================
-- buy (id_intent = 5)
-- =======================


INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES

(5, 'comment fonctionne ctexi buy', 'CTEXI Buy vous accompagne de la recherche du produit jusqu’à la livraison : sourcing, achat, contrôle qualité et expédition.'),

(5, 'comment acheter en chine avec vous', 'Vous nous envoyez le produit souhaité, nous recherchons le fournisseur, achetons et livrons le produit.'),

(5, 'quelles sont les étapes d’achat', 'Les étapes sont : demande client, recherche fournisseur, achat, contrôle qualité, expédition et livraison.'),

(5, 'est ce que vous achetez pour moi', 'Oui, nous achetons directement pour vous auprès de fournisseurs en Chine.'),

(5, 'comment passer une commande', 'Vous envoyez les détails du produit, nous nous occupons du reste jusqu’à la livraison.'),

(5, 'combien de temps prend une commande', 'Le délai est généralement de 7 à 45 jours selon le mode de transport.'),

(5, 'est ce que vous vérifiez les produits', 'Oui, nous faisons un contrôle qualité avant l’expédition pour vérifier la conformité.'),

(5, 'que faire si le produit est defectueux', 'Contactez notre service client avec photos, nous analyserons le problème avec le fournisseur.'),

(5, 'que faire si le produit n est pas conforme', 'Contactez-nous immédiatement avec des preuves, nous traitons le problème avec le fournisseur.'),

(5, 'proposez vous une assurance', 'Oui, une assurance transport peut être ajoutée pour couvrir pertes ou dommages.'),

(5, 'comment se passe la livraison', 'La livraison se fait par avion ou bateau selon votre choix et votre budget.'),

(5, 'puis je annuler ma commande', 'Oui, uniquement si la commande n’a pas encore été payée au fournisseur.'),

(5, 'quels produits pouvez vous acheter', 'Nous pouvons acheter presque tous les produits disponibles en Chine selon la légalité.'),

(5, 'comment payer la commande', 'Le paiement se fait après validation du devis et du produit choisi.'),

(5, 'est ce fiable d acheter avec vous', 'Oui, nous sécurisons l’achat, vérifions les produits et réduisons les risques liés aux fournisseurs chinois.');



-- =======================
-- travel (id_intent = 6)
-- =======================


INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES

(6, 'comment obtenir visa chine', 'CTEXI Travel vous accompagne dans l’obtention de votre visa chinois avec les documents, délais et assistance.'),

(6, 'documents visa chine', 'Vous devez fournir un passeport valide, des photos, un formulaire rempli, une preuve d’hébergement et un billet aller-retour.'),

(6, 'delai visa chine', 'Le délai est généralement de 5 à 15 jours ouvrables selon le type de visa.'),

(6, 'reservation billet avion chine', 'Nous pouvons vous aider à réserver vos billets d’avion et hôtels en Chine.'),

(6, 'assistance aeroport chine', 'Oui, une assistance peut être organisée à votre arrivée en Chine.'),

(6, 'modifier reservation', 'Les modifications dépendent des conditions du billet ou de l’hôtel.');



-- =======================
-- academie (id_intent = 7)
-- =======================

INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES

(7, 'formations ctexi', 'CTEXI Académie propose des formations en import-export, achats en Chine, marketing digital et coaching.'),

(7, 'inscription formation', 'Contactez-nous via WhatsApp, email ou formulaire pour vous inscrire.'),

(7, 'formation en ligne', 'Nos formations sont disponibles en ligne et en présentiel.'),

(7, 'certificat formation', 'Oui, un certificat est délivré à la fin de la formation.'),

(7, 'accompagnement formation', 'Certaines formations incluent un accompagnement pratique personnalisé.');


-- =======================
-- cargo (id_intent = 8)
-- =======================

INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES

(8, 'transport chine burkina', 'Nous assurons l’expédition de vos marchandises de la Chine vers le Burkina Faso.'),

(8, 'delai transport', 'Le délai varie selon le mode : 7 à 15 jours par avion et 30 à 45 jours par bateau.'),

(8, 'frais transport', 'Les frais dépendent du poids, volume, mode de transport et destination.'),

(8, 'produits interdits', 'Certains produits sont interdits comme les marchandises dangereuses ou contrefaites.'),

(8, 'frais douane', 'Des frais de douane peuvent s’appliquer selon la nature du produit.'),

(8, 'retard livraison', 'Les retards peuvent être causés par la douane ou le transport.'),

(8, 'service client', 'Notre service client est disponible aux heures ouvrables.');



-- =======================
-- suivi_colis (id_intent = 9)
-- =======================
INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES

(9, 'suivre colis', 'Connectez-vous avec votre numéro pour voir vos colis et leurs statuts.'),

(9, 'statut en transit', 'Votre colis est en cours d’acheminement vers le Burkina Faso.'),

(9, 'colis arrive depot', 'Votre colis est prêt pour retrait ou livraison.'),

(9, 'code colis invalide', 'Vérifiez votre code ou contactez le support.'),

(9, 'plusieurs colis', 'Vous pouvez suivre plusieurs colis simultanément.'),

(9, 'colis endommage', 'Signalez avec preuves pour lancer une procédure d’indemnisation.');



-- =======================
-- contact_agent (id_intent = 10)
-- =======================
INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES

(10, 'contacter agent', 'Je peux vous mettre en relation avec un agent.'),

(10, 'parler a un agent', 'Un agent est disponible via WhatsApp, email ou appel.'),

(10, 'besoin aide humaine', 'Un agent peut vous assister directement.'),

(10, 'support', 'Vous pouvez contacter un agent pour un support personnalisé.');



-- =======================
-- service_info (id_intent = 11)
-- =======================
INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES

(11, 'services ctexi', 'Nous proposons Buy, Cargo, Pay, Travel et Académie.'),

(11, 'liste services', 'Choisissez un service pour voir les détails.'),

(11, 'vos services', 'Découvrez nos services adaptés à vos besoins.'),

(11, 'offres ctexi', 'Nous avons plusieurs offres selon votre besoin.');


-- =======================
-- taux_change (id_intent = 12)
-- =======================


INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES

(12, 'delai transfert', 'Un transfert prend entre 24 et 72 heures.'),

(12, 'taux change rmb fcfa', 'Le taux du jour est disponible dans l’application CTEXI Pay.'),

(12, 'calcul paiement', 'Entrez le montant en RMB pour obtenir le total en FCFA.'),

(12, 'demande paiement', 'Cliquez pour contacter CTEXI Pay via WhatsApp.'),

(12, 'paiement securise', 'Toutes les transactions sont sécurisées.'),

(12, 'preuve paiement', 'Une preuve est fournie après chaque transaction.');

