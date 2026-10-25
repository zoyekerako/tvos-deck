"""Nachbau der Steam-Big-Picture-Oberfläche für die Vorschau.

Die Klassen sind hier in lesbarer Form (modul_Name) geschrieben und werden
beim Bauen genau wie das Theme über die CSS-Loader-Übersetzung in die echten
Steam-Hashes umgewandelt. Struktur und Klassen folgen dem Steam-Code
(Build 10/2026); Abstände und Größen sind angenähert.

Klassen mit Präfix „pv-“ gehören nur zur Vorschau (Layout-Hilfen).
Hauptmenü-Einträge nutzen die rohen Hashes, wie im echten Steam-DOM.
"""

GAMES = [
    (1245620, "ELDEN RING", "Zuletzt gespielt: heute"),
    (1086940, "Baldur's Gate 3", "Zuletzt gespielt: gestern"),
    (1145360, "Hades", "Spielzeit: 64 Std."),
    (367520, "Hollow Knight", "Spielzeit: 41 Std."),
    (413150, "Stardew Valley", "3 Freunde spielen"),
    (1091500, "Cyberpunk 2077", "Update verfügbar"),
    (814380, "Sekiro: Shadows Die Twice", "Spielzeit: 27 Std."),
    (1593500, "God of War", "Spielzeit: 33 Std."),
    (620, "Portal 2", "Spielzeit: 19 Std."),
    (1174180, "Red Dead Redemption 2", "Spielzeit: 88 Std."),
    (2050650, "Resident Evil 4", "Spielzeit: 22 Std."),
    (1888930, "The Last of Us Part I", "Spielzeit: 15 Std."),
]


def art(appid: int, kind: str) -> str:
    files = {"portrait": "library_600x900.jpg", "hero": "library_hero.jpg",
             "logo": "logo.png", "header": "header.jpg"}
    return f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/{files[kind]}"


# --------------------------------------------------------------------------
# Icons (einfache Linien-Icons im Stil der Steam-UI)
# --------------------------------------------------------------------------
_PATHS = {
    "home": '<path d="M3 11.5 12 4l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z"/>',
    "library": '<rect x="4" y="4" width="7" height="7" rx="1.5"/><rect x="13" y="4" width="7" height="7" rx="1.5"/><rect x="4" y="13" width="7" height="7" rx="1.5"/><rect x="13" y="13" width="7" height="7" rx="1.5"/>',
    "store": '<path d="M5 8h14l-1.2 12H6.2z"/><path d="M9 8V6.5a3 3 0 0 1 6 0V8"/>',
    "media": '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="10" r="1.6"/><path d="m21 16-5-5-8 8"/>',
    "download": '<path d="M12 4v11"/><path d="m7 10 5 5 5-5"/><path d="M5 20h14"/>',
    "friends": '<circle cx="9" cy="8" r="3.2"/><path d="M3 20c.6-3.6 3-5.5 6-5.5s5.4 1.9 6 5.5"/><circle cx="17" cy="9" r="2.4"/><path d="M16.5 14.6c2.4.2 4 1.9 4.5 5"/>',
    "settings": '<circle cx="12" cy="12" r="3"/><path d="M12 2.8v2.6M12 18.6v2.6M2.8 12h2.6M18.6 12h2.6M5.5 5.5l1.8 1.8M16.7 16.7l1.8 1.8M5.5 18.5l1.8-1.8M16.7 7.3l1.8-1.8"/>',
    "power": '<path d="M12 3v9"/><path d="M6.3 6.5a8 8 0 1 0 11.4 0"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6"/><path d="m15 15 5 5"/>',
    "bell": '<path d="M6 16V11a6 6 0 0 1 12 0v5l1.5 2h-15z"/><path d="M10 20a2 2 0 0 0 4 0"/>',
    "wifi": '<path d="M2.5 9a14 14 0 0 1 19 0"/><path d="M5.5 12.5a9.5 9.5 0 0 1 13 0"/><path d="M8.7 16a5 5 0 0 1 6.6 0"/><circle cx="12" cy="19.2" r=".6" fill="currentColor"/>',
    "battery": '<rect x="2.5" y="7" width="17" height="10" rx="2.2"/><rect x="4.5" y="9" width="11" height="6" rx="1" fill="currentColor" stroke="none"/><path d="M21.5 10.5v3"/>',
    "play": '<path d="M7 4.5v15l12.5-7.5z" fill="currentColor" stroke="none"/>',
    "heart": '<path d="M12 20s-7.5-4.6-7.5-10A4.3 4.3 0 0 1 12 7.4 4.3 4.3 0 0 1 19.5 10c0 5.4-7.5 10-7.5 10z"/>',
    "gamepad": '<path d="M7 8h10a4 4 0 0 1 3.9 4.9l-.9 3.8a2 2 0 0 1-3.4.9L14.5 15h-5l-2.1 2.6a2 2 0 0 1-3.4-.9l-.9-3.8A4 4 0 0 1 7 8z"/><path d="M8 11v3M6.5 12.5h3"/><circle cx="16" cy="11.5" r=".8" fill="currentColor"/><circle cx="17.6" cy="13.2" r=".8" fill="currentColor"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5"/><circle cx="12" cy="7.8" r=".8" fill="currentColor"/>',
    "music": '<path d="M9 18V5l11-2v13"/><circle cx="6.5" cy="18" r="2.5"/><circle cx="17.5" cy="16" r="2.5"/>',
    "help": '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.7.3-1 .9-1 1.7"/><circle cx="12" cy="16.8" r=".8" fill="currentColor"/>',
    "plug": '<path d="M9 3v5M15 3v5"/><path d="M6.5 8h11v3a5.5 5.5 0 0 1-11 0z"/><path d="M12 16.5V21"/>',
    "bolt": '<path d="M13 3 5 13.5h6L10 21l8-10.5h-6z"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M5.3 18.7l1.4-1.4M17.3 6.7l1.4-1.4"/>',
    "speaker": '<path d="M4 9.5h3.5L12 5.5v13l-4.5-4H4z"/><path d="M15.5 9a4 4 0 0 1 0 6"/><path d="M18 6.5a7.5 7.5 0 0 1 0 11"/>',
    "chevron": '<path d="m6 9 6 6 6-6"/>',
    "monitor": '<rect x="3" y="4.5" width="18" height="12" rx="2"/><path d="M8.5 20h7M12 16.5V20"/>',
    "lock": '<rect x="5" y="10.5" width="14" height="10" rx="2"/><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5"/>',
    "disk": '<rect x="3.5" y="6" width="17" height="12" rx="2"/><path d="M7 14h4"/><circle cx="16.5" cy="12" r="1.2"/>',
    "bluetooth": '<path d="m7 7 10 10-5 4V3l5 4L7 17"/>',
    "keyboard": '<rect x="2.5" y="6" width="19" height="12" rx="2"/><path d="M6 10h.01M9.5 10h.01M13 10h.01M16.5 10h.01M7 14.5h10"/>',
    "brush": '<path d="M14.5 4.5 19.5 9.5 11 18l-5-5z"/><path d="M6 13c-2 0-3 1.5-3 3.5V20h3.5C8.5 20 10 19 10 17"/>',
}


