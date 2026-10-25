#!/usr/bin/env python3
"""tvOS Deck – Theme prüfen und als ZIP verpacken.

  python3 tools/package_theme.py          # prüfen + release/*.zip erzeugen
  python3 tools/package_theme.py --lint   # nur prüfen (für CI)

Erzeugt:
  release/tvOS-Deck-<version>.zip             Ordner „tvOS-Deck/“ – zum manuellen Installieren
                                              (nach ~/homebrew/themes/ entpacken)
  release/tvOS-Deck-<version>-deckthemes.zip  Dateien direkt im ZIP-Wurzelverzeichnis – für den
                                              ZIP-Upload auf deckthemes.com

Die Prüfungen entsprechen den Regeln des DeckThemes-Servers (CssLoader-ThemeApi):
gültige Ziele, Längenlimits, existierende .css-Dateien, Theme < 10 MB.
"""
import json
import os
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
THEME = ROOT / "tvOS-Deck"
OUT = ROOT / "release"

VALID_TARGETS = ["System-Wide", "Keyboard", "Home", "Background", "Library", "Store", "Friends and Chat",
                 "Media", "Downloads", "Settings", "Lock Screen", "Tweak", "Other", "Snippet", "Desktop",
                 "Desktop-Library", "Desktop-Tweak", "Desktop-Friends", "Desktop-Store"]
MAX_SIZE = 10 * 1024 * 1024
# CSS Loader legt Einstellungen im Theme-Ordner ab – nie mit ausliefern
EXCLUDE = re.compile(r"(^|/)(\.DS_Store|config_[A-Z]+\.json|__pycache__)(/|$)")


def theme_files():
    for p in sorted(THEME.rglob("*")):
        rel = p.relative_to(THEME).as_posix()
        if p.is_file() and not EXCLUDE.search(rel):
            yield p, rel


def lint() -> dict:
    errors = []
    data = json.loads((THEME / "theme.json").read_text(encoding="utf-8"))

    def need(cond, msg):
        if not cond:
            errors.append(msg)

    need(data.get("manifest_version") == 9, "manifest_version muss 9 sein")
    need(isinstance(data.get("name"), str) and "/" not in data["name"] and 0 < len(data["name"]) <= 100, "name ungültig")
    need(len(str(data.get("version", ""))) <= 16, "version > 16 Zeichen")
    need(len(data.get("description", "")) <= 1000, "description > 1000 Zeichen")
    targets = data.get("target")
    for t in targets if isinstance(targets, list) else [targets]:
        need(t in VALID_TARGETS, f"target '{t}' ist bei DeckThemes nicht erlaubt")

    def check_injects(injects, where):
        for key, tabs in injects.items():
            need(isinstance(tabs, list), f"{where}: '{key}' braucht eine Liste")
            if key.startswith("--"):
                need(len(tabs) >= 1, f"{where}: Variable '{key}' ohne Wert")
                continue
            need(key.endswith(".css"), f"{where}: '{key}' ist keine .css-Datei")
            need((THEME / key).is_file(), f"{where}: Datei '{key}' fehlt")

    check_injects(data.get("inject", {}), "inject")
    for name, patch in data.get("patches", {}).items():
        values = patch.get("values", {})
        need(patch.get("default") in values, f"Option '{name}': default fehlt in values")
        if patch.get("type") == "checkbox":
            need(set(values) == {"Yes", "No"}, f"Option '{name}': checkbox braucht genau Yes/No")
        for opt, injects in values.items():
            check_injects(injects, f"Option '{name}' → '{opt}'")
        for comp in patch.get("components", []):
            need(comp.get("on") in values, f"Option '{name}': Komponente '{comp.get('name')}' zeigt auf fehlenden Wert")
            need(comp.get("type") in ("color-picker", "image-picker"), f"Komponente '{comp.get('name')}': Typ ungültig")

    referenced = set(data.get("inject", {}))
    for patch in data.get("patches", {}).values():
        for injects in patch.get("values", {}).values():
            referenced |= {k for k in injects if not k.startswith("--")}
    for p, rel in theme_files():
        if rel.endswith(".css"):
            need(rel in referenced, f"'{rel}' wird in theme.json nicht verwendet")
            need("\\" not in p.read_text(encoding="utf-8"), f"'{rel}': Backslash (CSS Loader verdoppelt ihn)")

    size = sum(p.stat().st_size for p, _ in theme_files())
    need(size < MAX_SIZE, f"Theme ist {size / 1e6:.1f} MB (Limit 10 MB)")

    tag = os.environ.get("GITHUB_REF_NAME", "")
    if tag.startswith("v"):
        need(tag[1:] == str(data.get("version")), f"Git-Tag {tag} passt nicht zu version {data.get('version')}")

    if errors:
        print("theme.json/Theme-Prüfung fehlgeschlagen:")
        for e in errors:
            print("  - " + e)
        sys.exit(1)
    print(f"Theme-Prüfung OK: {data['name']} {data.get('version')} ({size / 1024:.0f} KB)")
    return data


def package(data: dict) -> None:
    OUT.mkdir(exist_ok=True)
    version = data.get("version", "dev")
    manual = OUT / f"tvOS-Deck-{version}.zip"
    deckthemes = OUT / f"tvOS-Deck-{version}-deckthemes.zip"
    with zipfile.ZipFile(manual, "w", zipfile.ZIP_DEFLATED) as z1, \
            zipfile.ZipFile(deckthemes, "w", zipfile.ZIP_DEFLATED) as z2:
        for p, rel in theme_files():
            z1.write(p, f"tvOS-Deck/{rel}")
            z2.write(p, rel)
    for z in (manual, deckthemes):
        print(f"  {z.relative_to(ROOT)} ({z.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    info = lint()
    if "--lint" not in sys.argv:
        package(info)
