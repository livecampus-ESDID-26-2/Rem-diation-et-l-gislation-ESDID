(() => {
  const state = {
    manifest: null,
    currentId: null,
  };

  const els = {
    nav: document.querySelector("#nav"),
    search: document.querySelector("#search"),
    viewer: document.querySelector("#viewer"),
    welcome: document.querySelector("#welcome"),
    title: document.querySelector("#doc-title"),
    openTab: document.querySelector("#open-tab"),
    meta: document.querySelector("#sidebar-meta"),
    menuToggle: document.querySelector("#menu-toggle"),
  };

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function itemKey(categoryId, itemId) {
    return `${categoryId}/${itemId}`;
  }

  function findItem(id) {
    if (!state.manifest) return null;
    for (const category of state.manifest.categories) {
      for (const item of category.items) {
        if (itemKey(category.id, item.id) === id) {
          return { category, item };
        }
      }
    }
    return null;
  }

  function renderNav(filter = "") {
    const q = filter.trim().toLowerCase();
    const parts = [];

    for (const category of state.manifest.categories) {
      const links = category.items
        .map((item) => {
          const label = item.title;
          const hay = `${category.label} ${label}`.toLowerCase();
          const hidden = q && !hay.includes(q);
          const id = itemKey(category.id, item.id);
          const active = id === state.currentId ? "is-active" : "";
          const hide = hidden ? "is-hidden" : "";
          return `<li>
            <button type="button" class="nav-link ${active} ${hide}" data-id="${escapeHtml(id)}" data-path="${escapeHtml(item.path)}">
              ${escapeHtml(label)}
            </button>
          </li>`;
        })
        .join("");

      parts.push(`
        <section class="nav-section" data-category="${escapeHtml(category.id)}">
          <h2 class="nav-section__label">${escapeHtml(category.label)}</h2>
          <ul class="nav-list">${links}</ul>
        </section>
      `);
    }

    els.nav.innerHTML = parts.join("");
  }

  function showDocument(id, { pushHash = true } = {}) {
    const found = findItem(id);
    if (!found) return;

    state.currentId = id;
    renderNav(els.search.value);

    els.welcome.hidden = true;
    els.viewer.hidden = false;
    els.viewer.src = found.item.path;
    els.title.textContent = found.item.title;
    els.openTab.href = found.item.path;
    els.openTab.hidden = false;

    if (pushHash) {
      const hash = `#${encodeURIComponent(id)}`;
      if (location.hash !== hash) {
        history.pushState({ id }, "", hash);
      }
    }

    document.body.classList.remove("nav-open");
  }

  function showWelcome() {
    state.currentId = null;
    renderNav(els.search.value);
    els.viewer.hidden = true;
    els.viewer.removeAttribute("src");
    els.welcome.hidden = false;
    els.title.textContent = "Bibliothèque";
    els.openTab.hidden = true;
    document.body.classList.remove("nav-open");
  }

  function loadFromHash() {
    const raw = decodeURIComponent((location.hash || "").replace(/^#/, ""));
    if (!raw) {
      showWelcome();
      return;
    }
    if (findItem(raw)) {
      showDocument(raw, { pushHash: false });
    } else {
      showWelcome();
    }
  }

  async function init() {
    try {
      const res = await fetch("manifest.json", { cache: "no-store" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      state.manifest = await res.json();
    } catch (err) {
      els.welcome.hidden = true;
      document.querySelector("#main-panel").innerHTML = `
        <div class="error">
          <h1>Manifeste introuvable</h1>
          <p>Générez les pages avec <code>./scripts/convert_qcm_to_pdf.sh</code> (ou <code>python3 scripts/convert_qcm_to_pdf.py --html-only</code>), puis rechargez.</p>
          <p>${escapeHtml(err.message)}</p>
        </div>
      `;
      return;
    }

    const count = state.manifest.categories.reduce((n, c) => n + c.items.length, 0);
    els.meta.textContent = `${count} document(s) · généré le ${state.manifest.generated || "—"}`;

    renderNav();
    els.nav.addEventListener("click", (event) => {
      const btn = event.target.closest(".nav-link");
      if (!btn) return;
      showDocument(btn.dataset.id);
    });

    els.search.addEventListener("input", () => renderNav(els.search.value));
    els.menuToggle.addEventListener("click", () => {
      document.body.classList.toggle("nav-open");
    });

    window.addEventListener("popstate", loadFromHash);
    loadFromHash();
  }

  init();
})();
