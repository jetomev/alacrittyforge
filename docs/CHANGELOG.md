# alacrittyForge — full changelog

*The README carries the two most recent entries; the complete history lives here, newest-first.*

### v1.1.0 — October 8, 2026

**Keys that work like every other Forge app, a place inside hypeForge Settings, and buttons that name their keys.** From Javier's notes of October 3 and 8.

- ⌨ **Help has a number now**, and the bottom bar says what the numbers do: **1 – 6** go through the menu in order (Overview, Settings, Themes, Shortcuts, Backups, Help), and **Ctrl** + the underlined letter does the same, **Ctrl+H** for Help. The keys come from forgekit 0.10.0, the Forge Suite's shared base, so every Forge app works the same way; alacrittyForge's own number and Ctrl keys are gone. The bottom bar reads **1-6 menu** instead of the confusing "1-5 screens" (#19, F-8, found by Javier running alacrittyForge inside hypeForge Settings).
- 🧩 **Inside hypeForge Settings** (#20): hypeForge Settings starts alacrittyForge with `--hypeforge` (any spelling, `--hypeForge` too). There it has no Quit: none in the menu bar, and **Q** and **Ctrl+Q** do nothing. Settings closes it, and asks first if something isn't saved (the same **Before you go** window). `--help` and the man page don't list the option, because it is for Settings, not for people; the README, the manual and CLAUDE.md describe it.
- 🔘 **Every button names its key**, in Javier's format from October 3: words in title case, the key in brackets after them. **Back Up Now (n)**, **Change (F2)**, **Remove (Del)**, **Restore (r)**, **Delete (d)**, **Adjust Colours (a)**, **Install a Theme (i)**, **Add a Shortcut (+)**, **Cancel (Esc)**, **Stay (Esc)**, **Save Changes (s)** in the changes bar; the restore and delete windows say **Restore (y)** and **Delete (y)**. Buttons with no key of their own are in title case only (**Use This Theme**, **Show Whole File**). The manual quotes the new names.
- 🎙 **Recording a shortcut still takes every key.** Found by 1.0.0's own test when moving to forgekit 0.10.0: its new **Ctrl+T** (Themes) caught the key before the recorder in **Add a Shortcut** could. forgekit now leaves an open window its own keys (only Quit gets through), and a test here makes sure Ctrl+O, E, T, U, K and H are recorded and nothing moves behind the window.

Tests: 80 → 103 (23 new, each one also checked the other way: with its fix taken out, it fails); warnings 0 → 0. Needs `python-forgekit` ≥ 0.10.0 (was 0.5.1). The README's "any other distribution" steps now fetch forgekit from the Forge Suite repository, where it lives since October 6.

### v1.0.0 — October 2, 2026

**alacrittyForge, rebuilt, and safe.** Every screen was redesigned to match grubForge 2.0, from a plan Javier approved screen by screen before any code was written. Taking stock of 0.2.0 first found four ways it could damage your settings; all are fixed, each with a test.

- 💾 **Saving is safe now.** A save touches only the settings you changed; your notes and layout stay. A cleared setting no longer breaks the save. A file that can't be read is never saved over. One backup per save (0.2.0 made one per shortcut change, which could push out all your older backups). The file is written in one step, links are followed.
- 🔧 **Every setting**, about 60 on Linux, in plain words, with presets and lists; settings you haven't set say what Alacritty does instead.
- 🎨 **Themes** with a preview, **Adjust colours** (your own copy), hypeForge's themes locked, safe installs.
- ⌨ **Shortcuts in words**, recorded by pressing the keys; Alacritty's own can be turned off. Every part of a shortcut is kept when it's changed.
- 🗂 **Backups**: what restoring would change; restore and delete ask first. Backups are dated when they were made (0.2.0 showed your settings' last edit).
- 🐧 **Every major distribution**: writes the names your Alacritty reads (Ubuntu 24.04's 0.13 uses older ones); tested in Ubuntu, Debian, Fedora and openSUSE VMs with each one's own Alacritty.
- 📖 A manual inside the app, `--version` and `--help`, a closing note in the terminal, readable on a text console.

Found and fixed on the way, each with an issue: #9 (Ubuntu's older setting names), #10 (no font), #11 (0.2.0's saving), #12 (backup dates), #13 (Textual 8 crash), #14 (100 columns / 25 lines), #15 (text read as formatting). Tested by Javier on KognogOS as a package upgrade from 0.2.0 (9 saves, one backup each, an exact restore): *"a beautiful piece of software"*. Tests: 0 → 80; warnings 0. New dependency: `python-tomlkit`; `python-forgekit` ≥ 0.5.1; no longer `python-tomli-w`.

### v0.2.0 — August 10, 2026

**The forgekit redesign.** alacrittyForge became the second Forge app built on the shared foundation — and the release where the in-place editing style was invented.

The idea: one table per section, with values edited where they live. Settings with fixed options open a dropdown right at the cell, long lists open a filterable picker, free text opens a small editor. Staged changes are marked ⏳ in the table, and a fixed footer at the bottom holds the only button that writes anything.

Three rounds of hands-on review shaped it, and the shared foundation grew form styling and simpler window-closing along the way — improvements every other Forge app inherited.

One bug fixed here is worth calling out, because it's invisible until it bites you: colours written directly in `alacritty.toml` silently override any theme you import. You apply a theme, nothing appears to happen, and there's no error. Applying a theme now clears those inline colours first.

New dependency: [forgekit 0.3.0](https://github.com/jetomev/forgekit) or newer, packaged on the AUR as `python-forgekit`. `yay -S alacrittyforge` pulls it in for you.

### v0.1.1 — May 28, 2026

**A hardening batch**, closing six findings from an audit that borrowed grubForge's playbook.

- 🔒 **Staged edits stopped disappearing.** Switching away from a screen and back silently discarded everything you'd staged — the code that re-read from disk also reset the staging area. Reading and resetting are now separate things.
- 💬 **One feedback channel.** Every screen now reports through the same status line and toast, instead of five near-identical versions with their own inconsistent icons.
- ❓ **The help window stopped stacking.** Pressing `?` twice used to open two of them. It now toggles, and `Esc`, `q` or `?` all close it.
- 🎯 **Keys work on arrival.** Screen shortcuts used to be dead until you clicked into a panel first. Each screen now takes focus when you open it.
- ⌨ **Confirmation dialogs got keyboard-friendly** — `Esc` cancels, `Enter` confirms, no tabbing onto a button.

**Packaging:** published on the AUR. The build now launches the app headlessly as a check, so a styling or startup error is caught while building rather than when you first run it.

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
