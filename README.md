# ⚡ AlacrittyForge

> A terminal UI application for managing and customizing the Alacritty terminal emulator — safely, intuitively, and beautifully.

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Platform: Linux](https://img.shields.io/badge/Platform-Linux-lightgrey.svg)
![Python: 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)
![Status: Alpha](https://img.shields.io/badge/Status-Alpha-orange.svg)
![Version: 0.1.0](https://img.shields.io/badge/Version-0.1.0-purple.svg)

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

### Arch Linux (recommended)
```bash
sudo pacman -S python-textual python-rich python-tomli-w
git clone https://github.com/jetomev/alacrittyforge.git
cd alacrittyforge
```

### Other distributions
```bash
pip install textual rich tomli-w
git clone https://github.com/jetomev/alacrittyforge.git
cd alacrittyforge
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

### v0.1.0 — Current (Alpha)
- [x] Dashboard with config overview
- [x] Config editor with live validation
- [x] Theme browser with color palette preview
- [x] Font manager with system font listing
- [x] Key bindings viewer and editor
- [x] Automatic timestamped backups

### v0.2.0 — Planned
- [ ] Dropdown selectors for settings with fixed options (decorations, cursor shape, startup mode, etc.)
- [ ] Scrollable font picker from system fonts list
- [ ] Color picker for hex color fields
- [ ] Screenshots in README
- [ ] Backup restore screen

### Future
- [ ] AUR package
- [ ] Live preview of font changes
- [ ] Import/export config profiles

---

## Changelog

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