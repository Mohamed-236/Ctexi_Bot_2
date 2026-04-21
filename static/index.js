// ==========================================================
// SÉLECTION DES ÉLÉMENTS DU DOM
// ==========================================================
const chatBody = document.querySelector(".chat-body");
const messageInput = document.querySelector(".message-input");
const sendMessageButton = document.querySelector("#send-message");
const fileInput = document.querySelector("#file-input");
const chatbotToggler = document.querySelector("#chatbot-toggler");
const closeChatbot = document.querySelector("#close-chatbot");
const loginForm = document.querySelector("#login-form");
const loginEmail = document.querySelector("#email");
const loginPassword = document.querySelector("#mdp");

const userData = { message: null };
const initialInputHeight = messageInput.scrollHeight;

// ==========================================================
// LOGIN ET STOCKAGE DU TOKEN
// ==========================================================
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
      console.log("Login data:", data);
      localStorage.setItem("token", data.token);
      localStorage.setItem("user_name", data.user?.nom || "");
      window.location.href = "/";
    } catch (err) { console.error(err); alert(err.message); }
  });
}

// ==========================================================
// CRÉER UN ÉLÉMENT MESSAGE
// ==========================================================


// ==========================================================
// CRÉER MESSAGE
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

const createMessageElement = (content, ...classes) => {

  const div = document.createElement("div");

  div.classList.add("message", ...classes);

  if (classes.includes("bot-message")) {

    div.innerHTML = `
      ${BOT_AVATAR}
      ${content}
    `;

  } else {

    div.innerHTML = content;

  }

  return div;
};

// ==========================================================
// EFFET "TYPING"
// ==========================================================
function typeText(element, text, delay = 20) {
  return new Promise((resolve) => {
    let i = 0;
    element.innerHTML = "";
    const interval = setInterval(() => {
      element.innerHTML += text[i];
      i++;
      if (i >= text.length) { clearInterval(interval); resolve(); }
      chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });
    }, delay);
  });
}

// ==========================================================
// AFFICHAGE DES BOUTONS SERVICES (APPARITION PROGRESSIVE)
// ==========================================================
async function displayServiceButtons(services = [], delay = 200) {
  const serviceDiv = document.createElement("div");
  serviceDiv.classList.add("service-buttons");
  chatBody.appendChild(serviceDiv);

  for (const s of services) {
    const btn = document.createElement("button");
    btn.innerText = s.nom_service;
    btn.dataset.id = s.id_service;
    btn.addEventListener("click", () => fetchServiceDetails(s.id_service));
    serviceDiv.appendChild(btn);
    chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });
    await new Promise(r => setTimeout(r, delay));
  }
}

// ==========================================================
// FORMATAGE DU MENU JSONB
// ==========================================================
function formatMenu(menu) {
  if (!menu) return "";
  let html = "";

  if (menu.fonctionnalites) {
    html += `<div class="menu-section"><h3 class="menu-title">Fonctionnalités</h3><ul>`;
    menu.fonctionnalites.forEach(item => html += `<li>${item}</li>`);
    html += "</ul></div>";
  }

  if (menu.avantages) {
    html += `<div class="menu-section"><h3 class="menu-title">Avantages</h3><ul>`;
    menu.avantages.forEach(item => html += `<li>${item}</li>`);
    html += "</ul></div>";
  }

  if (menu.processus) {
    html += `<div class="menu-section"><h3 class="menu-title">Processus</h3><ol>`;
    menu.processus.forEach(step => {
      html += `<li><strong>${step.titre}</strong>${step.description ? ": " + step.description : ""}</li>`;
    });
    html += "</ol></div>";
  }

  return html;
}


function formatTracking(data) {
  return `
    <div class="tracking-card">
      📦 <b>Code colis</b> : ${data.code}<br>
      🚚 <b>Transport</b> : ${data.transport}<br>
      📌 <b>Statut</b> : ${data.statut}<br>
      📦 <b>Type</b> : ${data.type_colis}<br>
      🕒 <b>Dernière mise à jour</b> : ${data.derniere_maj}
    </div>
  `;
}



// ==========================================================
// RÉCUPÉRER LES DÉTAILS D’UN SERVICE
// ==========================================================
async function fetchServiceDetails(idService) {
  const token = localStorage.getItem("token");
  try {
    const response = await fetch(`/api/list/service/${idService}`, {
      method: "GET",
      headers: { "Authorization": `Bearer ${token}` }
    });
    const data = await response.json();

    const serviceMessage = createMessageElement(
      `<div class="message-text">
         <strong>${data.nom_service}</strong><br/>
         ${data.descriptions}<br/>
         ${formatMenu(data.menu)}
       </div>`,
      "bot-message"
    );
    chatBody.appendChild(serviceMessage);
    chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });
  } catch (err) {
    console.error(err);
  }
}

