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

SELECT * FROM chatbot.intention;

-- Supprime toutes les lignes et réinitialise les séquences
TRUNCATE TABLE chatbot.faq RESTART IDENTITY CASCADE;
TRUNCATE TABLE chatbot.intention RESTART IDENTITY CASCADE;


-- Supprimer la colonne embedding
ALTER TABLE chatbot.faq DROP COLUMN embedding;
ALTER TABLE chatbot.intention DROP COLUMN embedding;

ALTER TABLE chatbot.intention 
ADD COLUMN embedding vector(384);


SELECT * FROM chatbot.intention;

SELECT * FROM chatbot.faq;

-------------------------------Insertion des donnees dans les tables faq et intention----------------------------------





------------------------------------------Table Intention---------------------------------------------------------------



---------------------------------------------salutation ==> 1
INSERT INTO chatbot.intention(nom, type_intent, descriptions)
VALUES
(
'salutation',
'social',
'Intentions de salutation et interaction sociale initiale. L’utilisateur veut dire bonjour, commencer une conversation ou engager un contact poli. 
Exemples de phrases utilisateur : "salut", "bonjour", "bonsoir", "ça va ?", "cc", "coucou", "hello", "yo", "ça dit quoi"'
);


----------------------------------------------aurevoir ==>2
INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'au_revoir',
'social',
'Intentions de fin de conversation. L’utilisateur veut quitter la discussion ou dire au revoir. 
Exemples de phrases utilisateur : "au revoir", "bye", "a plus", "je pars", "bonne journée", "on se capte", "à bientôt", "bonne soirée"'

);


----------------------------------------------remerciement ==>3

INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'remerciement',
'social',
'Intentions où l’utilisateur exprime sa gratitude ou remercie après une aide. 
Exemples de phrases utilisateur : "merci", "merci beaucoup", "grand merci", "thanks", "c’est gentil", "merci bien", "je vous remercie"'
);


----------------------------------------------validation ==>4
INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'validation',
'social',
'Intentions où l’utilisateur confirme ou valide une information. 
Exemples de phrases utilisateur : "ok", "d’accord", "ça marche", "c’est bon", "cool", "parfait", "ok merci", "validé"'

);




----------------------------------------------buy(achat) ==>5

INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'faq_buy',
'information',

'
comment fonctionne ctexi buy
c’est quoi votre service achat
explique moi votre service achat chine
comment vous travaillez pour acheter en chine

comment acheter en chine
je veux acheter en chine
comment faire pour acheter un produit en chine
je veux acheter un produit en chine avec vous
comment commander produit chine

etapes achat chine
les etapes pour acheter
comment se passe un achat chez vous
processus achat chine comment ca marche

vous pouvez acheter pour moi
est ce que vous achetez pour moi
je veux que vous achetez pour moi
vous pouvez commander pour moi en chine

comment passer une commande
comment faire une commande
je veux faire une commande chez vous
comment commander avec vous
comment envoyer ma commande

commande chine dure combien de temps
delai commande chine
combien de jours pour recevoir commande chine
temps livraison commande chine

vous verifiez les produits
controle qualite produit chine
est ce que vous controler les produits
verification produit avant envoi

produit defectueux que faire
si produit gate que faire
si produit probleme que faire
produit non conforme solution
j’ai recu mauvais produit

vous avez assurance
assurance transport produit
est ce que colis est assure
assurance commande chine

livraison comment ca se passe
livraison chine burkina comment faire
comment vous livrez les produits
transport produit chine comment ca marche
livraison avion ou bateau

annuler commande possible
je peux annuler commande
comment annuler une commande
annulation commande chine

quel produit vous pouvez acheter
vous pouvez acheter quoi en chine
type de produit chine
est ce que vous achetez tout type produit

comment payer commande
paiement commande comment faire
comment je paie commande chine
mode de paiement commande

est ce fiable d’acheter avec vous
est ce que je peux vous faire confiance
achat chine avec vous c’est sur
est ce que votre service est fiable
vous etes fiable pour achat chine

Synonymes :
acheter, achat, commande, produit, fournisseur, chine, livraison, transport, payer, paiement, assurance, controle, qualite, verifier
'
);


-------------------------------------------travel  ==>6

INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'faq_travel',
'information',

'
je veux voyager en chine
comment aller en chine
je veux partir en chine
comment faire pour aller en chine
procedure voyage chine

comment obtenir visa chine
visa chine comment faire
comment faire visa chine
je veux visa chine
demande visa chine comment faire

documents visa chine
quels papiers pour visa chine
dossier visa chine
pieces pour visa chine
quels documents fournir visa chine

visa chine dure combien de temps
delai visa chine
visa chine prend combien de jours
temps traitement visa chine

billet avion chine comment faire
je veux billet avion chine
reservation billet chine
prix billet avion chine
acheter billet chine

