-- database: :memory:
-- Active: 1772149791498@@127.0.0.1@5435@ctexi_db@public498@@127.0.0.1@5435@ctexi_db@public498@@127.0.0.1@5435@ctexi_db498@@127.0.0.1@5435@ctexi_db069@@127.0.0.1@5435@ctexi_db069@@127.0.0.1@5435@ctexi_db069@@127.0.0.1@5435@ctexi_db069@@127.0.0.1@5435@ctexi_db069@@127.0.0.1@5435@ctexi_database402@@127.0.0.1@5433@ctexi_db@chatbot507@@127.0.0.1@5433@ctexi_db507@@127.0.0.1@5433@ctexi_db507@@127.0.0.1@5433@ctexi_db507@@127.0.0.1@5433@ctexi_db507@@127.0.0.1@5433@ctexi_db791@@127.0.0.1@5433@ctexi_db@chatbot791@@127.0.0.1@5433@ctexi_db527@@127.0.0.1@5433@ctexi_db510@@127.0.0.1@5433@ctexi_db

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



--Table agents
DROP TABLE auth.agents CASCADE;

CREATE TABLE auth.agents(
    id_agent SERIAL PRIMARY KEY,
    id_user INTEGER REFERENCES auth.users(id_user) ON DELETE CASCADE,
    services VARCHAR(100) NOT NULL, 
    whatsapp VARCHAR(20) NOT NULL,
    telephone VARCHAR(20) NOT NULL,
    email VARCHAR(50) NOT NULL,
    actif BOOLEAN DEFAULT TRUE,
    dates TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

----------------------------------NSERTION DES AGENTS EXEMPLE--------------------------------------

TRUNCATE TABLE auth.agents RESTART IDENTITY;

INSERT INTO auth.agents(id_user, services, whatsapp, telephone, email)
VALUES
(1, 'buy', '22674381094', '+22669090991', 'yakfismokonzi@gmail.com'),
(1, 'cargo', '22674381094', '+22669090991', 'yakfismokonzi@gmail.com'),
(1, 'academie', '22674381094', '+22669090991', 'yakfismokonzi@gmail.com'),
(1, 'travel', '22674381094', '+22669090991', 'yakfismokonzi@gmail.com')





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


SELECT * FROM chatbot.faq;



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
    nom_service VARCHAR (100),
    descriptions TEXT,
    menu JSONB,
    icone VARCHAR(255)
);


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
    statut VARCHAR(50),
    type_colis VARCHAR(50),
    modes VARCHAR(50)
);



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


----------------------------------------------Suppression et mise a jour----------------------------------


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






--Ajout d'embeding dans intention
SET search_path TO chatbot, public;



-- Supprime toutes les lignes et réinitialise les séquences
TRUNCATE TABLE chatbot.faq RESTART IDENTITY CASCADE;
TRUNCATE TABLE chatbot.intention RESTART IDENTITY CASCADE;


-- Supprimer la colonne embedding
ALTER TABLE chatbot.faq DROP COLUMN embedding;
ALTER TABLE chatbot.intention DROP COLUMN embedding;

-- Recréer la colonne embedding avec 768 dimensions
ALTER TABLE chatbot.faq ADD COLUMN embedding vector(768);
ALTER TABLE chatbot.intention ADD COLUMN embedding vector(768);












-------------------------------Insertion des donnees dans les tables faq----------------------------------

-- =======================
-- salutation (id_intent = 1)
-- =======================

INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES

(1, 'salut frere', 'Bonjour 👋 Comment puis-je vous aider aujourd''hui ?'),
(1, 'salut boss', 'Bonjour 👋 Comment puis-je vous aider aujourd''hui ?'),
(1, 'slt', 'Bonjour 👋 Comment puis-je vous aider aujourd''hui ?'),
(1, 'cc', 'Bonjour 👋 Comment puis-je vous aider aujourd''hui ?'),
(1, 'coucou', 'Bonjour 👋 Comment puis-je vous aider aujourd''hui ?'),
(1, 'yo', 'Bonjour 👋 Comment puis-je vous aider aujourd''hui ?'),