# Gefüllte Glyphen für Stellen, an denen Steam Icons per „fill“ einfärbt
_FILLED = {
    "gamepad": '<path d="M7.2 7h9.6a4.6 4.6 0 0 1 4.5 5.6l-.9 4a2.3 2.3 0 0 1-3.9 1.1L14.3 15H9.7l-2.2 2.7a2.3 2.3 0 0 1-3.9-1.1l-.9-4A4.6 4.6 0 0 1 7.2 7zM7 10v1.6H5.4v1.8H7V15h1.8v-1.6h1.6v-1.8H8.8V10zm9 .4a1 1 0 1 0 0 2 1 1 0 0 0 0-2zm1.8 1.9a1 1 0 1 0 0 2 1 1 0 0 0 0-2z" fill-rule="evenodd"/>',
    "heart": '<path d="M12 20.5S3.8 15.6 3.8 9.9A4.6 4.6 0 0 1 12 7.1a4.6 4.6 0 0 1 8.2 2.8c0 5.7-8.2 10.6-8.2 10.6z"/>',
    "info": '<path fill-rule="evenodd" d="M12 2.5a9.5 9.5 0 1 1 0 19 9.5 9.5 0 0 1 0-19zM11 10.5h2v6.5h-2zm0-3.8h2v2.1h-2z"/>',
    "settings": '<path fill-rule="evenodd" d="M10.6 2h2.8l.5 2.6 1.9.8 2.2-1.5 2 2-1.5 2.2.8 1.9 2.7.5v2.9l-2.7.5-.8 1.9 1.5 2.2-2 2-2.2-1.5-1.9.8-.5 2.7h-2.8l-.5-2.7-1.9-.8-2.2 1.5-2-2 1.5-2.2-.8-1.9L2 13.4v-2.9l2.6-.5.8-1.9-1.5-2.2 2-2 2.2 1.5 1.9-.8zM12 8.4a3.6 3.6 0 1 0 0 7.2 3.6 3.6 0 0 0 0-7.2z"/>',
}


def icon(name: str, size: int = 24, filled: bool = False) -> str:
    if filled:
        return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="currentColor" aria-hidden="true">'
                f'{_FILLED[name]}</svg>')
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="currentColor" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_PATHS[name]}</svg>')


# --------------------------------------------------------------------------
# Seitengerüst je Steam-Fenster
# --------------------------------------------------------------------------
def page(window: str, title: str, body: str, transparent: bool = False) -> tuple[str, str]:
    html = f"""<!doctype html>
<html lang="de" data-window="{window}">
<head>
<meta charset="utf-8">
<title>{title}</title>
<link rel="stylesheet" href="steam/sp.css">
<link rel="stylesheet" href="frame.css">
<script src="theme-data.js"></script>
</head>
<body class="pv-body{' pv-transparent' if transparent else ''}">
{body}
<script src="runtime.js"></script>
<script src="snapshot.js"></script>
</body>
</html>
"""
    return window, html


