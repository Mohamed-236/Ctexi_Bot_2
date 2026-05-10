// ==========================================================
// SÉLECTION DOM
// ==========================================================
const chatBody = document.querySelector(".chat-body");
const messageInput = document.querySelector(".message-input");
const sendMessageButton = document.querySelector("#send-message");
const chatbotToggler = document.querySelector("#chatbot-toggler");
const closeChatbot = document.querySelector("#close-chatbot");

const loginForm = document.querySelector("#login-form");
const loginEmail = document.querySelector("#email");
const loginPassword = document.querySelector("#mdp");

const initialInputHeight = messageInput.scrollHeight;

const userData = {
  message: null
};

// ==========================================================
// BOT SVG
// ==========================================================
const BOT_AVATAR = `
<svg class="bot-avatar" xmlns="http://www.w3.org/2000/svg"
width="50" height="50" viewBox="0 0 1024 1024">
  <path d="M738.3 287.6H285.7c-59 0-106.8 47.8-106.8 106.8v303.1
  c0 59 47.8 106.8 106.8 106.8h81.5v111.1c0 .7.8 1.1 1.4.7
  l166.9-110.6 41.8-.8h117.4l43.6-.4
  c59 0 106.8-47.8 106.8-106.8V394.5
  c0-59-47.8-106.9-106.8-106.9z"/>
</svg>
`;

// ==========================================================
// LOGIN
// ==========================================================
if (loginForm) {

  loginForm.addEventListener("submit", async (e) => {

    e.preventDefault();

    const email = loginEmail.value.trim();
    const mdp = loginPassword.value.trim();

    if (!email || !mdp) {
      alert("Veuillez remplir tous les champs.");
      return;
    }

    try {

      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          email,
          mdp
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || "Erreur connexion");
      }

      localStorage.setItem("token", data.token || "");
      localStorage.setItem("user_name", data.user?.nom || "");

      if (data.redirect) {
        window.location.href = data.redirect;
      } else {
        window.location.href = "/api/auth/chatbot";
      }

    } catch (error) {

      console.error(error);
      alert(error.message);

    }

  });

}

// ==========================================================
// CREATE MESSAGE
// ==========================================================
function createMessageElement(content, ...classes) {

  const div = document.createElement("div");

  div.classList.add("message", ...classes);

  if (classes.includes("bot-message")) {

    div.innerHTML = `
      ${BOT_AVATAR}
      <div class="message-text">${content}</div>
    `;

  } else {

    div.innerHTML = `
      <div class="message-text">${content}</div>
    `;

  }

  return div;

}

// ==========================================================
// FORMATAGE IA
// ==========================================================
function formatBotMessage(text) {

  if (!text) return "";

  let formatted = text;

  // gras markdown
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");

  // italique
  formatted = formatted.replace(/\*(.*?)\*/g, "<em>$1</em>");

  // bullet unicode
  formatted = formatted.replace(/^• (.*)$/gm, "<li>$1</li>");

  // bullet *
  formatted = formatted.replace(/^\* (.*)$/gm, "<li>$1</li>");

  // transformer listes
  formatted = formatted.replace(
    /(<li>.*<\/li>)/gs,
    "<ul>$1</ul>"
  );

  // retour ligne
  formatted = formatted.replace(/\n/g, "<br>");

  return formatted;

}

// ==========================================================
// TYPING EFFECT HTML
// ==========================================================
function typeHTML(element, html, speed = 8) {

  return new Promise((resolve) => {

    let i = 0;

    element.innerHTML = "";

    const interval = setInterval(() => {

      element.innerHTML = html.slice(0, i);

      i++;

      chatBody.scrollTo({
        top: chatBody.scrollHeight,
        behavior: "smooth"
      });

      if (i > html.length) {

        clearInterval(interval);
        resolve();

      }

    }, speed);

  });

}

// ==========================================================
// THINKING LOADER
// ==========================================================
function createThinkingMessage() {

  return createMessageElement(
    `
    <div class="thinking-indicator">
      <div class="dot"></div>
      <div class="dot"></div>
      <div class="dot"></div>
    </div>
    `,
    "bot-message",
    "thinking"
  );

}