(1, 'bonjour monsieur', 'Bonjour 👋 Comment puis-je vous aider aujourd''hui ?'),
(1, 'bonjour madame', 'Bonjour 👋 Comment puis-je vous aider aujourd''hui ?'),
(1, 'bonjour ctexi', 'Bonjour 👋 Comment puis-je vous aider aujourd''hui ?'),

(1, 'salut ca va', 'Bonjour 👋 Je vais très bien, merci ! Comment puis-je vous aider ?'),
(1, 'bonjour ca va', 'Bonjour 👋 Je vais très bien, merci ! Comment puis-je vous aider ?'),
(1, 'ca va', 'Je vais très bien 😊 Comment puis-je vous aider aujourd''hui ?'),

(1, 'bonsoir ca va', 'Bonsoir 👋 Je vais très bien, merci ! Comment puis-je vous aider ?'),
(1, 'hello ctexi', 'Hello 👋 Comment puis-je vous aider ?'),
(1, 'hi there', 'Hello 👋 Comment puis-je vous aider ?'),

(1, 'salutations', 'Bonjour 👋 Comment puis-je vous aider aujourd''hui ?'),
(1, 'bonjour equipe ctexi', 'Bonjour 👋 Comment puis-je vous aider aujourd''hui ?'),
(1, 'salut l equipe', 'Bonjour 👋 Comment puis-je vous aider aujourd''hui ?');



clea
INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES
(1, 'salut', 'Bonjour ! Comment puis-je vous aider aujourd''hui ?'),
(1, 'bonjour', 'Bonjour ! Que puis-je faire pour vous ?'),
(1, 'bonsoir', 'Bonsoir ! Comment puis-je vous aider ?'),
(1, 'hello', 'Hello 👋 Comment puis-je vous aider ?'),
(1, 'hi', 'Hi ! Que puis-je faire pour vous aujourd''hui ?'),
(1, 'hey', 'Hey ! Ravi de vous voir !');

-- =======================
-- au_revoir (id_intent = 2)
-- =======================
INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES
(2, 'au revoir', 'Au revoir ! À bientôt.'),
(2, 'bye', 'Bye ! Passez une excellente journée !'),
(2, 'a+', 'À la prochaine !');

-- =======================
-- remerciement (id_intent = 3)
-- =======================
INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES
(3, 'merci', 'Avec plaisir ! N''hésitez pas si vous avez d''autres questions.'),
(3, 'merci beaucoup', 'Je vous en prie !');

-- ==========================
-- validation (id_intent = 4)
-- ==========================
INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES
(4, 'ok', 'Bien. Avez-vous d''autres questions ?'),
(4, 'd''accord', 'Super !!! Si vous avez d''autres choses à me demander, n''hésitez pas !'),
(4, 'cool', 'Super !!! Si vous avez d''autres choses à me demander, n''hésitez pas !'),
(4, 'yfy', 'Bien reçu ! Avez-vous d''autres questions ?');

-- =======================
-- faq_buy (id_intent = 5)
-- =======================
INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES
(5, 'comment fonctionne votre service ctexi buy ?', 'CTEXI Buy vous aide à acheter des produits en Chine. Vous nous fournissez les caractéristiques du produit, nous recherchons les fournisseurs fiables, achetons, vérifions la qualité, conditionnons et expédions le produit vers vous.'),
(5, 'avantages ctexi buy ?', 'Les avantages incluent la sécurité, notre expertise en Chine, la réduction des risques et l''assurance de conformité avec vos demandes.'),
(5, 'combien de temps pour une commande ?', 'Le délai dépend du fournisseur et du mode de transport choisi. En moyenne : 3 à 7 jours pour l''achat et vérification, puis 7 à 45 jours pour la livraison selon transport aérien ou maritime.'),
(5, 'verification avant expédition possible ?', 'Oui, nous effectuons un contrôle qualité avant l''expédition pour vérifier la conformité des produits avec votre commande.'),
(5, 'produit non conforme que faire ?', 'Contactez immédiatement notre service client avec photos et description du problème. Nous analyserons la situation avec le fournisseur.'),
(5, 'assurance marchandise ?', 'Oui, une assurance transport peut être ajoutée pour couvrir les pertes ou dommages pendant l''expédition.'),
(5, 'je veux annuler ma commande', 'L''annulation est possible uniquement si la commande n''a pas encore été payée au fournisseur.');

