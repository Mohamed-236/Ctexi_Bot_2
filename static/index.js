// ==========================
// Sélection des éléments DOM
// ==========================
const chatBody = document.querySelector(".chat-body");
const messageInput = document.querySelector(".message-input");
const sendMessageButton = document.querySelector("#send-message");
const fileInput = document.querySelector("#file-input");
const chatbotToggler = document.querySelector("#chatbot-toggler");
const closeChatbot = document.querySelector("#close-chatbot");

// Pour login
const loginForm = document.querySelector("#login-form");
const loginEmail = document.querySelector("#email");
const loginPassword = document.querySelector("#mdp");

// Stockage des données utilisateur
const userData = {
  message: null
};

const initialInputHeight = messageInput.scrollHeight;

// ==========================
// Fonction login et stockage token
// ==========================
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = loginEmail.value.trim();
    const mdp = loginPassword.value.trim();
    if (!email || !mdp) return alert("Veuillez remplir tous les champs.");

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, mdp })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.message || "Erreur lors de la connexion");

      localStorage.setItem("token", data.token);
      localStorage.setItem("user_name", data.user?.nom || "");
      window.location.href = "/";
    } catch (err) {
      console.error(err);
      alert(err.message);
    }
  });
}

// ==========================
// Créer un message (user ou bot)
// ==========================
const createMessageElement = (content, ...classes) => {
  const div = document.createElement("div");
  div.classList.add("message", ...classes);
  div.innerHTML = content;
  return div;
};

// ==========================
// Fonction pour afficher le texte progressivement
// ==========================
function typeText(element, text, delay = 20) {
  return new Promise((resolve) => {
    let i = 0;
    element.innerHTML = "";
    const interval = setInterval(() => {
      element.innerHTML += text[i];
      i++;
      if (i >= text.length) {
        clearInterval(interval);
        resolve();
      }
      chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });
    }, delay);
  });
}

// ==========================
// Afficher les boutons pour contacter un agent
// ==========================
function displayAgentButtons(agent = { whatsapp: "", email: "", telephone: "" }) {
  const contactDiv = document.createElement("div");
  contactDiv.classList.add("agent-contact");

  const infoText = document.createElement("div");
  contactDiv.appendChild(infoText);

  if (agent.whatsapp) {
    const btnWhats = document.createElement("a");
    btnWhats.href = "https://wa.me/" + agent.whatsapp;
    btnWhats.innerText = "💬 WhatsApp";
    btnWhats.target = "_blank";
    contactDiv.appendChild(btnWhats);
  }

  if (agent.email) {
    const btnMail = document.createElement("a");
    btnMail.href = "mailto:" + agent.email;
    btnMail.innerText = "📧 Email";
    contactDiv.appendChild(btnMail);
  }

  if (agent.telephone) {
    const btnCall = document.createElement("a");
    btnCall.href = "tel:" + agent.telephone;
    btnCall.innerText = "📞 Appeler";
    contactDiv.appendChild(btnCall);
  }

  chatBody.appendChild(contactDiv);
  chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });
}

// ==========================
// Générer la réponse du bot via Flask API
// ==========================
const generateBotResponse = async (incomingMessageDiv) => {
  const messageElement = incomingMessageDiv.querySelector(".message-text");

  try {
    const token = localStorage.getItem("token");
    if (!token) {
      messageElement.innerText = "Vous devez être connecté pour utiliser le chatbot.";
      messageElement.style.color = "#ff0000";
      incomingMessageDiv.classList.remove("thinking");
      return;
    }

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
    await typeText(messageElement, botText);

    // Si un agent existe, afficher les boutons
    if (data.agent) displayAgentButtons(data.agent);

  } catch (error) {
    console.error(error);
    messageElement.innerText = "Erreur serveur, veuillez réessayer.";
    messageElement.style.color = "#ff0000";
  } finally {
    incomingMessageDiv.classList.remove("thinking");
    chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });
  }
};

// ==========================
// Envoi message utilisateur
// ==========================
const handleOutgoingMessage = (e) => {
  e.preventDefault();
  userData.message = messageInput.value.trim();
  if (!userData.message) return;
  messageInput.value = "";
  messageInput.dispatchEvent(new Event("input"));

  const userMessageDiv = createMessageElement(
    `<div class="message-text">${userData.message}</div>`,
    "user-message"
  );
  chatBody.appendChild(userMessageDiv);

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
  generateBotResponse(botThinkingDiv);
};

// ==========================
// Envoi avec ENTER
// ==========================
messageInput.addEventListener("keydown", (e) => {
  const userMessage = e.target.value.trim();
  if (e.key === "Enter" && userMessage && !e.shiftKey && window.innerWidth > 768) {
    handleOutgoingMessage(e);
  }
});

// ==========================
// Auto resize textarea
// ==========================
messageInput.addEventListener("input", () => {
  messageInput.style.height = `${initialInputHeight}px`;
  messageInput.style.height = `${messageInput.scrollHeight}px`;
  document.querySelector(".chat-form").style.borderRadius =
    messageInput.scrollHeight > initialInputHeight ? "15px" : "32px";
});

// ==========================
// Bouton envoi
// ==========================
sendMessageButton.addEventListener("click", (e) => handleOutgoingMessage(e));

// ==========================
// Toggle chatbot
// ==========================
chatbotToggler.addEventListener("click", () => {
  document.body.classList.toggle("show-chatbot");
});
closeChatbot.addEventListener("click", () => {
  document.body.classList.remove("show-chatbot");
});

// ==========================
// Quick buttons
// ==========================
document.querySelectorAll(".quick-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const action = btn.dataset.action;
    if (action === "agent") {
      handleContactAgent(); // clic direct sur "Contacter un agent"
      return;
    }
    let message = "";
    if (action === "services") message = "Pouvez-vous me donner des infos sur vos services ?";
    if (action === "faq") message = "J’aimerais consulter la FAQ.";
    messageInput.value = message;
    sendMessageButton.click();
  });
});

// ==========================
// Fonction Contact Agent
// ==========================
function handleContactAgent() {
  const userMessageDiv = createMessageElement(
    `<div class="message-text">Je souhaite contacter un agent.</div>`,
    "user-message"
  );
  chatBody.appendChild(userMessageDiv);
  chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });

  const botDiv = createMessageElement(`<div class="message-text"></div>`, "bot-message");
  chatBody.appendChild(botDiv);

  typeText(botDiv.querySelector(".message-text"), "Veuillez choisir un moyen de contact :")
    .then(() => {
      const agentInfo = {
        whatsapp: "22512345678",
        email: "agent@ctexi.com",
        telephone: "+22587654321"
      };
      displayAgentButtons(agentInfo);
    });
}