// ==========================================================
// SERVICES BUTTONS
// ==========================================================
async function displayServiceButtons(services = []) {

  const container = document.createElement("div");

  container.classList.add("service-buttons");

  chatBody.appendChild(container);

  for (const service of services) {

    const btn = document.createElement("button");

    btn.innerText = service.nom_service;

    btn.addEventListener("click", () => {
      fetchServiceDetails(service.id_service);
    });

    container.appendChild(btn);

    await new Promise(r => setTimeout(r, 150));

  }

}

// ==========================================================
// MENU FORMAT
// ==========================================================
function formatMenu(menu) {

  if (!menu) return "";

  let html = "";

  if (menu.fonctionnalites) {

    html += `
      <div class="menu-section">
        <h3>Fonctionnalités</h3>
        <ul>
          ${menu.fonctionnalites.map(i => `<li>${i}</li>`).join("")}
        </ul>
      </div>
    `;

  }

  if (menu.avantages) {

    html += `
      <div class="menu-section">
        <h3>Avantages</h3>
        <ul>
          ${menu.avantages.map(i => `<li>${i}</li>`).join("")}
        </ul>
      </div>
    `;

  }

  if (menu.processus) {

    html += `
      <div class="menu-section">
        <h3>Processus</h3>
        <ol>
          ${menu.processus.map(step => `
            <li>
              <strong>${step.titre}</strong>
              ${step.description ? " : " + step.description : ""}
            </li>
          `).join("")}
        </ol>
      </div>
    `;

  }

  return html;

}

// ==========================================================
// TRACKING CARD
// ==========================================================
function createTrackingCard(data) {

  return `
    <div class="tracking-card">
      <div>📦 <strong>Code :</strong> ${data.code}</div>
      <div>🚚 <strong>Transport :</strong> ${data.transport}</div>
      <div>📌 <strong>Statut :</strong> ${data.statut}</div>
      <div>📦 <strong>Type :</strong> ${data.type_colis}</div>
      <div>🕒 <strong>Mise à jour :</strong> ${data.derniere_maj}</div>
    </div>
  `;

}

// ==========================================================
// FETCH SERVICE DETAILS
// ==========================================================
async function fetchServiceDetails(idService) {

  try {

    const token = localStorage.getItem("token");

    const response = await fetch(`/api/list/service/${idService}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`
      }
    });

    const data = await response.json();

    const html = `
      <strong>${data.nom_service}</strong><br><br>
      ${data.descriptions}<br><br>
      ${formatMenu(data.menu)}
    `;

    const div = createMessageElement(html, "bot-message");

    chatBody.appendChild(div);

    chatBody.scrollTo({
      top: chatBody.scrollHeight,
      behavior: "smooth"
    });

  } catch (error) {

    console.error(error);

  }

}

