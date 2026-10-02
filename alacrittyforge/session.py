"""What you've changed but not saved yet, and saving it (v1.0.0).

The screens read through a ``Session`` and stage changes in it; nothing is
written until ``save()``. A change equal to what the file already says is no
change. ``REMOVE`` means "not set": Alacritty then uses its own default.
"""

from __future__ import annotations

import datetime as dt
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from . import backups
from .settings_file import (CONFIG_PATH, MISSING, REMOVE, RENAMED, SaveResult, SettingsFile, old_names,
                            rename_changes, save)
from .settings_spec import BY_KEY, Setting, default_words, problem, shell_program, shown

# where Alacritty's file may hold more than the settings screen shows; these
# are not "unknown" (they have screens of their own, or are kept untouched)
KNOWN_PREFIXES = ("colors.", "env.", "keyboard.", "mouse.", "hints.", "general.import",
                  "terminal.shell", "font.normal.", "font.bold.", "font.italic.", "font.bold_italic.",
                  "window.position", "cursor.vi_mode_style", "bell.command", "debug.",
                  "window.option_as_alt", "window.class")


def same(a: Any, b: Any) -> bool:
    """Not set, REMOVE and None all mean the same: Alacritty's default."""
    unset = (None, REMOVE, MISSING)
    if a in unset or b in unset:
        return a in unset and b in unset
    if isinstance(a, bool) or isinstance(b, bool):
        return a is b
    return a == b


def _leaves(d: dict, prefix: str = "") -> list[str]:
    out = []
    for k, v in d.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict) and not key.startswith(("env", "terminal.shell")):
            out += _leaves(v, key + ".")
        else:
            out.append(key)
    return out