-- =======================
-- faq_travel (id_intent = 6)
-- =======================
INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES
(6, 'comment obtenir visa chine ?', 'CTEXI Travel vous guide pour obtenir le visa chinois. Nous fournissons la liste des documents requis, les délais et vous aidons à remplir votre demande.'),
(6, 'reservation billet ou hotel ?', 'Oui, le service permet la réservation de billets d''avion et d''hôtels en Chine. Contactez directement un agent CTEXI.'),
(6, 'documents visa ?', 'Passeport valide, photos, formulaire rempli, preuve d''hébergement et billet aller-retour.'),
(6, 'delais obtention visa ?', 'Le délai varie selon le type de visa, généralement entre 5 et 15 jours ouvrables.'),
(6, 'assistance aeroport ?', 'Oui, une assistance peut être organisée selon votre demande.'),
(6, 'modification reservation ?', 'Les modifications dépendent des conditions du billet ou de l''hôtel réservé.');

-- =======================
-- faq_academie (id_intent = 7)
-- =======================
INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES
(7, 'formations proposees ?', 'CTEXI Académie propose des formations sur les achats en ligne en Chine, l''import-export, le marketing digital et du coaching.'),
(7, 'formation en ligne ou presentiel ?', 'Les formations peuvent être en ligne ou en présentiel selon le programme choisi.'),
(7, 'comment m inscrire ?', 'Cliquez sur ''S''inscrire / Demander infos'' et contactez-nous via WhatsApp, email ou formulaire pour réserver votre place.'),
(7, 'certificat formation ?', 'Oui, un certificat de participation peut être délivré à la fin de la formation.'),
(7, 'accompagnement pratique ?', 'Certaines formations incluent des études de cas et un accompagnement personnalisé.');

-- =======================
-- faq_cargo (id_intent = 8)
-- =======================
INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES
(8, 'quels services ctexi ?', 'CTEXI propose Buy (achat en Chine), Cargo (expédition), Pay (transfert d''argent), Travel (voyage) et Académie (formation et coaching).'),
(8, 'siege ctexi ?', 'Le siège est situé au Burkina Faso avec une représentation en Chine.'),
(8, 'produits interdits import ?', 'Les produits interdits incluent les marchandises dangereuses, contrefaçons et articles réglementés selon la législation locale.'),
(8, 'frais douane ?', 'Oui, des droits de douane peuvent s''appliquer selon la nature et la valeur des marchandises.'),
(8, 'responsable retard ?', 'Les délais peuvent être affectés par des facteurs externes (douane, transport). Nous faisons le maximum pour minimiser les retards.'),
(8, 'service client 24h ?', 'Le service client est disponible aux heures ouvrables. Vous pouvez laisser un message à tout moment.');

-- =======================
-- suivi_colis (id_intent = 9)
-- =======================
INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES
(9, 'cmt suiv mon colis ?', 'Connectez-vous avec votre numéro de téléphone pour voir tous vos colis et leurs statuts.'),
(9, 'je veu annuler ma cmd', 'L''annulation est possible uniquement si la commande n''a pas encore été payée au fournisseur.'),
(9, 'comment suivre mon colis ?', 'Connectez-vous avec votre numéro de téléphone. Tous les colis enregistrés sous ce numéro apparaissent avec leur statut actuel, mode de transport et dernière mise à jour.'),
(9, 'que signifie le statut en transit ?', 'Cela signifie que votre colis a quitté l''entrepôt et est en route vers le Burkina Faso.'),
(9, 'statut arrivé au dépôt ?', 'Votre colis est arrivé dans notre entrepôt local et est prêt pour retrait ou livraison.'),
(9, 'code colis invalide', 'Vérifiez le code et assurez-vous qu''il correspond à un colis enregistré. En cas de problème, contactez notre service client via WhatsApp ou mail.'),
(9, 'plusieurs colis suivi ?', 'Vous pouvez suivre plusieurs colis en même temps, aucun nombre limité.'),
(9, 'changement numero telephone', 'Vous pouvez ré-ajouter le code, le colis sera automatiquement rattaché à votre compte.'),
(9, 'delais fret aerien ?', 'Le fret aérien prend généralement entre 7 et 15 jours selon la destination.'),
(9, 'delais fret maritime ?', 'Le fret maritime prend en moyenne entre 30 et 45 jours selon le port de départ.'),
(9, 'frais transport calcul ?', 'Les frais sont calculés selon le poids volumétrique, le mode de transport et la destination finale.'),
(9, 'colis endommagé que faire ?', 'Signalez immédiatement le dommage avec preuves visuelles. Si une assurance a été souscrite, une procédure d''indemnisation sera lancée.');

