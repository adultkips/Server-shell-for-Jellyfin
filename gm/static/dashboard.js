
(function () {
  const STATS = window.DASH_STATS || {};
  const DEFAULT_FLAT = window.DASH_DEFAULT || [];
  const CFG = window.DASH_CFG || {};
  const LS_KEY = CFG.lsKey || "dash_cards_v1";
  const API_GET = CFG.apiGet || "/dash/layout";
  const API_SET = CFG.apiSet || "/dash/layout";
  const EMPTY = CFG.emptyToken || "__empty__";
  async function fetchServerLayout() {
    try {
      const r = await fetch(API_GET, { cache: "no-store" });
      if (r.status === 204) return null;
      if (!r.ok) return null;
      return await r.json();
    } catch (e) {
      return null;
    }
  }
  let persistTimer = null;
  function persistRowsDebounced(rows) {
    try {
      if (persistTimer) clearTimeout(persistTimer);
    } catch (e) {}
    persistTimer = setTimeout(async () => {
      try {
        await fetch(API_SET, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(rows),
        });
      } catch (e) {}
    }, 250);
  }
  async function deleteServerLayout() {
    try {
      await fetch(API_SET, { method: "DELETE" });
    } catch (e) {}
  }
  const rowsHost = document.getElementById("dashRows");
  const resetBtn = document.getElementById("dashReset");
  const picker = document.getElementById("dashPicker");
  const pickerList = document.getElementById("dashPickerList");
  const pickerClose = document.getElementById("dashPickerClose");
  const addTopBtn = document.getElementById("dashAddTop");
  const TOP_MODELS = Array.isArray(STATS.top_models) ? STATS.top_models : [];
  const TOP_STUDIOS = Array.isArray(STATS.top_studios) ? STATS.top_studios : [];
  const TOP_GENRES = Array.isArray(STATS.top_genres) ? STATS.top_genres : [];
  const FILMS_POOL = Array.isArray(STATS.films_pool) ? STATS.films_pool : [];
  const FILMS_LATEST = Array.isArray(STATS.films_latest) ? STATS.films_latest : [];
  function titleCase(s) {
    return String(s || "")
      .split(" ")
      .filter(Boolean)
      .map((w) => (w ? w[0].toUpperCase() + w.slice(1) : ""))
      .join(" ");
  }
  function imgUrlFromId(id) {
    if (!id) return "";
    return (CFG.jellyfinUrl || "") + "/Items/" + encodeURIComponent(id) + "/Images/Primary";
  }
  function jfDetailsUrlFromId(id) {
    const base = (CFG.jellyfinUrl || "") + "/web/index.html";
    if (!id) return base;
    return (
      base +
      "#/details?id=" +
      encodeURIComponent(id) +
      "&serverId=" +
      encodeURIComponent(CFG.serverId || "")
    );
  }
  function topEntry(kind, idx) {
    const i = Math.max(0, (parseInt(idx, 10) || 1) - 1);
    if (kind === "model") return TOP_MODELS[i] || null;
    if (kind === "studio") return TOP_STUDIOS[i] || null;
    if (kind === "genre") return TOP_GENRES[i] || null;
    return null;
  }
  function cardBgHtml(cardId) {
    const m = /^top_(model|studio|genre)_(\d+)$/.exec(cardId || "");
    if (!m) return "";
    const entry = topEntry(m[1], m[2]);
    if (!entry || !entry.id) return "";
    const url = imgUrlFromId(entry.id);
    if (!url) return "";
    return `<div class="dashCardBg" style="background-image:url('${url}')"></div>`;
  }
  function topHref(kind, entry) {
    if (kind === "model") {
      return entry && entry.name ? `films.html?model=${encodeURIComponent(entry.name)}` : "models.html";
    }
    if (kind === "studio") {
      return entry && entry.name ? `films.html?studio=${encodeURIComponent(entry.name)}` : "studios.html";
    }
    if (kind === "genre") {
      return entry && entry.name ? `films.html?genre=${encodeURIComponent(entry.name)}` : "genres.html";
    }
    return "films.html";
  }
  function isVertCard(cardId) {
    return /^vert_film_\d+$/.test(cardId || "");
  }
  function isLatestVertCard(cardId) {
    return /^vert_latest_\d+$/.test(cardId || "");
  }
  const CARD_DEFS = {
    films_total: {
      href: () => "films.html",
      number: () => STATS.films_total,
    },
    models_total: {
      href: () => "models.html",
      number: () => STATS.models_total,
    },
    studios_total: {
      href: () => "studios.html",
      number: () => STATS.studios_total,
    },
    genres_total: {
      href: () => "genres.html",
      number: () => STATS.genres_total,
    },
    films_missing_models: {
      href: () => "films.html?missing=NOPEOPLE",
      number: () => STATS.films_missing_models,
    },
    films_missing_studio: {
      href: () => "films.html?missing=NOSTUDIO",
      number: () => STATS.films_missing_studio,
    },
    films_missing_genre: {
      href: () => "films.html?missing=NOGENRE",
      number: () => STATS.films_missing_genre,
    },
    films_unwatched_total: {
      href: () => "films.html?missing=UNWATCHED",
      number: () => STATS.films_unwatched_total,
    },
    vert_latest_1: { href: () => "films.html" },
    vert_latest_2: { href: () => "films.html" },
    vert_latest_3: { href: () => "films.html" },
    vert_latest_4: { href: () => "films.html" },
    vert_film_1: { href: () => "films.html" },
    vert_film_2: { href: () => "films.html" },
    vert_film_3: { href: () => "films.html" },
    vert_film_4: { href: () => "films.html" },
    top_model_1: { href: () => topHref("model", topEntry("model", 1)), topKind: "model", topIdx: 1 },
    top_model_2: { href: () => topHref("model", topEntry("model", 2)), topKind: "model", topIdx: 2 },
    top_model_3: { href: () => topHref("model", topEntry("model", 3)), topKind: "model", topIdx: 3 },
    top_model_4: { href: () => topHref("model", topEntry("model", 4)), topKind: "model", topIdx: 4 },
    top_studio_1: { href: () => topHref("studio", topEntry("studio", 1)), topKind: "studio", topIdx: 1 },
    top_studio_2: { href: () => topHref("studio", topEntry("studio", 2)), topKind: "studio", topIdx: 2 },
    top_studio_3: { href: () => topHref("studio", topEntry("studio", 3)), topKind: "studio", topIdx: 3 },
    top_studio_4: { href: () => topHref("studio", topEntry("studio", 4)), topKind: "studio", topIdx: 4 },
    top_genre_1: { href: () => topHref("genre", topEntry("genre", 1)), topKind: "genre", topIdx: 1 },
    top_genre_2: { href: () => topHref("genre", topEntry("genre", 2)), topKind: "genre", topIdx: 2 },
    top_genre_3: { href: () => topHref("genre", topEntry("genre", 3)), topKind: "genre", topIdx: 3 },
    top_genre_4: { href: () => topHref("genre", topEntry("genre", 4)), topKind: "genre", topIdx: 4 },
  };
  const TOTAL_LABELS = {
    films_total: "FILMS",
    models_total: "MODELS",
    studios_total: "STUDIOS",
    genres_total: "GENRES",
    films_unwatched_total: "UNWATCHED",
  };
  const MISSING_LABELS = {
    films_missing_models: "MODELS",
    films_missing_studio: "STUDIOS",
    films_missing_genre: "GENRES",
  };
  function buildLines(cardId) {
    if (isVertCard(cardId) || isLatestVertCard(cardId)) {
      return { mode: "vert", lines: [] };
    }
    if (TOTAL_LABELS[cardId]) {
      return {
        mode: "total",
        lines: ["TOTAL", TOTAL_LABELS[cardId], String(CARD_DEFS[cardId].number())],
      };
    }
    if (MISSING_LABELS[cardId]) {
      return {
        mode: "missing",
        lines: ["MISSING", MISSING_LABELS[cardId], String(CARD_DEFS[cardId].number())],
      };
    }
    const m = /^top_(model|studio|genre)_(\d+)$/.exec(cardId || "");
    if (m) {
      const kind = m[1];
      const idx = parseInt(m[2], 10) || 1;
      const entry = topEntry(kind, idx);
      const title = (kind || "").toUpperCase();
      const name = entry && entry.name ? titleCase(entry.name) : "â€”";
      const count = entry && typeof entry.count !== "undefined" ? String(entry.count) : "0";
      return {
        mode: "top",
        lines: ["TOP #" + idx, title, name, count],
      };
    }
    return { mode: "other", lines: [cardId, "", ""] };
  }
  function shapeForInfo(info) {
    if (!info || !info.mode) return "square";
    if (info.mode === "top") return "rect";
    if (info.mode === "vert") return "vert";
    return "square";
  }
  function shapeForCardId(cardId) {
    if (isVertCard(cardId) || isLatestVertCard(cardId)) return "vert";
    const info = buildLines(cardId);
    return shapeForInfo(info);
  }
  function normalizeRows(raw) {
    const rows = [];
    function pushCard(id) {
      if (!id || !CARD_DEFS[id]) return;
      const shape = shapeForCardId(id);
      const last = rows.length ? rows[rows.length - 1] : null;
      const cap = 4;
      if (!last || last.shape !== shape || (last.cards && last.cards.length >= cap)) {
        rows.push({ shape, cards: [id] });
      } else {
        last.cards.push(id);
      }
    }
    if (Array.isArray(raw) && raw.length && typeof raw[0] === "object" && raw[0] && Array.isArray(raw[0].cards)) {
      for (const r of raw) {
        const shape = r.shape === "rect" ? "rect" : r.shape === "vert" ? "vert" : "square";
        const rawCards = Array.isArray(r.cards) ? r.cards : [];
        const cards = [];
        for (const id of rawCards) {
          if (id === EMPTY && shape === "square") {
            cards.push(EMPTY);
            continue;
          }
          if (CARD_DEFS[id]) cards.push(id);
        }
        while (cards.length > 4) cards.pop();
        if (shape === "square") {
          while (cards.length < 4 && cards.includes(EMPTY)) cards.push(EMPTY);
          rows.push({ shape, cards });
          continue;
        }
        const filtered = cards.filter((x) => x !== EMPTY);
        if (filtered.length) rows.push({ shape, cards: filtered });
      }
      return rows;
    }
    if (Array.isArray(raw)) {
      for (const id of raw) pushCard(id);
      return rows;
    }
    return rows;
  }
  function loadRows() {
    try {
      const raw = localStorage.getItem(LS_KEY);
      if (!raw) return normalizeRows(DEFAULT_FLAT);
      const parsed = JSON.parse(raw);
      const rows = normalizeRows(parsed);
      saveRows(rows);
      return rows;
    } catch (e) {
      const rows = normalizeRows(DEFAULT_FLAT);
      saveRows(rows);
      return rows;
    }
  }
  function saveRows(rows) {
    try {
      localStorage.setItem(LS_KEY, JSON.stringify(rows));
    } catch (e) {}
    persistRowsDebounced(rows);
  }
  function allCardIds(rows) {
    const out = [];
    for (const r of rows || []) {
      for (const id of r.cards || []) {
        if (id && id !== EMPTY) out.push(id);
      }
    }
    return out;
  }
  const PICKER_ITEMS = [
    { id: "films_total", title: "Total films", add: () => ["films_total"] },
    { id: "models_total", title: "Total models", add: () => ["models_total"] },
    { id: "studios_total", title: "Total studios", add: () => ["studios_total"] },
    { id: "genres_total", title: "Total genres", add: () => ["genres_total"] },
    { id: "films_unwatched_total", title: "Total unwatched", add: () => ["films_unwatched_total"] },
    { id: "films_missing_models", title: "Films missing models", add: () => ["films_missing_models"] },
    { id: "films_missing_studio", title: "Films missing studio", add: () => ["films_missing_studio"] },
    { id: "films_missing_genre", title: "Films missing genres", add: () => ["films_missing_genre"] },
    {
      id: "latest_films_group",
      title: "Latest films (4 cards)",
      add: () => ["vert_latest_1", "vert_latest_2", "vert_latest_3", "vert_latest_4"],
    },
    {
      id: "vert_films_group",
      title: "Random films (4 cards)",
      add: () => ["vert_film_1", "vert_film_2", "vert_film_3", "vert_film_4"],
    },
    {
      id: "top4_models_group",
      title: "Top 4 models",
      add: () => ["top_model_1", "top_model_2", "top_model_3", "top_model_4"],
    },
    {
      id: "top4_studios_group",
      title: "Top 4 studios",
      add: () => ["top_studio_1", "top_studio_2", "top_studio_3", "top_studio_4"],
    },
    {
      id: "top4_genres_group",
      title: "Top 4 genres",
      add: () => ["top_genre_1", "top_genre_2", "top_genre_3", "top_genre_4"],
    },
  ];
  const PICKER_ITEMS_SQUARE = PICKER_ITEMS.filter((it) => {
    const ids = it.add();
    return ids.length === 1 && shapeForCardId(ids[0]) === "square";
  });
  let pickerTarget = null;
  function addCardsRespectRows(idsToAdd) {
    const rows = loadRows();
    const have = new Set(allCardIds(rows));
    for (const cid of idsToAdd || []) {
      if (!cid || have.has(cid) || !CARD_DEFS[cid]) continue;
      const shape = shapeForCardId(cid);
      let target = null;
      for (let i = rows.length - 1; i >= 0; i--) {
        const r = rows[i];
        if (!r || r.shape !== shape || !Array.isArray(r.cards)) continue;
        const hasEmpty = r.cards.includes(EMPTY);
        const hasRoom = r.cards.length < 4;
        if (hasEmpty || hasRoom) {
          target = r;
          break;
        }
      }
      if (!target) {
        target = { shape, cards: [] };
        rows.push(target);
      }
      const ei = (target.cards || []).indexOf(EMPTY);
      if (ei >= 0) {
        target.cards[ei] = cid;
      } else {
        target.cards.push(cid);
      }
      have.add(cid);
    }
    saveRows(rows);
    draw();
  }
  function addCardIntoSquareSlot(rowIndex, slotIndex, cardId) {
    if (!cardId || !CARD_DEFS[cardId]) return false;
    if (shapeForCardId(cardId) !== "square") return false;
    const rows = loadRows();
    const ri = parseInt(rowIndex, 10);
    const si = parseInt(slotIndex, 10);
    if (!(ri >= 0 && ri < rows.length)) return false;
    const row = rows[ri];
    if (!row || row.shape !== "square" || !Array.isArray(row.cards)) return false;
    const have = new Set(allCardIds(rows));
    if (have.has(cardId)) return false;
    while (row.cards.length < 4) row.cards.push(EMPTY);
    if (row.cards[si] === EMPTY) {
      row.cards[si] = cardId;
    } else {
      const ei = row.cards.indexOf(EMPTY);
      if (ei < 0) return false;
      row.cards[ei] = cardId;
    }
    saveRows(rows);
    draw();
    return true;
  }
  const RAND_VERT_IDS = ["vert_film_1", "vert_film_2", "vert_film_3", "vert_film_4"];
  let RAND_VERT_MAP = null;
  function pickRandomVertSet() {
    if (RAND_VERT_MAP) return RAND_VERT_MAP;
    RAND_VERT_MAP = {};
    if (!FILMS_POOL.length) {
      for (const cid of RAND_VERT_IDS) RAND_VERT_MAP[cid] = "";
      return RAND_VERT_MAP;
    }
    const pool = FILMS_POOL.slice();
    for (let i = pool.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      const tmp = pool[i];
      pool[i] = pool[j];
      pool[j] = tmp;
    }
    const seen = new Set();
    const picked = [];
    for (const it of pool) {
      const id = it && it.id ? String(it.id) : "";
      if (!id || seen.has(id)) continue;
      seen.add(id);
      picked.push(id);
      if (picked.length >= 4) break;
    }
    for (let i = 0; i < RAND_VERT_IDS.length; i++) {
      RAND_VERT_MAP[RAND_VERT_IDS[i]] = picked[i] || "";
    }
    return RAND_VERT_MAP;
  }
  function renderRandomVertCard(cardId) {
    const map = pickRandomVertSet();
    const el = document.createElement("div");
    el.className = "dashCard dashVertCard";
    el.dataset.cardId = cardId;
    el.dataset.shape = "vert";
    const fid = map[cardId] || "";
    const obj = FILMS_POOL.find((x) => x && x.id === fid) || null;
    const name = obj && obj.name ? obj.name : "â€”";
    const href = jfDetailsUrlFromId(fid);
    const img = imgUrlFromId(fid);
    el.innerHTML = `
      <div class="dashVertBg" style="background-image:url('${img}')"></div>
      <button type="button" class="dashRemove" title="Remove">Ã—</button>
      <a class="dashVertLink" href="${href}" target="_blank" rel="noopener">
        <div class="dashVertText">
          <div class="dashVertName">${String(name)}</div>
        </div>
      </a>
    `;
    return el;
  }
  function latestFilmForCard(cardId) {
    const m = /^vert_latest_(\d+)$/.exec(cardId || "");
    if (!m) return null;
    const idx = Math.max(1, parseInt(m[1], 10) || 1) - 1;
    return FILMS_LATEST[idx] || null;
  }
  function renderLatestVertCard(cardId) {
    const el = document.createElement("div");
    el.className = "dashCard dashVertCard";
    el.dataset.cardId = cardId;
    el.dataset.shape = "vert";
    const obj = latestFilmForCard(cardId);
    const fid = obj && obj.id ? String(obj.id) : "";
    const name = obj && obj.name ? obj.name : "â€”";
    const href = jfDetailsUrlFromId(fid);
    const img = imgUrlFromId(fid);
    el.innerHTML = `
      <div class="dashVertBg" style="background-image:url('${img}')"></div>
      <button type="button" class="dashRemove" title="Remove">Ã—</button>
      <a class="dashVertLink" href="${href}" target="_blank" rel="noopener">
        <div class="dashVertText">
          <div class="dashVertName">${String(name)}</div>
        </div>
      </a>
    `;
    return el;
  }
  function removeRowAtIndex(rowIndex) {
    const rows = loadRows();
    const i = parseInt(rowIndex, 10);
    if (!(i >= 0 && i < rows.length)) return;
    rows.splice(i, 1);
    saveRows(rows);
    draw();
  }
  function confirmAndRemoveRow(rowIndex) {
    const ok = window.confirm("Remove this row and all its cards?");
    if (!ok) return;
    removeRowAtIndex(rowIndex);
  }
  function removeSquareCardLeavePlaceholder(cardId) {
    const rows = loadRows();
    for (let ri = 0; ri < rows.length; ri++) {
      const r = rows[ri];
      if (!r || r.shape !== "square" || !Array.isArray(r.cards)) continue;
      const idx = r.cards.indexOf(cardId);
      if (idx >= 0) {
        r.cards[idx] = EMPTY;
        while (r.cards.length < 4) r.cards.push(EMPTY);
        saveRows(rows);
        draw();
        return;
      }
    }
  }
  let draggingCard = false;
  let draggingCardId = "";
  function rowIndexOfCard(rows, cardId) {
    for (let ri = 0; ri < (rows || []).length; ri++) {
      const r = rows[ri];
      const idx = r && Array.isArray(r.cards) ? r.cards.indexOf(cardId) : -1;
      if (idx >= 0) return { ri, ci: idx };
    }
    return null;
  }
  function trySwapSquareCards(fromCardId, toCardId) {
    if (!fromCardId || !toCardId) return false;
    if (fromCardId === toCardId) return false;
    const rows = loadRows();
    const a = rowIndexOfCard(rows, fromCardId);
    const b = rowIndexOfCard(rows, toCardId);
    if (!a || !b) return false;
    const rowA = rows[a.ri];
    const rowB = rows[b.ri];
    if (!rowA || !rowB) return false;
    if (rowA.shape !== "square" || rowB.shape !== "square") return false;
    const cardA = rowA.cards[a.ci];
    const cardB = rowB.cards[b.ci];
    if (cardA === EMPTY || cardB === EMPTY) return false;
    if (shapeForCardId(cardA) !== "square") return false;
    if (shapeForCardId(cardB) !== "square") return false;
    rowA.cards[a.ci] = cardB;
    rowB.cards[b.ci] = cardA;
    saveRows(rows);
    draw();
    return true;
  }
  function attachSquareSwapDnD(cardEl) {
    if (!cardEl) return;
    const cardId = cardEl.dataset.cardId || "";
    if (!cardId) return;
    if (shapeForCardId(cardId) !== "square") return;
    cardEl.draggable = true;
    cardEl.addEventListener("dragstart", (e) => {
      draggingCard = true;
      draggingCardId = cardId;
      try {
        e.dataTransfer.effectAllowed = "move";
        e.dataTransfer.setData("text/plain", "card:" + cardId);
      } catch (err) {}
      try {
        e.stopPropagation();
      } catch (err) {}
      cardEl.classList.add("dragging");
    });
    cardEl.addEventListener("dragend", () => {
      draggingCard = false;
      draggingCardId = "";
      cardEl.classList.remove("dragging");
      rowsHost.querySelectorAll(".dashCard").forEach((x) => x.classList.remove("dropTarget"));
    });
    cardEl.addEventListener("dragover", (e) => {
      if (!draggingCard || !draggingCardId) return;
      if (draggingCardId === cardId) return;
      if (shapeForCardId(draggingCardId) !== "square") return;
      if (shapeForCardId(cardId) !== "square") return;
      e.preventDefault();
      try {
        e.dataTransfer.dropEffect = "move";
      } catch (err) {}
      cardEl.classList.add("dropTarget");
    });
    cardEl.addEventListener("dragleave", () => {
      cardEl.classList.remove("dropTarget");
    });
    cardEl.addEventListener("drop", (e) => {
      if (!draggingCard) return;
      e.preventDefault();
      cardEl.classList.remove("dropTarget");
      let payload = "";
      try {
        payload = e.dataTransfer.getData("text/plain") || "";
      } catch (err) {}
      const m = /^card:(.+)$/.exec(payload);
      const fromId = m && m[1] ? String(m[1]) : draggingCardId;
      const toId = cardId;
      trySwapSquareCards(fromId, toId);
    });
  }
  function renderSquarePlaceholder(rowIndex, slotIndex) {
    const el = document.createElement("button");
    el.type = "button";
    el.className = "dashCard dashPlaceholder dashShape-square";
    el.dataset.shape = "square";
    el.dataset.rowIndex = String(rowIndex);
    el.dataset.slotIndex = String(slotIndex);
    el.setAttribute("aria-label", "Add card");
    el.innerHTML = `
      <div class="dashPlaceholderPlus">+</div>
    `;
    el.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      pickerTarget = { rowIndex, slotIndex };
      openPicker(true);
    });
    return el;
  }
  function renderCard(cardId, rowIndex) {
    if (isLatestVertCard(cardId)) {
      const el = renderLatestVertCard(cardId);
      if (el) el.dataset.rowIndex = String(rowIndex);
      return el;
    }
    if (isVertCard(cardId)) {
      const el = renderRandomVertCard(cardId);
      if (el) el.dataset.rowIndex = String(rowIndex);
      return el;
    }
    const def = CARD_DEFS[cardId];
    if (!def) return null;
    const info = buildLines(cardId);
    const shape = shapeForInfo(info);
    const el = document.createElement("div");
    el.className = "dashCard";
    el.dataset.cardId = cardId;
    el.dataset.rowIndex = String(rowIndex);
    el.dataset.shape = shape;
    el.classList.add("dashShape-" + shape);
    if (info && info.mode === "top") el.classList.add("dashCardTop");
    const href = def.href();
    const bg = cardBgHtml(cardId);
    const lines = info.lines || [];
    const lineHtml = lines.map((t, i) => `<div class="dashLine dashLine${i + 1}">${String(t || "")}</div>`).join("");
    el.innerHTML = `
      ${bg}
      <button type="button" class="dashRemove" title="Remove">Ã—</button>
      <a class="dashLink" href="${href}">
        <div class="dashText dashMode-${info.mode}">
          ${lineHtml}
        </div>
      </a>
    `;
    if (shape === "square") {
      attachSquareSwapDnD(el);
    }
    return el;
  }
  let draggingRowIndex = -1;
  function renderRow(row, rowIndex) {
    const rowEl = document.createElement("div");
    rowEl.className = "dashRow";
    rowEl.draggable = true;
    rowEl.dataset.rowIndex = String(rowIndex);
    rowEl.dataset.shape = row.shape || "square";
    rowEl.classList.add("dashRow-" + (row.shape || "square"));
    rowEl.innerHTML = `
      <div class="dashRowInner">
        <div class="dashGrid"></div>
      </div>
    `;
    const gridEl = rowEl.querySelector(".dashGrid");
    const shape = row.shape || "square";
    if (shape === "square") {
      const cards = Array.isArray(row.cards) ? row.cards.slice(0, 4) : [];
      while (cards.length < 4) cards.push(EMPTY);
      for (let i = 0; i < 4; i++) {
        const cid = cards[i];
        if (!cid || cid === EMPTY) {
          gridEl.appendChild(renderSquarePlaceholder(rowIndex, i));
          continue;
        }
        const cardEl = renderCard(cid, rowIndex);
        if (!cardEl) {
          gridEl.appendChild(renderSquarePlaceholder(rowIndex, i));
          continue;
        }
        const rm = cardEl.querySelector(".dashRemove");
        if (rm) {
          rm.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            removeSquareCardLeavePlaceholder(cid);
          });
        }
        gridEl.appendChild(cardEl);
      }
    } else {
      for (const cardId of (row.cards || []).slice(0, 4)) {
        const cardEl = renderCard(cardId, rowIndex);
        if (!cardEl) continue;
        const rm = cardEl.querySelector(".dashRemove");
        if (rm) {
          rm.addEventListener("click", (e) => {
            e.preventDefault();
            e.stopPropagation();
            confirmAndRemoveRow(rowIndex);
          });
        }
        gridEl.appendChild(cardEl);
      }
    }
    rowEl.addEventListener("dragstart", (e) => {
      if (draggingCard) {
        try {
          e.preventDefault();
        } catch (err) {}
        return;
      }
      draggingRowIndex = rowIndex;
      try {
        e.dataTransfer.setData("text/plain", "row:" + rowIndex);
      } catch (err) {}
      rowEl.classList.add("dragging");
    });
    rowEl.addEventListener("dragend", () => {
      draggingRowIndex = -1;
      rowEl.classList.remove("dragging");
      rowsHost.querySelectorAll(".dashRow").forEach((x) => x.classList.remove("dropTarget"));
    });
    rowEl.addEventListener("dragover", (e) => {
      if (draggingRowIndex < 0) return;
      e.preventDefault();
      rowEl.classList.add("dropTarget");
    });
    rowEl.addEventListener("dragleave", () => {
      rowEl.classList.remove("dropTarget");
    });
    rowEl.addEventListener("drop", (e) => {
      if (draggingRowIndex < 0) return;
      e.preventDefault();
      const toIndex = rowIndex;
      const fromIndex = draggingRowIndex;
      if (fromIndex === toIndex) return;
      const rows = loadRows();
      if (fromIndex < 0 || fromIndex >= rows.length) return;
      if (toIndex < 0 || toIndex >= rows.length) return;
      const moved = rows.splice(fromIndex, 1)[0];
      rows.splice(toIndex, 0, moved);
      saveRows(rows);
      draw();
    });
    return rowEl;
  }
  function draw() {
    const rows = loadRows();
    rowsHost.innerHTML = "";
    for (let i = 0; i < rows.length; i++) {
      const rowEl = renderRow(rows[i], i);
      rowsHost.appendChild(rowEl);
    }
  }
  function openPicker(squareOnly) {
    const rows = loadRows();
    const current = new Set(allCardIds(rows));
    pickerList.innerHTML = "";
    const base = squareOnly ? PICKER_ITEMS_SQUARE : PICKER_ITEMS;
    const available = base.filter((item) => {
      const ids = item.add();
      return ids.some((x) => !current.has(x));
    });
    if (available.length === 0) {
      const empty = document.createElement("div");
      empty.className = "dashPickerEmpty";
      empty.textContent = "All cards are already added.";
      pickerList.appendChild(empty);
    } else {
      for (const item of available) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "dashPickItem";
        btn.innerHTML = `<div class="dashPickTitle">${item.title}</div><div class="dashPickSub">Add to dashboard</div>`;
        btn.addEventListener("click", () => {
          const ids = item.add();
          if (squareOnly && pickerTarget && ids.length === 1) {
            addCardIntoSquareSlot(pickerTarget.rowIndex, pickerTarget.slotIndex, ids[0]);
            pickerTarget = null;
            closePicker();
            return;
          }
          addCardsRespectRows(ids);
          closePicker();
        });
        pickerList.appendChild(btn);
      }
    }
    picker.style.display = "flex";
    picker.setAttribute("aria-hidden", "false");
    document.body.classList.add("noScroll");
  }
  function closePicker() {
    picker.style.display = "none";
    picker.setAttribute("aria-hidden", "true");
    document.body.classList.remove("noScroll");
    pickerTarget = null;
  }
  if (addTopBtn) {
    addTopBtn.addEventListener("click", () => openPicker(false));
  }
  window.addEventListener("dashOpenPicker", () => openPicker(false));
  if (pickerClose) pickerClose.addEventListener("click", closePicker);
  if (picker) {
    picker.addEventListener("click", (e) => {
      if (e.target === picker) closePicker();
    });
  }
  if (resetBtn) {
    resetBtn.addEventListener("click", async () => {
      try {
        localStorage.removeItem(LS_KEY);
      } catch (e) {}
      await deleteServerLayout();
      draw();
    });
  }
  async function init() {
    const srv = await fetchServerLayout();
    if (srv) {
      const rows = normalizeRows(srv);
      saveRows(rows);
    }
    draw();
  }
  init();
})();