def header(title: str = "") -> str:
    left = f'<div class="header_Title pv-header-title">{title}</div>' if title else '<div class="pv-header-title"></div>'
    return f"""
<div class="header_Header">
  {left}
  <div class="header_HeaderItem header_Clickable Panel Focusable" tabindex="0" aria-label="Suche">{icon("search")}</div>
  <div class="header_HeaderItem header_NotificationsIcon header_Clickable Panel Focusable" tabindex="0" aria-label="Benachrichtigungen">{icon("bell")}</div>
  <div class="header_HeaderItem header_WirelessIcon">{icon("wifi")}</div>
  <div class="header_HeaderItem header_BatteryIcon"><span class="header_Percentage">87%</span>{icon("battery")}</div>
  <div class="header_Clock">21:41</div>
</div>"""


def footer(items=(("A", "Auswählen"), ("B", "Zurück"), ("☰", "Optionen"))) -> str:
    legend = "".join(f'<div class="pv-legend"><span class="pv-glyph">{k}</span>{label}</div>' for k, label in items)
    return f'<div class="footer_BasicFooter"><div class="footer_FooterLegend">{legend}</div></div>'


def sp_shell(content: str, title: str = "", overlay: str = "") -> str:
    return f"""
<div class="gamepadui_BasicUiRoot BasicUI pv-root">
  <div class="gamepadui_BasicHome gamepadui_OpaqueBackground">
    <div class="gamepadui_Content pv-content">{content}</div>
    {header(title)}
    {footer()}
  </div>
  {overlay}
</div>"""


# --------------------------------------------------------------------------
# Bausteine
# --------------------------------------------------------------------------
def capsule(game, w, h, landscape=False, ctx="InRecentGames", autofocus=False) -> str:
    appid, name, _sub = game
    img = art(appid, "header" if landscape else "portrait")
    lcls = " appportrait_Landscape" if landscape else ""
    af = " data-autofocus" if autofocus else ""
    return f"""<div class="appportrait_LibraryItemBox appportrait_{ctx}{lcls} Panel Focusable" tabindex="0"{af}
     aria-label="{name}" data-hero="{art(appid, 'hero')}" style="width:{w}px;height:{h}px">
  <img class="appportrait_PortraitImage appportrait_Capsule appportrait_CapsuleVisible{lcls}" src="{img}" alt="">
</div>"""


def carousel(games) -> str:
    cap_h, label_h, gap = 216, 52, 12
    item_h = cap_h + label_h
    portrait_w = 144
    featured_w = round(1.5 * 460 / 215 * portrait_w)
    x, items = 0, []
    for i, g in enumerate(games):
        featured = i == 0
        w = featured_w if featured else portrait_w
        fcls = " basicgamecarousel_Featured" if featured else ""
        glow = art(g[0], "header" if featured else "portrait")
        items.append(f"""
<div class="basicgamecarousel_BasicGameCarouselItem Panel" style="position:absolute;left:{x}px;top:12px;width:{w}px;height:{item_h}px">
  <div class="basicgamecarousel_BasicGameCarouselItemMediaContainer{fcls} Panel" style="width:{w}px;height:{item_h}px">
    <div class="basicgamecarousel_AppPortraitWrapper" style="height:{cap_h}px;position:relative">
      {capsule(g, w, cap_h, landscape=featured, autofocus=featured)}
      <img class="basicgamecarousel_CarouselCapsuleBackgroundGlow basicgamecarousel_PortraitImage basicgamecarousel_Capsule basicgamecarousel_CapsuleVisible" src="{glow}" alt="">
    </div>
    <div class="basicgamecarousel_CarouselGameLabelWrapper" style="width:460px">
      <div class="basicgamecarousel_CarouselGameLabel">
        <div class="pv-labelstack"><div>{g[1]}</div>
          <div class="basicgamecarousel_SubMessage basicgamecarousel_Play">{icon("play", 12)}<span>{g[2]}</span></div></div>
      </div>
    </div>
  </div>
</div>""")
        x += w + gap
    grid_h = item_h + 58
    return f"""
<div class="basicgamecarousel_BasicGameCarousel basicgamecarousel_VirtualizedBoxCarousel Panel">
  <div class="ReactVirtualized__Grid pv-hscroll" style="position:relative;height:{grid_h}px;width:100%;overflow-x:auto;overflow-y:hidden">
    <div class="ReactVirtualized__Grid__innerScrollContainer" style="position:relative;width:{x + 40}px;height:{grid_h}px;overflow:visible">{''.join(items)}</div>
  </div>
</div>"""


