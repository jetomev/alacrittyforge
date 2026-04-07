#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════
#  AlacrittyForge — Entry Point
#  Run with: python main.py
#  or after install: alacrittyforge
# ═══════════════════════════════════════════════════════════

import sys
from alacrittyforge.app import AlacrittyForge


def main() -> None:
    """Launch the AlacrittyForge TUI application."""
    app = AlacrittyForge()
    app.run()


if __name__ == "__main__":
    main()