hotel chine comment reserver
je veux hotel en chine
ou dormir en chine
logement chine comment ca marche
hebergement chine
je vais loger ou en chine

assistance aeroport chine
accueil aeroport chine
quelquun peut me recuperer aeroport chine
service accueil chine

modifier reservation chine
changer billet avion chine
annuler reservation chine
modifier hotel chine

Synonymes :
visa, billet, avion, hotel, logement, hebergement, dormir, loger, aeroport, reservation, voyage, chine
'
);



-----------------------------------------academie ==>7

INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'faq_academie',
'information',

'
quelles formations vous proposez
vous faites quelles formations
c’est quoi vos formations
je veux connaitre vos formations
vous formez dans quoi


je veux apprend import export
apprendre le commerce international
je veux me lancer dans le business
formation business chine burkina
je veux devenir importateur
apprendre a importer depuis la chine
je veux lancer mon business import

je veux me former chez vous
je veux apprendre import export
je veux apprendre achat chine
je veux apprendre business chine
je veux faire une formation chez vous

comment s’inscrire a une formation
comment faire inscription formation
je veux m’inscrire formation
inscription formation comment ca marche
je fais comment pour m’inscrire

formation en ligne ou presentiel
est ce que formation est en ligne
je peux suivre a distance
vous faites cours en ligne
formation se passe comment

formation dure combien de temps
duree formation combien de jours
combien de temps pour finir formation
formation prend combien de temps

formation commence quand
date debut formation
prochaine session formation quand

formation coute combien
prix formation combien
tarif formation c’est combien
je dois payer combien pour formation

est ce que vous donnez certificat
il y a certificat apres formation
je vais avoir attestation
diplome formation disponible

vous accompagnez les apprenants
il y a suivi apres formation
est ce que vous aidez apres formation
accompagnement apres formation comment ca marche
vous suivez les etudiants

Synonymes :
formation, apprendre, cours, coaching, academie, etudier, certificat, attestation, inscription, apprendre, formation en ligne
'
);


--------------------------------------cargo  ==>8

INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'faq_cargo',
'information',

'
envoyer colis chine burkina
comment envoyer marchandise chine burkina
transport chine burkina comment faire
je veux envoyer colis depuis chine
faire venir produit chine burkina
livraison chine burkina

transport dure combien de temps
delai livraison chine burkina
colis arrive en combien de jours
temps transport chine burkina
livraison prend combien de temps

transport coute combien
prix transport chine burkina
frais expedition chine
je vais payer combien transport
tarif envoi colis chine

produits interdits chine
quels produits sont interdits
je peux envoyer quel produit
produit autorise ou non chine

frais douane comment ca marche
douane burkina colis chine
est ce que je dois payer douane
taxe douane colis chine

colis en retard pourquoi
mon colis tarde a arriver
retard livraison chine
pourquoi colis bloque

colis en transit ca veut dire quoi
mon colis est en route
colis en chemin chine burkina
statut colis transit signification

code colis ne marche pas
code suivi invalide
je n’arrive pas a suivre colis
probleme suivi colis

suivre plusieurs colis
j’ai plusieurs colis comment faire
suivi plusieurs colis possible

colis gate que faire
colis abime que faire
colis casse solution
produit endommage livraison

Synonymes :
colis, marchandise, transport, livraison, expedition, chine, burkina, douane, frais, prix, delai, transit, suivi
'
);

-----------------------------------suivi_colis ==>9

INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'suivi_colis',
'operation',
'Suivi de colis et vérification de statut d’expédition.

Exemples utilisateur :
"ou est mon colis"
"je veux suivre mon colis"
"suivi colis"
"verifier mon colis"
"mon colis est ou"
"je veux voir mon colis"
"tracking colis"
"suivre commande"
"statut colis"
"localiser mon colis"
"mon colis est arrive ou"
"je veux savoir ou se trouve mon colis"
"suivi expedition"
"tracking commande chine"
"voir statut livraison"
"mon colis est en cours ou"
"colis tracking"
"je veux verifier livraison"
"suivre livraison chine"
"ou en est ma commande"
'
);




----------------------------------contact_agent ==> 10
INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'contact_agent',
'operation',
'Demande de contact avec un agent humain ou assistance directe.

Exemples utilisateur :
"je veux parler a un agent"
"je veux parler a quelqu’un"
"contact service client"
"je veux un conseiller"
"parler a un humain"
"support client"
"besoin d’aide"
"aidez moi"
"je ne comprends pas"
"expliquez moi mieux"
"je veux plus d’explication"
"votre reponse ne m’aide pas"
"je ne suis pas satisfait"
"je veux contacter le support"
"comment vous contacter"
"je veux votre whatsapp"
"donne moi votre numero"
"je veux appeler un agent"
"je veux discuter avec quelqu’un"
"assistance urgente"
"aide humaine"
'
);

--------------------------------service_info ==> 11
INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'service_info',
'operation',
'Demande d’information sur les services CTEXI et sélection interactive d’un service.

