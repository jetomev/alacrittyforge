"""Starting alacrittyForge from the terminal (v1.1.0).

``--version`` and ``--help`` answer and exit without opening the app.
``--hypeforge`` (any case, so ``--hypeForge`` too) is how hypeForge Settings
starts it: the app is then one page of Settings and has no Quit of its own.
It is for Settings, not for people, so ``--help`` doesn't list it (1.1.0, #20).
Otherwise the app runs full-screen, and when it closes the terminal gets the
record of the session: the start banner, then a closing note saying what was
saved, where the run was logged, and a thank-you (the same start and end as
grubForge and nog).
"""

from __future__ import annotations

import datetime as dt
import os
import sys

from . import __version__

USAGE = f"""alacrittyForge {__version__} — Alacritty's settings, without editing the file by hand

Usage:
  alacrittyforge             open alacrittyForge
  alacrittyforge --version   print the version
  alacrittyforge --help      print this

Inside: Tab moves, Enter opens, F10 saves (with a review first), F1 explains,
M opens the manual, ? lists every key.
Manual: https://github.com/jetomev/alacrittyforge/tree/main/alacrittyforge/manual
"""

LOG_DIR = "~/.local/share/alacrittyforge/logs"

# forgekit's HYPEFORGE_FLAG, spelled here so --version and --help answer without
# loading forgekit (tests/test_v110.py checks the two agree)
HYPEFORGE_FLAG = "--hypeforge"


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    hypeforge = any(a.lower() == HYPEFORGE_FLAG for a in args)
    args = [a for a in args if a.lower() != HYPEFORGE_FLAG]
    if args and args[0] in ("--version", "-V", "version"):
        print(f"alacrittyForge {__version__}")
        return 0
    if args and args[0] in ("--help", "-h", "help"):
        print(USAGE)
        return 0
    if args:
        print(f"alacrittyforge: unknown option {args[0]!r}\n\n{USAGE}", file=sys.stderr)
        return 2

    from forgekit import closing_notice, runs_log_row, session_banner
    from .app import AlacrittyForgeApp

    app = AlacrittyForgeApp(hypeforge=hypeforge)
    app.run()
    s = app.session
    ended = dt.datetime.now()
    heading, lines, level = s.summary()
    user = os.environ.get("USER") or os.environ.get("LOGNAME") or "unknown"
    logs = []
    try:
        logs.append(runs_log_row(LOG_DIR, "alacrittyforge",
                                 [f"{s.started:%m/%d/%Y}", f"{s.started:%I:%M %p}", user, "alacrittyforge",
                                  heading.split("·", 1)[-1].strip(), " ".join(lines)]))
    except OSError as e:
        lines = lines + [f"(This run could not be logged: {e})"]
    print(session_banner("alacrittyForge", __version__, "alacrittyforge", s.started, ended, user))
    print(closing_notice(heading, lines, level=level, logs=logs, thanks="Thank you for using alacrittyForge!"))
    return 0
