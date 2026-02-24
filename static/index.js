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

      if (!response.ok) {
        throw new Error(data.message || "Erreur lors de la connexion");
      }

      // 🔑 Stocker le token JWT dans localStorage
      localStorage.setItem("token", data.token);
      localStorage.setItem("user_name", data.user?.nom || "");

      // Redirection après login
      window.location.href = "/"; // ou page d'accueil
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
// Générer la réponse du bot via Flask API
// ==========================
const generateBotResponse = async (incomingMessageDiv) => {
  const messageElement = incomingMessageDiv.querySelector(".message-text");

  try {
    const token = localStorage.getItem("token"); // récupère le token JWT

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
      body: JSON.stringify({
        message: userData.message
      })
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Erreur serveur");
    }

    messageElement.innerText = data.response || data.reponse || "Pas de réponse disponible.";

  } catch (error) {
    console.error(error);
    messageElement.innerText = "Erreur serveur, veuillez réessayer.";
    messageElement.style.color = "#ff0000";
  } finally {
    incomingMessageDiv.classList.remove("thinking");
    chatBody.scrollTo({
      top: chatBody.scrollHeight,
      behavior: "smooth"
    });
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

  // Message utilisateur
  const userMessageDiv = createMessageElement(
    `<div class="message-text">${userData.message}</div>`,
    "user-message"
  );
  chatBody.appendChild(userMessageDiv);

  // Message bot (thinking)
  const botThinkingDiv = createMessageElement(
    `<svg 
        class="bot-avatar"
        xmlns="http://www.w3.org/2000/svg"
        width="50"
        height="50"
        viewBox="0 0 1024 1024">
        <path d="M738.3 287.6H285.7c-59 0-106.8 47.8-106.8 106.8v303.1c0 59 47.8 106.8 106.8 106.8h81.5v111.1c0 .7.8 1.1 1.4.7l166.9-110.6 41.8-.8h117.4l43.6-.4c59 0 106.8-47.8 106.8-106.8V394.5c0-59-47.8-106.9-106.8-106.9z"/>
      </svg>
      <div class="message-text">
        <div class="thinking-indicator">
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
      </div>`,
    "bot-message",
    "thinking"
  );
  chatBody.appendChild(botThinkingDiv);

  chatBody.scrollTo({
    top: chatBody.scrollHeight,
    behavior: "smooth"
  });

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
sendMessageButton.addEventListener("click", (e) =>
  handleOutgoingMessage(e)
);

// ==========================
// Toggle chatbot
// ==========================
chatbotToggler.addEventListener("click", () => {
  document.body.classList.toggle("show-chatbot");
});

closeChatbot.addEventListener("click", () => {
  document.body.classList.remove("show-chatbot");
});



document.querySelectorAll(".quick-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const action = btn.dataset.action;
    let message = "";

    if (action === "services") message = "Pouvez-vous me donner des infos sur vos services ?";
    if (action === "faq") message = "J’aimerais consulter la FAQ.";
    if (action === "agent") message = "Je souhaite contacter un agent.";

    messageInput.value = message;
    sendMessageButton.click();
  });
});