-- =======================
-- taux_change (id_intent = 10)
-- =======================
INSERT INTO chatbot.faq (id_intent, message_user, reponse_bot) VALUES
(10, 'combien le transfert', 'Un transfert prend généralement entre 24 et 72 heures selon la banque du bénéficiaire.'),
(10, 'taux change du jour', 'Le taux indicatif du jour est affiché dans l''application CTEXI Pay. Exemple : 1 RMB = 85 FCFA.'),
(10, 'simulation paiement', 'Entrez le montant en RMB, l''application calcule automatiquement le total à payer en FCFA.'),
(10, 'demande paiement', 'Cliquez sur "Valider et contacter CTEXI Pay" pour envoyer un message WhatsApp pré-rempli avec vos informations.'),
(10, 'transaction securisee ?', 'Oui, toutes les transactions sont traitées de manière sécurisée et confidentielle.'),
(10, 'preuve paiement ?', 'Oui, une confirmation ou preuve de transaction est fournie après chaque paiement effectué.'),
(10, 'montant minimum transfert ?', 'Un montant minimum peut être requis selon la réglementation en vigueur.'),
(10, 'delai transfert ?', 'Un transfert prend généralement entre 24 et 72 heures selon la banque du bénéficiaire.');



--FAQ

INSERT INTO chatbot.faq (message_user, reponse_bot) VALUES
('salut','Bonjour ! Comment puis-je vous aider aujourd''hui ?'),
('bonjour','Bonjour ! Que puis-je faire pour vous ?'),
('bonsoir','Bonsoir ! Comment puis-je vous aider ?'),
('merci','Avec plaisir ! N''hésitez pas si vous avez d''autres questions.'),
('merci beaucoup','Je vous en prie !'),
('au revoir','Au revoir ! À bientôt.'),
('a+','À la prochaine !'),
('ça va ?','Tout va bien, merci ! Et vous ?'),
('comment ça va ?','Je vais bien, merci ! Que puis-je faire pour vous ?'),

('cmt suiv mon colis ?','Connectez-vous avec votre numéro de téléphone pour voir tous vos colis et leurs statuts.'),
('je veu annuler ma cmd','L''annulation est possible uniquement si la commande n''a pas encore été payée au fournisseur.'),
('combien le transfert','Un transfert prend généralement entre 24 et 72 heures selon la banque du bénéficiaire.'),
('visa chine cmt faire ?','CTEXI Travel vous guide pour obtenir le visa chinois. Nous fournissons la liste des documents requis, les délais et vous aidons à remplir votre demande.'),

('comment creer un compte ?','Cliquez sur Inscription, remplissez vos informations personnelles et validez votre compte.'),
('je veux m inscrire','Pour créer un compte, cliquez sur Inscription et suivez les étapes.'),
('j ai oublié mon mot de passe','Cliquez sur Mot de passe oublié et suivez les instructions pour réinitialiser votre accès.'),
('comment supprimer mon compte','Contactez le service client pour faire une demande de suppression de compte.'),
('comment modifier mes infos','Accédez à votre profil dans l''application et mettez à jour vos informations.'),
('mon compte est sécurisé ?','Oui, toutes les données et informations personnelles sont protégées et sécurisées.'),
('je veux changer mon mot de passe','Allez dans votre profil et sélectionnez Modifier le mot de passe.'),

