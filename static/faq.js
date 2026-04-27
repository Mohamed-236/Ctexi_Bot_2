let faqs = [];

/* =====================
   LOAD FAQ
===================== */
async function loadFaq() {
  const res = await fetch("/api/dashboard/faq/list");
  faqs = await res.json();
  renderFaq(faqs);
}

/* =====================
   RENDER
===================== */
function renderFaq(data) {
  const container = document.getElementById("faqList");

  container.innerHTML = data.map(f => `
    <div class="faq-card">

      <div class="faq-header">
        <span>ID Intent: ${f.intent}</span>
        <span>${f.date}</span>
      </div>

      <div class="faq-question">
        ❓ ${f.question}
      </div>

      <div class="faq-response">
        🤖 ${f.response}
      </div>

      <div class="faq-actions">
        <button onclick="editFaq(${f.id})">Modifier</button>
        <button onclick="deleteFaq(${f.id})">Supprimer</button>
      </div>

    </div>
  `).join("");
}

/* =====================
   ADD FAQ
===================== */
async function addFaq() {

  const intent = document.getElementById("intent").value;
  const question = document.getElementById("question").value;
  const response = document.getElementById("response").value;

  await fetch("/api/dashboard/faq/add", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({intent, question, response})
  });

  loadFaq();
}

/* =====================
   DELETE FAQ
===================== */
async function deleteFaq(id) {

  if (!confirm("Supprimer cette FAQ ?")) return;

  await fetch(`/api/dashboard/faq/delete/${id}`, {
    method: "DELETE"
  });

  loadFaq();
}

/* =====================
   EDIT FAQ
===================== */
async function editFaq(id) {

  const intent = prompt("Nouvel intent ID ?");
  const question = prompt("Nouvelle question ?");
  const response = prompt("Nouvelle réponse ?");

  await fetch(`/api/dashboard/faq/update/${id}`, {
    method: "PUT",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({intent, question, response})
  });

  loadFaq();
}

/* =====================
   SEARCH
===================== */
async function searchFaq() {

  const q = document.getElementById("search").value;

  const res = await fetch(`/api/dashboard/faq/search?q=${q}`);
  const data = await res.json();

  renderFaq(data);
}

loadFaq();




async function loadOperations() {
  const res = await fetch("/api/dashboard/operations/list");
  const data = await res.json();

  const container = document.getElementById("operationsTab");

  container.innerHTML = data.map(op => `
    <div class="card">

      <h3>${op.name}</h3>
      <p>${op.description}</p>

      <span class="${op.active ? 'ok' : 'bad'}">
        ${op.active ? "Actif" : "Inactif"}
      </span>

      <button onclick="toggleOp(${op.id})">Toggle</button>
      <button onclick="deleteOp(${op.id})">Delete</button>

    </div>
  `).join("");
}

async function deleteOp(id) {
  await fetch(`/api/dashboard/operations/delete/${id}`, {
    method: "DELETE"
  });
  loadOperations();
}

async function toggleOp(id) {
  await fetch(`/api/dashboard/operations/toggle/${id}`, {
    method: "PUT"
  });
  loadOperations();
}