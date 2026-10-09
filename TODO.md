# alacrittyForge — the list

*The live work list and the handoff between sessions. Newest work first. Updated after every step.*

**Current release: v1.0.0** (2 Oct 2026): rebuilt to match grubForge 2.0, "so far the best of the 3" (Javier). **v1.1.0 built (8 Oct), waiting for Javier's test.** Next after it: #16 hints, #17 mouse shortcuts.

## 1.1.0 — built, waiting for Javier's test; GitHub + AUR at release
Issues [#19](https://github.com/jetomev/alacrittyforge/issues/19) (F-8: Help has no number, "1-5 screens" confusing; found by Javier inside hypeForge Settings, 8 Oct) and [#20](https://github.com/jetomev/alacrittyforge/issues/20) (`--hypeforge`, button labels). Needs forgekit 0.10.0 (released first).
- [x] Menu keys from forgekit 0.10.0: the app's own 1-5 and Ctrl+O/E/T/U/K are gone; 1-6 in bar order (Help = 6) and Ctrl + the underlined letter for every entry
- [x] Round 2 (Javier's second run, 8 Oct; forgekit `d3e8e90`): Javier's letter rule → **Ctrl+O, S, T, R, B, H** (Settings was E, Shortcuts U, Backups K); the app's `acc` removed; 6 again closes Help, Help lit while open; About and License as pages, Esc goes back. Manual, README, man page, changelog, matrix updated
- [x] Round 3 (Javier: "yes, Keys and Manual as pages too"; forgekit `d7b7ba3`): the manual opens with `show_manual` (F1 still lands on the setting's page), Keys is a page; Esc back, Backspace = previous manual page
- [x] Bottom bar "1-6 menu" (`MENU_HINT`); the Keys list says 1-6, Help, and "none inside hypeForge Settings" under Quit
- [x] `--hypeforge` (any case): no Quit, Q / Ctrl+Q do nothing; Settings closes it and unsaved changes still ask; not in `--help` or the man page; written in README, manual (All keys, Getting started), CLAUDE.md, changelog
- [x] Every button "Words In Title Case (k)" (the 3 Oct item below); manual + README quote the new names
- [x] Found on the way: forgekit 0.10.0's Ctrl+T took the key from the shortcut recorder (1.0.0's own test caught it); forgekit now leaves an open window its keys, and a test here guards it
- [x] Tests 80 → 109, warnings 0 → 0; each new test proven the other way (fix out → it fails; 29 checks)
- [x] Test matrix: `testing/20261008 - Test Matrix for alacrittyForge v1-1-0.md` (§2 is Javier's run)
- [ ] **Javier's run** (matrix §2: on its own, then inside hypeForge Settings)
- [ ] At release (the lead): forgekit 0.10.0 first; AUR `PKGBUILD`: `python-forgekit>=0.10.0` and add `tests.test_v110` to `check()`'s list; tag, GitHub release, close #19 #20, AUR after Javier's pass; Vault entry

- [x] Installed on the desktop through nog (2 Oct, 22:50): alacrittyforge 1.0.0-1, python-forgekit 0.5.1-1, python-tomlkit — the public AUR path works. Javier used it right away: 5 saves, one backup each; the 0.2.0-era backups still listed.


- [x] **Next version — button labels in Javier's format (3 Oct 2026):** "Words In Title Case (k)", e.g. "Review Updates (u)": the key in brackets after the words, for every Forge Suite app. Done in 1.1.0 (8 Oct, #20).
## Next — the grubForge 2.0 look (Javier, 2026-10-02)
Same method as grubForge 2.0, which worked:
- [x] Project kit: `CLAUDE.md` + this TODO (2 Oct); GitHub About/topics checked; Vault folder exists
- [x] Research (2 Oct): inventory of 0.2.0 (found 4 save-safety bugs: blank font value breaks the save; whole-file rewrite drops comments, unparseable file → near-empty save; one backup per shortcut change; brackets vanish in the theme preview) + every Alacritty 0.17 setting and value
- [x] Design approved (2 Oct): https://claude.ai/artifact/EaYPYBBpM93B97KgMcrSVL · `docs/design/v1.0.0-screens.html`. Javier's rulings: **1.0.0**; five screens (Fonts → Settings "Text", Backups a screen); every Linux setting in plain words; keep comments (python-tomlkit); Adjust colours (own copy); record shortcuts by pressing keys ("Even better, good one"); hypeForge themes **locked**; one "Update it" for old names
- [x] Step 1 · safe saving (`settings_file.py`, `backups.py`, `tests/test_saving.py`, 18 tests): edits as a document so comments/layout stay; REMOVE instead of None; never saves over an unreadable file; one backup per save (old names + notes still read); write next to the file then swap in; links followed; old names → new. Found on the way: tomlkit 0.15 writes Esc as `\e` (TOML 1.1), which TOML 1.0 readers reject — strings are written with `\u001b`, and every save is re-read before writing
- [x] Step 2 · the frame, Overview, Settings (`f5c062c`, `27330dd`): ~60 settings in 8 groups, 38 tests; found + fixed: shell-as-table false change at start, 4 rows over 100 columns, forgekit number field too narrow / no decimals (forgekit 0.5.1-dev: `66874fe`, `c8967b2` — release 0.5.1 before 1.0.0). Screens shown on the design page (version 3)
- [x] The manual, started now (Javier, 2 Oct: "don't forget about the manual too"): 13 pages in `alacrittyforge/manual/` — Getting started, the 8 Settings groups (F1 opens the group's page), Backups and undo, Changes made elsewhere, On a text console, All keys. `tests/test_manual.py` keeps it in step (every setting named on its page, links, F1). **Each new screen adds its page as it is built.**
- [x] Step 3 · Themes + Adjust colours (`cd6e108`): in use first, hypeForge files locked, new themes staged until save, install colour-only files; Adjust colours scrolls on a 25-line console; console note; manual page. 55 tests
- [x] **Every major distribution, the same** (Javier, 2 Oct): Ubuntu 24.04 (Alacritty 0.13.2), Debian 13 (0.15.1), Fedora 44, openSUSE Tumbleweed (0.17.0) all PASS with `scripts/vm-distro-check.py` — tests there, a real save read clean by each distro's own Alacritty under Xvfb, wrong names caught (`7b992c6`, `5c7cbbf`). Fixed on the way: F-1 version-aware setting names (0.14 moved five; Ubuntu would have ignored a chosen theme), F-2 no monospace font → the Overview says so. Matrix §9 in `testing/`. Rerun the script before the release
- [x] Step 4 · Shortcuts + key recording (`7052fb9`): in words (Esc, Enter named; modes in words), Alacritty's 96 Linux defaults from its manual, turn one off/on, record by pressing the keys (lists as fallback), every field kept; found: Textual 8 Select.BLANK is False (crash on opening), list too wide at 100, undo left a change. Manual page. 77 tests
- [x] Step 5 · Backups screen, --version/--help, closing note + runs log, 0.2.0 code removed (`f64f0c3`); all 5 screens pass the console check; found: backups dated by the settings' last edit (now from their names), long reasons scrolled the list. 80 tests. In-app name is alacrittyForge (README/man page in step 6)
- [x] Step 6 · released 2 Oct: Javier's run PASS ("a beautiful piece of software"); forgekit 0.5.1 + AUR first; alacrittyForge 1.0.0 tag, GitHub release, AUR; issues #8 (redesign), #9–#15 (F-1…F-7) opened + closed, #7 closed; backlog #16 hints, #17 mouse shortcuts; memory + Vault
- [ ] Build on the 0.5.0 pieces; tests per screen (incl. the 100-column checks); Javier's own run; release (GitHub + AUR)