@dataclass
class Session:
    path: Path = CONFIG_PATH
    backup_dir: Path | None = None
    file: SettingsFile = field(default=None)
    pending: dict[str, Any] = field(default_factory=dict)
    saved_at: dt.datetime | None = None
    saves: list[str] = field(default_factory=list)      # for the closing note
    last_backup: Path | None = None

    @classmethod
    def load(cls, path: Path = CONFIG_PATH, backup_dir: Path | None = None) -> "Session":
        s = cls(path=Path(path), backup_dir=backup_dir)
        s.file = SettingsFile.load(s.path)
        return s

    def reload(self) -> None:
        """Read the file again (it may have changed elsewhere); your unsaved
        changes stay, except those that now match the file."""
        self.file = SettingsFile.load(self.path)
        self.pending = {k: v for k, v in self.pending.items() if not same(v, self.original(k))}

    # ── reading ──────────────────────────────────────────────────────────
    @property
    def readable(self) -> bool:
        return self.file.readable

    def original(self, key: str) -> Any:
        v = self.file.get(key)
        return None if v is MISSING else v

    def value(self, key: str) -> Any:
        if key in self.pending:
            v = self.pending[key]
            return None if v is REMOVE else v
        return self.original(key)

    def shown(self, key: str, value: Any = MISSING) -> str:
        s = BY_KEY[key]
        v = self.value(key) if value is MISSING else value
        if v is None or v is REMOVE:
            return f"not set ({default_words(s)})"
        return shown(s, v)

    # ── changing ─────────────────────────────────────────────────────────
    def set(self, key: str, value: Any) -> bool:
        """Stage a change. True when it differs from the file."""
        if same(value, self.original(key)):
            self.pending.pop(key, None)
            return False
        self.pending[key] = REMOVE if value is None else value
        return True

    def discard(self) -> None:
        self.pending.clear()

    @property
    def change_count(self) -> int:
        return len(self.pending)

    def problems(self) -> list[str]:
        out = []
        for k, v in self.pending.items():
            s = BY_KEY.get(k)
            if s and (p := problem(s, None if v is REMOVE else v)):
                out.append(f"{s.label}: {p}")
        return out

    def changes(self) -> list[tuple[str, str, str]]:
        """(label, old, new) for the review, in the order settings are shown."""
        order = list(BY_KEY)
        out = []
        for k in sorted(self.pending, key=lambda k: order.index(k) if k in order else len(order)):
            if k in BY_KEY:
                out.append((BY_KEY[k].label, self.shown(k, self.original(k)), self.shown(k, self.pending[k])))
            else:
                out.append((k, str(self.original(k)), "removed" if self.pending[k] is REMOVE
                            else str(self.pending[k])))
        return out

    def file_changes(self) -> dict[str, Any]:
        """``pending`` as the file needs it."""
        out = dict(self.pending)
        if "terminal.shell" in out:
            prog = out.pop("terminal.shell")
            current = self.original("terminal.shell")
            if isinstance(current, dict) and prog is not REMOVE:
                out["terminal.shell.program"] = prog    # keep its args
            else:
                out["terminal.shell"] = prog
        return out

    # ── saving ───────────────────────────────────────────────────────────
    def save(self, note: str = "Before a save") -> SaveResult:
        n = self.change_count
        r = save(self.file_changes(), path=self.path, note=note, backup_dir=self.backup_dir)
        self.pending.clear()
        self.saved_at = dt.datetime.now()
        self.last_backup = r.backup
        self.saves.append(f"Saved {n} change{'s' if n != 1 else ''} at {self.saved_at:%I:%M %p}.")
        self.reload()
        return r

    # ── what needs attention ─────────────────────────────────────────────
    def old_names(self) -> list[tuple[str, str]]:
        return old_names(self.file) if self.readable else []

    def stage_renames(self) -> None:
        for k, v in rename_changes(self.file).items():
            self.pending[k] = v

    def unknown_keys(self) -> list[str]:
        """Settings in the file that Alacritty 0.17 doesn't use (it warns, then ignores them)."""
        if not self.readable:
            return []
        out = []
        for key in _leaves(self.file.values()):
            if key in BY_KEY or key.split(".")[0] in RENAMED:
                continue
            if key.startswith(KNOWN_PREFIXES) or key in ("env", "terminal.shell"):
                continue
            out.append(key)
        return out

    def live_reload(self) -> bool:
        v = self.original("general.live_config_reload")
        return True if v is None else bool(v)


# ── fonts on this computer ───────────────────────────────────────────────

def monospace_families() -> list[str]:
    try:
        out = subprocess.run(["fc-list", ":spacing=mono", "family"], capture_output=True, text=True,
                             timeout=10).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    fams = {line.split(",")[0].strip() for line in out.splitlines() if line.strip()}
    return sorted(fams, key=str.lower)


def font_styles(family: str) -> list[str]:
    try:
        out = subprocess.run(["fc-list", f"{family}:spacing=mono", "style"], capture_output=True,
                             text=True, timeout=10).stdout
    except (OSError, subprocess.TimeoutExpired):
        return []
    styles = set()
    for line in out.splitlines():
        if "=" in line:
            styles.add(line.split("=", 1)[1].split(",")[0].strip())
    order = ["Regular", "Medium", "Light", "Thin", "ExtraLight", "SemiBold", "Bold", "ExtraBold",
             "Italic", "Bold Italic"]
    return sorted(styles, key=lambda s: (order.index(s) if s in order else len(order), s))


NOT_SHELLS = {"rbash", "git-shell", "nologin", "systemd-home-fallback-shell", "false", "true"}


def shells() -> list[str]:
    try:
        lines = Path("/etc/shells").read_text().splitlines()
    except OSError:
        return []
    seen, out = set(), []
    for l in lines:
        l = l.strip()
        if l.startswith("/") and Path(l).exists():
            name = Path(l).name
            # in /etc/shells for system reasons, not shells a person types into
            if name in NOT_SHELLS:
                continue
            if name not in seen:
                seen.add(name)
                out.append(l)
    return out
