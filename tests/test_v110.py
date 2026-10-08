"""alacrittyForge 1.1.0: the menu keys from forgekit 0.10.0 (#19), --hypeforge (#20) and
the button labels in Javier's format, "Words In Title Case (k)" (asked 2026-10-03).

Headless; needs Textual and forgekit 0.10.0 or newer.
"""

from __future__ import annotations

import contextlib
import io
import re
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from forgekit import HintBar, menu_key_clashes  # noqa: E402
from forgekit.menu import MenuDropdown, accel  # noqa: E402

from alacrittyforge import cli  # noqa: E402
from alacrittyforge.app import AlacrittyForgeApp  # noqa: E402
import test_screens  # noqa: E402

SECTIONS = ["overview", "settings", "themes", "shortcuts", "backups"]
CTRL = {"overview": "ctrl+o", "settings": "ctrl+e", "themes": "ctrl+t", "shortcuts": "ctrl+u",
        "backups": "ctrl+k"}


def active(app) -> list[str]:
    return [w.id.removeprefix("menu-") for w in app.query(".menu-title.active")]


class MenuLetters(unittest.TestCase):
    def test_every_underlined_letter_is_different(self):
        self.assertEqual(menu_key_clashes(AlacrittyForgeApp.MENU), [])

    def test_the_letters_are_the_ones_the_manual_names(self):
        self.assertEqual({m["id"]: accel(m) for m in AlacrittyForgeApp.MENU},
                         {**{k: v[-1] for k, v in CTRL.items()}, "help": "h", "quit": "q"})

    def test_no_key_of_ours_takes_a_menu_key(self):
        """The numbers and Ctrl+<letter> are forgekit's now: none of alacrittyForge's own
        bindings, on the app or on any screen or window, may use one."""
        from alacrittyforge import app as app_mod
        from alacrittyforge.ui import backups, overview, settings, shortcuts, themes
        menu_keys = {f"ctrl+{accel(m)}" for m in AlacrittyForgeApp.MENU} | {str(n) for n in range(1, 10)}
        found = []
        for mod in (app_mod, backups, overview, settings, shortcuts, themes):
            for name in dir(mod):
                cls = getattr(mod, name)
                if not isinstance(cls, type) or cls.__module__ != mod.__name__:
                    continue
                for b in cls.__dict__.get("BINDINGS", []):
                    keys = b.key if hasattr(b, "key") else b[0]
                    for k in keys.split(","):
                        if k.strip() in menu_keys:
                            found.append((name, k.strip()))
        self.assertEqual(found, [], "a key of ours on top of a menu key")