def tabs_row(labels, selected=0, group="tabs") -> str:
    tabs = "".join(
        f'<div class="gamepadtabbedpage_Tab{" gamepadtabbedpage_Selected" if i == selected else ""} Panel Focusable" tabindex="0" '
        f'data-select="gamepadtabbedpage_Selected" data-group="{group}"><div class="gamepadtabbedpage_TabTitle">{label}</div></div>'
        for i, label in enumerate(labels))
    return f"""
<div class="gamepadtabbedpage_TabHeaderRowWrapper">
  <div class="gamepadtabbedpage_TabRow">
    <div class="gamepadtabbedpage_TabRowTabs"><div class="gamepadtabbedpage_TabsRowScroll">
      <div class="gamepadtabbedpage_FixCenterAlignScroll Panel">{tabs}</div>
    </div></div>
  </div>
</div>"""


def tabbed_page(labels, content, height="100%", extra_cls="", group="tabs") -> str:
    return f"""
<div class="gamepadtabbedpage_GamepadTabbedPage {extra_cls}" style="height:{height}">
  {tabs_row(labels, group=group)}
  <div class="gamepadtabbedpage_TabContents"><div class="gamepadtabbedpage_ContentTransition">
    <div class="gamepadtabbedpage_TabContentsScroll pv-vscroll" style="overflow-y:auto">{content}</div>
  </div></div>
</div>"""


def grid(games, w=150, h=225, ctx="InLibraryManager") -> str:
    cells = "".join(f'<div class="Panel pv-cell">{capsule(g, w, h, ctx="pv", autofocus=(i == 0))}</div>'
                    for i, g in enumerate(games))
    return f'<div class="pv-grid" style="grid-template-columns:repeat(auto-fill,{w}px)">{cells}</div>'


def field(label, children="", desc="", highlight=True, sep=True, clickable=False, below=False) -> str:
    cls = ["gamepaddialog_Field", "gamepaddialog_StandardPadding", "Panel"]
    if highlight:
        cls.append("gamepaddialog_HighlightOnFocus")
    if sep:
        cls.append("gamepaddialog_WithBottomSeparatorStandard")
    if clickable:
        cls += ["gamepaddialog_Clickable", "Focusable"]
    if below:
        cls += ["gamepaddialog_WithChildrenBelow", "gamepaddialog_ChildrenWidthGrow"]
    else:
        cls += ["gamepaddialog_ChildrenWidthFixed", "gamepaddialog_VerticalAlignCenter"]
    tab = ' tabindex="0"' if clickable else ""
    desc_html = f'<div class="gamepaddialog_FieldDescription">{desc}</div>' if desc else ""
    label_html = f'<div class="gamepaddialog_FieldLabelRow"><div class="gamepaddialog_FieldLabel">{label}</div></div>'
    kids = (f'<div class="gamepaddialog_FieldChildrenWithIcon"><div class="gamepaddialog_FieldChildrenInner">'
            f'{children}</div></div>') if children else ""
    if below:
        return f"""<div class="{' '.join(cls)}"{tab} style="flex-direction:column;align-items:stretch">
  {label_html}{kids}{desc_html}
</div>"""
    return f"""<div class="{' '.join(cls)}"{tab} style="align-items:center">
  <div class="_EifR99lo_FieldLeftColumn" style="flex:1;min-width:0">{label_html}{desc_html}</div>
  <div class="_EifR99lo_FieldRightColumn">{kids}</div>
</div>"""


def toggle(on: bool) -> str:
    return (f'<div class="gamepaddialog_Toggle{" gamepaddialog_On" if on else ""} Panel Focusable" tabindex="0" '
            f'data-toggle="gamepaddialog_On"><div class="gamepaddialog_ToggleRail"></div>'
            f'<div class="gamepaddialog_ToggleSwitch"></div></div>')


def slider(value: float, ico: str = "") -> str:
    icon_html = f'<div class="gamepadslider_Icon">{icon(ico)}</div>' if ico else ""
    return f"""<div class="gamepadslider_SliderControlPanelGroup pv-sliderrow">{icon_html}
  <div class="gamepadslider_SliderControlAndNotches Panel Focusable pv-grow" tabindex="0" data-slider>
    <div class="gamepadslider_SliderControl" style="--normalized-slider-value:{value};--normalized-slider-origin:0;--slider-extra-notch-padding:0px;--normalized-slider-default-value:0">
      <div class="gamepadslider_SliderTrack"></div>
      <div class="gamepadslider_SliderHandleContainer"><div class="gamepadslider_SliderHandle"></div></div>
    </div>
  </div>
</div>"""


def button(label, primary=False, cls="", autofocus=False) -> str:
    p = " Primary" if primary else ""
    af = " data-autofocus" if autofocus else ""
    return f'<button class="DialogButton gamepaddialog_Button{p} {cls} Panel Focusable" tabindex="0"{af}>{label}</button>'


def dropdown(value: str) -> str:
    return (f'<button class="DialogButton gamepaddialog_Button gamepaddropdown_DropDownControlButton Panel Focusable pv-dropdown" tabindex="0">'
            f'<div class="dropdownlabel_DropDownLabelContainer"><div class="dropdownlabel_DropDownLabelTextColumn">'
            f'<div class="dropdownlabel_DropDownLabelTitle">{value}</div></div></div>{icon("chevron", 18)}</button>')


