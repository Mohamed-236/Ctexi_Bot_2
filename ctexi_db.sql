-- Active: 1771246225510@@127.0.0.1@5433@ctexi_db

-----------------------------------CREATION DES SCHEMA---------------------------------------------------

-- ---------AUTH
CREATE SCHEMA IF NOT EXISTS auth;

-----------CHATBOT
CREATE SCHEMA IF NOT EXISTS chatbot;

------------CORE
CREATE SCHEMA IF NOT EXISTS core;

-----------SYSTEM
CREATE SCHEMA IF NOT EXISTS systems;


---------------------CREATION DES TABLES POUR LES SCHEMAS-------------------------------------------








--------------------------------------SCHEMA AUTH-----------------------------------------------

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

--table faq
CREATE TABLE chatbot.faq(
    id_faq SERIAL PRIMARY KEY,
    message_user TEXT,
    reponse_bot TEXT,
    dates TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



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