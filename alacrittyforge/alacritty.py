"""Which Alacritty is installed, and which setting names it reads (v1.0.0).

Distributions ship different Alacritty versions (checked 2 Oct 2026):
Arch, Fedora 44, openSUSE Tumbleweed 0.17.0 · Debian 13 0.15.1 · Ubuntu 24.04
0.13.2. Alacritty 0.14 moved five settings: ``import``, ``working_directory``,
``live_config_reload`` and ``ipc_socket`` into ``[general]``, and ``shell``
into ``[terminal]``. An older Alacritty doesn't read the new names (a theme
named in ``general.import`` would silently not apply), and a newer one warns
about the old ones on every start. So alacrittyForge writes the names the
installed Alacritty reads. Compared from each version's own manual page:
0.15.1 knows every setting alacrittyForge shows; 0.13.2 lacks ``window.level``.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from functools import lru_cache

# 0.14's moves: name it reads now → the name before 0.14
MOVED_IN_0_14 = {
    "general.import": "import",
    "general.working_directory": "working_directory",
    "general.live_config_reload": "live_config_reload",
    "general.ipc_socket": "ipc_socket",
    "terminal.shell": "shell",
}

# settings an older Alacritty doesn't have: key → first version known to have it
SINCE = {"window.level": (0, 15)}

NEWEST = (0, 17, 0)


@lru_cache(maxsize=1)
def installed_version() -> tuple[int, ...] | None:
    """(0, 13, 2) from ``alacritty --version``; None when Alacritty isn't installed."""
    exe = shutil.which("alacritty")
    if not exe:
        return None
    try:
        out = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=10).stdout
    except (OSError, subprocess.TimeoutExpired):
        return None
    m = re.search(r"(\d+)\.(\d+)(?:\.(\d+))?", out)
    if not m:
        return None
    return tuple(int(x) for x in m.groups(default="0"))


def shown_version(v: tuple[int, ...] | None) -> str:
    return ".".join(map(str, v)) if v else "not installed"


class Names:
    """Setting names for one Alacritty version."""

    def __init__(self, version: tuple[int, ...] | None) -> None:
        self.version = version
        self.legacy = version is not None and version < (0, 14)

    def file_key(self, key: str) -> str:
        """The name to read and write for a setting (alacrittyForge uses the new names)."""
        if self.legacy:
            for new, old in MOVED_IN_0_14.items():
                if key == new or key.startswith(new + "."):
                    return old + key[len(new):]
        return key

    def has(self, key: str) -> bool:
        since = SINCE.get(key)
        return since is None or self.version is None or self.version >= since

    def misnamed(self) -> dict[str, str]:
        """Names this Alacritty doesn't read → the names it does."""
        if self.legacy:
            return dict(MOVED_IN_0_14)                     # new → old
        return {old: new for new, old in MOVED_IN_0_14.items()}   # old → new
