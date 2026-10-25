/* Laufzeit in jedem nachgebauten Steam-Fenster:
   - spielt die Theme-Dateien ein wie CSS Loader (nur die für dieses Fenster)
   - wendet die gewählten Optionen an
   - Steuerkreuz-Navigation: setzt gpfocus / gpfocuswithin wie Steam */
(function () {
  "use strict";

  const WINDOW = document.documentElement.dataset.window;
  const THEME = window.TVDECK;
  const styles = new Map();

  // ---------------------------------------------------------------- Theme
  function setStyle(id, css) {
    let el = styles.get(id);
    if (!el) {
      el = document.createElement("style");
      el.className = "css-loader-style";
      el.dataset.tv = id;
      document.head.appendChild(el);
      styles.set(id, el);
    }
    el.textContent = css;
  }

  function clearStyles() {
    for (const el of styles.values()) el.remove();
    styles.clear();
  }

  function hexToRgb(hex) {
    let h = hex.replace("#", "");
    if (h.length <= 4) h = h.split("").map((c) => c + c).join("");
    return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16) || 0);
  }

  function applyOptions(opts) {
    clearStyles();
    document.documentElement.classList.toggle("pv-ingame-on", !!opts.ingame);
    document.querySelectorAll("[data-bigart]").forEach((el) => el.classList.toggle("BigArtMode", !!opts.bigart));
    if (!opts.enabled || !THEME) return;

    THEME.injects.forEach((inj, i) => {
      if (inj.windows.includes(WINDOW)) setStyle("i" + i, inj.css);
    });
    THEME.patches.forEach((patch, pi) => {
      const value = (opts.patches && opts.patches[patch.name]) || patch.default;
      (patch.values[value] || []).forEach((inj, j) => {
        if (inj.windows.includes(WINDOW)) setStyle(`p${pi}-${j}`, inj.css);
      });
      patch.components.forEach((c, ci) => {
        if (c.on !== value || !c.windows.includes(WINDOW)) return;
        const v = (opts.components && opts.components[c.name]) || c.default;
        const [r, g, b] = hexToRgb(v);
        setStyle(`c${pi}-${ci}`,
          `:root { ${c.var}: ${v}; ${c.var}_r: ${r}; ${c.var}_g: ${g}; ${c.var}_b: ${b}; ${c.var}_rgb: ${r}, ${g}, ${b}; }`);
      });
    });
  }

  function initialOptions() {
    try {
      if (window.parent !== window && window.parent.TVPreview) return window.parent.TVPreview.options;
    } catch (e) { /* anderer Ursprung */ }
    return { enabled: true, patches: {}, components: {} };
  }

  window.addEventListener("message", (e) => {
    if (e.data && e.data.type === "tv-options") applyOptions(e.data.opts);
  });

  // ------------------------------------------------------------ Navigation
  let current = null;

  function isVisible(el) {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) return false;
    const cs = getComputedStyle(el);
    return cs.visibility !== "hidden" && cs.display !== "none";
  }

  // Modale Ebenen (Dialog, Kontextmenü, Tastatur) fangen den Fokus wie in Steam
  function focusRoot() {
    const modals = [...document.querySelectorAll("[data-modal]")].filter(isVisible);
    return modals.length ? modals[modals.length - 1] : document;
  }

  function focusables() {
    return [...focusRoot().querySelectorAll(".Focusable")].filter(isVisible);
  }

  function setFocus(el, instant) {
    if (!el) return;
    if (current) {
      current.classList.remove("gpfocus");
      if (current.dataset.focusclass) current.classList.remove(...current.dataset.focusclass.split(" "));
    }
    document.querySelectorAll(".gpfocuswithin").forEach((n) => n.classList.remove("gpfocuswithin"));
    current = el;
    el.classList.add("gpfocus");
    if (el.dataset.focusclass) el.classList.add(...el.dataset.focusclass.split(" "));
    for (let p = el.parentElement; p; p = p.parentElement) {
      if (p.classList.contains("Panel")) p.classList.add("gpfocuswithin");
    }
    el.focus({ preventScroll: true });
    el.scrollIntoView({ block: "nearest", inline: "nearest", behavior: instant ? "auto" : "smooth" });

    const hero = el.dataset.hero;
    const target = document.querySelector("[data-hero-target]");
    if (hero && target && target.getAttribute("src") !== hero) target.setAttribute("src", hero);
  }

  function gap(a1, a2, b1, b2) {
    if (b2 < a1) return a1 - b2;
    if (b1 > a2) return b1 - a2;
    return 0;
  }

  function score(dir, r, q) {
    const rcx = (r.left + r.right) / 2, rcy = (r.top + r.bottom) / 2;
    const qcx = (q.left + q.right) / 2, qcy = (q.top + q.bottom) / 2;
    let main, cross;
    if (dir === "right") {
      if (qcx <= rcx + 2) return null;
      main = Math.max(0, q.left - r.right); cross = gap(r.top, r.bottom, q.top, q.bottom);
    } else if (dir === "left") {
      if (qcx >= rcx - 2) return null;
      main = Math.max(0, r.left - q.right); cross = gap(r.top, r.bottom, q.top, q.bottom);
    } else if (dir === "down") {
      if (qcy <= rcy + 2) return null;
      main = Math.max(0, q.top - r.bottom); cross = gap(r.left, r.right, q.left, q.right);
    } else {
      if (qcy >= rcy - 2) return null;
      main = Math.max(0, r.top - q.bottom); cross = gap(r.left, r.right, q.left, q.right);
    }
    return main + cross * 3 + Math.hypot(qcx - rcx, qcy - rcy) * 0.05;
  }

  function move(dir) {
    const all = focusables();
    if (!current || !all.includes(current)) return setFocus(all[0]);

    // Slider: links/rechts verändert den Wert
    if (current.hasAttribute("data-slider") && (dir === "left" || dir === "right")) {
      const ctl = current.querySelector('[style*="--normalized-slider-value"]');
      if (ctl) {
        const v = parseFloat(ctl.style.getPropertyValue("--normalized-slider-value")) || 0;
        const nv = Math.min(1, Math.max(0, v + (dir === "right" ? 0.05 : -0.05)));
        ctl.style.setProperty("--normalized-slider-value", nv.toFixed(2));
        return;
      }
    }

    const r = current.getBoundingClientRect();
    let best = null, bestScore = Infinity;
    for (const el of all) {
      if (el === current) continue;
      const s = score(dir, r, el.getBoundingClientRect());
      if (s !== null && s < bestScore) { bestScore = s; best = el; }
    }
    if (best) setFocus(best);
  }

  function activate(el) {
    if (!el) return;
    if (el.dataset.toggle) el.classList.toggle(el.dataset.toggle);
    if (el.dataset.select && el.dataset.group) {
      document.querySelectorAll(`[data-group="${el.dataset.group}"]`).forEach((n) => n.classList.remove(el.dataset.select));
      el.classList.add(el.dataset.select);
    }
    el.classList.add("pv-pressed");
    setTimeout(() => el.classList.remove("pv-pressed"), 120);
  }

  const KEYS = { ArrowUp: "up", ArrowDown: "down", ArrowLeft: "left", ArrowRight: "right" };

  function key(k) {
    if (KEYS[k]) { move(KEYS[k]); return true; }
    if (k === "Enter" || k === " ") { activate(current); return true; }
    return false;
  }

  window.addEventListener("keydown", (e) => {
    if (key(e.key)) e.preventDefault();
  });

  document.addEventListener("click", (e) => {
    const el = e.target.closest(".Focusable");
    if (!el) return;
    setFocus(el);
    activate(el);
  });

  window.TVNav = { key, focusFirst: () => {
    const marked = [...focusRoot().querySelectorAll("[data-autofocus]")].filter(isVisible);
    setFocus(marked[marked.length - 1] || focusables()[0], true);
  } };

  applyOptions(initialOptions());
  requestAnimationFrame(() => window.TVNav.focusFirst());
})();