# --------------------------------------------------------------------------
# Screens
# --------------------------------------------------------------------------
def home_content() -> str:
    hero = art(GAMES[0][0], "hero")
    lower = tabbed_page(["Neuigkeiten", "Freunde", "Empfohlen"],
                        f'<div class="pv-shelf">{"".join(capsule(g, 136, 204, ctx="InFriendsActivity") for g in GAMES[4:11])}</div>',
                        height="420px", group="hometabs")
    return f"""
<div class="gamepadhome_BackstackRootTest" data-bigart>
  <div class="gamepadhome_ScrollArea pv-vscroll" style="overflow-y:auto;overflow-x:hidden;height:100%;width:100%">
    <div class="gamepadhome_RecentSection Panel">
      <div class="gamepadhomerecentgames_RecentGamesContainer">
        <div class="gamepadhomerecentgames_RecentGamesBackgroundContainer">
          <div class="gamepadhomerecentgames_RecentGamesBackgroundImages">
            <div class="gamepadhomerecentgames_RecentGamesBackground">
              <img class="gamepadhomerecentgames_RecentGamesBackgroundImage" data-hero-target src="{hero}" alt="">
            </div>
          </div>
        </div>
        <div class="gamepadhomerecentgames_RecentGamesInnerContainer">
          <div class="gamepadhomerecentgames_RecentGamesHeader">
            <div class="gamepadhomerecentgames_RecentGamesHeaderLabel gamepadhomerecentgames_HeaderEnter">Zuletzt gespielt</div>
            <div class="gamepadhomerecentgames_Spacer"></div>
          </div>
          {carousel(GAMES[:9])}
        </div>
      </div>
    </div>
    <div class="gamepadhome_TabbedContent pv-tabbedcontent">{lower}</div>
  </div>
</div>"""


def library_content() -> str:
    page_ = tabbed_page(["Großartig auf dem Deck", "Alle Spiele", "Installiert", "Sammlungen"],
                        grid(GAMES), height="100%", group="libtabs")
    return f'<div class="gamepadlibrary_GamepadLibrary pv-fill">{page_}</div>'


def game_content() -> str:
    appid, name, _ = GAMES[0]
    stats = "".join(
        f'<div class="appdetailsplaysection_GameStat"><div class="appdetailsplaysection_GameStatRight">'
        f'<div class="appdetailsplaysection_PlayBarLabel">{a}</div><div class="appdetailsplaysection_PlayBarDetailLabel">{b}</div>'
        f'</div></div>'
        for a, b in (("Zuletzt gespielt", "Heute"), ("Spielzeit", "126,4 Std."), ("Erfolge", "38/42")))
    menu_buttons = "".join(
        f'<div class="appdetailsplaysection_MenuButton {extra} Panel Focusable" tabindex="0" aria-label="{label}">{icon(ico, filled=True)}</div>'
        for ico, extra, label in (
            ("gamepad", "appdetailsplaysection_ControllerConfigButton", "Controller"),
            ("heart", "appdetailsplaysection_FavoriteButton appdetailsplaysection_Favorited", "Favorit"),
            ("info", "appdetailsplaysection_GameInfoButton", "Info"),
            ("settings", "", "Einstellungen")))
    sections = "".join(
        f'<div class="appdetailssection_AppDetailsSectionContainer appdetailssection_RightColumnSection Panel Focusable pv-section" tabindex="0">'
        f'<div class="appdetailssection_Body"><div class="pv-section-title">{t}</div><div class="pv-section-text">{d}</div></div></div>'
        for t, d in (("Patch 1.16 verfügbar", "Neue Balance-Änderungen und Fehlerbehebungen für Mehrspieler-Sitzungen."),
                     ("3 Freunde haben gespielt", "Lea, Jonas und Mia waren diese Woche unterwegs in den Zwischenlanden."),
                     ("Erfolg freigeschaltet", "„Elden-Herrscher“ – nur 9,8 % aller Spieler haben ihn.")))
    tabs = tabbed_page(["Aktivität", "Deine Inhalte", "Community", "Spielinfos"], sections,
                       height="560px", group="gametabs")
    return f"""
<div class="basicappdetailssectionstyler_AppDetailsRoot pv-fill pv-vscroll" style="overflow-y:auto">
  <div class="basicappdetailssectionstyler_AppDetailsContainer" style="height:auto">
    <div class="basicappdetailssectionstyler_Header" style="position:relative">
      <div class="sharedappdetailsheader_TopCapsule" style="height:100%">
        <div class="sharedappdetailsheader_HeaderBackgroundImage" style="height:100%">
          <div class="sharedappdetailsheader_ImgContainer"><img class="sharedappdetailsheader_ImgSrc" src="{art(appid, 'hero')}" alt=""></div>
        </div>
      </div>
      <div class="sharedappdetailsheader_BoxSizerContainer">
        <div class="sharedappdetailsheader_BoxSizerValidRegion">
          <div class="sharedappdetailsheader_BoxSizer sharedappdetailsheader_BottomLeft" style="left:2%;top:38%;width:36%;height:44%">
            <img class="sharedappdetailsheader_TitleLogo sharedappdetailsheader_Loaded" src="{art(appid, 'logo')}" alt="{name}">
          </div>
        </div>
      </div>
    </div>
    <div class="basicappdetailssectionstyler_PlaySection">
      <div class="appdetailsplaysection_Container"><div class="appdetailsplaysection_PlayBar"><div class="appdetailsplaysection_InnerContainer">
        <div class="appdetailsplaysection_Row">
          <div class="basicappdetailssectionstyler_ActionRow pv-grow">
            <div class="basicappdetailssectionstyler_ActionButtonAndStatusPanel">
              <div class="basicappdetailssectionstyler_AppActionButton basicappdetailssectionstyler_InvertFocusedIcon">
                <div class="appactionbutton_PlayButtonContainer appactionbutton_Green">
                  <div class="appactionbutton_PlayButton appactionbutton_ButtonChild Panel Focusable pv-playbutton" tabindex="0" data-autofocus>
                    {icon("play", 22)}<div class="appactionbutton_ButtonText">Spielen</div>
                  </div>
                </div>
              </div>
            </div>
            <div class="appdetailsplaysection_StatusAndStats appdetailsplaysection_PermanentlyUnavailable">
              <div class="appdetailsplaysection_GameStatsSection">{stats}</div>
            </div>
            <div class="basicappdetailssectionstyler_AppButtons">{menu_buttons}</div>
          </div>
        </div>
      </div></div></div>
    </div>
    {tabs}
  </div>
</div>"""


