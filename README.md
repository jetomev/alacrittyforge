# ⚡ alacrittyForge

> Alacritty's settings, without editing the file by hand: every setting in plain words, picked from lists, reviewed before it's saved, with a backup first and your own notes kept.

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Platform: Linux](https://img.shields.io/badge/Platform-Linux-lightgrey.svg)
![Python: 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)
![Status: Stable](https://img.shields.io/badge/Status-Stable-brightgreen.svg)
![Version: 1.1.0](https://img.shields.io/badge/Version-1.1.0-purple.svg)
[![AUR](https://img.shields.io/aur/version/alacrittyforge?v=1.0.0-1)](https://aur.archlinux.org/packages/alacrittyforge)

> 🛡 **Security** — every release is GPG-signed and every commit is GitHub-Verified. **[Where We Stand](https://github.com/jetomev/KognogOS/blob/main/docs/where-we-stand.md)** covers our response to the 2026 AUR supply-chain attacks and how to check us yourself.

---

## Why alacrittyForge?

Alacritty is one of the fastest and most elegant terminals on Linux. But it has no settings window: you change it by editing a file, `~/.config/alacritty/alacritty.toml`, knowing which settings exist and which values they take.

**alacrittyForge is that settings window, in the terminal.** It should be:

- **Safe**: a review of every change before it's saved, one backup first, and the file written in one step, so it is never left half-written
- **Respectful**: your own notes and layout in the file stay; only the settings you change are touched
- **Clear**: every setting in plain words, with Alacritty's own name in the help line for those who want it
- **Easy**: known values are picked from lists and presets; you type only names and the odd number

---

## Features

- 🏠 **Overview**: "is my terminal set up right?" in four boxes. Anything that needs attention comes with the button that fixes it: a file that can't be read, settings with old names, misspelled settings, no font installed.
- 🔧 **Settings**: every Alacritty setting on Linux, in eight groups (Window, Text, Cursor, Scrolling & copy, Bell, Shell & start, Mouse & links, Advanced). Presets for numbers, worded switches, fonts and shells from your computer. A setting you haven't set shows what Alacritty does instead.
- 🎨 **Themes**: a preview of a terminal in each theme's colours. **Adjust Colours… (a)** makes your own copy; themes another tool maintains (hypeForge's) stay locked; install theme files safely.
- ⌨ **Shortcuts**: every shortcut in words ("Make the text bigger"). Add one by **pressing its keys**; turn off any of Alacritty's own.
- 🗂 **Backups**: why each was made, and what restoring it would change, before you do.
- 💾 **Save with a review**: **F10** shows every change, old → new. Alacritty picks the change up straight away, in every open window.
- 📖 **A manual inside the app** (**M**), and **F1** on any setting opens its page.
- ⌨ **Every button names its key**, like **Back Up Now (n)** or **Change (F2)**; **1 – 6** or **Ctrl** + the underlined letter reach every menu entry, Help included.
- 🐧 **Every major distribution**: alacrittyForge writes the setting names your Alacritty reads. Ubuntu 24.04 ships Alacritty 0.13, which uses older names than Debian, Fedora, openSUSE and Arch.
- 🖥 **Readable on a plain text console**, and nothing cut off at 100 columns.
- 🌙 **Catppuccin Mocha**, on [forgekit](https://github.com/jetomev/forge-suite/tree/main/forgekit), the Forge Suite's shared base.

---

## Screenshots

### Overview
![Overview](docs/screenshots/01-overview.svg)

### Settings
![Settings](docs/screenshots/02-settings.svg)

### Themes
![Themes](docs/screenshots/05-themes.svg)

### Shortcuts, and adding one by pressing its keys
![Shortcuts](docs/screenshots/06-shortcuts.svg)
![Add a shortcut](docs/screenshots/07-add-shortcut.svg)

### Backups
![Backups](docs/screenshots/08-backups.svg)

### Review before saving
![Review](docs/screenshots/04-review.svg)

---

## Requirements

- Linux, with **Alacritty 0.13 or newer** (alacrittyForge reads `alacritty --version` and writes the names that version reads)
- Python 3.11 or newer
- `python-textual`, `python-rich`, `python-tomlkit` and [`python-forgekit`](https://github.com/jetomev/forge-suite/tree/main/forgekit) 0.10.0 or newer
- `fontconfig` (`fc-list`), to list your fonts

---

## Installation

### Arch Linux and KognogOS, from the AUR (recommended)

```bash
nog install alacrittyforge      # KognogOS
yay -S alacrittyforge           # any AUR helper
```

### Any other distribution

```bash
git clone https://github.com/jetomev/alacrittyforge.git
git clone https://github.com/jetomev/forge-suite.git     # forgekit lives here
cd alacrittyforge
python3 -m venv .venv && .venv/bin/pip install textual rich tomlkit
PYTHONPATH=../forge-suite/forgekit .venv/bin/python main.py
```

A virtual environment is used because most current distributions refuse `pip install` into the system Python. If yours packages `textual`, `rich` and `tomlkit`, prefer those.

| Distribution | Alacritty | Tested in a VM |
|---|---|---|
| Arch, KognogOS | 0.17 | KognogOS |
| Fedora 44 | 0.17 | yes |
| openSUSE Tumbleweed | 0.17 | yes |
| Debian 13 | 0.15 | yes |
| Ubuntu 24.04 | 0.13 (older setting names) | yes |

In each, alacrittyForge's tests ran, and that distribution's own Alacritty read a file alacrittyForge had saved without a single warning.

---

## Usage

```bash
alacrittyforge              # open alacrittyForge
alacrittyforge --version    # print the version
alacrittyforge --help       # print the usage
```

No `sudo`: alacrittyForge only changes your own files.

When it closes, the terminal gets a short record: what you saved, the newest backup, where the run was logged (`~/.local/share/alacrittyforge/logs/`), and a thank-you.

### Inside hypeForge Settings

hypeForge Settings (the KognogOS desktop's settings window) opens alacrittyForge as one of its pages, by starting it with `--hypeforge`. There it has **no Quit**: none in the menu bar, and **Q** and **Ctrl+Q** do nothing. You close it from Settings, which asks alacrittyForge first, so unsaved changes still get the **Before you go** window. The option is meant for Settings, not for people, so `--help` doesn't list it.

---

## Keys

| Key | Does |
|---|---|
| Tab / Shift+Tab | next / previous field or button |
| Enter | open a list, press a button, confirm |
| Space | flip a switch |
| ↑ ↓ in a number | step through its presets |
| Esc | close a window |
| 1 – 6, or Ctrl + the underlined letter | Overview, Settings, Themes, Shortcuts, Backups, then Help (6, Ctrl+H) |
| F10, or S | save, with a review first |
| R | read the file again (your unsaved changes stay) |
| F1 | help on what is selected |
| M | the manual |
| ? | all keys |
| Q, or Ctrl+Q | quit (asks first if something isn't saved); not there inside hypeForge Settings |

In Themes: **Enter** uses a theme, **A** adjusts its colours, **I** installs one. In Shortcuts: **+** adds, **F2** changes, **Delete** removes. In Backups: **R** restores, **N** backs up now, **D** deletes. Letter keys and numbers never act while you're typing in a field; Ctrl + a menu letter does. Every button shows its key in brackets after its name, like **Back Up Now (n)**.

The full manual is in [`alacrittyforge/manual/`](alacrittyforge/manual/), and inside the app with **M**.

---

## Safety

1. **Review**: before anything is written you see every change as old → new.
2. **Backup**: the settings file is copied first: one backup per save, the newest 20 kept in `~/.config/alacritty/backups/`.
3. **A careful write**: only the settings you changed are touched; your notes and layout stay. The new file is checked, written next to the old one and swapped in, so a crash leaves the old file or the new one, never half of one. A settings file that's a link (dotfiles) stays a link.
4. **Never over a broken file**: if the file can't be read, alacrittyForge says why and offers the newest backup instead of saving over it.

Themes are only ever *added*, never written over. Files another tool maintains (hypeForge's themes) are never changed.

---

## How this project is built

A human and AI collaboration. The 1.0 redesign was drawn screen by screen and approved before any code was written: [`docs/design/v1.0.0-screens.html`](docs/design/v1.0.0-screens.html). The `testing/` folder holds the test matrices, published on purpose.

---

## Roadmap

### Next

- [ ] Edit the hints (which text on screen can be opened with Ctrl+Shift+O) ([#16](https://github.com/jetomev/alacrittyforge/issues/16))
- [ ] Mouse shortcuts, alongside the keyboard ones ([#17](https://github.com/jetomev/alacrittyforge/issues/17))

### Done

- [x] **v1.1.0** ([#19](https://github.com/jetomev/alacrittyforge/issues/19), [#20](https://github.com/jetomev/alacrittyforge/issues/20)): 1 – 6 and Ctrl + the underlined letter for every menu entry, Help included; "1-6 menu" in the bottom bar; no Quit inside hypeForge Settings; every button names its key
- [x] **v1.0.0** ([#8](https://github.com/jetomev/alacrittyforge/issues/8)): rebuilt to match grubForge 2.0; safe saving that keeps your notes; every setting; shortcuts recorded by pressing keys; backups you can restore; every major distribution
- [x] Earlier releases: [docs/ROADMAP.md](docs/ROADMAP.md)

---

## Changelog

### v1.1.0 — October 8, 2026

**Keys that work like every other Forge app, a place inside hypeForge Settings, and buttons that name their keys.** From Javier's notes of October 3 and 8.

- ⌨ **Help has a number now**, and the bottom bar says what the numbers do: **1 – 6** go through the menu in order (Overview, Settings, Themes, Shortcuts, Backups, Help), and **Ctrl** + the underlined letter does the same, **Ctrl+H** for Help. The keys come from forgekit 0.10.0, the Forge Suite's shared base, so every Forge app works the same way. The bottom bar reads **1-6 menu** instead of the confusing "1-5 screens" ([#19](https://github.com/jetomev/alacrittyforge/issues/19), F-8).
- 🧩 **Inside hypeForge Settings** ([#20](https://github.com/jetomev/alacrittyforge/issues/20)): hypeForge Settings starts alacrittyForge with `--hypeforge` (any spelling, `--hypeForge` too). There it has no Quit: none in the menu bar, and **Q** and **Ctrl+Q** do nothing. Settings closes it, and asks first if something isn't saved. `--help` doesn't list the option, because it is for Settings, not for people.
- 🔘 **Every button names its key**, in Javier's format: words in title case, the key in brackets after them. **Back Up Now (n)**, **Change (F2)**, **Restore… (r)**, **Cancel (Esc)**, **Save… (s)** in the changes bar. The manual quotes the new names.
- 🎙 **Recording a shortcut still takes every key.** Found by 1.0.0's own test when moving to forgekit 0.10.0: its new **Ctrl+T** (Themes) caught the key before the recorder in **Add a Shortcut** could. forgekit now leaves an open window its own keys (only Quit gets through), and a test here makes sure Ctrl+O, E, T, U, K and H are recorded.

Tests: 80 → **103**; warnings 0 → 0. Needs `python-forgekit` ≥ 0.10.0.

### v1.0.0 — October 2, 2026

**alacrittyForge, rebuilt, and safe.** Every screen was redesigned to match grubForge 2.0, from a plan Javier approved screen by screen before any code was written. Taking stock of 0.2.0 first found four ways it could damage your settings; all are fixed, each with a test.

- 💾 **Saving is safe now.** A save touches only the settings you changed; your notes and layout stay. A cleared setting no longer breaks the save. A file that can't be read is never saved over. One backup per save (0.2.0 made one per shortcut change, which could push out all your older backups). The file is written in one step, links are followed.
- 🔧 **Every setting**, about 60 on Linux, in plain words, with presets and lists; settings you haven't set say what Alacritty does instead.
- 🎨 **Themes** with a preview, **Adjust colours** (your own copy), hypeForge's themes locked, safe installs.
- ⌨ **Shortcuts in words**, recorded by pressing the keys; Alacritty's own can be turned off. Every part of a shortcut is kept when it's changed.
- 🗂 **Backups**: what restoring would change; restore and delete ask first. Backups are dated when they were made (0.2.0 showed your settings' last edit).
- 🐧 **Every major distribution**: writes the names your Alacritty reads (Ubuntu 24.04's 0.13 uses older ones); tested in Ubuntu, Debian, Fedora and openSUSE VMs with each one's own Alacritty.
- 📖 A manual inside the app, `--version` and `--help`, a closing note in the terminal, readable on a text console.

Found and fixed on the way, each with an issue: [#9](https://github.com/jetomev/alacrittyforge/issues/9)–[#15](https://github.com/jetomev/alacrittyforge/issues/15). Tested by Javier on KognogOS as a package upgrade from 0.2.0: *"a beautiful piece of software"*. Tests: 0 → **80**; warnings 0. New dependency: `python-tomlkit`; `python-forgekit` ≥ 0.5.1; no longer `python-tomli-w`.

*The complete history lives in [docs/CHANGELOG.md](docs/CHANGELOG.md).*

---

## Related Projects

- **[KognogOS](https://github.com/jetomev/KognogOS)**: the distribution alacrittyForge ships with
- **[forgekit](https://github.com/jetomev/forge-suite/tree/main/forgekit)**: the shared foundation for the Forge apps, in the Forge Suite
- **[nog](https://github.com/jetomev/nog)**: tier-aware package manager
- **[grubForge](https://github.com/jetomev/grubforge)**: bootloader manager
- **[bitlaForge](https://github.com/jetomev/bitlaforge)**: solo Bitcoin mining, honestly framed

---

## Authors

**jetomev**: idea, vision, direction, testing

**Claude (Anthropic)**: co-developer, architecture, implementation

Built as a collaboration between a human with a good idea and an AI that helped bring it to life.

---

## License

alacrittyForge is free software, released under the **GNU General Public License v3.0**. See [LICENSE](LICENSE) for the full text.

---

## Contributing

Contributions are welcome: open an issue or a pull request. Bug reports are genuinely valued.

If you find alacrittyForge useful, a star helps others find it.
