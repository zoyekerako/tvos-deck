# tvOS Deck veröffentlichen

CSS-Loader-Themes kommen **nicht in den Decky Store**. Der Decky Store ist nur für Plugins; Themes werden über
**[DeckThemes](https://deckthemes.com)** verteilt. Dort sucht CSS Loader, wenn man unter *Find themes* stöbert.
GitHub ist der Ort für Code, Releases und Fehlermeldungen. Die Einreichung bei DeckThemes holt das Theme am
einfachsten direkt aus dem GitHub-Repo.

## 1. Vorher prüfen

```bash
python3 tools/package_theme.py                      # Regeln wie DeckThemes + baut release/*.zip
python3 preview/build_preview.py --refresh --check  # alle Klassen im aktuellen Steam-Build vorhanden?
python3 preview/build_preview.py --validate         # W3C-CSS-Prüfung wie DeckThemes (Java nötig)
```

Alle drei müssen ohne Fehler durchlaufen.

## 2. GitHub-Repo anlegen

```bash
gh repo create tvos-deck --public --source . --push
```

Alternativ legst du auf github.com ein leeres Repo an und führst dann
`git remote add origin <URL>` und `git push -u origin main` aus.

Danach prüft die Action *Check* jeden Push und einmal pro Woche, ob Steam Klassen umbenannt hat.

## 3. Release erstellen

```bash
git tag v1.1.0
git push origin v1.1.0
```

Die Action *Release* baut daraus zwei ZIPs und hängt sie an das GitHub-Release:

| Datei | Wofür |
| --- | --- |
| `tvOS-Deck-1.1.0.zip` | Manuelle Installation: nach `~/homebrew/themes/` entpacken |
| `tvOS-Deck-1.1.0-deckthemes.zip` | Upload bei DeckThemes, falls du nicht die Git-Variante nimmst (Dateien liegen im ZIP-Stamm) |

## 4. Bei DeckThemes einreichen

1. Auf [deckthemes.com](https://deckthemes.com) mit **Discord** anmelden.
2. **Submit** öffnen und als Quelle **Git** wählen:
   - Repo-URL: `https://github.com/<dein-name>/tvos-deck`
   - Commit: leer lassen (neuester Stand) oder den Commit des Release-Tags
   - Unterordner: **`tvOS-Deck`**

   Alternativ wählst du **Zip** und lädst `release/tvOS-Deck-1.1.0-deckthemes.zip` hoch.
3. Name, Version, Ziel (*System-Wide*) und Beschreibung kommen aus `tvOS-Deck/theme.json`. Als Autor wird dein
   DeckThemes-Name eingetragen, weil `author` absichtlich fehlt.
4. **Bilder:** bis zu **5** JPG/PNG mit je höchstens **1 MB** und ohne eingefügten Text. Passend sind
   `images/01-home-topshelf.jpg`, `04-steam-menu.jpg`, `05-quick-access.jpg`, `03-game.jpg` und
   `06-settings.jpg` (je 1920 × 1080, unter 300 KB).
5. Absenden. Ein Moderator prüft das Theme, danach erscheint es in CSS Loader unter *Find themes*.

**Echte Screenshots sind besser.** Die Bilder in `images/` stammen aus der Web-Vorschau mit Steams echtem CSS.
Sie zeigen aber Beispiel-Spielgrafiken aus dem Steam-Shop. Mache auf der Steam Machine eigene Aufnahmen mit
**Steam-Taste + R1** und nimm sie für die Einreichung, sobald das Theme dort so aussieht wie gewünscht.

## 5. Updates

1. Version in `tvOS-Deck/theme.json` erhöhen und `CHANGELOG.md` ergänzen.
2. `python3 tools/package_theme.py` ausführen.
3. Committen, dann `git tag v<version>` und `git push origin main v<version>` ausführen. Die Release-Action
   bricht ab, wenn Tag und `version` nicht übereinstimmen.
4. Bei DeckThemes das Theme mit demselben Namen erneut einreichen. Es wird dann als Update geführt.

## Wenn Steam ein Update bringt

Schlägt die wöchentliche *Check*-Action fehl, hat Valve Klassen entfernt oder umbenannt. Lokal zeigt
`python3 preview/build_preview.py --refresh --check` genau, welche Klassen fehlen. Danach testest du mit
`--serve` und veröffentlichst eine neue Version.