SETTINGS_PAGES = [("settings", "Allgemein"), ("monitor", "System"), ("lock", "Sicherheit"),
                  ("disk", "Interner Speicher"), ("sun", "Anzeige"), ("speaker", "Audio"),
                  ("bluetooth", "Bluetooth"), ("gamepad", "Controller"), ("keyboard", "Tastatur"),
                  ("brush", "Anpassung"), ("library", "Bibliothek")]


def settings_content() -> str:
    items = "".join(
        f'<div class="gamepadpagedsettings_PagedSettingsDialog_PageListItem{" gamepadpagedsettings_Active" if label == "Anzeige" else ""} Panel Focusable" tabindex="0"'
        f'{" data-autofocus" if label == "Anzeige" else ""} data-select="gamepadpagedsettings_Active" data-group="settingspages">'
        f'<div class="_4hESt2MY_ScaledChildren"><div class="gamepadpagedsettings_PageListItem_Icon">{icon(ico)}</div>'
        f'<div class="gamepadpagedsettings_PageListItem_Title">{label}</div></div></div>'
        for ico, label in SETTINGS_PAGES)
    fields = "".join([
        '<div class="DialogHeader">Anzeige</div>',
        field("Helligkeit", slider(0.62, "sun"), below=True),
        field("Automatische Helligkeit", toggle(True), desc="Passt die Helligkeit an das Umgebungslicht an."),
        field("Nachtmodus", toggle(False)),
        field("Sprache", dropdown("Deutsch")),
        field("Skalierung der Benutzeroberfläche", dropdown("100 %")),
        '<div class="DialogControlsSectionHeader">Erweitert</div>',
        field("HDR aktivieren", toggle(True)),
        field("Externe Anzeige", button("Einstellungen öffnen")),
        field("Über dieses Gerät", desc="SteamOS 3.8 · Steam-Client Oktober 2026", clickable=True),
    ])
    return f"""
<div class="gamepadpagedsettings_PagedSettingsDialog pv-fill">
  <div class="gamepadpagedsettings_PagedSettingsDialog_PageListColumn">
    <div class="gamepadpagedsettings_PagedSettingsDialog_PageList pv-vscroll" style="padding-top:56px">
      <div class="gamepadpagedsettings_PagedSettingsDialog_Title pv-settings-title">Einstellungen</div>
      {items}
    </div>
  </div>
  <div class="gamepadpagedsettings_PagedSettingDialog_ContentColumn pv-settings-content">
    <div class="DialogContent gamepadpagedsettings_PagedSettingsDialog_PageContent pv-vscroll">
      <div class="DialogBody">{fields}</div>
    </div>
  </div>
</div>"""


def dialog_overlay() -> str:
    return f"""
<div class="gamepadui_GamepadDialogOverlay FullModalOverlay pv-overlay" data-modal>
  <div class="ModalOverlayContent pv-fill">
    <div class="ModalOverlayBackground pv-fill"></div>
    <div class="gamepaddialog_ModalPosition gamepaddialog_WithStandardPadding Panel">
      <div class="gamepaddialog_GamepadDialogContent">
        <div class="DialogHeader">Spiel beenden?</div>
        <div class="DialogBody"><div class="DialogBodyText">Nicht gespeicherter Fortschritt in „ELDEN RING“ geht dabei verloren.</div></div>
        <div class="DialogFooter"><div class="pv-dialog-buttons">
          {button("Spiel beenden", primary=True, autofocus=True)}
          {button("Abbrechen")}
        </div></div>
      </div>
    </div>
  </div>
</div>"""


