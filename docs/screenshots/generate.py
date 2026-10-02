#!/usr/bin/env python3
"""Regenerate the README screenshots (v1.0.0) — Textual SVGs at 100 columns.

Run from the repo root (forgekit on PYTHONPATH if not installed):
    python docs/screenshots/generate.py
Works on a temporary copy of ~/.config/alacritty/alacritty.toml and reads
the real themes and backups, so nothing of yours is ever written.
"""
import asyncio
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from textual.widgets import OptionList  # noqa: E402

from alacrittyforge.app import AlacrittyForgeApp  # noqa: E402
from alacrittyforge.session import Session  # noqa: E402

OUT = Path(__file__).resolve().parent
SIZE = (100, 32)
REAL = Path.home() / ".config" / "alacritty"


def shot(app, name: str) -> None:
    app.save_screenshot(filename=f"{name}.svg", path=str(OUT))
    print(f"  {name}.svg")


async def main() -> None:
    tmp = Path(tempfile.mkdtemp())
    cfg = tmp / "alacritty.toml"
    if (REAL / "alacritty.toml").exists():
        shutil.copy2(REAL / "alacritty.toml", cfg)
    s = Session.load(cfg, backup_dir=REAL / "backups", themes_dir=REAL / "themes")
    app = AlacrittyForgeApp(session=s)
    try:
        async with app.run_test(size=SIZE) as pilot:
            await pilot.pause(0.8)
            shot(app, "01-overview")
            await pilot.press("2")
            await pilot.pause(0.5)
            app.query_one("#row-window-opacity").control.set_value(90)
            await pilot.pause(0.3)
            shot(app, "02-settings")
            app.query_one("#af-groups", OptionList).highlighted = 1
            await pilot.pause(0.4)
            shot(app, "03-text")
            await pilot.press("f10")
            await pilot.pause(0.6)
            shot(app, "04-review")
            await pilot.press("escape")
            await pilot.pause(0.3)
            app.session.discard()                 # nothing is saved
            await pilot.press("3")
            await pilot.pause(0.6)
            shot(app, "05-themes")
            await pilot.press("4")
            await pilot.pause(0.6)
            shot(app, "06-shortcuts")
            await pilot.press("plus")
            await pilot.pause(0.5)
            await pilot.press("ctrl+shift+t")
            await pilot.pause(0.4)
            shot(app, "07-add-shortcut")
            await pilot.press("escape")
            await pilot.pause(0.3)
            await pilot.press("5")
            await pilot.pause(0.6)
            shot(app, "08-backups")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("alacrittyForge screenshots done.")


asyncio.run(main())
