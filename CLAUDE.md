# alacrittyForge — how this project works (L2)

A terminal app for Alacritty's settings (`~/.config/alacritty/alacritty.toml`): view, edit, theme, fonts, key bindings, with a backup before every save. Python 3.11+, Textual, on **forgekit**. Part of the Forge Suite; ships on the AUR as `alacrittyforge`. Name: **alacrittyForge** (lowercase a). People: Javier and Claude — never the Rullynastre persona names here.

## Run and test
- Run from the tree: `PYTHONPATH=../forgekit python main.py` (`../forgekit` is a link to `../forge-suite/forgekit`; the installed `python-forgekit` works too, if it is 0.10.0 or newer).
- Tests: `PYTHONPATH=../forgekit python -W always -m unittest discover -s tests` (109 at 1.1.0). Every release reports the count, which must never drop silently, and the warnings. A new test file must also be added to the AUR `check()` and to `testing/RELEASE-CHECKLIST.md`, which name the files one by one.
- **`--hypeforge`** (1.1.0, #20): hypeForge Settings starts the app with it (any case, `--hypeForge` too). Then there is no Quit: none in the menu bar, Q and Ctrl+Q do nothing; Settings closes the app through forgekit's `host_quit()`, which runs `before_quit()`, so unsaved changes still ask first. It is for Settings, not for people: kept out of `--help` and the man page (a test checks both), written down in the README, the manual's All keys page, this file and the changelog. `cli.py` spells the flag itself so `--version` stays instant; a test checks it matches forgekit's `HYPEFORGE_FLAG`.
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
- **Menu keys are forgekit's** (0.10.0): a number 1-6 in bar order (Help is 6 and 6 again closes it; Quit has none) and Ctrl + each entry's underlined letter. **The letters follow Javier's rule** (forgekit's `assign_accels`): the first letter of the title unless taken, else the next letter of the title; Help H, Quit Q; the app's own Ctrl keys count as taken. So O S T R B. MENU carries **no `"acc"`** (ignored since 0.10.0; a test keeps it out). Renaming an entry or adding a Ctrl key of our own can move a letter: update the manual, README, man page and `CTRL` in `tests/test_v110.py`. No app or screen binding may take a menu number.
- **Help's pages are forgekit pages** in the content area, not windows: About and License (`show_page`), Keys (`act('shortcuts')`), the manual (`show_manual(title, pages, start=page)`, which F1 uses for a setting's page); Help lit, Esc back. `MENU_HINT` in the hints shows as "1-6 menu".
- **Button labels** (Javier, 2026-10-03): "Words In Title Case (k)", the key in round brackets after the words: the letter key when the button has one (lowercase, like `(n)`), else its other key (`(F2)`, `(Esc)`, `(Del)`, `(+)`); no key, title case only. Small words stay lowercase ("Restore the Newest Backup"), as in nogForge. The manual quotes labels exactly; `tests/test_v110.py` lists every one.
- A design is approved by Javier, screen by screen, **before** code is written.