def context_overlay() -> str:
    entries = [("Spielen", "gamepadcontextmenu_Positive"), ("Zu Favoriten hinzufügen", ""),
               ("Zur Sammlung hinzufügen …", ""), (None, ""), ("Eigenschaften …", ""),
               ("Verwalten", "gamepadcontextmenu_SubMenu"), ("Deinstallieren", "gamepadcontextmenu_Destructive")]
    items = ""
    for i, (label, extra) in enumerate(entries):
        if label is None:
            items += '<div class="gamepadcontextmenu_ContextMenuSeparator"></div>'
            continue
        af = " data-autofocus" if i == 0 else ""
        items += (f'<div class="gamepadcontextmenu_contextMenuItem {extra} Panel Focusable" tabindex="0"{af} '
                  f'data-focusclass="gamepadcontextmenu_Focused">{label}</div>')
    return f"""
<div class="gamepadcontextmenu_BasicContextMenuModal pv-overlay" data-modal>
  <div class="gamepadcontextmenu_contextMenuFade pv-fill"></div>
  <div class="gamepadcontextmenu_BasicContextMenuHeader" style="position:relative">ELDEN RING</div>
  <div class="gamepadcontextmenu_BasicContextMenuHeaderShrinkableSpacing"></div>
  <div class="gamepadcontextmenu_BasicContextMenuContainer" style="position:relative">
    <div class="gamepadcontextmenu_contextMenuContents Panel">{items}</div>
  </div>
</div>"""


KEY_ROWS = [list("1234567890ß") + ["⌫"], ["Tab"] + list("qwertzuiopü"), ["⇪"] + list("asdfghjklöä") + ["Enter"],
            ["⇧"] + list("yxcvbnm,.-") + ["⇧"], ["&123", "🙂", "Leertaste", "←", "→", "Ausblenden"]]


def keyboard_overlay() -> str:
    rows = ""
    for r, row in enumerate(KEY_ROWS):
        keys = ""
        for key in row:
            grow = 6 if key == "Leertaste" else (1.6 if len(key) > 1 else 1)
            af = " data-autofocus" if (r == 1 and key == "w") else ""
            keys += (f'<div class="virtualkeyboard_KeyboardKey Panel Focusable" tabindex="0"{af} '
                     f'data-focusclass="virtualkeyboard_Focused" style="flex:{grow} 1 0;margin:3px"><span>{key}</span></div>')
        rows += f'<div class="virtualkeyboard_KeyboardRow pv-kbrow">{keys}</div>'
    return f"""
<div class="pv-keyboard-host" data-modal>
  <div class="virtualkeyboard_Keyboard DefaultTheme">{rows}</div>
</div>"""


def keyboard_content() -> str:
    return f"""
<div class="pv-fill pv-search">
  <div class="pv-search-inner">
    <div class="DialogHeader pv-search-title">Suche</div>
    <input class="gamepaddialog_BasicTextInput DialogInput gpfocus" value="Hollow Kn" readonly>
    <div class="pv-search-results">{"".join(capsule(g, 120, 180, ctx="pv") for g in GAMES[3:4])}</div>
  </div>
</div>"""


def main_menu() -> str:
    entries = [("home", "Startseite", True), ("library", "Bibliothek", False), ("store", "Shop", False),
               ("media", "Medien", False), ("download", "Downloads", False), ("friends", "Freunde & Chat", False),
               ("settings", "Einstellungen", False), ("power", "Ein/Aus", False)]
    items = ""
    for ico, label, active in entries:
        dot = '<div class="_1uLVHdiiCg78BRnhqLxUID" style="width: 10px; height: 50%;"></div>' if active else ""
        act = " _10bq5BppQ3fcLqTNXms8yA" if active else ""
        af = " data-autofocus" if active else ""
        items += f"""
  <div class="_1BbM8Qq8OL5N8gL4PYH397">
    <div role="menuitem" aria-label="{label}" class="_2w9TpQwxU7vcwaAbf3KGv_{act} Panel Focusable" tabindex="0"{af}>
      {dot}<div class="_3xZ3ZujYllkNRr5UdDfNmz">{icon(ico)}</div>
      <div class="_3x-ZK1MiNB1Uvo7Aa6qEBs"><div class="pv-marquee">{label}</div></div>
    </div>
  </div>"""
    nav = "".join(
        f'<div class="_xfZ18oWU_NavigationMenuItem{" _xfZ18oWU_Active" if i == 0 else ""} Panel Focusable pv-navitem" tabindex="0">{label}</div>'
        for i, label in enumerate(["Spiel fortsetzen", "Controller-Einstellungen", "Erfolge", "Anleitungen",
                                   "Notizen", "Spielaufnahme", "Spiel beenden"]))
    return f"""
<div class="BasicUI mainmenu_Container mainmenu_Open">
  <div role="menu" aria-label="Steam-Menü" class="mainmenu_Menu mainmenu_Open Panel">{items}
    <div class="_3kHmfV9Pej6JhVOBMGhcgq"></div>
  </div>
  <div class="_xfZ18oWU_ScrollMask _xfZ18oWU_Visible pv-ingame" data-ingame>
    <div class="_xfZ18oWU_NavigationColumn Panel pv-navcolumn">
      <img class="_xfZ18oWU_CurrentGameLogo" src="{art(GAMES[0][0], 'logo')}" alt="">
      {nav}
    </div>
    <div class="_xfZ18oWU_AppColumn _xfZ18oWU_FocusedColumn"><div class="pv-appcolumn">ELDEN RING läuft</div></div>
  </div>
</div>"""


