# alacrittyForge v1.0.0 — Test Matrix

Design: `docs/design/v1.0.0-screens.html` (Javier's rulings, 2 Oct 2026). Filled section by section as the steps are built. Each result was read from the run itself, not assumed.

## 1–8 · Built and checked by Claude (2 Oct 2026)

Automated: **80 tests**, all passing (also inside the AUR build, and in the four distribution VMs). Each fix was checked against the old code, where its test fails.

| ID | Area | Proven by | Result |
|---|---|---|---|
| 1 | Safe saving: one line per change, notes and layout kept, cleared setting removed, never over an unreadable file, one backup per save, 20 kept, written in one step, links followed, permissions kept, changes made elsewhere kept, old names moved | `tests/test_saving.py`; a copy of Javier's real file: one change = one changed line | **PASS** |
| 2 | Overview: your terminal, needs attention (unreadable file → restore, old names → update, unknown settings, no font, live reload off), safety, tasks | `test_screens.py`; real-file render | **PASS** |
| 3 | Settings: ~60 settings, 8 groups, nothing changed at start or after visiting every group, Alacritty's own value leaves a setting unset, a change marked and reviewed, every row fits at 100 columns | `test_session.py`, `test_screens.py` | **PASS** |
| 4 | Themes: in use first, preview, hypeForge's locked (never written), use = imports + own colours out, Adjust colours → own copy only on save, installs colour-only files, Adjust colours fits a 25-line console | `test_themes.py`, `test_screens.py` | **PASS** |
| 5 | Shortcuts: in words (Esc, Enter named), 96 Linux defaults from Alacritty's manual, turn off/on leaves no change, record Ctrl+T (also a screen key), every field kept, window fits 25 lines | `test_bindings.py`, `test_screens.py` | **PASS** |
| 6 | Backups: dated when made, plain reasons, what a restore would change, restore/delete start on Cancel, long reasons fit | `test_saving.py`, `test_screens.py`; real backups render | **PASS** |
| 7 | Manual: a page per group and screen, every setting named on its page, links, F1 lands right | `test_manual.py` | **PASS** |
| 8 | Text console (100×30) every screen: console font only, nothing invisible; nothing cut off at 100 columns | forgekit `console-preview.py`; `*_100_columns` tests | **PASS** |

## 9 · Every major distribution, the same (Javier, 2 Oct: "check alacritty functionality in all major linux distros, all the same")

Run in the grubForge test VMs (cloud images, UEFI, snapshot `fresh`), as root, with `scripts/vm-distro-check.py`:
1. alacrittyForge's own tests, with the distribution's Python and its tomlkit version;
2. alacrittyForge saves real changes (theme, font size, opacity, cursor, shell, scroll-back), then **that distribution's own Alacritty** starts on the file in Xvfb, and every config warning or error is collected; clean means none;
3. the failing direction: the same Alacritty on a file using the names this version does **not** read must warn, or step 2's "clean" proves nothing.

| ID | Distribution | Alacritty | Python · tomlkit | Tests | Alacritty on alacrittyForge's file | Wrong names caught | Result |
|---|---|---|---|---|---|---|---|
| 9.1 | Ubuntu 24.04 | **0.13.2** | 3.12 · 0.12.4 | 64 pass | clean (writes `import`, `shell` at the top, as 0.13 reads them) | yes: "Unused config key: general" | **PASS** |
| 9.2 | Debian 13 | 0.15.1 | 3.13 · 0.13.2 | 64 pass | clean | yes: "live_config_reload has been deprecated" | **PASS** |
| 9.3 | Fedora 44 | 0.17.0 | 3.14 · 0.13.2 | 64 pass | clean | yes | **PASS** |
| 9.4 | openSUSE Tumbleweed | 0.17.0 | 3.13 · 0.15.1 | 64 pass | clean (after installing a font, F-2) | yes | **PASS** |
| 9.5 | Arch / KognogOS (this desktop) | 0.17.0 | 3.14 · 0.15.1 | 65 pass | — (Javier's run, §10) | — | — |

**Findings from this section** (fixed, with tests):
- **F-1:** distributions ship different Alacritty versions, and 0.14 moved five settings (`import`, `working_directory`, `live_config_reload`, `ipc_socket` → `[general]`; `shell` → `[terminal]`). Writing the new names on Ubuntu 24.04 would make its Alacritty ignore them; a chosen theme would silently not apply. alacrittyForge now reads `alacritty --version`, writes the names the installed version reads, hides settings it lacks (`window.level` before 0.15, compared from each version's own manual page), and the Overview's name check works in whichever direction that version needs. A test caught the first version flagging Ubuntu's correct names as old.
- **F-2:** a minimal openSUSE install has no font at all; Alacritty then refuses to start ("font monospace not found"). The Overview now says so, with the package to install; it says nothing when fonts can't be listed at all, so it never warns falsely.

**All findings of the 1.0 cycle, as issues** (each opened with the explanation and closed with the fix): F-1 #9 Ubuntu's older names · F-2 #10 no font · F-3 #11 0.2.0's saving could damage settings · F-4 #12 backups dated by the settings' last edit · F-5 #13 Textual 8 crash in the shortcut window · F-6 #14 cut off / sideways at 100 columns, 25 lines · F-7 #15 text read as formatting, raw control characters.

**Test-environment notes** (the VMs, not alacrittyForge): the cloud images lack the X11 runtime libraries winit loads (libxkbcommon-x11, libXcursor, libXi, libXrandr), so Alacritty first failed with "NotSupported" before even reading its config; Xvfb needs 24-bit colour. A first version of the check counted that failed start as "warned (good)"; it now counts a warning only when Alacritty really ran.

## 10 · Javier's run (KognogOS VM, at the keyboard)

Setup by Claude (2 Oct, done): `kognog-hypeforge` from `clean-install-3` (alacrittyForge 0.2.0, forgekit 0.3.0, Alacritty 0.17), brought up to date (`pacman -Syu fakeroot`, the step nog 1.5.5 itself names), then **with nog**: `nog install python-tomlkit`, and `nog install ./python-forgekit-0.5.1rc1… ./alacrittyforge-1.0.0rc1…` (upgrades). Built by `scripts/make-rc-packages.sh` from `ac29f4d` / forgekit `c8967b2`; the build ran all 80 tests. A headless check as the user: nothing pending at start, Alacritty 0.17 found. Saved as snapshot **`alacrittyforge-1.0.0rc1`**.

| ID | Task | EXPECT | Result | Notes |
|---|---|---|---|---|
| 10.1 | `alacrittyforge --version`, then `alacrittyforge` | the version; the Overview | — | |
| 10.2 | Overview | Alacritty 0.17, the theme, the font; "Nothing needs attention" | — | |
| 10.3 | Settings ▸ Window: Opacity preset 90, F10, Save | the review (95/100 → 90); an open Alacritty window turns see-through at once | — | the real proof |
| 10.4 | Settings ▸ Text: Size preset 14, F10, Save | open Alacritty windows' text grows | — | |
| 10.5 | Settings ▸ Text: Font → Choose a font…, type part of a name, pick one, Save | the font changes in Alacritty | — | |
| 10.6 | Themes: pick a hypeForge theme, Enter, F10, Save | Alacritty's colours change; the hypeForge file is untouched | — | |
| 10.7 | Themes: A (Adjust colours), change Red, Keep, F10, Save | a "(mine)" copy appears and is in use | — | |
| 10.8 | Shortcuts: + , press Ctrl+Shift+T, An action "Open a new window", Add it, F10, Save; then press Ctrl+Shift+T in Alacritty | a new Alacritty window opens | — | |
| 10.9 | Shortcuts: pick one of Alacritty's, Turn this one off, Save | that key types as normal in Alacritty | — | |
| 10.10 | Backups: pick the oldest, look at "Restoring this would change", R, Restore | Alacritty goes back to how it was | — | |
| 10.11 | Change something, then Q | "Before you go" asks; quitting prints the closing note | — | |
| 10.12 | M, and F1 on a setting | the manual, on the right page | — | |
| 10.13 | Ctrl+Alt+F3, log in, `alacrittyforge` | readable and usable on the text console | — | |
| 10.14 | Anything that looks wrong, reads badly, or is slow | noted here as F-n | — | |

**Javier's verdict (2 Oct, ~22:30): "fantastic job my friend. alacrittyForge its a beautiful piece of software. I am incredibly happy with the results!!!"**

Read back from the VM afterwards (alacrittyForge's run log, the backups and their notes, the files' times, the login journal):
- 2 runs, 22:21–22:25. **9 saves**, each with exactly **one** backup ("Before a save"); the closing record says "Alacritty is already using them".
- Then a **restore**: a "pre-restore" backup first, and the settings file is now **byte for byte** the backup made before the first save. The notes in the file (`# solid: transparency made the light themes look bad (Javier, 2026-09-30)`, the hypeForge comments) came through every save unchanged.
- Five hypeForge theme files show 22:21:39: **hypeForge rewrote them at login** (login 22:21:36; `~/.config/hypeforge` changed the same second; `hypeforge-current`, which hypeForge doesn't regenerate at login, is unchanged since 30 Sep). alacrittyForge never writes existing theme files (`test_themes.py`).

Rows 10.1–10.6, 10.8–10.12, 10.14: **PASS** on Javier's word and the log. **10.7 (Adjust colours) is not in the log**: no "(mine)" copy exists, and a restore doesn't remove theme files. **10.13 (text console)** can't be read from the log. No findings reported.
