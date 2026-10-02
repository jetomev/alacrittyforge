"""Saving alacritty.toml safely (v1.0.0, step 1). No Alacritty, no display needed.

Each test feeds the case 0.2.0 got wrong: comments, a cleared value, a file it
couldn't read, a shortcut with extra fields, many changes in one save, a link.
"""

from __future__ import annotations

import os
import sys
import tempfile
import time
import tomllib
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from alacrittyforge import backups  # noqa: E402
from alacrittyforge.settings_file import (  # noqa: E402
    MISSING, REMOVE, SettingsFile, Unreadable, old_names, rename_changes, save,
)

JAVIER = '''# my terminal
[env]
TERM = "xterm-256color"

[window]
decorations = "Full"
opacity = 0.95   # a bit see-through
blur = true

[window.padding]
x = 15
y = 15

[font]
size = 12.0

[font.normal]
family = "JetBrainsMono Nerd Font"
style = "Regular"

[keyboard]
bindings = [
    { key = "V", mods = "Control|Shift", action = "Paste" },
    { key = "Return", mods = "Shift", chars = "\\u001b\\r" },
    { key = "F", mods = "Control|Shift", mode = "~Search", action = "SearchForward" },
]

[general]
import = [
    "~/.config/alacritty/themes/KognogOS-theme.toml",
]
'''


