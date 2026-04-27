let data = { users: [], agents: [] };

async function loadData() {
  const res = await fetch("/api/dashboard/admin/users-agents");
  data = await res.json();

  renderUsers();
  renderAgents();
}

/* ================= USERS ================= */
function renderUsers() {
  const container = document.getElementById("usersTab");

  container.innerHTML = data.users.map(u => `
    <div class="card">

      <div class="card-header">
        <h3>${u.nom} ${u.prenom}</h3>
        <span class="badge ${u.is_admin ? 'admin' : 'user'}">
          ${u.is_admin ? "Admin" : "User"}
        </span>
      </div>

      <div class="card-body">
        <p>📧 ${u.email}</p>
        <p>📞 ${u.telephone}</p>
        <p class="date">📅 ${u.date}</p>
      </div>

      <div class="card-actions">
        <button class="danger" onclick="deleteUser(${u.id})">Supprimer</button>
      </div>

    </div>
  `).join("");
}

/* ================= AGENTS ================= */
function renderAgents() {
  const container = document.getElementById("agentsTab");

  container.innerHTML = data.agents.map(a => `
    <div class="card">

      <div class="card-header">
        <h3>Agent #${a.id}</h3>
        <span class="badge ${a.actif ? 'active' : 'inactive'}">
          ${a.actif ? "Actif" : "Inactif"}
        </span>
      </div>

      <div class="card-body">
        <p>🎯 Intent: ${a.intent}</p>
        <p>📧 ${a.email}</p>
        <p>📞 ${a.telephone}</p>
        <p>💬 ${a.whatsapp}</p>
        <p class="date">📅 ${a.date}</p>
      </div>

      <div class="card-actions">
        <button onclick="toggleAgent(${a.id})">Activer</button>
        <button class="danger" onclick="deleteAgent(${a.id})">Supprimer</button>
      </div>

    </div>
  `).join("");
}

/* ================= ACTIONS ================= */
async function deleteUser(id) {
  await fetch(`/api/dashboard/user/delete/${id}`, { method: "DELETE" });
  loadData();
}

async function deleteAgent(id) {
  await fetch(`/api/dashboard/agent/delete/${id}`, { method: "DELETE" });
  loadData();
}

async function toggleAgent(id) {
  await fetch(`/api/dashboard/agent/toggle/${id}`, { method: "PUT" });
  loadData();
}

/* ================= TABS ================= */
function showTab(tab) {
  document.getElementById("usersTab").style.display = tab === "users" ? "grid" : "none";
  document.getElementById("agentsTab").style.display = tab === "agents" ? "grid" : "none";

  document.querySelectorAll(".tab-btn").forEach(btn => btn.classList.remove("active"));
}

loadData();