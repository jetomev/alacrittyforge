# alacrittyForge — the list

*The live work list and the handoff between sessions. Newest work first. Updated after every step.*

**Current release: v0.2.0.** **Next: a redesign to match grubForge 2.0**, "so far the best of the 3" (Javier, 2 Oct 2026).

## Next — the grubForge 2.0 look (Javier, 2026-10-02)
Same method as grubForge 2.0, which worked:
- [x] Project kit: `CLAUDE.md` + this TODO (2 Oct); GitHub About/topics checked; Vault folder exists
- [x] Research (2 Oct): inventory of 0.2.0 (found 4 save-safety bugs: blank font value breaks the save; whole-file rewrite drops comments, unparseable file → near-empty save; one backup per shortcut change; brackets vanish in the theme preview) + every Alacritty 0.17 setting and value
- [x] Design approved (2 Oct): https://claude.ai/artifact/EaYPYBBpM93B97KgMcrSVL · `docs/design/v1.0.0-screens.html`. Javier's rulings: **1.0.0**; five screens (Fonts → Settings "Text", Backups a screen); every Linux setting in plain words; keep comments (python-tomlkit); Adjust colours (own copy); record shortcuts by pressing keys ("Even better, good one"); hypeForge themes **locked**; one "Update it" for old names
- [x] Step 1 · safe saving (`settings_file.py`, `backups.py`, `tests/test_saving.py`, 18 tests): edits as a document so comments/layout stay; REMOVE instead of None; never saves over an unreadable file; one backup per save (old names + notes still read); write next to the file then swap in; links followed; old names → new. Found on the way: tomlkit 0.15 writes Esc as `\e` (TOML 1.1), which TOML 1.0 readers reject — strings are written with `\u001b`, and every save is re-read before writing
- [x] Step 2 · the frame, Overview, Settings (`f5c062c`, `27330dd`): ~60 settings in 8 groups, 38 tests; found + fixed: shell-as-table false change at start, 4 rows over 100 columns, forgekit number field too narrow / no decimals (forgekit 0.5.1-dev: `66874fe`, `c8967b2` — release 0.5.1 before 1.0.0). Screens shown on the design page (version 3)
- [x] The manual, started now (Javier, 2 Oct: "don't forget about the manual too"): 13 pages in `alacrittyforge/manual/` — Getting started, the 8 Settings groups (F1 opens the group's page), Backups and undo, Changes made elsewhere, On a text console, All keys. `tests/test_manual.py` keeps it in step (every setting named on its page, links, F1). **Each new screen adds its page as it is built.**
- [x] Step 3 · Themes + Adjust colours (`cd6e108`): in use first, hypeForge files locked, new themes staged until save, install colour-only files; Adjust colours scrolls on a 25-line console; console note; manual page. 55 tests
- [ ] **Every major distribution, the same** (Javier, 2 Oct: "check alacritty functionality in all major linux distros, all the same"): Debian 13, Ubuntu 24.04, Fedora 44, openSUSE Tumbleweed in the grubForge test VMs (`gf-*`, snapshot `fresh`). First: which Alacritty each ships — 0.14 renamed settings (`general.*`, `terminal.shell`), so an older Alacritty needs the old names. Then each distro's own Alacritty must accept what alacrittyForge writes (run headless under Xvfb, no config errors or warnings)
- [ ] Step 4 · Shortcuts + key recording — and its manual page
- [ ] Step 5 · Backups screen, manual, --version/--help, closing note, console, 100 columns; the name "alacrittyForge" everywhere
- [ ] Step 6 · test matrix, Javier's run (KognogOS VM, package upgrade from 0.2.0), release 1.0.0 (PKGBUILD: + python-tomlkit, forgekit>=0.5.0; − python-tomli-w)
- [ ] Build on the 0.5.0 pieces; tests per screen (incl. the 100-column checks); Javier's own run; release (GitHub + AUR)