('comment fonctionne ctexi buy ?','CTEXI Buy vous aide à acheter des produits en Chine. Vous nous fournissez les caractéristiques du produit, nous recherchons les fournisseurs fiables, achetons, vérifions la qualité, conditionnons et expédions le produit vers vous.'),
('avantages ctexi buy ?','Les avantages incluent la sécurité, notre expertise en Chine, la réduction des risques et l''assurance de conformité avec vos demandes.'),
('combien de temps pour une commande ?','Le délai dépend du fournisseur et du mode de transport choisi. En moyenne : 3 à 7 jours pour l''achat et vérification, puis 7 à 45 jours pour la livraison selon transport aérien ou maritime.'),
('je veux annuler ma commande','L''annulation est possible uniquement si la commande n''a pas encore été payée au fournisseur.'),
('verification avant expédition possible ?','Oui, nous effectuons un contrôle qualité avant l''expédition pour vérifier la conformité des produits avec votre commande.'),
('produit non conforme que faire ?','Contactez immédiatement notre service client avec photos et description du problème. Nous analyserons la situation avec le fournisseur.'),
('assurance marchandise ?','Oui, une assurance transport peut être ajoutée pour couvrir les pertes ou dommages pendant l''expédition.'),

('comment suivre mon colis ?','Connectez-vous avec votre numéro de téléphone. Tous les colis enregistrés sous ce numéro apparaissent avec leur statut actuel, mode de transport et dernière mise à jour.'),
('que signifie le statut en transit ?','Cela signifie que votre colis a quitté l''entrepôt et est en route vers le Burkina Faso.'),
('statut arrivé au dépôt ?','Votre colis est arrivé dans notre entrepôt local et est prêt pour retrait ou livraison.'),
('code colis invalide','Vérifiez le code et assurez-vous qu''il correspond à un colis enregistré. En cas de problème, contactez notre service client via WhatsApp ou mail.'),
('plusieurs colis suivi ?','Vous pouvez suivre plusieurs colis en même temps, aucun nombre limité.'),
('changement numero telephone','Vous pouvez ré-ajouter le code, le colis sera automatiquement rattaché à votre compte.'),
('delais fret aerien ?','Le fret aérien prend généralement entre 7 et 15 jours selon la destination.'),
('delais fret maritime ?','Le fret maritime prend en moyenne entre 30 et 45 jours selon le port de départ.'),
('frais transport calcul ?','Les frais sont calculés selon le poids volumétrique, le mode de transport et la destination finale.'),
('colis endommagé que faire ?','Signalez immédiatement le dommage avec preuves visuelles. Si une assurance a été souscrite, une procédure d''indemnisation sera lancée.'),

('comment fonctionne ctexi pay ?','CTEXI Pay permet de connaître le taux de change du jour et de déclencher une demande de paiement via WhatsApp.'),
('taux change du jour','Le taux indicatif du jour est affiché dans l''application CTEXI Pay. Exemple : 1 RMB = 85 FCFA.'),
('simulation paiement','Entrez le montant en RMB, l''application calcule automatiquement le total à payer en FCFA.'),
('demande paiement','Cliquez sur "Valider et contacter CTEXI Pay" pour envoyer un message WhatsApp pré-rempli avec vos informations.'),
('transaction securisee ?','Oui, toutes les transactions sont traitées de manière sécurisée et confidentielle.'),
('preuve paiement ?','Oui, une confirmation ou preuve de transaction est fournie après chaque paiement effectué.'),
('montant minimum transfert ?','Un montant minimum peut être requis selon la réglementation en vigueur.'),
('delai transfert ?','Un transfert prend généralement entre 24 et 72 heures selon la banque du bénéficiaire.'),

('comment obtenir visa chine ?','CTEXI Travel vous guide pour obtenir le visa chinois. Nous fournissons la liste des documents requis, les délais et vous aidons à remplir votre demande.'),
('reservation billet ou hotel ?','Oui, le service permet la réservation de billets d''avion et d''hôtels en Chine. Contactez directement un agent CTEXI.'),
('documents visa ?','Passeport valide, photos, formulaire rempli, preuve d''hébergement et billet aller-retour.'),
('delais obtention visa ?','Le délai varie selon le type de visa, généralement entre 5 et 15 jours ouvrables.'),
('assistance aeroport ?','Oui, une assistance peut être organisée selon votre demande.'),
('modification reservation ?','Les modifications dépendent des conditions du billet ou de l''hôtel réservé.'),