Exemples utilisateur :
"quels sont vos services"
"vous faites quoi"
"je veux connaitre vos services"
"c’est quoi vos services"
"vous proposez quoi"
"je veux voir vos services"
"explique vos services"
"vos offres"
"que faites-vous"
"je peux faire quoi avec vous"
"je veux choisir un service"
"donne moi vos services"
"liste des services"
"présente tes services"
"services disponibles"
"CTEXI c’est quoi"
'
);



-----------------------------------taux_de_change ==> 12

INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES
(
'taux_change',
'operation',
'Gestion des paiements internationaux, conversion de devise RMB (yuan) vers FCFA, délais de transfert, sécurité des transactions et demande de paiement via CTEXI Pay.

Exemples utilisateur :
"combien de temps prend un transfert"
"un transfert dure combien de jours"
"delai paiement chine"
"je vais attendre combien de temps pour mon paiement"
"comment calculer le paiement"
"convertir yuan en fcfa"
"je veux savoir combien je vais payer"
"prix en fcfa"
"taux de change chine burkina"
"rmb en fcfa"
"comment faire un paiement"
"payer fournisseur chine"
"envoyer de l’argent en chine"
"je veux payer en chine"
"comment payer un fournisseur chinois"
"vous pouvez payer pour moi"
"paiement chine sécurisé"
"est ce fiable de payer avec vous"
"preuve de paiement"
"reçu de paiement"
"justificatif paiement"
"transfert d’argent chine burkina"
"ctexi pay comment ça marche"
"comment fonctionne le paiement international"
'
);





SELECT * FROM chatbot.intention;
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
(3, 'c’est gentil', 'Merci à vous 😊 Si vous avez d’autres questions n’hesitez pas.');



-- =======================
-- validation (id_intent = 4)
-- =======================

INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES

(4, 'ok', 'Parfait 👍 Avez-vous d’autres questions ?'),
(4, 'd’accord', 'Très bien 👍 N’hésitez pas si besoin !'),
(4, 'cool', 'Super 😄 Autres choses a me demander ?'),
(4, 'ca marche', 'Parfait 👍Si vous avez d’autres questions n’hesitez pas.'),
(4, 'c’est bon', 'Très bien 👍Si vous avez d’autres questions n’hesitez pas.');



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


(5, 'on fait comment si le produit est defectueux', 'Contactez notre service client avec photos, nous analyserons le problème avec le fournisseur.'),
(5, 'que faire si le produit n’est pas conforme', 'Contactez notre service client avec photos, nous analyserons le problème avec le fournisseur.'),
(5, 'que faire si le produit a un probleme', 'Contactez notre service client avec photos, nous analyserons le problème avec le fournisseur.'),
(5, 'si le produit a un probleme', 'Contactez notre service client avec photos, nous analyserons le problème avec le fournisseur.'),
(5, 'je fais comment si le produit n’est pas identique', 'Contactez notre service client avec photos, nous analyserons le problème avec le fournisseur.'),
(5, 'comment on va faire si le produit n’est pas conforme', 'Contactez-nous immédiatement avec des preuves, nous traitons le problème avec le fournisseur.'),


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
(5, 'puis je annuler ma commande', 'Oui, uniquement si la commande n’a pas encore été payée au fournisseur.'),
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

(8, 'est ce que vous pouvez envoyer mes colis de chine au burkina', 'Nous assurons l’expédition de vos marchandises de la Chine vers le Burkina Faso.'),
(8, 'comment envoyer de la marchandise de la chine vers le burkina', 'Nous assurons l’expédition de vos marchandises de la Chine vers le Burkina Faso.'),
(8, 'vous faites transport de la chine vers le burkina', 'Nous assurons l’expédition de vos marchandises de la Chine vers le Burkina Faso.'),
(8, 'je veux faire venir des produits de chine', 'Nous assurons l’expédition de vos marchandises de la Chine vers le Burkina Faso.'),
(8, 'vous pouvez livrer mes colis depuis la chine', 'Nous assurons l’expédition de vos marchandises de la Chine vers le Burkina Faso.'),

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
-- suivi_colis (id_intent = 9)
-- =======================

INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot)
VALUES
(9, 'suivre colis', 'Veuillez entrer votre code colis pour consulter son statut.');


-- =======================
-- contact_agent (id_intent = 10)
-- =======================
INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot)
VALUES
(10, 'contact agent', 'Je peux vous mettre en relation avec un agent. Veuillez choisir : WhatsApp, appel ou email.');



-- =======================
-- service_info (id_intent = 11)
-- =======================

INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES

(11, 'service', 'Nous proposons plusieurs services : achat en Chine (Buy), transport de colis (Cargo), paiement international (Pay), voyages (Travel) et formations (Académie).');


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
SELECT * FROM chatbot.intention;




TRUNCATE TABLE chatbot.faq RESTART IDENTITY;