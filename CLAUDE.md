# alacrittyForge — how this project works (L2)

A terminal app for Alacritty's settings (`~/.config/alacritty/alacritty.toml`): view, edit, theme, fonts, key bindings, with a backup before every save. Python 3.11+, Textual, on **forgekit**. Part of the Forge Suite; ships on the AUR as `alacrittyforge`. Name: **alacrittyForge** (lowercase a). People: Javier and Claude — never the Rullynastre persona names here.

## Run and test
- Run from the tree: `PYTHONPATH=../forgekit python main.py` (the installed `python-forgekit` works too, if it is new enough).
- Tests: none committed yet (the AUR `check()` does a headless mount). The 2.0-style rework adds `tests/`, and every release reports the count, which must never drop silently.
- It writes only user files, so it needs **no sudo and has no read-only mode**. Before testing a save on this desktop, copy `alacritty.toml` aside (see `testing/RELEASE-CHECKLIST.md`). Backups go to `~/.config/alacritty/backups/` (20 kept).
- Look at it on a text console and at 100 columns: forgekit's `tools/console-preview.py --size 100x30`.

## Ship
- Release discipline: `~/.claude/rules/release.md` and `testing/RELEASE-CHECKLIST.md` (version surfaces: `__init__.py`, README badge, `alacrittyforge.1`, PKGBUILD + `.SRCINFO`).
- Packaging lives in `~/Programs/aur-alacrittyforge/` (the AUR clone): signed release asset + `.asc`, `depends` includes `python-forgekit` at the version whose pieces we use. **forgekit goes to the AUR first** when a release needs a newer one.
- Test matrices/results in `testing/`, named `YYYYMMDD - Test Matrix for alacrittyForge vX-Y-Z.md`.
- Roadmap and changelog: the README keeps upcoming work + the two newest releases; the rest is in `docs/ROADMAP.md` and `docs/CHANGELOG.md`.
- Every push → a Vault entry in `~/Google Drive/Rullynastre/AlacrittyForge/` (notes there are named "AlacrittyForge - Step N").

## Design rules (binding)
- **The look to match is grubForge 2.0** (Javier, 2026-10-02: "so far the best of the 3"): forgekit 0.5.0's pieces — settings as forms (`SettingRow`, `Toggle`, `Choices`, `CheckList`, `NumberPresets`, `FilterPicker`), the changes bar, the hint line, a review (old → new) before every save, a manual inside the app, the closing note and run log.
- Javier's message and flow rules: memory `feedback_designed_messages`.
- Known values are picked, not typed (fonts, themes, colours, shells, booleans, key names).
- Colours and marks only through forgekit's roles and `glyph()`, never raw hex in screens, so the text console works.
- A design is approved by Javier, screen by screen, **before** code is written.
