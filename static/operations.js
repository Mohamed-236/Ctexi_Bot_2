/* =========================
   VARIABLE GLOBALE
========================= */
let currentOp = null;


/* =========================
   LOAD OPERATIONS
========================= */
async function loadOperations() {

  const res = await fetch("/api/dashboard/operations/list");
  const data = await res.json();

  document.getElementById("opList").innerHTML = data.map(op => `
    <div class="card">

      <div>
        <h3>${op.name}</h3>
        <p>${op.description}</p>

        <span class="status ${op.active ? 'active' : 'inactive'}">
          ${op.active ? "Actif" : "Inactif"}
        </span>
      </div>

      <div>
        <button onclick="selectOperation(${op.id}, '${op.name}')">
          Voir Patterns
        </button>

        <button onclick="deleteOp(${op.id})">
          Supprimer
        </button>
      </div>

    </div>
  `).join("");
}


/* =========================
   SELECTION OPERATION
========================= */
function selectOperation(id, name) {

  currentOp = id;

  document.getElementById("selectedOpText").innerText =
    "Opération sélectionnée : " + name;

  loadPatterns(id);
}


/* =========================
   ADD OPERATION
========================= */
async function addOperation() {

  const name = document.getElementById("name").value;
  const description = document.getElementById("description").value;

  await fetch("/api/dashboard/operations/add", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({name, description})
  });

  loadOperations();
}


/* =========================
   DELETE OPERATION
========================= */
async function deleteOp(id) {

  await fetch(`/api/dashboard/operations/delete/${id}`, {
    method: "DELETE"
  });

  loadOperations();

  if (currentOp === id) {
    document.getElementById("patternList").innerHTML = "";
    document.getElementById("selectedOpText").innerText =
      "Aucune opération sélectionnée";
    currentOp = null;
  }
}


/* =========================
   LOAD PATTERNS
========================= */
async function loadPatterns(op_id) {

  const res = await fetch(`/api/dashboard/operations/patterns/${op_id}`);
  const data = await res.json();

  document.getElementById("patternList").innerHTML = data.map(p => `
    <div class="card">

      <p>🧠 ${p.phrase}</p>

      <button onclick="deletePattern(${p.id}, ${op_id})">
        Supprimer
      </button>

    </div>
  `).join("");
}


/* =========================
   ADD PATTERN
========================= */
async function addPattern() {

  const intent_id = document.getElementById("intent_id").value;
  const phrase = document.getElementById("phrase").value;

  if (!currentOp) {
    alert("Veuillez sélectionner une opération d'abord");
    return;
  }

  if (!phrase) {
    alert("Veuillez saisir une phrase");
    return;
  }

  await fetch("/api/dashboard/operations/patterns/add", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      operation_id: currentOp,
      intent_id,
      phrase
    })
  });

  loadPatterns(currentOp);

  document.getElementById("phrase").value = "";
}


/* =========================
   DELETE PATTERN
========================= */
async function deletePattern(id, op_id) {

  await fetch(`/api/dashboard/operations/patterns/delete/${id}`, {
    method: "DELETE"
  });

  loadPatterns(op_id);
}


/* =========================
   INIT
========================= */
loadOperations();