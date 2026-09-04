const slipsEl = document.getElementById("slips");
const statusEl = document.getElementById("status");
const refreshBtn = document.getElementById("refresh-btn");

const VOTER_KEY = "obedy_voter_id";

function getVoterId() {
  let id = localStorage.getItem(VOTER_KEY);
  if (!id) {
    id = crypto.randomUUID();
    localStorage.setItem(VOTER_KEY, id);
  }
  return id;
}

const voterId = getVoterId();

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

async function loadMenus() {
  try {
    const res = await fetch("/api/menus", {
      headers: { "X-Voter-Id": voterId },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    renderRestaurants(data.restaurants || [], data.note);
  } catch (err) {
    statusEl.textContent = "Nepodařilo se načíst menu. Zkontroluj, že backend běží.";
    console.error(err);
  }
}

function renderRestaurants(restaurants, note) {
  slipsEl.innerHTML = "";

  if (!restaurants.length) {
    const p = document.createElement("p");
    p.className = "status";
    p.textContent = note || "Zatím tu nejsou žádné restaurace. Doplň je v backend/restaurants.py.";
    slipsEl.appendChild(p);
    return;
  }

  const maxVotes = Math.max(...restaurants.map((r) => r.votes || 0));

  restaurants.forEach((r) => {
    const slip = document.createElement("article");
    const isLeading = maxVotes > 0 && r.votes === maxVotes;
    slip.className = "slip" + (isLeading ? " slip--leading" : "");

    const itemsHtml = (r.items || [])
      .map(
        (item) => `
        <li class="slip__item">
          <span class="slip__item-name">${escapeHtml(item.name)}</span>
          <span class="slip__leader"></span>
          <span class="slip__price">${escapeHtml(item.price || "")}</span>
        </li>`
      )
      .join("");

    slip.innerHTML = `
      <div class="slip__header">
        <h2 class="slip__name">
          ${r.url ? `<a href="${escapeHtml(r.url)}" target="_blank" rel="noopener">${escapeHtml(r.name)}</a>` : escapeHtml(r.name)}
        </h2>
        ${r.address ? `<p class="slip__address">${escapeHtml(r.address)}</p>` : ""}
      </div>
      <ul class="slip__items">
        ${itemsHtml || '<li class="slip__empty">Dnešní menu se nepodařilo rozpoznat.</li>'}
      </ul>
      ${r.error ? `<p class="slip__error">${escapeHtml(r.error)}</p>` : ""}
      <div class="slip__footer">
        <button class="vote-btn" data-id="${escapeHtml(r.id)}" aria-pressed="${r.my_vote ? "true" : "false"}">
          ${r.my_vote ? "✓ Tvoje volba" : "Hlasovat"}
        </button>
        <span class="vote-count">
          ${isLeading ? '<span class="leading-badge">VEDE &middot; </span>' : ""}${r.votes || 0} ${voteWord(r.votes || 0)}
        </span>
      </div>
    `;
    slipsEl.appendChild(slip);
  });

  slipsEl.querySelectorAll(".vote-btn").forEach((btn) => {
    btn.addEventListener("click", () => castVote(btn.dataset.id));
  });
}

function voteWord(n) {
  if (n === 1) return "hlas";
  if (n >= 2 && n <= 4) return "hlasy";
  return "hlasů";
}

async function castVote(restaurantId) {
  try {
    const res = await fetch("/api/vote", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Voter-Id": voterId,
      },
      body: JSON.stringify({ restaurant_id: restaurantId }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    await loadMenus(); // znovu vykreslí se čerstvými počty hlasů
  } catch (err) {
    console.error("Hlasování selhalo", err);
  }
}

async function refreshMenus() {
  statusEl.style.display = "block";
  statusEl.textContent = "Stahuji čerstvá data…";
  slipsEl.innerHTML = "";
  slipsEl.appendChild(statusEl);
  try {
    await fetch("/api/menus/refresh", { method: "POST" });
  } finally {
    loadMenus();
  }
}

refreshBtn.addEventListener("click", refreshMenus);

loadMenus();
// lehký polling počtu hlasů, ať kolegové vidí aktuální stav bez ručního refreshe
setInterval(loadMenus, 20000);
