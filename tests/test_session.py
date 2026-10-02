"""The settings list and the session (v1.0.0, step 2). No display needed."""

from __future__ import annotations

import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from alacrittyforge.session import Session, same  # noqa: E402
from alacrittyforge.settings_file import REMOVE  # noqa: E402
from alacrittyforge.settings_spec import BY_KEY, GROUPS, SETTINGS, problem, shown, to_store  # noqa: E402

SAMPLE = '''[window]
opacity = 0.95
opactiy = 0.5

[terminal.shell]
program = "/usr/bin/fish"
args = ["-l"]

[font]
size = 12.0
'''


class TheList(unittest.TestCase):
    def test_every_setting_is_consistent(self):
        groups = {g for g, _l, _d in GROUPS}
        for s in SETTINGS:
            with self.subTest(s.key):
                self.assertIn(s.group, groups)
                self.assertTrue(s.label and s.help)
                if s.choices and s.default is not None:
                    self.assertIn(s.default, [v for v, _l in s.choices])
                self.assertEqual(problem(s, s.default), "")
                for p in s.presets:
                    self.assertEqual(problem(s, p), "", f"preset {p}")
        self.assertEqual(len(BY_KEY), len(SETTINGS), "a key is listed twice")

    def test_every_group_has_settings(self):
        for g, label, _d in GROUPS:
            self.assertTrue([s for s in SETTINGS if s.group == g], label)

    def test_numbers_read_the_way_people_say_them(self):
        self.assertEqual(shown(BY_KEY["window.opacity"], 0.9), "90 %")
        self.assertEqual(shown(BY_KEY["scrolling.history"], 10000), "10 000 lines")
        self.assertEqual(to_store(BY_KEY["window.opacity"], 85), 0.85)
        self.assertEqual(to_store(BY_KEY["window.padding.x"], 12.0), 12)
        self.assertIsInstance(to_store(BY_KEY["window.padding.x"], 12.0), int)

    def test_bad_values_say_why(self):
        self.assertIn("above", problem(BY_KEY["window.opacity"], 1.5))
        self.assertIn("below", problem(BY_KEY["window.padding.x"], -3))
        self.assertIn("colour", problem(BY_KEY["bell.color"], "red"))
        self.assertEqual(problem(BY_KEY["bell.color"], "#ff00aa"), "")


class TheSession(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.cfg = Path(self._tmp.name) / "alacritty.toml"
        self.cfg.write_text(SAMPLE)
        self.s = Session.load(self.cfg, backup_dir=Path(self._tmp.name) / "bk")

    def tearDown(self):
        self._tmp.cleanup()

    def test_nothing_is_changed_at_start(self):
        self.assertEqual(self.s.pending, {})

    def test_setting_the_files_value_is_no_change(self):
        self.assertTrue(self.s.set("window.opacity", 0.9))
        self.assertFalse(self.s.set("window.opacity", 0.95))
        self.assertEqual(self.s.pending, {})

    def test_not_set_is_not_set_whatever_its_spelling(self):
        self.assertFalse(self.s.set("bell.duration", None))
        self.assertTrue(same(None, REMOVE))
        self.assertFalse(same(False, None))
        self.assertFalse(same(0, False))          # 0 ms is not "off"

    def test_unset_reads_as_alacrittys_default(self):
        self.assertEqual(self.s.shown("bell.duration"), "not set (0 ms)")
        self.assertEqual(self.s.shown("terminal.osc52"), "not set (Copy only)")

    def test_the_review_lists_old_and_new_in_plain_words(self):
        self.s.set("window.opacity", 0.9)
        self.s.set("cursor.style.shape", "Beam")
        self.assertEqual(self.s.changes(), [("Opacity", "95 %", "90 %"),
                                            ("Shape", "not set (Block)", "Beam")])

    def test_the_shell_as_a_table_is_no_change(self):
        # the file says [terminal.shell] program = ...; the screen picks the program
        self.assertFalse(self.s.set("terminal.shell", "/usr/bin/fish"))
        self.assertEqual(self.s.pending, {})

    def test_changing_the_shell_keeps_its_options(self):
        self.s.set("terminal.shell", "/usr/bin/bash")
        self.s.save()
        data = tomllib.loads(self.cfg.read_text())
        self.assertEqual(data["terminal"]["shell"], {"program": "/usr/bin/bash", "args": ["-l"]})

    def test_a_save_leaves_nothing_pending_and_notes_it(self):
        self.s.set("font.size", 14.0)
        r = self.s.save()
        self.assertEqual(self.s.pending, {})
        self.assertEqual(self.s.value("font.size"), 14.0)
        self.assertIsNotNone(r.backup)
        self.assertTrue(self.s.saves[0].startswith("Saved 1 change at"))

    def test_a_typo_in_the_file_is_found(self):
        # Alacritty warns "Unused config key" and ignores it
        self.assertEqual(self.s.unknown_keys(), ["window.opactiy"])

    def test_unsaved_changes_survive_a_reread(self):
        self.s.set("font.size", 14.0)
        self.cfg.write_text(SAMPLE.replace("opacity = 0.95", "opacity = 0.8"))
        self.s.reload()
        self.assertEqual(self.s.pending, {"font.size": 14.0})
        self.assertEqual(self.s.value("window.opacity"), 0.8)


if __name__ == "__main__":
    unittest.main()
