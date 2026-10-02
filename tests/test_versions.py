"""Each distribution's Alacritty gets the names it reads (v1.0.0).

Checked 2 Oct 2026: Arch/Fedora 44/openSUSE ship 0.17.0, Debian 13 0.15.1,
Ubuntu 24.04 0.13.2. Alacritty 0.14 moved import, working_directory,
live_config_reload, ipc_socket into [general] and shell into [terminal]: an
older Alacritty ignores the new names, so a theme set through general.import
would silently not apply on Ubuntu 24.04.
"""

from __future__ import annotations

import os
import stat
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from alacrittyforge import alacritty, themes  # noqa: E402
from alacrittyforge.alacritty import Names  # noqa: E402
from alacrittyforge.session import Session  # noqa: E402

UBUNTU = (0, 13, 2)
DEBIAN = (0, 15, 1)
ARCH = (0, 17, 0)


class Case(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.cfg = self.dir / "alacritty.toml"
        self.tdir = self.dir / "themes"
        self.tdir.mkdir()
        (self.tdir / "mocha.toml").write_text('[colors.primary]\nbackground = "#1e1e2e"\n')

    def tearDown(self):
        self._tmp.cleanup()

    def session(self, text: str, version):
        self.cfg.write_text(text)
        return Session.load(self.cfg, backup_dir=self.dir / "bk", themes_dir=self.tdir, version=version)


class TheNames(unittest.TestCase):
    def test_before_0_14_the_old_names_are_used(self):
        n = Names(UBUNTU)
        self.assertEqual(n.file_key("general.import"), "import")
        self.assertEqual(n.file_key("terminal.shell.program"), "shell.program")
        self.assertEqual(n.file_key("window.opacity"), "window.opacity")

    def test_from_0_14_the_new_names_are_used(self):
        for v in (DEBIAN, ARCH, None):
            self.assertEqual(Names(v).file_key("general.import"), "general.import")

    def test_keep_on_top_is_only_offered_where_it_exists(self):
        self.assertFalse(Names(UBUNTU).has("window.level"))
        self.assertTrue(Names(DEBIAN).has("window.level"))
        self.assertTrue(Names(None).has("window.level"))

    def test_the_installed_version_is_read_from_alacritty_itself(self):
        bindir = Path(tempfile.mkdtemp())
        exe = bindir / "alacritty"
        exe.write_text("#!/bin/sh\necho 'alacritty 0.13.2 (bb8ea18)'\n")
        exe.chmod(exe.stat().st_mode | stat.S_IEXEC)
        old = os.environ["PATH"]
        os.environ["PATH"] = f"{bindir}{os.pathsep}{old}"
        alacritty.installed_version.cache_clear()
        try:
            self.assertEqual(alacritty.installed_version(), (0, 13, 2))
        finally:
            os.environ["PATH"] = old
            alacritty.installed_version.cache_clear()


class Ubuntu2404(Case):
    def test_a_theme_is_written_where_0_13_reads_it(self):
        s = self.session('[font]\nsize = 12.0\n', UBUNTU)
        for k, v in themes.use_changes(s, self.tdir / "mocha.toml", self.tdir).items():
            s.set(k, v)
        s.save()
        data = tomllib.loads(self.cfg.read_text())
        self.assertEqual(data["import"], [themes.import_path(self.tdir / "mocha.toml")])
        self.assertNotIn("general", data)

    def test_the_shell_is_written_where_0_13_reads_it(self):
        s = self.session('shell = "/bin/bash"\n', UBUNTU)
        self.assertEqual(s.value("terminal.shell"), "/bin/bash")
        s.set("terminal.shell", "/usr/bin/fish")
        s.save()
        self.assertEqual(tomllib.loads(self.cfg.read_text()), {"shell": "/usr/bin/fish"})

    def test_new_names_are_flagged_and_moved_back(self):
        s = self.session('[general]\nimport = ["a.toml"]\nlive_config_reload = false\n', UBUNTU)
        self.assertEqual(sorted(w for w, _r in s.old_names()), ["general.import", "general.live_config_reload"])
        s.stage_renames()
        s.save()
        self.assertEqual(tomllib.loads(self.cfg.read_text()), {"import": ["a.toml"], "live_config_reload": False})

    def test_old_names_are_not_flagged_on_0_13(self):
        s = self.session('import = ["a.toml"]\n\n[shell]\nprogram = "/bin/bash"\n', UBUNTU)
        self.assertEqual(s.old_names(), [])
        self.assertEqual(s.unknown_keys(), [])


class Newer(Case):
    def test_old_names_are_flagged_and_moved_forward(self):
        s = self.session('import = ["a.toml"]\n\n[shell]\nprogram = "/bin/bash"\n', DEBIAN)
        self.assertEqual(sorted(w for w, _r in s.old_names()), ["import", "shell"])
        s.stage_renames()
        s.save()
        self.assertEqual(tomllib.loads(self.cfg.read_text()),
                         {"general": {"import": ["a.toml"]}, "terminal": {"shell": {"program": "/bin/bash"}}})


if __name__ == "__main__":
    unittest.main()
