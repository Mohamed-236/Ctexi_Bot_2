let allConversations = [];

/* =========================
   CHARGER LES CONVERSATIONS
========================= */
async function loadConversations(userId = null) {
  let url = "/api/dashboard/discussion";

  if (userId) {
    url += `?user_id=${userId}`;
  }

  const res = await fetch(url);
  const data = await res.json();

  allConversations = data;
  renderConversations(data);
}

/* =========================
   RENDU UI
========================= */
function renderConversations(data) {
  const container = document.getElementById("conversationList");

  if (!data || data.length === 0) {
    container.innerHTML = "<p>Aucune conversation trouvée.</p>";
    return;
  }

  container.innerHTML = data.map(c => `
    <div class="conv-card">

      <div class="conv-header">
        <span>👤 ${c.username || "User"} (ID: ${c.user_id})</span>
        <span>🕒 ${c.date}</span>
      </div>

      <div class="user-msg">
        🧑 ${c.message}
      </div>

      <div class="bot-msg">
        🤖 ${c.response || "Pas de réponse"}
      </div>

      <div class="conv-footer">

        <span class="badge ${getBadge(c.confidence)}">
          confidence: ${c.confidence}
        </span>

        <span class="badge ok">
          ${c.operation || "no-op"}
        </span>

        <button class="delete-btn" onclick="deleteConversation(${c.id})">
          Supprimer
        </button>

      </div>

    </div>
  `).join("");
}

/* =========================
   BADGE CONFIDENCE
========================= */
function getBadge(conf) {
  if (conf >= 0.8) return "ok";
  if (conf >= 0.5) return "low";
  return "bad";
}

/* =========================
   SUPPRESSION CONVERSATION
========================= */
async function deleteConversation(id) {
  if (!confirm("Voulez-vous vraiment supprimer cette conversation ?")) return;

  await fetch(`/api/dashboard/delete/${id}`, {
    method: "DELETE"
  });

  // recharger après suppression
  loadConversations();
}

/* =========================
   FILTRER PAR USER
========================= */
function filterByUser() {
  const userId = document.getElementById("userFilter").value;

  if (!userId) {
    loadConversations();
  } else {
    loadConversations(userId);
  }
}

/* =========================
   RECHERCHE TEXTE
========================= */
document.getElementById("searchInput").addEventListener("input", function () {
  const value = this.value.toLowerCase();

  const filtered = allConversations.filter(c =>
    c.message.toLowerCase().includes(value) ||
    (c.response && c.response.toLowerCase().includes(value)) ||
    (c.username && c.username.toLowerCase().includes(value))
  );

  renderConversations(filtered);
});

/* =========================
   INITIAL LOAD
========================= */
loadConversations();