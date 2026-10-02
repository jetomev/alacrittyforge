#!/usr/bin/env python3
"""Run inside a distro test VM, as root: does this distribution's Alacritty
read what alacrittyForge writes? (v1.0.0, Javier: "all major linux distros,
all the same")

1. alacrittyForge's tests, here.
2. alacrittyForge saves real changes (theme, font size, opacity, cursor,
   shell); this distribution's Alacritty then starts on that file in an
   invisible display (Xvfb), and every config warning or error it prints is
   collected. Clean means none.
3. The failing direction: the same Alacritty on a file with the names this
   version does NOT read must warn, or step 2's "clean" proves nothing.

Prints a summary; the last line is PASS or FAIL.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

from alacrittyforge import alacritty, themes  # noqa: E402
from alacrittyforge.session import Session  # noqa: E402

WARN = re.compile(r"(config (warning|error)|unused config key|deprecated|failed to|error:)", re.I)


def run_alacritty(cfg: Path) -> tuple[bool, list[str]]:
    """Start Alacritty on ``cfg`` headless for a few seconds: (did it run, its config complaints)."""
    env = dict(os.environ, LIBGL_ALWAYS_SOFTWARE="1", WINIT_UNIX_BACKEND="x11")
    # 24-bit colour: Xvfb's default depth gives Alacritty no usable GL config
    cmd = ["xvfb-run", "-a", "-s", "-screen 0 1280x800x24", "timeout", "6", "alacritty", "--config-file", str(cfg), "-e", "sh", "-c", "sleep 4"]
    p = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=60)
    out = (p.stdout + p.stderr).splitlines()
    started = p.returncode in (0, 124)          # 124: timeout ended it, i.e. it ran
    lines = [l for l in out if WARN.search(l) and "XDG_RUNTIME_DIR" not in l]
    if not started:
        lines.insert(0, f"(Alacritty didn't run: exit {p.returncode}) " + " | ".join(out[-3:]))
    return started, lines


def main() -> int:
    ok = True
    v = alacritty.installed_version()
    print(f"Alacritty {alacritty.shown_version(v)} · Python {sys.version.split()[0]}")

    # 1. the tests
    r = subprocess.run([sys.executable, "-m", "unittest", "tests.test_saving", "tests.test_session",
                        "tests.test_themes", "tests.test_versions", "tests.test_manual", "tests.test_screens"],
                       cwd=HERE, capture_output=True, text=True)
    summary = [l for l in r.stderr.splitlines() if l.startswith(("Ran ", "OK", "FAILED"))]
    print("tests:", " · ".join(summary))
    if r.returncode:
        ok = False
        print(r.stderr[-1500:])

    # 2. a real save, read by this Alacritty
    home = Path("/root/.config/alacritty")
    shutil.rmtree(home, ignore_errors=True)
    (home / "themes").mkdir(parents=True)
    (home / "themes" / "mocha.toml").write_text(
        '[colors.primary]\nbackground = "#1e1e2e"\nforeground = "#cdd6f4"\n')
    cfg = home / "alacritty.toml"
    cfg.write_text("# written by hand\n[font]\nsize = 11.0\n")
    s = Session.load(cfg, backup_dir=home / "backups", themes_dir=home / "themes")
    s.set("window.opacity", 0.9)
    s.set("font.size", 13.0)
    s.set("cursor.style.shape", "Beam")
    s.set("terminal.shell", "/bin/sh")
    s.set("scrolling.history", 5000)
    for k, val in themes.use_changes(s, home / "themes" / "mocha.toml", home / "themes").items():
        s.set(k, val)
    s.save()
    print("written:\n  " + cfg.read_text().strip().replace("\n", "\n  "))
    ran, complaints = run_alacritty(cfg)
    print("Alacritty on alacrittyForge's file:", "clean" if ran and not complaints else "")
    for c in complaints:
        print("   ", c)
    ok &= ran and not complaints

    # 3. the failing direction: names this version doesn't read must be reported
    wrong = home / "wrong.toml"
    if s.names.legacy:
        wrong.write_text('[general]\nlive_config_reload = true\n')
    else:
        wrong.write_text('live_config_reload = true\n')
    ran, control = run_alacritty(wrong)
    good = ran and bool(control)
    print("Alacritty on a file with the wrong names:", "warned (good)" if good else
          ("SILENT" if ran else "didn't run"))
    for c in control[:3]:
        print("   ", c)
    ok &= good

    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
