#!/usr/bin/env python3
"""tvOS Deck – Web-Vorschau bauen (und optional starten).

Was das Skript macht:
  1. Lädt (einmalig, gecacht in preview/.cache) Steams aktuelles Big-Picture-CSS
     direkt vom Valve-CDN (Steam-Deck-Stable-Kanal) und die Klassen-Übersetzung
     von DeckThemes, die auch CSS Loader verwendet.
  2. Übersetzt die Theme-Dateien exakt wie CSS Loader (Alias -> aktueller Hash).
  3. Erzeugt in preview/dist/ Testseiten, die Steams DOM mit den echten
     Klassen nachbauen – je Steam-Fenster eine Seite (Big Picture, Hauptmenü,
     Quick Access, Benachrichtigungen), weil CSS Loader pro Fenster injiziert.

Aufruf:
  python3 preview/build_preview.py            # bauen
  python3 preview/build_preview.py --serve    # bauen und auf http://localhost:8765 starten
  python3 preview/build_preview.py --refresh  # Steam-CSS und Übersetzung neu laden

Nur Python-Standardbibliothek nötig.
"""
import argparse
import functools
import http.server
import io
import json
import re
import shutil
import socketserver
import subprocess
import sys
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
THEME_DIR = ROOT.parent / "tvOS-Deck"
SRC = ROOT / "src"
CACHE = ROOT / ".cache"
DIST = ROOT / "dist"

MANIFEST_URL = "https://media.steampowered.com/client/steam_client_steamdeck_stable_ubuntu12"
CDN_BASE = "https://media.steampowered.com/client/"
MAPPING_URL = "https://api.deckthemes.com/stable.json"

sys.path.insert(0, str(ROOT))
import screens  # noqa: E402  (liegt neben diesem Skript)


# --------------------------------------------------------------------------
# Downloads (gecacht)
# --------------------------------------------------------------------------
def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "tvOS-Deck-preview/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            return resp.read()
    except urllib.error.URLError as err:
        # python.org-Python auf macOS hat oft keine Root-Zertifikate -> curl nutzen
        if "CERTIFICATE_VERIFY_FAILED" not in str(err) or not shutil.which("curl"):
            raise
        return subprocess.run(["curl", "-fsSL", "--max-time", "300", url],
                              check=True, capture_output=True).stdout


def steam_css(refresh: bool) -> tuple[Path, str]:
    manifest = fetch(MANIFEST_URL).decode("utf-8", "replace")
    version = re.search(r'"version"\s+"(\d+)"', manifest).group(1)
    target = CACHE / f"steamui-{version}" / "sp.css"
    if target.exists() and (target.parent / "sp.js").exists() and not refresh:
        return target, version

    block = re.search(r'"steamui_websrc_all"\s*\{([^}]*)\}', manifest)
    if not block:
        sys.exit("steamui_websrc_all nicht im Steam-Manifest gefunden")
    file_name = re.search(r'"file"\s+"([^"]+)"', block.group(1)).group(1)
    print(f"Lade Steam-UI {version} ({file_name}) …")
    data = fetch(CDN_BASE + file_name)
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        target.parent.mkdir(parents=True, exist_ok=True)
        for wanted in ("steamui/css/sp.css", "steamui/sp.js"):
            member = next(n for n in zf.namelist() if n.replace("\\", "/").endswith(wanted))
            (target.parent / Path(wanted).name).write_bytes(zf.read(member))
    return target, version


def class_mapping(refresh: bool) -> dict:
    path = CACHE / "stable.json"
    if refresh or not path.exists() or time.time() - path.stat().st_mtime > 86400:
        print("Lade CSS-Loader-Übersetzung (api.deckthemes.com/stable.json) …")
        CACHE.mkdir(parents=True, exist_ok=True)
        path.write_bytes(fetch(MAPPING_URL))
    data = json.loads(path.read_text(encoding="utf-8"))
    mapping = {}
    for values in data.values():          # wie CSS Loader: jede alte Variante -> neueste
        for alias in values[:-1]:
            mapping[alias] = values[-1]
    return mapping