class Case(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.cfg = self.dir / "alacritty.toml"
        self.bk = self.dir / "backups"
        self.cfg.write_text(JAVIER)

    def tearDown(self):
        self._tmp.cleanup()

    def save(self, changes, **kw):
        return save(changes, path=self.cfg, backup_dir=self.bk, **kw)


class KeepsWhatYouWrote(Case):
    def test_a_change_touches_only_its_line(self):
        self.save({"window.opacity": 0.9})
        after = self.cfg.read_text()
        self.assertIn("# my terminal", after)
        self.assertIn("opacity = 0.9   # a bit see-through", after)
        # everything else byte for byte
        self.assertEqual(after.replace("opacity = 0.9 ", "opacity = 0.95 ", 1), JAVIER)

    def test_a_new_setting_lands_in_its_section(self):
        self.save({"window.dynamic_padding": True, "cursor.style.shape": "Beam"})
        data = tomllib.loads(self.cfg.read_text())
        self.assertIs(data["window"]["dynamic_padding"], True)
        self.assertEqual(data["cursor"]["style"]["shape"], "Beam")
        self.assertNotIn("[cursor]\n", self.cfg.read_text())   # no empty header

    def test_shortcuts_keep_every_field_and_one_per_line(self):
        sf = SettingsFile.load(self.cfg)
        b = sf.get("keyboard.bindings")
        b.append({"key": "T", "mods": "Control|Shift", "action": "CreateNewWindow"})
        self.save({"keyboard.bindings": b})
        data = tomllib.loads(self.cfg.read_text())["keyboard"]["bindings"]
        self.assertEqual(data[1]["chars"], "\x1b\r")
        self.assertEqual(data[2]["mode"], "~Search")              # 0.2.0 dropped it
        self.assertEqual(data[3]["action"], "CreateNewWindow")
        self.assertEqual(self.cfg.read_text().count("\n    {"), 4)
        self.assertIn('chars = "\\u001b\\r"', self.cfg.read_text())   # not \\e (TOML 1.1 only)


class ClearingASetting(Case):
    def test_remove_takes_the_line_out(self):
        # 0.2.0: a blank font value became None and the save failed
        self.save({"font.normal.style": REMOVE})
        sf = SettingsFile.load(self.cfg)
        self.assertIs(sf.get("font.normal.style"), MISSING)
        self.assertEqual(sf.get("font.normal.family"), "JetBrainsMono Nerd Font")

    def test_a_section_left_empty_goes_too(self):
        self.save({"window.padding.x": REMOVE, "window.padding.y": REMOVE})
        self.assertNotIn("[window.padding]", self.cfg.read_text())
        self.assertIn("[window]", self.cfg.read_text())

    def test_removing_what_isnt_there_changes_nothing(self):
        self.save({"bell.duration": REMOVE})
        self.assertEqual(self.cfg.read_text(), JAVIER)


class AFileThatCantBeRead(Case):
    def test_it_is_never_saved_over(self):
        broken = JAVIER.replace('decorations = "Full"', "decorations = Full")
        self.cfg.write_text(broken)
        sf = SettingsFile.load(self.cfg)
        self.assertFalse(sf.readable)
        self.assertTrue(sf.error)
        with self.assertRaises(Unreadable):
            self.save({"window.opacity": 0.9})
        self.assertEqual(self.cfg.read_text(), broken)          # untouched
        self.assertEqual(backups.list_all(self.bk), [])         # and no backup made

    def test_a_missing_file_is_created_without_a_backup(self):
        self.cfg.unlink()
        r = self.save({"font.size": 13.0})
        self.assertIsNone(r.backup)
        self.assertEqual(tomllib.loads(self.cfg.read_text()), {"font": {"size": 13.0}})


class Backups(Case):
    def test_one_backup_per_save_however_many_changes(self):
        # 0.2.0 made one per shortcut change
        self.save({"window.opacity": 0.9, "font.size": 14.0, "window.blur": False,
                   "cursor.style.shape": "Beam", "keyboard.bindings": []})
        self.assertEqual(len(backups.list_all(self.bk)), 1)
        self.assertEqual(backups.list_all(self.bk)[0].path.read_text(), JAVIER)

    def test_two_saves_in_the_same_second_keep_both_backups(self):
        self.save({"font.size": 13.0})
        self.save({"font.size": 14.0})
        self.assertEqual(len(backups.list_all(self.bk)), 2)

    def test_only_the_newest_twenty_are_kept(self):
        for i in range(23):
            self.save({"font.size": float(10 + i)})
        kept = backups.list_all(self.bk)
        self.assertEqual(len(kept), 20)
        self.assertEqual(len(list(self.bk.glob("*.note"))), 20)

    def test_older_backups_still_show_with_plain_reasons(self):
        self.bk.mkdir()
        old = self.bk / "alacritty_20260809_203521_374190.bak.toml"
        old.write_text(JAVIER)
        (self.bk / "alacritty_20260809_203521_374190.note").write_text("pre-theme-KognogOS-theme")
        self.assertEqual(backups.list_all(self.bk)[0].why, "Before using a theme (KognogOS-theme)")

    def test_a_backup_is_dated_when_it_was_made_not_when_settings_changed(self):
        # copying keeps the file's time; 0.2.0's list showed the settings' last edit
        os.utime(self.cfg, (0, 946684800))                      # settings last edited in 2000
        made = self.save({"font.size": 13.0}).backup
        listed = backups.list_all(self.bk)[0]
        self.assertEqual(listed.path, made)
        self.assertGreater(listed.made.year, 2020)

    def test_restore_puts_it_back_and_backs_up_today_first(self):
        self.save({"font.size": 16.0})
        first = backups.list_all(self.bk)[0]
        time.sleep(0.01)
        backups.restore(first, path=self.cfg, backup_dir=self.bk)
        self.assertEqual(self.cfg.read_text(), JAVIER)
        self.assertEqual(backups.list_all(self.bk)[0].note, "pre-restore")


class TheWriteItself(Case):
    def test_a_linked_file_stays_a_link(self):
        real = self.dir / "dotfiles" / "alacritty.toml"
        real.parent.mkdir()
        real.write_text(JAVIER)
        self.cfg.unlink()
        self.cfg.symlink_to(real)
        self.save({"font.size": 13.0})
        self.assertTrue(self.cfg.is_symlink())
        self.assertIn("size = 13.0", real.read_text())

    def test_permissions_are_kept_and_no_temp_file_is_left(self):
        os.chmod(self.cfg, 0o600)
        self.save({"font.size": 13.0})
        self.assertEqual(self.cfg.stat().st_mode & 0o777, 0o600)
        self.assertEqual([p.name for p in self.dir.iterdir() if p.name.endswith(".new")], [])

    def test_a_change_made_elsewhere_meanwhile_is_kept(self):
        sf = SettingsFile.load(self.cfg)                        # screens loaded this
        self.cfg.write_text(JAVIER.replace("size = 12.0", "size = 15.0"))   # someone else
        self.save({"window.opacity": 0.9})
        data = tomllib.loads(self.cfg.read_text())
        self.assertEqual(data["font"]["size"], 15.0)
        self.assertEqual(data["window"]["opacity"], 0.9)
        self.assertEqual(sf.get("font.size"), 12.0)


class OldNames(Case):
    def test_old_names_are_found_and_moved(self):
        self.cfg.write_text('import = ["a.toml"]\nlive_config_reload = false\n\n[shell]\nprogram = "/usr/bin/fish"\n')
        sf = SettingsFile.load(self.cfg)
        self.assertEqual(sorted(o for o, _n in old_names(sf)), ["import", "live_config_reload", "shell"])
        self.save(rename_changes(sf))
        data = tomllib.loads(self.cfg.read_text())
        self.assertEqual(data, {"general": {"import": ["a.toml"], "live_config_reload": False},
                                "terminal": {"shell": {"program": "/usr/bin/fish"}}})

    def test_where_both_are_set_the_new_one_wins(self):
        self.cfg.write_text('[shell]\nprogram = "bash"\n\n[terminal.shell]\nprogram = "fish"\n')
        sf = SettingsFile.load(self.cfg)
        self.save(rename_changes(sf))
        self.assertEqual(tomllib.loads(self.cfg.read_text()), {"terminal": {"shell": {"program": "fish"}}})


if __name__ == "__main__":
    unittest.main()
