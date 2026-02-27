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


SELECT * FROM chatbot.faq;



--------------------------------------SCHEMA AUTH---------------------------------------------------

#  DROP TABLE auth.users;



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
    id_user INTEGER REFERENCES auth.users(id_user) ON DELETE CASCADE,
    moyen_contact VARCHAR(100),
    messages TEXT,
    redirect_link VARCHAR(255),
    dates TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);



-------------------------------------SCHEMA CHATBOT--------------------------------------------------------------
DROP TABLE chatbot.faq CASCADE;
DROP TABLE chatbot.intention CASCADE;



SET search_path TO chatbot, public;


SELECT extname FROM pg_extension;


--table faq

CREATE TABLE chatbot.faq(
    id_faq SERIAL PRIMARY KEY,
    message_user TEXT,
    reponse_bot TEXT,
    embedding vector(768),
    dates TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



SELECT * FROM auth.users;


SELECT id_user FROM auth.users;


--Table convesation
CREATE TABLE chatbot.conversations(
    id_conv SERIAL PRIMARY KEY,
    id_user INTEGER NOT NULL REFERENCES auth.users(id_user) ON DELETE CASCADE,
    message_user TEXT NOT NULL,
    reponse_bot TEXT,
    dates TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);





--table sessions
CREATE TABLE chatbot.sessions(
    id_sess SERIAL PRIMARY KEY,
    id_user INTEGER REFERENCES auth.users(id_user) ON DELETE CASCADE,
    heure_debut TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    heure_fin TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    statut VARCHAR(50)
);


--Table intention

CREATE TABLE chatbot.intention(
    id_intent SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    descriptions TEXT
);




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


-------------------------------Insertion des donnees dans les tables faq----------------------------------

--FAQ
INSERT INTO chatbot.faq (message_user, reponse_bot) VALUES

('Comment fonctionne le service CTEXI Buy ?',
'CTEXI Buy vous aide à acheter des produits en Chine. Vous nous fournissez les caractéristiques du produit, nous recherchons les fournisseurs fiables, achetons, vérifions la qualité, conditionnons et expédions le produit vers vous.'),

('Quels sont les avantages de CTEXI Buy ?',
'Les avantages incluent la sécurité, notre expertise en Chine, la réduction des risques liés à l''achat et l''assurance de conformité avec vos demandes.'),

('Comment suivre le processus de mon achat ?',
'Vous pouvez suivre chaque étape : recherche produit, sourcing, achat, vérification qualité, conditionnement et expédition. Nous vous tenons informé à chaque étape.'),

('Comment suivre mon colis ?',
'Connectez-vous avec votre numéro de téléphone. Tous les colis enregistrés sous ce numéro apparaissent avec leur statut actuel, mode de transport et dernière mise à jour.'),

('Que signifie le statut "En transit" ?',
'Cela signifie que votre colis a quitté l''entrepôt et est en route vers le Burkina Faso.'),

('Que faire si mon code de colis est invalide ?',
'Vérifiez le code et assurez-vous qu''il correspond à un colis enregistré. En cas de problème, contactez notre service client via WhatsApp ou mail.'),

('Quel est le taux de change du jour ?',
'Le taux indicatif du jour est affiché dans l''application CTEXI Pay. Exemple : 1 RMB = 85 FCFA.'),

('Comment calculer le montant à payer ?',
'Entrez le montant en RMB dans la simulation. L''application calcule automatiquement le total à payer en FCFA selon le taux du jour.'),

('Comment effectuer un paiement ?',
'Cliquez sur "Valider et contacter CTEXI Pay" pour envoyer un message WhatsApp pré-rempli avec vos informations de paiement.'),

('Comment obtenir un visa pour la Chine ?',
'CTEXI Travel vous guide dans l''obtention du visa chinois. Nous fournissons la liste des documents requis, les délais et vous aidons à remplir votre demande.'),

('Puis-je réserver un billet d''avion ou un hôtel via CTEXI Travel ?',
'Oui, le service permet la réservation de billets d''avion et d''hôtels en Chine. Vous pouvez contacter directement un agent CTEXI pour assistance.'),

('Quels types de formations propose CTEXI Académie ?',
'CTEXI Académie propose des formations sur les achats en ligne en Chine, l''import-export, le marketing digital et du coaching.'),

('Comment m''inscrire à une formation ?',
'Cliquez sur "S''inscrire / Demander infos" et contactez-nous via WhatsApp, email ou formulaire pour réserver votre place.'),

('Comment contacter CTEXI ?',
'Vous pouvez nous contacter via WhatsApp, email ou téléphone depuis l''application.'),

('Quels services propose CTEXI ?',
'CTEXI propose Buy (achat en Chine), Cargo (expédition), Pay (transfert d''argent), Travel (voyage) et Académie (formation et coaching).'),

('Combien de temps prend une commande via CTEXI Buy ?',
'Le délai dépend du fournisseur et du mode de transport choisi. En moyenne : 3 à 7 jours pour l''achat et vérification, puis 7 à 45 jours pour la livraison selon transport aérien ou maritime.'),

('Puis-je demander une vérification qualité avant expédition ?',
'Oui, nous effectuons un contrôle qualité avant l''expédition afin de vérifier la conformité des produits avec votre commande.'),

('Que faire si le produit reçu n''est pas conforme ?',
'Contactez immédiatement notre service client avec photos et description du problème. Nous analyserons la situation avec le fournisseur.'),

('Puis-je annuler une commande ?',
'L''annulation est possible uniquement si la commande n''a pas encore été payée au fournisseur.'),

('Proposez-vous une assurance marchandise ?',
'Oui, une assurance transport peut être ajoutée pour couvrir les pertes ou dommages pendant l''expédition.'),

('Quels sont les délais de livraison en fret aérien ?',
'Le fret aérien prend généralement entre 7 et 15 jours selon la destination.'),

('Quels sont les délais de livraison en fret maritime ?',
'Le fret maritime prend en moyenne entre 30 et 45 jours selon le port de départ.'),

('Comment sont calculés les frais de transport ?',
'Les frais sont calculés selon le poids volumétrique, le mode de transport et la destination finale.'),

('Que signifie le statut "Arrivé au dépôt" ?',
'Cela signifie que votre colis est arrivé dans notre entrepôt local et est prêt pour retrait ou livraison.'),

('Que faire en cas de colis endommagé ?',
'Signalez immédiatement le dommage avec preuves visuelles. Si une assurance a été souscrite, une procédure d''indemnisation sera lancée.'),

('Le taux de change peut-il changer ?',
'Oui, le taux de change est mis à jour régulièrement en fonction du marché international.'),

('Combien de temps prend un transfert via CTEXI Pay ?',
'Un transfert prend généralement entre 24 et 72 heures selon la banque du bénéficiaire.'),

('Mes transactions sont-elles sécurisées ?',
'Oui, toutes les transactions sont traitées de manière sécurisée et confidentielle.'),

('Puis-je obtenir une preuve de paiement ?',
'Oui, une confirmation ou preuve de transaction est fournie après chaque paiement effectué.'),

('Y a-t-il un montant minimum pour un transfert ?',
'Oui, un montant minimum peut être requis selon la réglementation en vigueur.'),

('Quels documents sont nécessaires pour une demande de visa ?',
'Les documents incluent généralement passeport valide, photos, formulaire rempli, preuve d''hébergement et billet aller-retour.'),

('Combien de temps prend l''obtention du visa ?',
'Le délai varie selon le type de visa, généralement entre 5 et 15 jours ouvrables.'),

('Proposez-vous une assistance à l''aéroport ?',
'Oui, une assistance peut être organisée selon votre demande.'),

('Puis-je modifier ma réservation ?',
'Les modifications dépendent des conditions du billet ou de l''hôtel réservé.'),

('Les formations sont-elles en ligne ou en présentiel ?',
'Les formations peuvent être proposées en ligne ou en présentiel selon le programme choisi.'),

('Recevrai-je un certificat après la formation ?',
'Oui, un certificat de participation peut être délivré à la fin de la formation.'),

('Les formations incluent-elles un accompagnement pratique ?',
'Oui, certaines formations incluent des études de cas et un accompagnement personnalisé.'),

('Comment créer un compte sur l''application ?',
'Cliquez sur Inscription, remplissez vos informations personnelles et validez votre compte.'),

('J''ai oublié mon mot de passe, que faire ?',
'Cliquez sur Mot de passe oublié et suivez les instructions pour réinitialiser votre accès.'),

('Comment supprimer mon compte ?',
'Contactez le service client pour faire une demande de suppression de compte.'),

('Comment modifier mes informations personnelles ?',
'Accédez à votre profil dans l''application et mettez à jour vos informations.'),

('L''application est-elle disponible sur Android et iOS ?',
'Oui, l''application CTEXI est disponible sur Android et iOS.'),

('Quels produits sont interdits à l''importation ?',
'Les produits interdits incluent les marchandises dangereuses, contrefaçons et articles réglementés selon la législation locale.'),

('Dois-je payer des frais de douane ?',
'Oui, des droits de douane peuvent s''appliquer selon la nature et la valeur des marchandises.'),

('CTEXI est-il responsable en cas de retard ?',
'Les délais peuvent être affectés par des facteurs externes (douane, transport). Nous faisons le maximum pour minimiser les retards.'),

('Proposez-vous un service client 24h/24 ?',
'Le service client est disponible aux heures ouvrables. Vous pouvez laisser un message à tout moment.'),

('Où se situe le siège de CTEXI ?',
'Le siège est situé au Burkina Faso avec une représentation en Chine.');


SELECT * FROM ctexi_db;


--INSERT INTO chatbot.intentions (nom_intention, mots_cles, reponse) VALUES
--('salutation', ARRAY['bonjour','salut','hello','bonsoir','hey'], 
--'Bonjour 👋 Je suis votre assistant virtuel CTEXI-BOT. Comment puis-je vous aider aujourd’hui ?');




SELECT * FROM auth.users;

SELECT * FROM chatbot.faq;
SELECT * FROM chatbot.intention;


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