# --------------------------------------------------------------------------
# Übersetzung wie CSS Loader (css_inject.py)
# --------------------------------------------------------------------------
def translate_css(css: str, mapping: dict) -> str:
    parts = re.split(r"(\.[_a-zA-Z]+[_a-zA-Z0-9-]*)", css)
    parts = ["." + mapping[p[1:]] if p.startswith(".") and p[1:] in mapping else p for p in parts]
    css = "".join(parts)
    parts = re.split(r'(\[class[*^|~]="[_a-zA-Z0-9-]*"\])', css)
    out = []
    for p in parts:
        if p.startswith("[class") and p.endswith('"]') and p[9:-2] in mapping:
            p = p[:9] + mapping[p[9:-2]] + p[-2:]
        out.append(p)
    return "".join(out)


def translate_html(html: str, mapping: dict) -> str:
    def repl(m):
        tokens = [mapping.get(t, t) for t in m.group(2).split()]
        return f'{m.group(1)}="{" ".join(tokens)}"'
    return re.sub(r'\b(class|data-focusclass|data-toggle|data-select)="([^"]*)"', repl, html)


# --------------------------------------------------------------------------
# Tab-Zuordnung wie CSS Loader -> Vorschau-Fenster
# --------------------------------------------------------------------------
DEFAULT_MAPPINGS = {
    "bigpicture": ["~Valve Steam Gamepad/default~", "~Valve%20Steam%20Gamepad~"],
    "bigpictureoverlay": ["QuickAccess", "MainMenu"],
    "SP": ["bigpicture"],
    "Steam Big Picture Mode": ["bigpicture"],
    "MainMenu": ["MainMenu.*"],
    "MainMenu_.*": ["MainMenu"],
    "QuickAccess": ["QuickAccess.*"],
    "QuickAccess_.*": ["QuickAccess"],
    "All": ["bigpicture", "bigpictureoverlay"],
}


def extend_tabs(tabs: list, theme_tabs: dict) -> list:
    if not tabs:
        return extend_tabs(theme_tabs.get("default", []), theme_tabs) if "default" in theme_tabs else []
    out = []
    for t in tabs:
        if t in theme_tabs:
            out += extend_tabs(theme_tabs[t], theme_tabs)
        elif t in DEFAULT_MAPPINGS:
            out += extend_tabs(DEFAULT_MAPPINGS[t], theme_tabs)
        else:
            out.append(t)
    return out


def to_windows(tabs: list) -> list:
    wins = set()
    for t in tabs:
        if "Gamepad" in t:
            wins.add("sp")
        elif t.startswith("QuickAccess"):
            wins.add("qam")
        elif t.startswith("MainMenu"):
            wins.add("menu")
        elif t.startswith("notificationtoasts"):
            wins.add("toasts")
    return sorted(wins)


def build_theme_data(mapping: dict) -> dict:
    theme = json.loads((THEME_DIR / "theme.json").read_text(encoding="utf-8"))
    ttabs = theme.get("tabs", {})

    def make_inject(key, tabs):
        if key.startswith("--"):
            return {"file": key, "windows": to_windows(extend_tabs(tabs[1:], ttabs)),
                    "css": f":root {{ {key}: {tabs[0]}; }}"}
        css = (THEME_DIR / key).read_text(encoding="utf-8")
        return {"file": key, "windows": to_windows(extend_tabs(tabs, ttabs)),
                "css": translate_css(css, mapping)}

    data = {"name": theme["name"], "version": theme.get("version", ""),
            "injects": [make_inject(k, v) for k, v in theme.get("inject", {}).items()],
            "patches": []}
    for name, patch in theme.get("patches", {}).items():
        values = patch.get("values", {})
        data["patches"].append({
            "name": name,
            "type": patch.get("type", "dropdown"),
            "default": patch.get("default", next(iter(values))),
            "values": {opt: [make_inject(k, v) for k, v in injects.items()] for opt, injects in values.items()},
            "components": [{
                "name": c["name"], "type": c["type"], "on": c["on"], "default": c["default"],
                "var": c["css_variable"] if c["css_variable"].startswith("--") else "--" + c["css_variable"],
                "windows": to_windows(extend_tabs(c.get("tabs", []), ttabs)),
            } for c in patch.get("components", [])],
        })
    return data


