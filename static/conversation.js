async function loadConversations() {
  const res = await fetch("/api/auth/discussion");
  return await res.json();
}

function getBadge(conf) {
  if (conf >= 0.8) return "ok";
  if (conf >= 0.5) return "low";
  return "bad";
}

async function renderConversations() {
  const data = await loadConversations();

  const container = document.getElementById("conversationList");

  container.innerHTML = data.map(c => `
    <div class="conv-card">

      <div class="conv-header">
        <span>👤 User: ${c.username || c.user_id}</span>
        <span>🕒 ${c.date}</span>
      </div>

      <div class="user-msg">
        🧑 ${c.message}
      </div>

      <div class="bot-msg">
        🤖 ${c.response}
      </div>

      <div style="margin-top:8px;">
        <span class="badge ${getBadge(c.confidence)}">
          confidence: ${c.confidence}
        </span>

        <span class="badge ok">
          ${c.operation || "no-op"}
        </span>
      </div>

    </div>
  `).join("");
}

renderConversations();