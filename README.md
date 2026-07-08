# ⚡ AlacrittyForge

> A terminal UI application for managing and customizing the Alacritty terminal emulator — safely, intuitively, and beautifully.

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Platform: Linux](https://img.shields.io/badge/Platform-Linux-lightgrey.svg)
![Python: 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)
![Status: Alpha](https://img.shields.io/badge/Status-Alpha-orange.svg)
![Version: 0.1.1](https://img.shields.io/badge/Version-0.1.1-purple.svg)
[![AUR](https://img.shields.io/aur/version/alacrittyforge)](https://aur.archlinux.org/packages/alacrittyforge)

---

## Why AlacrittyForge?

Alacritty is one of the fastest and most elegant terminal emulators available on Linux. But
configuring it means opening a TOML file in a text editor, knowing exactly what keys and values
are valid, and hoping you don't make a mistake that breaks your terminal.

There is no GUI. There is no safety net.

**AlacrittyForge exists to change that.**

We believe managing your terminal configuration should be:
- **Safe** — automatic backups before every change, confirmation dialogs before every write
- **Clear** — every setting explained in plain language, live validation before anything is saved
- **Beautiful** — a Catppuccin Mocha themed TUI that feels like a proper application
- **Accessible** — keyboard-driven, fast, and usable by people who just want their terminal to look right

AlacrittyForge was born from a simple frustration: why is configuring one of the best terminal
emulators also one of the most unfriendly experiences on Linux? It doesn't have to be.

---

## Features

- 🏠 **Dashboard** — system overview showing config status, active theme, font, opacity, and backup count
- 🔧 **Config Editor** — browse and edit all Alacritty settings with descriptions and live validation
- 🎨 **Theme Browser** — browse locally installed color themes, preview color palettes, apply with one key, and get guided help on installing new themes
- 🔤 **Font Manager** — view and edit all font settings including family, style, size, spacing, and offsets — with a live list of system fonts
- ⌨  **Key Bindings** — view all default and user-defined bindings, add custom bindings, delete user bindings
- 🗂 **Backup & Restore** — timestamped backups created automatically before every change, stored in `~/.config/alacritty/backups/`

---

## Screenshots

*Screenshots coming in v0.2.0*

---

## Requirements

- Linux
- Python 3.11 or newer
- Alacritty installed and configured
- `python-textual`, `python-rich`, `python-tomli-w`

---

## Installation

### Arch Linux — AUR (recommended)
```bash
yay -S alacrittyforge
```
Then just run `alacrittyforge`.

### Arch Linux — from source
```bash
sudo pacman -S python-textual python-rich python-tomli-w
git clone https://github.com/jetomev/alacrittyforge.git
cd alacrittyforge
python main.py
```

### Other distributions
```bash
pip install textual rich tomli-w
git clone https://github.com/jetomev/alacrittyforge.git
cd alacrittyforge
python main.py
```

---

## Usage
```bash
cd alacrittyforge
python main.py
```

> No `sudo` required — AlacrittyForge writes only to your user config at
> `~/.config/alacritty/alacritty.toml` and backups at `~/.config/alacritty/backups/`.

---

## Keybindings

### Global

| Key | Action |
|-----|--------|
| `1` | Dashboard |
| `2` | Config Editor |
| `3` | Theme Browser |
| `4` | Font Manager |
| `5` | Key Bindings |
| `?` | Help |
| `q` | Quit |

### Config Editor

| Key | Action |
|-----|--------|
| `E` | Edit selected value |
| `S` | Save all pending changes |
| `R` | Refresh from disk |

### Theme Browser

| Key | Action |
|-----|--------|
| `A` | Apply selected theme |
| `F5` | Refresh theme list |
| `H` | Toggle installation help guide |

### Font Manager

| Key | Action |
|-----|--------|
| `E` | Edit selected value |
| `S` | Save all pending changes |
| `R` | Refresh from disk |

### Key Bindings

| Key | Action |
|-----|--------|
| `N` | Add new binding |
| `D` | Delete selected binding |
| `R` | Refresh |

---

## Project Structure

```
alacrittyforge/
├── main.py                        # Entry point
├── alacrittyforge/
│   ├── app.py                     # Main Textual application shell
│   ├── config_manager.py          # TOML config parser, writer, validator
│   ├── backup_manager.py          # Backup create, list, restore, delete
│   ├── theme_manager.py           # Theme scanner, color extractor, applier
│   ├── font_manager.py            # Font settings reader and writer
│   ├── keybind_manager.py         # Keybinding reader, writer, defaults
│   ├── alacrittyforge.css         # Catppuccin Mocha stylesheet
│   ├── screens/
│   │   ├── dashboard.py           # System overview screen
│   │   ├── config_editor.py       # Config editor screen
│   │   ├── themes.py              # Theme browser screen
│   │   ├── fonts.py               # Font manager screen
│   │   └── keybindings.py         # Key bindings screen
│   └── widgets/
│       └── confirm_dialog.py      # Reusable confirmation dialog
```


---

## Safety Philosophy

AlacrittyForge is built around one principle: **never silently modify your config**.

Every change goes through three layers of protection:

1. **Validation** — input is checked before it is staged
2. **Confirmation** — a dialog asks you to confirm before anything is written
3. **Backup** — a timestamped backup of your current config is created automatically before every write

Backups are stored in `~/.config/alacritty/backups/` and kept up to a maximum of 20.

---

## Roadmap

### Future
- [ ] Live preview of font changes
- [ ] Import/export config profiles

### v0.2.0 — Planned
- [ ] Dropdown selectors for settings with fixed options (decorations, cursor shape, startup mode, etc.)
- [ ] Scrollable font picker from system fonts list
- [ ] Color picker for hex color fields
- [ ] Screenshots in README
- [ ] Backup restore screen

### v0.1.1 — Current (hardening + first AUR release)
- [x] Pending edits survive a screen switch (A1)
- [x] Unified status-line + toast feedback across all screens (A3, A6)
- [x] Help modal toggles instead of stacking; Esc/q/? dismiss (A2)
- [x] Screen bindings fire on entry without a panel click (A4)
- [x] ConfirmDialog: Esc cancels, Enter confirms (A5)
- [x] Published on the AUR

### v0.1.0 — April 2026 (initial alpha)
- [x] Dashboard with config overview
- [x] Config editor with live validation
- [x] Theme browser with color palette preview
- [x] Font manager with system font listing
- [x] Key bindings viewer and editor
- [x] Automatic timestamped backups

---

## Changelog

### v0.1.1 — May 28, 2026
**Hardening batch + first AUR release**

Closes 6 findings (A1–A6) from a systematic audit borrowing the grubForge hardening playbook (grubForge is the Forge-suite sibling for the GRUB bootloader). Shipped in four thematic groups:

- 🔒 **G1 — Pending safety + refresh-on-show split** *(A1)*. `on_show()` on Config Editor and Fonts used to call `_load_settings()`, which begins with `self._pending = {}` — so staging an edit, switching screens, and coming back silently wiped the stage. Split into `_reload_view()` (silent re-read; preserves `_pending` and selection) and `_load_settings()` (full reset; used by `on_mount` and as a hard-reset). `on_show` / `action_refresh` / post-save now route through the silent path.
- 💬 **G2 — Unified feedback surface** *(A3, A6)*. New `widgets/status.py::StatusMixin` provides one `_set_status(msg, level, popup=True)` that writes a colored icon + message to a per-screen status line **and** fires an app-level toast. `popup=False` for passive mount-time hints so the five screens don't spray notifications at app launch. The Dashboard gains an `R` action with toast; redundant duplicate status labels in Fonts (`#font-save-status`) and Key Bindings (`#keys-add-status`) are gone. Icons consolidated to the unicode set used in grubForge: `✓ ● ⚠ ✗`.
- ❓ **G3 — Help modal hardening** *(A2)*. The help overlay used to be an inline-nested `ModalScreen` class defined inside `action_show_help`, which `push_screen`'d on every keypress — pressing `?` twice stacked two help modals. Extracted to `widgets/help_screen.py`; the app now toggles (pop if already on top, else push). The modal binds `?` itself so a second `?` while open closes it directly; `q` stays bound on the modal so it shadows the app-level quit.
- 🎯 **G4 — Focus-on-show + ConfirmDialog keys** *(A4, A5)*. Screen bindings used to be inert until the user clicked into a panel — `ContentSwitcher` doesn't move focus on its own. Each action screen now declares `DEFAULT_FOCUS` (`#settings-table`, `#themes-list`, `#fonts-table`, `#keys-table`) and `App.action_show_screen` focuses it after `on_show`. `ConfirmDialog` gains `escape` → cancel, `enter` → confirm so keyboard users don't have to Tab+Space onto a button.

**Packaging:** Published on the AUR (`alacrittyforge`). The PKGBUILD's `check()` step runs a **headless mount** smoke under Textual's `run_test` harness — catches CSS-parse and `on_mount` failures at build time, not just import breaks.

No dependency changes. Same `python`, `python-textual`, `python-rich`, `python-tomli-w`.

### v0.1.0 — April 6, 2026
**First Alpha Release**
- 🏠 Dashboard with system overview
- 🔧 Config Editor with live validation
- 🎨 Theme Browser with color palette preview and installation guide
- 🔤 Font Manager with system font listing
- ⌨  Key Bindings viewer, adder, and deleter
- 🗂 Automatic timestamped backups before every change
- 🌙 Catppuccin Mocha theme throughout

---

## Authors

**jetomev** — idea, vision, direction, testing

**Claude (Anthropic)** — co-developer, architecture, implementation

This project was built as a collaboration between a human with a great idea and an AI that
helped bring it to life — one command at a time.

---

## License

AlacrittyForge is free software: you can redistribute it and/or modify it under the terms
of the **GNU General Public License v3.0** as published by the Free Software Foundation.

See [LICENSE](LICENSE) for the full license text.

---

## Contributing

Contributions are welcome! Please open an issue or pull request on GitHub.

If you find AlacrittyForge useful, consider starring the repository — it helps others find it.