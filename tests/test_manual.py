"""The manual stays in step with the app (v1.0.0). No display needed for most."""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from forgekit import load_pages  # noqa: E402

from alacrittyforge.settings_spec import GROUPS, SETTINGS  # noqa: E402

PAGES = {pid: (title, md) for pid, title, md in load_pages(ROOT / "alacrittyforge" / "manual")}


class Manual(unittest.TestCase):
    def test_every_settings_group_has_its_page(self):
        # F1 on a setting opens the page named after its group
        for gid, label, _d in GROUPS:
            self.assertIn(gid, PAGES, f"no manual page for {label}")

    def test_every_setting_is_explained_on_its_page(self):
        for s in SETTINGS:
            md = PAGES[s.group][1]
            with self.subTest(s.key):
                self.assertIn(f"**{s.label}**", md, f"{s.label} missing from the {s.group} page")

    def test_every_link_goes_to_a_page(self):
        for pid, (_t, md) in PAGES.items():
            for target in re.findall(r"\]\(#([\w-]+)\)", md):
                self.assertIn(target, PAGES, f"{pid} links to #{target}")

    def test_the_start_page_comes_first(self):
        self.assertEqual(next(iter(PAGES)), "start")


class F1(unittest.IsolatedAsyncioTestCase):
    async def test_f1_on_a_setting_opens_its_page(self):
        import tempfile
        from forgekit import ManualScreen
        from alacrittyforge.app import AlacrittyForgeApp
        from alacrittyforge.session import Session
        with tempfile.TemporaryDirectory() as t:
            cfg = Path(t) / "alacritty.toml"
            cfg.write_text("[font]\nsize = 12.0\n")
            app = AlacrittyForgeApp(session=Session.load(cfg, backup_dir=Path(t) / "bk", version=(0, 17, 0)))
            async with app.run_test(size=(120, 40)) as pilot:
                await pilot.press("2")
                await pilot.pause(0.4)
                app.query_one("#af-groups").highlighted = 2          # Cursor
                await pilot.pause(0.3)
                app.query_one("#row-cursor-style-shape").control.focus()
                await pilot.pause(0.2)
                await pilot.press("f1")
                await pilot.pause(0.4)
                self.assertIsInstance(app.screen, ManualScreen)
                self.assertEqual(app.screen._start, "cursor")


if __name__ == "__main__":
    unittest.main()