// ==========================================================
// BOT RESPONSE
// ==========================================================
async function generateBotResponse(thinkingDiv) {

  const messageElement = thinkingDiv.querySelector(".message-text");

  try {

    const token = localStorage.getItem("token");

    if (!token) {

      messageElement.innerHTML = "Vous devez être connecté.";
      return;

    }

    const response = await fetch("/api/faq/message", {

      method: "POST",

      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${token}`
      },

      body: JSON.stringify({
        message: userData.message
      })

    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Erreur serveur");
    }

    thinkingDiv.classList.remove("thinking");

    // ======================================================
    // SERVICES
    // ======================================================
    if (data.type === "service" && data.services) {

      const html = formatBotMessage(data.reponse);

      await typeHTML(messageElement, html);

      await displayServiceButtons(data.services);

    }

    // ======================================================
    // TRACKING
    // ======================================================
    else if (data.type === "tracking" && data.data) {

      const html = `
        ${formatBotMessage(data.reponse)}
        <br><br>
        ${createTrackingCard(data.data)}
      `;

      await typeHTML(messageElement, html);

    }

    // ======================================================
    // NORMAL MESSAGE
    // ======================================================
    else {

      const botText = data.reponse || data.response || "Pas de réponse.";

      const formatted = formatBotMessage(botText);

      await typeHTML(messageElement, formatted);

    }

    // ======================================================
    // AGENT BUTTONS
    // ======================================================
    if (data.agent) {

      await displayAgentButtons(data.agent);

    }

  } catch (error) {

    console.error(error);

    thinkingDiv.classList.remove("thinking");

    messageElement.innerHTML = `
      <span style="color:red;">
        Erreur serveur. Veuillez réessayer.
      </span>
    `;

  }

}

// ==========================================================
// USER MESSAGE
// ==========================================================
function handleOutgoingMessage(e) {

  e.preventDefault();

  const message = messageInput.value.trim();

  if (!message) return;

  userData.message = message;

  // user message
  const userDiv = createMessageElement(
    message,
    "user-message"
  );

  chatBody.appendChild(userDiv);

  // reset input
  messageInput.value = "";

  messageInput.dispatchEvent(new Event("input"));

  // bot thinking
  const thinkingDiv = createThinkingMessage();

  chatBody.appendChild(thinkingDiv);

  chatBody.scrollTo({
    top: chatBody.scrollHeight,
    behavior: "smooth"
  });

  generateBotResponse(thinkingDiv);

}

// ==========================================================
// AGENT BUTTONS
// ==========================================================
async function displayAgentButtons(agent) {

  const container = document.createElement("div");

  container.classList.add("agent-contact");

  chatBody.appendChild(container);

  const buttons = [];

  if (agent.whatsapp) {

    const btn = document.createElement("a");

    btn.href = `https://wa.me/${agent.whatsapp}`;

    btn.target = "_blank";

    btn.innerText = "💬 WhatsApp";

    buttons.push(btn);

  }

  if (agent.email) {

    const btn = document.createElement("a");

    btn.href = `mailto:${agent.email}`;

    btn.innerText = "📧 Email";

    buttons.push(btn);

  }

  if (agent.telephone) {

    const btn = document.createElement("a");

    btn.href = `tel:${agent.telephone}`;

    btn.innerText = "📞 Appeler";

    buttons.push(btn);

  }

  for (const btn of buttons) {

    container.appendChild(btn);

    await new Promise(r => setTimeout(r, 150));

  }

}

// ==========================================================
// INPUT AUTO HEIGHT
// ==========================================================
messageInput.addEventListener("input", () => {

  messageInput.style.height = `${initialInputHeight}px`;

  messageInput.style.height = `${messageInput.scrollHeight}px`;

});

// ==========================================================
// SEND EVENTS
// ==========================================================
sendMessageButton.addEventListener("click", handleOutgoingMessage);

messageInput.addEventListener("keydown", (e) => {

  if (
    e.key === "Enter" &&
    !e.shiftKey &&
    window.innerWidth > 768
  ) {

    e.preventDefault();

    handleOutgoingMessage(e);

  }

});

// ==========================================================
// CHAT TOGGLE
// ==========================================================
chatbotToggler.addEventListener("click", () => {

  document.body.classList.toggle("show-chatbot");

});

closeChatbot.addEventListener("click", () => {

  document.body.classList.remove("show-chatbot");

});

// ==========================================================
// QUICK BUTTONS
// ==========================================================
document.querySelectorAll(".quick-btn").forEach(btn => {

  btn.addEventListener("click", () => {

    const action = btn.dataset.action;

    let message = "";

    if (action === "services") {
      message = "Quels sont vos services ?";
    }

    if (action === "suivi_colis") {
      message = "Je veux suivre mon colis";
    }

    if (action === "agent") {
      message = "Je veux contacter un agent";
    }

    messageInput.value = message;

    sendMessageButton.click();

  });

});

// ==========================================================
// AUTO OPEN
// ==========================================================
window.addEventListener("load", () => {

  setTimeout(() => {

    document.body.classList.add("show-chatbot");

  }, 1200);

});

// ==========================================================
// SPEECH TO TEXT
// ==========================================================
const SpeechRecognition =
  window.SpeechRecognition ||
  window.webkitSpeechRecognition;

let recognition;

if (SpeechRecognition) {

  recognition = new SpeechRecognition();

  recognition.lang = "fr-FR";

  recognition.continuous = false;

  recognition.interimResults = false;

}

const micButton = document.querySelector("#mic-btn");

if (micButton && recognition) {

  micButton.addEventListener("click", () => {

    recognition.start();

    micButton.classList.add("listening");

  });

  recognition.onresult = (event) => {

    const transcript = event.results[0][0].transcript;

    messageInput.value = transcript;

    messageInput.dispatchEvent(new Event("input"));

    setTimeout(() => {

      sendMessageButton.click();

    }, 300);

  };

  recognition.onerror = (err) => {

    console.error(err);

  };

  recognition.onend = () => {

    micButton.classList.remove("listening");

  };

}