def qam() -> str:
    tab_icons = [("bell", False), ("friends", False), ("settings", True), ("bolt", False),
                 ("music", False), ("help", False), ("plug", False)]
    tabs = "".join(
        f'<div class="quickaccessmenu_Tab{" quickaccessmenu_Selected" if sel else ""} Panel Focusable" tabindex="0" '
        f'data-select="quickaccessmenu_Selected" data-group="qamtabs">{icon(ico)}</div>'
        for ico, sel in tab_icons)
    def section(title, rows):
        return (f'<div class="quickaccessmenu_PanelSection"><div class="quickaccessmenu_PanelSectionTitle">'
                f'<div class="quickaccessmenu_Text">{title}</div></div>'
                + "".join(f'<div class="quickaccessmenu_PanelSectionRow">{r}</div>' for r in rows) + "</div>")
    content = "".join([
        section("Akku", ['<div class="pv-battery"><span class="quickaccesscontrols_BatteryPercentageLabel">87%</span>'
                         '<span class="quickaccesscontrols_BatteryDetailsLabels pv-batterydetails">ca. 4 Std. 12 Min.</span></div>']),
        section("Allgemein", [field("Flugmodus", toggle(False)), field("WLAN", toggle(True)),
                              field("Bluetooth", toggle(True))]),
        section("Anzeige", [field("Helligkeit", slider(0.7, "sun"), below=True),
                            field("Nachtmodus", toggle(False))]),
        section("Audio", [field("Lautstärke", slider(0.45, "speaker"), below=True)]),
    ])
    return f"""
<div class="BasicUI quickaccessmenu_Container quickaccessmenu_Open" id="QuickAccess-NA">
  <div id="QuickAccess-Menu" class="quickaccessmenu_QuickAccessMenu">
    <div class="quickaccessmenu_HeaderContainer"></div>
    <div class="quickaccessmenu_Menu">
      <div class="quickaccessmenu_Tabs Panel"><div class="_2zh9IsDz_TabList">{tabs}</div></div>
      <div class="quickaccessmenu_PanelOuterNav Panel">
        <div class="quickaccessmenu_AllTabContents">
          <div class="quickaccessmenu_ContentTransition quickaccessmenu_ActiveTab">
            <div class="quickaccessmenu_Title">Schnelleinstellungen</div>
            <div class="quickaccessmenu_TabGroupPanel pv-vscroll" style="overflow-y:auto" data-autofocus-scope>{content}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>"""


def toast() -> str:
    appid = GAMES[0][0]
    return f"""
<div class="gamepadtoasts_GamepadToastPlaceholder pv-toastplace">
  <div class="gamepadtoasts_GamepadToastPopup" style="--toast-duration: 99999s">
    <div class="shorttemplates_ShortTemplate shorttemplates_TwoLine">
      <img class="shorttemplates_ShortLogoDimensions" src="{art(appid, 'portrait')}" alt="" style="object-fit:cover">
      <div class="shorttemplates_Content shorttemplates_FullWidth">
        <div class="shorttemplates_Header"><div class="shorttemplates_Title">Erfolg freigeschaltet</div></div>
        <div class="shorttemplates_Body">Elden-Herrscher</div>
      </div>
    </div>
  </div>
</div>"""


def pages() -> dict:
    home = home_content()
    lib = library_content()
    return {
        "sp-home.html": page("sp", "Startseite", sp_shell(home)),
        "sp-library.html": page("sp", "Bibliothek", sp_shell(lib, "Bibliothek")),
        "sp-game.html": page("sp", "Spieleseite", sp_shell(game_content())),
        "sp-settings.html": page("sp", "Einstellungen", sp_shell(settings_content())),
        "sp-dialog.html": page("sp", "Dialog", sp_shell(lib, "Bibliothek", dialog_overlay())),
        "sp-contextmenu.html": page("sp", "Kontextmenü", sp_shell(lib, "Bibliothek", context_overlay())),
        "sp-keyboard.html": page("sp", "Tastatur", sp_shell(keyboard_content(), "Suche", keyboard_overlay())),
        "menu.html": page("menu", "Hauptmenü", main_menu(), transparent=True),
        "qam.html": page("qam", "Quick Access", qam(), transparent=True),
        "toast.html": page("toasts", "Benachrichtigung", toast(), transparent=True),
    }