# --------------------------------------------------------------------------
# Prüfen: gibt es jede Klasse des Themes im aktuellen Steam-Build?
# --------------------------------------------------------------------------
def check_theme(mapping: dict, css_path: Path) -> int:
    steam_css_text = css_path.read_text(encoding="utf-8", errors="replace")
    steam_js = (css_path.parent / "sp.js").read_text(encoding="utf-8", errors="replace")
    known = set(re.findall(r"\.([_a-zA-Z][_a-zA-Z0-9-]*)", steam_css_text))
    missing = {}
    for css_file in sorted((THEME_DIR / "css").rglob("*.css")):
        raw = css_file.read_text(encoding="utf-8")
        if "\\" in raw:
            missing.setdefault(css_file.name, []).append("Backslash (CSS Loader verdoppelt ihn)")
        css = re.sub(r"/\*.*?\*/", "", raw, flags=re.S)
        css = re.sub(r"url\([^)]*\)", "url()", css)
        css = translate_css(css, mapping)
        tokens = set(re.findall(r"\.([_a-zA-Z][_a-zA-Z0-9-]*)", css))
        tokens |= set(re.findall(r"\[class[~*^|]?=['\"]([^'\"]+)['\"]\]", css))
        for tok in sorted(tokens):
            if tok not in known and f'"{tok}"' not in steam_js:
                missing.setdefault(css_file.name, []).append(tok)
    if missing:
        print("Klassen, die es im aktuellen Steam-Build nicht (mehr) gibt:")
        for name, toks in missing.items():
            print(f"  {name}: {', '.join(toks)}")
    else:
        print("Prüfung OK: alle Theme-Klassen existieren im aktuellen Steam-Build.")
    return sum(len(v) for v in missing.values())


# --------------------------------------------------------------------------
# W3C-Validierung wie bei der DeckThemes-Einreichung (vnu --css)
# --------------------------------------------------------------------------
VNU_URL = "https://github.com/validator/validator/releases/download/latest/vnu.jar"


def validate_css() -> int:
    if not shutil.which("java"):
        sys.exit("Für --validate wird Java benötigt (z. B. Temurin 17).")
    jar = CACHE / "vnu.jar"
    if not jar.exists():
        print("Lade W3C Nu Validator (vnu.jar) …")
        CACHE.mkdir(parents=True, exist_ok=True)
        jar.write_bytes(fetch(VNU_URL))
    files = [str(p.relative_to(THEME_DIR)) for p in sorted((THEME_DIR / "css").rglob("*.css"))]
    res = subprocess.run(["java", "-jar", str(jar), "--css", "--asciiquotes", *files],
                         cwd=THEME_DIR, capture_output=True, text=True)
    errors = [line.replace("file:" + str(THEME_DIR) + "/", "") for line in res.stderr.splitlines() if "error:" in line]
    for line in errors:
        print("  " + line)
    print(f"W3C-Validierung: {len(files)} Dateien, {len(errors)} Fehler.")
    return len(errors)