class MenuKeys(test_screens.Screens):
    """Every menu entry has a number (1-6, Help included) and Ctrl + its underlined letter."""

    async def test_a_number_reaches_every_entry_help_is_6(self):
        app = self.app()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause(0.4)
            for n, sid in enumerate(SECTIONS, 1):
                app.set_focus(None)                    # a list or field would keep a digit
                await pilot.press(str(n))
                await pilot.pause(0.3)
                self.assertEqual(active(app), [sid], f"{n} goes to {sid}")
            app.set_focus(None)
            await pilot.press("6")
            await pilot.pause(0.3)
            self.assertIsInstance(app.screen, MenuDropdown, "6 opens Help")
            self.assertEqual(app.screen.menu_id, "help")
            await pilot.press("escape")
            await pilot.pause(0.2)
            app.set_focus(None)
            await pilot.press("7")
            await pilot.pause(0.2)
            self.assertEqual(len(app.screen_stack), 1, "Quit has no number")

    async def test_ctrl_and_the_underlined_letter_reach_every_entry(self):
        app = self.app()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause(0.4)
            for sid in reversed(SECTIONS):             # Overview last: it is where we start
                await pilot.press(CTRL[sid])
                await pilot.pause(0.3)
                self.assertEqual(active(app), [sid], f"{CTRL[sid]} goes to {sid}")
            await pilot.press("ctrl+h")
            await pilot.pause(0.3)
            self.assertIsInstance(app.screen, MenuDropdown)
            self.assertEqual(app.screen.menu_id, "help")

    async def test_ctrl_letter_works_from_inside_a_field(self):
        from textual.widgets import Input
        app = self.app()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.press("2")
            await pilot.pause(0.4)
            field = next(i for i in app.query_one("#sec-settings").query(Input) if i.display)
            field.focus()
            await pilot.press("ctrl+k")
            await pilot.pause(0.3)
            self.assertEqual(active(app), ["backups"])

    async def test_the_bottom_bar_says_1_6_menu(self):
        from forgekit import MENU_HINT
        self.assertIn(MENU_HINT, AlacrittyForgeApp.HINTS, "the app's own hints")
        self.assertNotIn(("1-5", "screens"), AlacrittyForgeApp.HINTS)
        app = self.app()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause(0.4)                     # the Overview's hints
            text = str(app.query_one(HintBar).render())
            self.assertIn("1-6 menu", text)
            self.assertNotIn("1-5", text)
            self.assertNotIn("{menu}", text)

    async def test_the_keys_list_names_1_6_and_help(self):
        text = " ".join(f"{k} {d}" for k, d in AlacrittyForgeApp.SHORTCUTS)
        self.assertIn("1-6", text)
        self.assertIn("Help", text)
        self.assertNotIn("1-5", text)
        self.assertIn("hypeForge Settings", text)

    async def test_recording_keeps_every_menu_key(self):
        """forgekit 0.10.0 takes Ctrl+<letter> before anything else, but an open window keeps its
        keys (Quit aside): inside the recorder they are recorded, and nothing moves behind it."""
        from alacrittyforge.ui.shortcuts import ShortcutDialog
        app = self.app()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.press("4")
            await pilot.pause(0.4)
            await pilot.press("plus")
            await pilot.pause(0.4)
            self.assertIsInstance(app.screen, ShortcutDialog)
            for key in list(CTRL.values()) + ["ctrl+h"]:
                await pilot.press(key)
                await pilot.pause(0.2)
                self.assertIsInstance(app.screen, ShortcutDialog, f"{key} left the window")
                self.assertEqual(app.screen.keys, {"key": key[-1].upper(), "mods": "Control"}, key)
            self.assertEqual(active(app), ["shortcuts"], "nothing moved behind the window")

    async def test_an_open_window_keeps_its_fields_ctrl_keys(self):
        """Ctrl+E inside a window's text field is the field's (end of line); no screen switch
        happens behind the window."""
        from textual.widgets import Input
        from alacrittyforge.ui.shortcuts import ShortcutDialog
        app = self.app()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.press("4")
            await pilot.pause(0.4)
            await pilot.press("plus")
            await pilot.pause(0.4)
            self.assertIsInstance(app.screen, ShortcutDialog)
            app.screen.query_one("#sd-kind").set_value("command")      # Run a program
            await pilot.pause(0.2)
            field = app.screen.query_one("#sd-command", Input)
            self.assertTrue(field.display)
            field.focus()
            await pilot.press(*"firefox")
            await pilot.press("home", "ctrl+e")
            await pilot.pause(0.3)
            self.assertIsInstance(app.screen, ShortcutDialog)
            self.assertEqual(active(app), ["shortcuts"], "Ctrl+E switched the screen behind the window")
            self.assertEqual(field.cursor_position, len("firefox"), "Ctrl+E is the field's: end of line")


class InsideHypeForgeSettings(test_screens.Screens):
    """Started with --hypeforge: no Quit in the bar, and Q and Ctrl+Q do nothing."""

    def app(self, text=None, **kw):
        from alacrittyforge.session import Session
        if text is not None:
            self.cfg.write_text(text)
        return AlacrittyForgeApp(session=Session.load(self.cfg, backup_dir=self.dir / "bk", themes_dir=self.tdir,
                                                      version=(0, 17, 0)), **kw)

    async def _quit_keys(self, hypeforge: bool) -> tuple[list, int]:
        app = self.app(hypeforge=hypeforge)
        calls: list = []
        async with app.run_test(size=(120, 40)) as pilot:
            app.exit = lambda *a, **k: calls.append(1)
            await pilot.pause(0.4)
            quit_titles = len(app.query("#menu-quit"))
            for key in ("q", "ctrl+q"):
                app.set_focus(None)
                await pilot.press(key)
                await pilot.pause(0.3)
        return calls, quit_titles

    async def test_no_quit_and_q_does_nothing(self):
        calls, quit_titles = await self._quit_keys(hypeforge=True)
        self.assertEqual(quit_titles, 0, "no Quit in the bar")
        self.assertEqual(calls, [], "Q and Ctrl+Q do nothing inside Settings")

    async def test_outside_settings_q_and_ctrl_q_quit(self):
        calls, quit_titles = await self._quit_keys(hypeforge=False)
        self.assertEqual(quit_titles, 1)
        self.assertEqual(calls, [1, 1])

    async def test_help_is_still_6_inside_settings(self):
        app = self.app(hypeforge=True)
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause(0.4)
            app.set_focus(None)
            await pilot.press("6")
            await pilot.pause(0.3)
            self.assertEqual(getattr(app.screen, "menu_id", None), "help")
            self.assertIn("1-6", str(app.query_one(HintBar).render()))

    async def test_settings_closing_it_still_asks_about_unsaved_changes(self):
        from alacrittyforge.app import QuitDialog
        app = self.app(hypeforge=True)
        calls: list = []
        async with app.run_test(size=(120, 40)) as pilot:
            app.exit = lambda *a, **k: calls.append(1)
            await pilot.pause(0.4)
            app.session.set("font.size", 14.0)
            app.host_quit()
            await pilot.pause(0.3)
            self.assertIsInstance(app.screen, QuitDialog)
            self.assertEqual(calls, [])
            app.screen.query_one("#quit").press()
            await pilot.pause(0.3)
            self.assertEqual(calls, [1])


