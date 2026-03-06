// ==========================================================
// SÉLECTION DES ÉLÉMENTS DU DOM
//e DOM est le lien entre JavaScript et ta page HTML, il te permet de contrôler ce que l’utilisateur voit et interagit avec.
// ==========================================================

// Zone où les messages apparaissent
const chatBody = document.querySelector(".chat-body");

// Zone de saisie du message utilisateur
const messageInput = document.querySelector(".message-input");

// Bouton pour envoyer le message
const sendMessageButton = document.querySelector("#send-message");

// Input pour fichiers (non utilisé dans ce code pour l'instant)
const fileInput = document.querySelector("#file-input");

// Bouton pour ouvrir le chatbot
const chatbotToggler = document.querySelector("#chatbot-toggler");

// Bouton pour fermer le chatbot
const closeChatbot = document.querySelector("#close-chatbot");

// Formulaire de login
const loginForm = document.querySelector("#login-form");

// Inputs du formulaire login
const loginEmail = document.querySelector("#email");
const loginPassword = document.querySelector("#mdp");

// Stockage temporaire du message utilisateur
const userData = {
  message: null
};

// Hauteur initiale du textarea pour le redimensionnement automatique
const initialInputHeight = messageInput.scrollHeight;


// ==========================================================
// LOGIN ET STOCKAGE DU TOKEN
// ==========================================================

if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    // Récupérer et nettoyer les valeurs saisies
    const email = loginEmail.value.trim();
    const mdp = loginPassword.value.trim();

    if (!email || !mdp) return alert("Veuillez remplir tous les champs.");

    try {
      // Appel API POST pour authentification
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, mdp })
      });

      const data = await response.json();
      if (!response.ok) throw new Error(data.message || "Erreur lors de la connexion");

      // Stocker le token et le nom de l'utilisateur dans localStorage
      localStorage.setItem("token", data.token);
      localStorage.setItem("user_name", data.user?.nom || "");

      // Redirection vers la page d'accueil
      window.location.href = "/";
    } catch (err) {
      console.error(err);
      alert(err.message);
    }
  });
}


// ==========================================================
// CRÉER UN ÉLÉMENT MESSAGE (user ou bot)
// ==========================================================

const createMessageElement = (content, ...classes) => {
  const div = document.createElement("div");
  div.classList.add("message", ...classes); // ajouter les classes CSS
  div.innerHTML = content; // insérer le texte HTML
  return div;
};


// ==========================================================
// AFFICHAGE DU TEXTE PROGRESSIVEMENT (EFFET "TYPING")
// ==========================================================

function typeText(element, text, delay = 20) {
  return new Promise((resolve) => {
    let i = 0;
    element.innerHTML = "";

    // Ajouter une lettre toutes les `delay` millisecondes
    const interval = setInterval(() => {
      element.innerHTML += text[i];
      i++;
      if (i >= text.length) {
        clearInterval(interval);
        resolve(); // fin du typing
      }
      // Scroll automatique vers le bas
      chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });
    }, delay);
  });
}


// ==========================================================
// AFFICHER LES BOUTONS POUR CONTACTER UN AGENT
// ==========================================================

function displayAgentButtons(agent = { whatsapp: "", email: "", telephone: "" }) {
  const contactDiv = document.createElement("div");
  contactDiv.classList.add("agent-contact");

  const infoText = document.createElement("div");
  contactDiv.appendChild(infoText);

  // Crée le bouton WhatsApp si disponible
  if (agent.whatsapp) {
    const btnWhats = document.createElement("a");
    btnWhats.href = "https://wa.me/" + agent.whatsapp;
    btnWhats.innerText = "💬 WhatsApp";
    btnWhats.target = "_blank"; // ouvre dans un nouvel onglet
    contactDiv.appendChild(btnWhats);
  }

  // Crée le bouton Email si disponible
  if (agent.email) {
    const btnMail = document.createElement("a");
    btnMail.href = "mailto:" + agent.email;
    btnMail.innerText = "📧 Email";
    contactDiv.appendChild(btnMail);
  }

  // Crée le bouton Appel si disponible
  if (agent.telephone) {
    const btnCall = document.createElement("a");
    btnCall.href = "tel:" + agent.telephone;
    btnCall.innerText = "📞 Appeler";
    contactDiv.appendChild(btnCall);
  }

  chatBody.appendChild(contactDiv);
  chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });
}


// ==========================================================
// GÉNÉRER LA RÉPONSE DU BOT VIA L'API FLASK
// ==========================================================

