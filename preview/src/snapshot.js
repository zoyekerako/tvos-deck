/* Entwickler-Hilfe: Stil-Snapshot aller Elemente für Vorher/Nachher-Vergleiche.
   window.TVSnapshot("save") speichert, window.TVSnapshot("diff") vergleicht. */
window.TVSnapshot = async function (mode) {
  await new Promise((r) => setTimeout(r, 1500));
  const props = ["background-color", "background-image", "color", "border-top-left-radius", "box-shadow",
    "font-size", "font-weight", "text-transform", "letter-spacing", "padding-left", "padding-top", "margin-left",
    "opacity", "backdrop-filter", "clip-path", "transform", "border-top-width", "border-left-width", "height",
    "width", "display", "visibility", "mask-image", "outline-style", "animation-name", "filter", "z-index"];
  const out = {};
  document.querySelectorAll("body *").forEach((el, i) => {
    const running = el.getAnimations && el.getAnimations().length > 0;
    for (const pseudo of [null, "::before", "::after"]) {
      const cs = getComputedStyle(el, pseudo);
      if (pseudo && (cs.content === "none" || cs.content === "normal")) continue;
      out[i + ":" + el.tagName + (pseudo || "")] = props
        .filter((p) => !(running && (p === "transform" || p === "background-position")))
        .map((p) => p + "=" + cs.getPropertyValue(p)).join("|");
    }
  });
  const key = "tvsnap:" + location.pathname;
  if (mode === "save") {
    localStorage.setItem(key, JSON.stringify(out));
    return Object.keys(out).length + " saved";
  }
  const before = JSON.parse(localStorage.getItem(key) || "{}");
  const diffs = [];
  for (const k of Object.keys(out)) {
    if (before[k] === undefined) { diffs.push(k + " NEW"); continue; }
    if (before[k] !== out[k]) {
      const a = before[k].split("|"), b = out[k].split("|");
      diffs.push(k + " " + b.filter((x, j) => x !== a[j]).join(" ; ") + "  (vorher: " + a.filter((x, j) => x !== b[j]).join(" ; ") + ")");
    }
  }
  return diffs.length ? diffs.slice(0, 25) : "keine Unterschiede (" + Object.keys(out).length + " Elemente)";
};
