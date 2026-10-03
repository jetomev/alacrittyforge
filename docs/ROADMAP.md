# alacrittyForge — full roadmap history

*The README carries the upcoming work and the two most recent releases; everything older lives here, newest-first.*

### v1.0.0 — October 2, 2026
- [x] Safe saving: notes and layout kept, one backup per save, never over an unreadable file, written in one step
- [x] Every Alacritty setting on Linux, in plain words, in eight groups
- [x] Themes with a preview, Adjust colours, hypeForge's themes locked, safe installs
- [x] Shortcuts in words, recorded by pressing the keys; Alacritty's own can be turned off
- [x] Backups screen: what restoring would change
- [x] Every major distribution: the setting names each Alacritty version reads
- [x] Manual inside the app, --version/--help, closing note, text console, 100 columns

### v0.2.0 — August 10, 2026

- [x] Rebuilt on [forgekit](https://github.com/jetomev/forgekit), the shared Forge foundation
- [x] Config: one-table in-place editing — dropdowns at the cell, filterable pickers, colour swatches, and a fixed footer where Save is the only thing that writes
- [x] Themes: preview-and-stage flow, support for **both** theming models, and one-click promotion of inline colours into a theme file
- [x] Fonts: the same table pattern, with a monospace-only picker (486 families on the test machine — the filter earns its keep)
- [x] Bindings: cell-level editing, with new, changed and deleted entries all saved together
- [x] Fixed a silent trap: colours written directly in your config quietly override an imported theme, so applying a theme now clears them

### v0.1.1 — May 2026

- [x] Staged edits survive switching screens
- [x] One consistent way of reporting what happened, across every screen
- [x] Help window toggles instead of stacking
- [x] Screen keys work as soon as you arrive, without clicking first
- [x] Confirmation dialogs: `Esc` cancels, `Enter` confirms
- [x] Published on the AUR

### v0.1.0 — April 2026 (initial alpha)
- [x] Dashboard with config overview
- [x] Config editor with live validation
- [x] Theme browser with color palette preview
- [x] Font manager with system font listing
- [x] Key bindings viewer and editor
- [x] Automatic timestamped backups

---