class StartOption(unittest.TestCase):
    class Started(Exception):
        pass

    def start(self, *argv: str) -> dict:
        got: dict = {}

        class FakeApp:
            def __init__(fake, **kw):
                got.update(kw)

            def run(fake):
                raise self.Started

        with mock.patch("alacrittyforge.app.AlacrittyForgeApp", FakeApp), self.assertRaises(self.Started):
            cli.main(list(argv))
        return got

    def test_both_spellings_reach_the_app(self):
        self.assertEqual(self.start("--hypeforge"), {"hypeforge": True})
        self.assertEqual(self.start("--hypeForge"), {"hypeforge": True})
        self.assertEqual(self.start(), {"hypeforge": False})

    def test_help_does_not_mention_it(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(cli.main(["--help"]), 0)
        self.assertNotIn("hypeforge", out.getvalue().lower())

    def test_the_man_page_does_not_mention_it(self):
        man = Path(__file__).resolve().parent.parent / "alacrittyforge.1"
        text = man.read_text().lower().replace("\\-", "-")          # groff writes - as \-
        self.assertNotIn("--hypeforge", text, "the man page is for people; --hypeforge is for Settings")

    def test_other_options_still_answer(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(cli.main(["--hypeforge", "--version"]), 0)
        self.assertIn("alacrittyForge", out.getvalue())
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cli.main(["--hypeforgex"]), 2, "only the exact flag")

    def test_the_flag_is_forgekits(self):
        from forgekit import HYPEFORGE_FLAG, hypeforge_mode
        self.assertEqual(cli.HYPEFORGE_FLAG, HYPEFORGE_FLAG)
        for argv in (["--hypeforge"], ["--HypeForge"], ["x"], ["--hypeforgex"], []):
            self.assertEqual(any(a.lower() == cli.HYPEFORGE_FLAG for a in argv), hypeforge_mode(argv), argv)


# Javier, 2026-10-03: "Words In Title Case (k)", the key in round brackets after the words
LABELS = {
    "overview": {"ov-restore": "Restore the Newest Backup", "ov-rename": "Update Them",
                 "task-theme": "Pick a Theme", "task-font": "Change the Font", "task-size": "Text Size",
                 "task-backup": "Back Up Now"},
    "themes": {"th-use": "Use This Theme", "th-adjust": "Adjust Colours… (a)",
               "th-saveown": "Save My Colours as a Theme…", "th-install": "Install a Theme… (i)",
               "th-get": "Where to Get Themes"},
    "shortcuts": {"sc-add": "Add a Shortcut… (+)", "sc-change": "Change (F2)", "sc-remove": "Remove (Del)",
                  "sc-off": "Turn This One Off", "sc-modes": "Show Vi and Search Keys"},
    "backups": {"bk-restore": "Restore… (r)", "bk-new": "Back Up Now (n)", "bk-show": "Show Whole File",
                "bk-delete": "Delete… (d)"},
    "bar": {"af-save": "Save… (s)", "af-discard": "Discard"},
    "quit": {"save": "Save First", "quit": "Quit Without Saving", "stay": "Stay (Esc)"},
    "shortcut-window": {"sd-ok": "Add It", "sd-cancel": "Cancel (Esc)"},
    "adjust-window": {"ad-keep": "Keep These Colours", "ad-cancel": "Cancel (Esc)"},
    "restore-window": {"ok": "Restore (y)"},
}
SMALL = {"a", "an", "the", "and", "or", "as", "of", "to", "in", "on", "for", "with", "by", "at"}


def title_case(label: str) -> bool:
    words = re.sub(r" \([^)]+\)$", "", label).replace("…", "").split()
    return bool(words) and all(w[0].isupper() or (i and w in SMALL) for i, w in enumerate(words))


class ButtonLabels(test_screens.Screens):
    def labels(self, screen, ids) -> dict:
        from textual.widgets import Button
        return {b.id: str(b.label) for b in screen.query(Button) if b.id in ids}

    def test_the_expected_labels_are_title_case(self):
        for where, labels in LABELS.items():
            for bid, label in labels.items():
                self.assertTrue(title_case(label), f"{where} {bid}: {label!r}")
        self.assertFalse(title_case("Back up now"), "the check itself catches the old style")
        self.assertFalse(title_case("Use this theme"))

    async def test_every_button_reads_words_in_title_case_then_its_key(self):
        from forgekit import ConfirmDialog
        from alacrittyforge import backups
        from alacrittyforge.app import QuitDialog
        from alacrittyforge.ui.shortcuts import ShortcutDialog
        backups.create("manual", path=self.cfg, backup_dir=self.dir / "bk")
        app = self.app()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause(0.4)
            seen = {}
            for n, sid in enumerate(["overview", None, "themes", "shortcuts", "backups"], 1):
                if sid is None:
                    continue
                app.set_focus(None)
                await pilot.press(str(n))
                await pilot.pause(0.4)
                # the Overview shows both fix buttons only when needed: read them all, shown or not
                seen[sid] = self.labels(app.query_one(f"#sec-{sid}"), LABELS[sid])
            app.session.set("font.size", 14.0)
            app.refresh_state()
            await pilot.pause(0.2)
            seen["bar"] = self.labels(app.screen, LABELS["bar"])
            app.set_focus(None)
            await pilot.press("q")
            await pilot.pause(0.3)
            self.assertIsInstance(app.screen, QuitDialog)
            seen["quit"] = self.labels(app.screen, LABELS["quit"])
            await pilot.press("escape")
            await pilot.pause(0.2)
            app.session.discard()
            app.refresh_state()
            await pilot.press("4")
            await pilot.pause(0.3)
            await pilot.press("plus")
            await pilot.pause(0.3)
            self.assertIsInstance(app.screen, ShortcutDialog)
            seen["shortcut-window"] = self.labels(app.screen, LABELS["shortcut-window"])
            await pilot.press("escape")
            await pilot.pause(0.2)
            await pilot.press("3")
            await pilot.pause(0.4)
            await pilot.press("a")
            await pilot.pause(0.4)
            seen["adjust-window"] = self.labels(app.screen, LABELS["adjust-window"])
            await pilot.press("escape")
            await pilot.pause(0.2)
            await pilot.press("5")
            await pilot.pause(0.4)
            await pilot.press("r")
            await pilot.pause(0.4)
            self.assertIsInstance(app.screen, ConfirmDialog)
            seen["restore-window"] = self.labels(app.screen, LABELS["restore-window"])
        self.assertEqual(seen, LABELS)

    async def test_the_labels_that_change(self):
        app = self.app()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.press("4")
            await pilot.pause(0.4)
            app.query_one("#sc-modes").press()
            await pilot.pause(0.3)
            self.assertEqual(str(app.query_one("#sc-modes").label), "Hide Vi and Search Keys")
            t = app.query_one("#sc-table")
            row = next(i for i, r in enumerate(app.query_one("#sec-shortcuts").rows) if r[0] == "alacritty")
            t.move_cursor(row=row)
            await pilot.pause(0.2)
            labels = {str(app.query_one("#sc-off").label)}
            app.query_one("#sc-off").press()                 # one of Alacritty's, turned off
            await pilot.pause(0.3)
            for i, r in enumerate(app.query_one("#sec-shortcuts").rows):
                if r[0] == "alacritty":
                    t.move_cursor(row=i)
                    await pilot.pause(0.05)
                    labels.add(str(app.query_one("#sc-off").label))
            self.assertIn("Turn It Back On", labels)
            self.assertTrue(all(title_case(x) for x in labels), labels)

    async def test_the_delete_window_says_y(self):
        from forgekit import ConfirmDialog
        from alacrittyforge import backups
        backups.create("manual", path=self.cfg, backup_dir=self.dir / "bk")
        app = self.app()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.press("5")
            await pilot.pause(0.4)
            await pilot.press("d")
            await pilot.pause(0.4)
            self.assertIsInstance(app.screen, ConfirmDialog)
            self.assertEqual(str(app.screen.query_one("#ok").label), "Delete (y)")


# test_screens' own tests run from test_screens.py; don't run them again from here
for _cls in (MenuKeys, InsideHypeForgeSettings, ButtonLabels):
    for _name in [n for n in vars(test_screens.Screens) if n.startswith("test_")]:
        setattr(_cls, _name, None)
del _cls, _name                  # a name left holding a test class would load it twice

if __name__ == "__main__":
    unittest.main()
