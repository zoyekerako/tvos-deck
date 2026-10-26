# Changelog

## 1.1.0 – 2026-10-25

- **Steam Machine / 16:9 / 4K:** checked at 1920 × 1080 logical pixels (4K at 200 % scaling); hairline separators
  on high-DPI screens; wide first home tile zooms less and tilts softer, and the tiles next to it move aside
  while it is focused instead of being covered.
- Removed `font-optical-sizing` (the validator on DeckThemes does not know it yet; it was the default anyway).
- Steam menu, Quick Access and toasts are now fully opaque glass (overlay windows cannot blur, text behind used
  to shine through).
- Quick Access: focus tile no longer touches the panel edge.
- New option **Keyboard Styling** (DeckThemes rule: keyboard theming must be switchable).
- Unique CSS variable prefix `--tvdeck-`.
- Removed 178 unnecessary `!important` (verified against Steam's CSS; computed styles unchanged).
- Option labels in English for the public theme browser.
- CSS passes the W3C validator used by DeckThemes (0 errors).

## 1.0.0 – 2026-10-25

- First version: tvOS focus, Top Shelf home, sidebar Steam menu, Control-Center-style Quick Access, game page,
  settings, controls, keyboard, toasts, options for focus effect, background, font, footer, reduce transparency
  and colors.