const generateBotResponse = async (incomingMessageDiv) => {
  const messageElement = incomingMessageDiv.querySelector(".message-text");

  try {
    const token = localStorage.getItem("token");

    // Si l'utilisateur n'est pas connecté
    if (!token) {
      messageElement.innerText = "Vous devez être connecté pour utiliser le chatbot.";
      messageElement.style.color = "#ff0000";
      incomingMessageDiv.classList.remove("thinking");
      return;
    }

    // Appel API POST pour obtenir la réponse du bot
    const response = await fetch("/api/faq/message", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + token
      },
      body: JSON.stringify({ message: userData.message })
    });

    const data = await response.json();
    console.log("REPONSE API :", data);
    if (!response.ok) throw new Error(data.message || "Erreur serveur");

    const botText = data.response || data.reponse || "Pas de réponse disponible.";

    // Affiche le texte du bot avec effet typing
    await typeText(messageElement, botText);

    // Si un agent est associé, afficher les boutons
    if (data.agent) displayAgentButtons(data.agent);

  } catch (error) {
    console.error(error);
    messageElement.innerText = "Erreur serveur, veuillez réessayer.";
    messageElement.style.color = "#ff0000";
  } finally {
    // Supprimer l'état "thinking" et scroll vers le bas
    incomingMessageDiv.classList.remove("thinking");
    chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });
  }
};


// ==========================================================
// ENVOI DU MESSAGE UTILISATEUR
// ==========================================================

const handleOutgoingMessage = (e) => {
  e.preventDefault();
  userData.message = messageInput.value.trim();
  if (!userData.message) return;

  messageInput.value = "";
  messageInput.dispatchEvent(new Event("input")); // déclenche resize du textarea

  // Création message utilisateur
  const userMessageDiv = createMessageElement(
    `<div class="message-text">${userData.message}</div>`,
    "user-message"
  );
  chatBody.appendChild(userMessageDiv);

  // Création message "thinking" du bot
  const botThinkingDiv = createMessageElement(
    `<svg class="bot-avatar" xmlns="http://www.w3.org/2000/svg" width="50" height="50" viewBox="0 0 1024 1024">
      <path d="M738.3 287.6H285.7c-59 0-106.8 47.8-106.8 106.8v303.1c0 59 47.8 106.8 106.8 106.8h81.5v111.1c0 .7.8 1.1 1.4.7l166.9-110.6 41.8-.8h117.4l43.6-.4c59 0 106.8-47.8 106.8-106.8V394.5c0-59-47.8-106.9-106.8-106.9z"/>
    </svg>
    <div class="message-text">
      <div class="thinking-indicator">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
      </div>
    </div>`,
    "bot-message", "thinking"
  );
  chatBody.appendChild(botThinkingDiv);

  chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });

  // Appel API pour générer réponse bot
  generateBotResponse(botThinkingDiv);
};


// ==========================================================
// ENVOI AVEC LA TOUCHE ENTER
// ==========================================================

messageInput.addEventListener("keydown", (e) => {
  const userMessage = e.target.value.trim();
  // Si ENTER pressé, pas de SHIFT, et écran large
  if (e.key === "Enter" && userMessage && !e.shiftKey && window.innerWidth > 768) {
    handleOutgoingMessage(e);
  }
});


// ==========================================================
// AUTO-RESIZE DU TEXTAREA
// ==========================================================

messageInput.addEventListener("input", () => {
  messageInput.style.height = `${initialInputHeight}px`;
  messageInput.style.height = `${messageInput.scrollHeight}px`;
  document.querySelector(".chat-form").style.borderRadius =
    messageInput.scrollHeight > initialInputHeight ? "15px" : "32px";
});


// ==========================================================
// BOUTON ENVOI
// ==========================================================

sendMessageButton.addEventListener("click", (e) => handleOutgoingMessage(e));


// ==========================================================
// TOGGLE CHATBOT
// ==========================================================

chatbotToggler.addEventListener("click", () => {
  document.body.classList.toggle("show-chatbot");
});
closeChatbot.addEventListener("click", () => {
  document.body.classList.remove("show-chatbot");
});


// ==========================================================
// QUICK BUTTONS (actions rapides)
// ==========================================================

document.querySelectorAll(".quick-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const action = btn.dataset.action;

    if (action === "agent") {
      handleContactAgent(); // Contact direct d'un agent
      return;
    }

    let message = "";
    if (action === "services") message = "Pouvez-vous me donner des infos sur vos services ?";
    if (action === "faq") message = "J’aimerais consulter la FAQ.";

    messageInput.value = message;
    sendMessageButton.click();
  });
});


// ==========================================================
// FONCTION CONTACT AGENT
// ==========================================================

function handleContactAgent() {
  // Message utilisateur
  const userMessageDiv = createMessageElement(
    `<div class="message-text">Je souhaite contacter un agent.</div>`,
    "user-message"
  );
  chatBody.appendChild(userMessageDiv);
  chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });

  // Message bot vide pour afficher le texte progressivement
  const botDiv = createMessageElement(`<div class="message-text"></div>`, "bot-message");
  chatBody.appendChild(botDiv);

  // Affichage texte "Veuillez choisir un moyen de contact"
  typeText(botDiv.querySelector(".message-text"), "Veuillez choisir un moyen de contact :")
    .then(() => {
      const agentInfo = {
        whatsapp: "22674381094",
        email: "yakfismokonzi@gmail.com",
        telephone: "+22674381094"
      };
      displayAgentButtons(agentInfo); // Affiche boutons WhatsApp, Email et Téléphone
    });
}