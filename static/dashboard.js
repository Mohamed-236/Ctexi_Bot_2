/* ================= USERS CHART ================= */
new Chart(document.getElementById("usersChart"), {
  type: "line",
  data: {
    labels: ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"],
    datasets: [{
      label: "Utilisateurs",
      data: [10, 20, 35, 40, 60, 80, 100],
      borderColor: "#1d4ed8",
      fill: false
    }]
  }
});

/* ================= CONVERSATIONS ================= */
new Chart(document.getElementById("convChart"), {
  type: "bar",
  data: {
    labels: ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"],
    datasets: [{
      label: "Conversations",
      data: [5, 15, 25, 30, 45, 60, 70],
      backgroundColor: "#3b82f6"
    }]
  }
});

/* ================= INTENTS ================= */
new Chart(document.getElementById("intentChart"), {
  type: "doughnut",
  data: {
    labels: ["FAQ", "Conversion", "Tracking", "Agent", "Fallback"],
    datasets: [{
      data: [40, 20, 15, 10, 15],
      backgroundColor: [
        "#1d4ed8",
        "#40eb49",
        "#60a5fa",
        "#93c5fd",
        "#ca2a88"
      ]
    }]
  }
});