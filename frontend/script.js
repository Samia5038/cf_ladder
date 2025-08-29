async function fetchLadder() {
  const handle = "Samia5038";
  const min = document.getElementById("minRating").value;
  const max = document.getElementById("maxRating").value;
  const sort = document.getElementById("sortKey").value;

  try {
    const res = await fetch(`http://127.0.0.1:5000/api/ladder?handle=${handle}&min=${min}&max=${max}&sort=${sort}`);
    const data = await res.json();
    renderTable(data);
  } catch (err) {
    console.error(err);
    alert("Failed to fetch ladder. Make sure backend is running.");
  }
}

function renderTable(data) {
  const tbody = document.querySelector("#ladder tbody");
  tbody.innerHTML = "";
  data.forEach((p, i) => {
    const row = document.createElement("tr");

    const tags = p.tags.map(t => `<span class="tag">${t}</span>`).join(" ");
    row.innerHTML = `
      <td>${i+1}</td>
      <td><a href="${p.link}" target="_blank">${p.index} — ${p.name}</a></td>
      <td>${p.contestName}</td>
      <td>${p.division}</td>
      <td>${p.rating}</td>
      <td>${p.solvedCount}</td>
      <td>${tags}</td>
    `;
    tbody.appendChild(row);
  });
}

// Initial fetch
fetchLadder();

// Apply filters button
document.getElementById("applyFilters").addEventListener("click", fetchLadder);
