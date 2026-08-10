#!/usr/bin/env python3
"""Regenerate the README screenshot gallery — pixel-perfect Textual SVGs.

Run from the repo root (forgekit on PYTHONPATH if not installed):
    python docs/screenshots/generate.py
Read-only: opens the real ~/.config/alacritty but never writes.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from alacrittyforge.app import AlacrittyForge, AlacShortcuts  # noqa: E402

OUT = Path(__file__).resolve().parent
SIZE = (120, 36)


def shot(app, name: str) -> None:
    app.save_screenshot(filename=f"{name}.svg", path=str(OUT))
    print(f"  {name}.svg")


async def main() -> None:
    app = AlacrittyForge()
    async with app.run_test(size=SIZE) as pilot:
        await pilot.pause()
        shot(app, "01-dashboard")

        # Config with an anchored dropdown open
        await pilot.press("2"); await pilot.pause()
        cfg = app.query_one("#sec-config")
        keys = [s["key"] for s in cfg._settings]
        if "window.decorations" in keys:
            app.query_one("#settings-table").move_cursor(
                row=keys.index("window.decorations"))
            cfg.action_edit_selected(); await pilot.pause()
            shot(app, "02-config-dropdown")
            await pilot.press("escape"); await pilot.pause()

        # Font-family filter picker mid-search
        if "font.normal.family" in keys:
            app.query_one("#settings-table").move_cursor(
                row=keys.index("font.normal.family"))
            cfg.action_edit_selected(); await pilot.pause()
            try:
                flt = app.screen.query_one("#picker-filter")
                flt.value = "JetBrains"
                await pilot.pause()
            except Exception:
                pass
            shot(app, "03-config-font-picker")
            await pilot.press("escape"); await pilot.pause()

        # Themes list + preview window
        await pilot.press("3"); await pilot.pause()
        shot(app, "04-themes")
        th = app.query_one("#sec-themes")
        if any(r["kind"] == "file" for r in th._rows):
            lv = app.query_one("#themes-list")
            lv.index = next(i for i, r in enumerate(th._rows)
                            if r["kind"] == "file")
            th.action_preview(); await pilot.pause()
            shot(app, "05-theme-preview")
            await pilot.press("escape"); await pilot.pause()

        # Bindings cell editor
        await pilot.press("5"); await pilot.pause()
        shot(app, "06-bindings")

        # Shortcuts window
        app.push_screen(AlacShortcuts(app.SHORTCUTS)); await pilot.pause()
        shot(app, "07-shortcuts")

    print("alacrittyForge gallery done.")


asyncio.run(main())
