# alacrittyForge — the list

*The live work list and the handoff between sessions. Newest work first. Updated after every step.*

**Current release: v0.2.0.** **Next: a redesign to match grubForge 2.0**, "so far the best of the 3" (Javier, 2 Oct 2026).

## Next — the grubForge 2.0 look (Javier, 2026-10-02)
Same method as grubForge 2.0, which worked:
- [x] Project kit: `CLAUDE.md` + this TODO (2 Oct); GitHub About/topics checked; Vault folder exists
- [x] Research (2 Oct): inventory of 0.2.0 (found 4 save-safety bugs: blank font value breaks the save; whole-file rewrite drops comments, unparseable file → near-empty save; one backup per shortcut change; brackets vanish in the theme preview) + every Alacritty 0.17 setting and value
- [x] Design approved (2 Oct): https://claude.ai/artifact/EaYPYBBpM93B97KgMcrSVL · `docs/design/v1.0.0-screens.html`. Javier's rulings: **1.0.0**; five screens (Fonts → Settings "Text", Backups a screen); every Linux setting in plain words; keep comments (python-tomlkit); Adjust colours (own copy); record shortcuts by pressing keys ("Even better, good one"); hypeForge themes **locked**; one "Update it" for old names
- [x] Step 1 · safe saving (`settings_file.py`, `backups.py`, `tests/test_saving.py`, 18 tests): edits as a document so comments/layout stay; REMOVE instead of None; never saves over an unreadable file; one backup per save (old names + notes still read); write next to the file then swap in; links followed; old names → new. Found on the way: tomlkit 0.15 writes Esc as `\e` (TOML 1.1), which TOML 1.0 readers reject — strings are written with `\u001b`, and every save is re-read before writing
- [ ] Step 2 · the frame, Overview, Settings (every setting, `settings_spec.py`)
- [ ] Step 3 · Themes + Adjust colours (hypeForge files locked)
- [ ] Step 4 · Shortcuts + key recording
- [ ] Step 5 · Backups screen, manual, --version/--help, closing note, console, 100 columns; the name "alacrittyForge" everywhere
- [ ] Step 6 · test matrix, Javier's run (KognogOS VM, package upgrade from 0.2.0), release 1.0.0 (PKGBUILD: + python-tomlkit, forgekit>=0.5.0; − python-tomli-w)
- [ ] Build on the 0.5.0 pieces; tests per screen (incl. the 100-column checks); Javier's own run; release (GitHub + AUR)