# --------------------------------------------------------------------------
# Bauen
# --------------------------------------------------------------------------
def build(refresh: bool) -> None:
    css_path, version = steam_css(refresh)
    mapping = class_mapping(refresh)
    check_theme(mapping, css_path)

    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "steam").mkdir(parents=True)
    shutil.copy2(css_path, DIST / "steam" / "sp.css")
    for f in SRC.iterdir():
        shutil.copy2(f, DIST / f.name)
    # damit /themes_custom/tvOS-Deck/fonts/… wie auf dem Deck aufgelöst wird
    shutil.copytree(THEME_DIR, DIST / "themes_custom" / THEME_DIR.name)

    data = build_theme_data(mapping)
    data["steamVersion"] = version
    (DIST / "theme-data.js").write_text(
        "window.TVDECK = " + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")

    for name, (window, html) in screens.pages().items():
        (DIST / name).write_text(translate_html(html, mapping), encoding="utf-8")

    print(f"Fertig: {DIST} (Steam-Build {version}, {len(mapping)} Klassen-Aliasse)")


# --------------------------------------------------------------------------
# Screenshots (16:9 in 4K) mit einem lokal installierten Chrome/Chromium
# --------------------------------------------------------------------------
SHOTS = [  # (Datei, Bildschirm, Zusatz-Parameter)
    ("01-home-topshelf", "home", "bigart=1"),
    ("02-library", "library", ""),
    ("03-game", "game", ""),
    ("04-steam-menu", "menu", "bigart=1"),
    ("05-quick-access", "qam", "bigart=1"),
    ("06-settings", "settings", ""),
    ("07-dialog", "dialog", ""),
    ("08-context-menu", "context", ""),
    ("09-keyboard", "keyboard", ""),
    ("10-home-classic", "home", "bigart=0"),
]


def find_chrome() -> str | None:
    import os
    candidates = [os.environ.get("CHROME", ""),
                  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                  "/Applications/Chromium.app/Contents/MacOS/Chromium",
                  shutil.which("google-chrome") or "", shutil.which("chromium") or "",
                  shutil.which("chromium-browser") or ""]
    return next((c for c in candidates if c and Path(c).exists()), None)


def screenshots(out_dir: Path, scale: int = 2) -> None:
    import threading
    chrome = find_chrome()
    if not chrome:
        sys.exit("Kein Chrome/Chromium gefunden (Pfad per Umgebungsvariable CHROME angeben).")
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DIST))
    handler.log_message = lambda *a, **k: None
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()

    import tempfile
    (out_dir / "4k").mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp())
    try:
        for name, screen, extra in SHOTS:
            png = tmp / f"{name}.png"
            url = f"http://127.0.0.1:{port}/?shot={screen}&device=tv&{extra}"
            subprocess.run([chrome, "--headless=new", "--hide-scrollbars", "--mute-audio",
                            "--window-size=1920,1080", f"--force-device-scale-factor={scale}",
                            "--virtual-time-budget=12000", f"--screenshot={png}", url],
                           check=True, capture_output=True, timeout=120)
            uhd = out_dir / "4k" / f"{name}.jpg"
            to_jpeg(png, uhd, size=(1920 * scale, 1080 * scale), max_bytes=2_500_000)
            jpg = out_dir / f"{name}.jpg"
            to_jpeg(png, jpg)
            print(f"  {name}: 4K {uhd.stat().st_size // 1024} KB, 1080p {jpg.stat().st_size // 1024} KB")
    finally:
        httpd.shutdown()
        shutil.rmtree(tmp, ignore_errors=True)


def to_jpeg(png: Path, jpg: Path, size=(1920, 1080), max_bytes: int = 1_000_000) -> None:
    """JPEG in Zielgröße; 1080p bleibt unter 1 MB (Limit von DeckThemes)."""
    try:
        from PIL import Image
        img = Image.open(png).convert("RGB").resize(size, Image.LANCZOS)
        for q in (90, 85, 80, 75, 70):
            img.save(jpg, "JPEG", quality=q, optimize=True, progressive=True)
            if jpg.stat().st_size <= max_bytes:
                return
    except ImportError:
        for q in (85, 75, 65):
            subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", str(q), "-z", str(size[1]), str(size[0]),
                            str(png), "--out", str(jpg)], check=True, capture_output=True)
            if jpg.stat().st_size <= max_bytes:
                return


def serve(port: int) -> None:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DIST))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
        print(f"Vorschau läuft auf http://localhost:{port}  (Strg+C zum Beenden)")
        httpd.serve_forever()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--serve", action="store_true", help="nach dem Bauen lokal starten")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--refresh", action="store_true", help="Steam-CSS und Übersetzung neu laden")
    ap.add_argument("--check", action="store_true", help="nur prüfen, ob alle Theme-Klassen in Steam existieren")
    ap.add_argument("--screenshots", metavar="ORDNER", help="16:9-Screenshots in 4K (PNG) und 1080p (JPG < 1 MB) erzeugen")
    ap.add_argument("--validate", action="store_true", help="CSS mit dem W3C-Validator prüfen (wie DeckThemes)")
    args = ap.parse_args()
    if args.check or args.validate:
        problems = 0
        if args.check:
            css, _ = steam_css(args.refresh)
            problems += check_theme(class_mapping(args.refresh), css)
        if args.validate:
            problems += validate_css()
        sys.exit(1 if problems else 0)
    build(args.refresh)
    if args.screenshots:
        print("Erzeuge Screenshots …")
        screenshots(Path(args.screenshots).resolve())
    if args.serve:
        serve(args.port)