// ==========================================================
// GÉNÉRER LA RÉPONSE DU BOT
// ==========================================================
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
      headers: { "Content-Type": "application/json", "Authorization": "Bearer " + token },
      body: JSON.stringify({ message: userData.message })
    });

    const data = await response.json();
    console.log("FULL DATA :", data);
    console.log("TRACKING DATA :", data.data);
    if (!response.ok) throw new Error(data.message || "Erreur serveur");

    if (data.type === "service" && data.services) {
      await typeText(messageElement, "Voici la liste de nos services disponibles : Cliquez-pour plus de details");
      await displayServiceButtons(data.services);
      

    }else if (data.type === "tracking" && data.data) {

    // 🔥 animation texte d'abord
    await typeText(messageElement, data.reponse);

    // 🔥 ensuite affichage propre
    const d = data.data;

    const trackingHTML = `
      📦 <b>Code colis</b> : ${d.code}<br>
      🚚 <b>Transport</b> : ${d.transport}<br>
      📌 <b>Statut</b> : ${d.statut}<br>
      📦 <b>Type</b> : ${d.type_colis}<br>
      🕒 <b>Dernière mise à jour</b> : ${d.derniere_maj}
    `;

    const trackingDiv = createMessageElement(
      `<div class="message-text">${trackingHTML}</div>`,
      "bot-message"
    );

    chatBody.appendChild(trackingDiv);

  }else if (data.type === "erreur_suivi_colis") {
  await typeText(messageElement, data.reponse);
  }else {
    const botText = data.response || data.reponse || "Pas de réponse disponible.";
    await typeText(messageElement, botText);
  }

    if (data.agent) await displayAgentButtons(data.agent);

  } catch (error) {
    console.error(error);
    messageElement.innerText = "Erreur serveur, veuillez réessayer.";
    messageElement.style.color = "#ff0000";
  } finally {
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
  messageInput.dispatchEvent(new Event("input"));

  const userMessageDiv = createMessageElement(`<div class="message-text">${userData.message}</div>`, "user-message");
  chatBody.appendChild(userMessageDiv);
    
  const botThinkingDiv = createMessageElement(
    `<div class="message-text">
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
  chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });

  generateBotResponse(botThinkingDiv);
};

// ==========================================================
// EVENTS
// ==========================================================
messageInput.addEventListener("keydown", (e) => {
  const userMessage = e.target.value.trim();
  if (e.key === "Enter" && userMessage && !e.shiftKey && window.innerWidth > 768) {
    handleOutgoingMessage(e);
  }
});

messageInput.addEventListener("input", () => {
  messageInput.style.height = `${initialInputHeight}px`;
  messageInput.style.height = `${messageInput.scrollHeight}px`;
  document.querySelector(".chat-form").style.borderRadius =
    messageInput.scrollHeight > initialInputHeight ? "15px" : "32px";
});

sendMessageButton.addEventListener("click", (e) => handleOutgoingMessage(e));
chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));
closeChatbot.addEventListener("click", () => document.body.classList.remove("show-chatbot"));

// ==========================================================
// QUICK BUTTONS
// ==========================================================
document.querySelectorAll(".quick-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const action = btn.dataset.action;
    if (action === "agent") { handleContactAgent(); return; }
    let message = "";
    if (action === "services") message = "Pouvez-vous me donner des infos sur vos services ?";
    if (action === "suivi_colis") message = "Je veux suivre mon colis";
    messageInput.value = message;
    sendMessageButton.click();
  });
});

// ==========================================================
// CONTACT AGENT (APPARITION PROGRESSIVE)
// ==========================================================
async function handleContactAgent() {
  const userMessageDiv = createMessageElement(`<div class="message-text">Je souhaite contacter un agent.</div>`, "user-message");
  chatBody.appendChild(userMessageDiv);

  const botDiv = createMessageElement(`<div class="message-text"></div>`, "bot-message");
  chatBody.appendChild(botDiv);

  await typeText(botDiv.querySelector(".message-text"), "Bien reçu !!! Pour contacter un agent, veuillez choisir une option afin que je puisse vous mettre en contact avec nos agents.");

  try {
    const token = localStorage.getItem("token");
    if (!token) { await typeText(botDiv.querySelector(".message-text"), "Vous devez être connecté."); return; }

    const response = await fetch("http://127.0.0.1:5000/api/agent/contact-agent", {
      method: "GET",
      headers: { "Authorization": `Bearer ${token}` }
    });

    const data = await response.json();
    if (data.status === "succes" || data.status === "success") await displayAgentButtons(data.agent);
    else await typeText(botDiv.querySelector(".message-text"), "Aucun agent disponible pour le moment.");
  } catch (error) {
    console.error(error);
    await typeText(botDiv.querySelector(".message-text"), "Impossible de récupérer les informations de contact.");
  }
}

// ==========================================================
// AFFICHER LES BOUTONS POUR CONTACTER UN AGENT (APPARITION PROGRESSIVE)
// ==========================================================
async function displayAgentButtons(agent = { whatsapp: "", email: "", telephone: "" }, delay = 200) {
  const contactDiv = document.createElement("div");
  contactDiv.classList.add("agent-contact");
  chatBody.appendChild(contactDiv);

  const buttons = [];

  if (agent.whatsapp) {
    const btn = document.createElement("a");
    btn.href = "https://wa.me/" + agent.whatsapp;
    btn.innerText = "💬 WhatsApp";
    btn.target = "_blank";
    buttons.push(btn);
  }
  if (agent.email) {
    const btn = document.createElement("a");
    btn.href = "mailto:" + agent.email;
    btn.innerText = "📧 Email";
    buttons.push(btn);
  }
  if (agent.telephone) {
    const btn = document.createElement("a");
    btn.href = "tel:" + agent.telephone;
    btn.innerText = "📞 Appeler";
    buttons.push(btn);
  }

  for (const btn of buttons) {
    contactDiv.appendChild(btn);
    chatBody.scrollTo({ top: chatBody.scrollHeight, behavior: "smooth" });
    await new Promise(r => setTimeout(r, delay));
  }
}


// Ouverture automatique pop up
window.addEventListener("load", () => {
  setTimeout(() => {
    document.body.classList.add("show-chatbot");
  }, 1200);
});