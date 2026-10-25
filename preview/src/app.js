/* Vorschau-Oberfläche: Bildschirme, Optionen und Weiterleitung der Eingaben. */
(function () {
  "use strict";

  const THEME = window.TVDECK;
  const STORAGE_KEY = "tvdeck-preview-v1";

  // Geräte: logische Auflösung der Steam-Oberfläche. Eine Steam Machine an
  // einem 4K-Fernseher rendert mit 200 % Skalierung = 1920 × 1080 logische px.
  const DEVICES = {
    tv: { w: 1920, h: 1080, label: "Steam Machine · 16:9 (4K @ 200 %)" },
    deck: { w: 1280, h: 800, label: "Steam Deck · 16:10" },
  };

  // Steam-Fenster je Bildschirm. Overlay-Fenster (Menü, QAM, Toast) liegen
  // wie auf dem Gerät als eigene Fenster über Big Picture.
  const SCREENS = [
    { id: "home", label: "Startseite", frames: () => [{ src: "sp-home.html" }] },
    { id: "library", label: "Bibliothek", frames: () => [{ src: "sp-library.html" }] },
    { id: "game", label: "Spieleseite", frames: () => [{ src: "sp-game.html" }] },
    { id: "settings", label: "Einstellungen", frames: () => [{ src: "sp-settings.html" }] },
    { id: "menu", label: "Hauptmenü (Steam)", frames: () => [{ src: "sp-home.html", bg: true }, { src: "menu.html" }] },
    {
      id: "qam", label: "Quick Access (…)", frames: (d) => [
        { src: "sp-home.html", bg: true },
        { src: "qam.html", rect: { top: 40, right: 0, width: 348, height: d.h - 80 } }],
    },
    { id: "dialog", label: "Dialog", frames: () => [{ src: "sp-dialog.html" }] },
    { id: "context", label: "Kontextmenü", frames: () => [{ src: "sp-contextmenu.html" }] },
    { id: "keyboard", label: "Tastatur", frames: () => [{ src: "sp-keyboard.html" }] },
    {
      id: "toast", label: "Benachrichtigung", frames: () => [
        { src: "sp-home.html", bg: true },
        { src: "toast.html", rect: { right: 0, bottom: 40, width: 340, height: 110 } }],
    },
  ];

  // Screenshot-Modus: index.html?shot=home&device=tv&bigart=1&ingame=0
  const params = new URLSearchParams(location.search);
  const SHOT = params.get("shot");

  const PREVIEW_TOGGLES = [
    { key: "enabled", label: "Theme aktiv", hint: "Aus = Steam-Original zum Vergleich" },
    { key: "bigart", label: "Steam: „Große Grafik“", hint: "Einstellungen → Anpassung → Startseite" },
    { key: "ingame", label: "Spiel läuft (Hauptmenü)" },
  ];

  function load() {
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
      if (saved && typeof saved === "object") return saved;
    } catch (e) { /* privates Fenster o. Ä. */ }
    return null;
  }

  const saved = SHOT ? null : load();
  const state = {
    screen: SHOT || (saved && saved.screen) || "home",
    device: params.get("device") || (saved && saved.device) || "tv",
    options: Object.assign(
      { enabled: true, bigart: true, ingame: false, patches: {}, components: {} },
      saved && saved.options),
  };
  if (SHOT) {
    ["bigart", "ingame", "enabled"].forEach((k) => {
      if (params.has(k)) state.options[k] = params.get(k) === "1";
    });
    document.body.classList.add("shot");
  }

  function save() {
    if (SHOT) return;
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (e) { /* egal */ }
  }

  window.TVPreview = { get options() { return state.options; } };

  // ------------------------------------------------------------ Bildschirme
  const stage = document.getElementById("stage");
  const device = document.getElementById("device");
  const wrap = document.getElementById("stage-wrap");
  let frames = [];

  function activeFrame() {
    const fg = frames.filter((f) => !f.classList.contains("is-bg"));
    return fg[fg.length - 1];
  }

  function showScreen(id) {
    const screen = SCREENS.find((s) => s.id === id) || SCREENS[0];
    state.screen = screen.id;
    save();
    const dev = DEVICES[state.device] || DEVICES.tv;
    stage.style.width = dev.w + "px";
    stage.style.height = dev.h + "px";
    stage.innerHTML = "";
    frames = screen.frames(dev).map((def) => {
      const f = document.createElement("iframe");
      f.src = def.src;
      f.title = screen.label;
      const r = def.rect || { top: 0, left: 0, width: dev.w, height: dev.h };
      Object.entries(r).forEach(([k, v]) => { f.style[k] = v + "px"; });
      if (def.bg) { f.classList.add("is-bg"); f.tabIndex = -1; }
      stage.appendChild(f);
      return f;
    });
    const fg = activeFrame();
    if (fg) fg.addEventListener("load", () => fg.contentWindow.focus(), { once: true });
    document.querySelectorAll("#screens button").forEach((b) => {
      b.setAttribute("aria-current", String(b.dataset.id === screen.id));
    });
    fit();
  }

  const nav = document.getElementById("screens");
  SCREENS.forEach((s) => {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = s.label;
    b.dataset.id = s.id;
    b.addEventListener("click", () => showScreen(s.id));
    nav.appendChild(b);
  });

  // ------------------------------------------------------------ Optionen
  function broadcast() {
    save();
    frames.forEach((f) => {
      try { f.contentWindow.postMessage({ type: "tv-options", opts: state.options }, "*"); } catch (e) { /* lädt noch */ }
    });
  }

  function addSelect(host, label, values, current, onChange) {
    const wrapEl = document.createElement("div");
    wrapEl.className = "opt";
    const id = "opt-" + Math.random().toString(36).slice(2);
    wrapEl.innerHTML = `<label for="${id}"></label><select id="${id}"></select>`;
    wrapEl.querySelector("label").textContent = label;
    const sel = wrapEl.querySelector("select");
    values.forEach((v) => {
      const o = document.createElement("option");
      o.value = v; o.textContent = v; o.selected = v === current;
      sel.appendChild(o);
    });
    sel.addEventListener("change", () => onChange(sel.value));
    host.appendChild(wrapEl);
  }

  function addCheck(host, label, checked, onChange, hint) {
    const wrapEl = document.createElement("div");
    wrapEl.className = "opt";
    wrapEl.innerHTML = `<label class="opt-check"><span><span class="t"></span>${hint ? '<br><small class="h"></small>' : ""}</span>` +
      `<input type="checkbox"><span class="switch" aria-hidden="true"></span></label>`;
    wrapEl.querySelector(".t").textContent = label;
    if (hint) wrapEl.querySelector(".h").textContent = hint;
    const cb = wrapEl.querySelector("input");
    cb.checked = checked;
    cb.addEventListener("change", () => onChange(cb.checked));
    host.appendChild(wrapEl);
  }

  function addColor(host, label, value, onChange) {
    const wrapEl = document.createElement("div");
    wrapEl.className = "opt";
    const id = "opt-" + Math.random().toString(36).slice(2);
    wrapEl.innerHTML = `<label for="${id}"></label><input id="${id}" type="color">`;
    wrapEl.querySelector("label").textContent = label;
    const input = wrapEl.querySelector("input");
    input.value = value.length === 7 ? value : "#ffffff";
    input.addEventListener("input", () => onChange(input.value));
    host.appendChild(wrapEl);
  }

  const optHost = document.getElementById("options");
  THEME.patches.forEach((p) => {
    const current = state.options.patches[p.name] || p.default;
    const values = Object.keys(p.values);
    if (p.type === "checkbox") {
      addCheck(optHost, p.name, current === "Yes", (on) => {
        state.options.patches[p.name] = on ? "Yes" : "No"; broadcast();
      });
    } else if (p.type !== "none") {
      addSelect(optHost, p.name, values, current, (v) => { state.options.patches[p.name] = v; broadcast(); });
    }
    p.components.forEach((c) => {
      addColor(optHost, c.name, state.options.components[c.name] || c.default, (v) => {
        state.options.components[c.name] = v; broadcast();
      });
    });
  });

  const pvHost = document.getElementById("preview-options");
  addSelect(pvHost, "Gerät", Object.values(DEVICES).map((d) => d.label), (DEVICES[state.device] || DEVICES.tv).label, (v) => {
    state.device = Object.keys(DEVICES).find((k) => DEVICES[k].label === v);
    showScreen(state.screen);
  });
  PREVIEW_TOGGLES.forEach((t) => {
    addCheck(pvHost, t.label, !!state.options[t.key], (on) => { state.options[t.key] = on; broadcast(); }, t.hint);
  });

  document.getElementById("theme-version").textContent = THEME.version || "";
  document.getElementById("build-info").textContent =
    `Echtes Steam-CSS · Steam-Deck-Stable-Build ${THEME.steamVersion || "?"}`;

  // ------------------------------------------------------------ Eingaben
  document.addEventListener("keydown", (e) => {
    if (e.target.closest && e.target.closest("select, input")) return;
    const f = activeFrame();
    if (f && f.contentWindow && f.contentWindow.TVNav && f.contentWindow.TVNav.key(e.key)) e.preventDefault();
  });

  // ------------------------------------------------------------ Skalierung
  function fit() {
    if (SHOT) { device.style.transform = "none"; return; }
    const dev = DEVICES[state.device] || DEVICES.tv;
    const pad = 32;
    const w = wrap.clientWidth - pad, h = wrap.clientHeight - pad;
    const scale = Math.min(1, w / (dev.w + 28), h / (dev.h + 28));
    device.style.transform = `scale(${Math.max(0.1, scale)})`;
  }
  new ResizeObserver(fit).observe(wrap);
  fit();

  showScreen(state.screen);
})();