('formations proposees ?','CTEXI Académie propose des formations sur les achats en ligne en Chine, l''import-export, le marketing digital et du coaching.'),
('formation en ligne ou presentiel ?','Les formations peuvent être en ligne ou en présentiel selon le programme choisi.'),
('comment m inscrire ?','Cliquez sur "S''inscrire / Demander infos" et contactez-nous via WhatsApp, email ou formulaire pour réserver votre place.'),
('certificat formation ?','Oui, un certificat de participation peut être délivré à la fin de la formation.'),
('accompagnement pratique ?','Certaines formations incluent des études de cas et un accompagnement personnalisé.'),

('quels services ctexi ?','CTEXI propose Buy (achat en Chine), Cargo (expédition), Pay (transfert d''argent), Travel (voyage) et Académie (formation et coaching).'),
('siege ctexi ?','Le siège est situé au Burkina Faso avec une représentation en Chine.'),
('produits interdits import ?','Les produits interdits incluent les marchandises dangereuses, contrefaçons et articles réglementés selon la législation locale.'),
('frais douane ?','Oui, des droits de douane peuvent s''appliquer selon la nature et la valeur des marchandises.'),
('responsable retard ?','Les délais peuvent être affectés par des facteurs externes (douane, transport). Nous faisons le maximum pour minimiser les retards.'),
('service client 24h ?','Le service client est disponible aux heures ouvrables. Vous pouvez laisser un message à tout moment.');



INSERT INTO chatbot.intention (nom, type_intent, descriptions)
VALUES

(
'salutation',
'social',
'
salut
salut mec
coucou
yo
hello
bonjour
bonjour monsieur
bonjour madame
je vous salue
permettez moi de vous adresser mes salutations

'
),

(
'au_revoir',
'social',
'
au revoir
bye
a plus
a bientot
bonne journee
bonne soiree
je vous souhaite une excellente journee
au plaisir de vous revoir
a la prochaine occasion
je vous remercie et vous dis au revoir
'
),

(
'remerciement',
'social',
'
merci
merci beaucoup
merci mec
grand merci
thanks
je vous remercie
je vous remercie infiniment
je vous suis reconnaissant
mille mercis
avec toute ma gratitude
'
),

(
'validation',
'social',
'
ok
d accord
cool
ca marche
c est bon
tres bien
cela me convient parfaitement
c est parfait
je confirme
entendu c est valide
'
),

(
'faq_buy',
'information',
'
je veux acheter en chine
comment acheter en chine
je veux commander un produit
vous pouvez acheter pour moi
c est quoi ctexi buy
expliquez le fonctionnement du service buy
quelles sont les etapes d achat
comment passer commande
quels sont les avantages de votre service d achat
est ce que vous verifiez les produits avant expedition
'
),

(
'faq_travel',
'information',
'
je veux voyager en chine
comment obtenir un visa
reservation billet avion
reservation hotel chine
aidez moi pour le visa
quels sont les documents necessaires pour le visa
quel est le delai d obtention du visa
proposez vous une assistance aeroport
comment modifier ma reservation
je souhaite obtenir des informations pour voyager
'
),

(
'faq_academie',
'information',
'
je veux suivre une formation
formations proposees
formation import export
formation marketing digital
coaching ctexi
comment m inscrire a la formation
formation en ligne disponible
formation presentielle
certificat de participation
proposez vous un accompagnement pratique
'
),

(
'faq_cargo',
'information',
'
quels sont vos services
services ctexi
expedition chine burkina
transport marchandise
frais de douane
produits interdits importation
retard de livraison
information sur le transport
ou se trouve le siege ctexi
comment fonctionne le service cargo
'
),

(
'suivi_colis',
'operation',
'
suivre mon colis
ou est mon colis
statut de ma commande
code colis
colis en transit
comment suivre ma commande
delai fret aerien
delai fret maritime
colis arrive au depot
probleme avec mon colis
'
),

(
'taux_change',
'operation',
'
taux de change
taux rmb fcfa
simulation paiement
combien coute le transfert
delai de transfert
comment payer en chine
transaction securisee
preuve de paiement
montant minimum transfert
combien je dois payer
'
);