"""Backups of alacritty.toml (v1.0.0).

Same folder, names and note files as 0.2.0, so older backups still show:
``alacritty_<date>_<time>_<n>.bak.toml`` with ``alacritty_<…>.note`` beside it.
New in 1.0: one backup per save (0.2.0 made one per shortcut change, which
could push all older backups out of the 20 kept), names that can't collide
within a second, and a restore that goes through the same safe write.
"""

from __future__ import annotations

import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .settings_file import CONFIG_PATH, SettingsFile, write_atomic

BACKUP_DIR = Path.home() / ".config" / "alacritty" / "backups"
MAX_BACKUPS = 20

# what the note says → why it was made, in plain words (0.2.0 notes included)
REASONS = {
    "pre-config-edit": "Before a save",
    "pre-font-edit": "Before a save",
    "pre-keybind-add": "Before a shortcut change",
    "pre-keybind-delete": "Before a shortcut change",
    "pre-keybind-update": "Before a shortcut change",
    "pre-restore": "Before restoring a backup",
    "pre-edit": "Before a save",
    "manual": "Made by you",
}


@dataclass
class Backup:
    path: Path
    made: datetime
    note: str

    @property
    def why(self) -> str:
        if self.note.startswith("pre-theme-"):
            return f"Before using a theme ({self.note[len('pre-theme-'):]})"
        return REASONS.get(self.note, self.note or "Before a save")

    @property
    def note_path(self) -> Path:
        return _note_path(self.path)


_STAMP = re.compile(r"alacritty_(\d{8})_(\d{6})_")


def made_at(p: Path) -> datetime | None:
    """When the backup was made: from its name. The file's own time is the
    settings file's last edit, because copying keeps it (0.2.0 showed that)."""
    m = _STAMP.match(p.name)
    if m:
        try:
            return datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S")
        except ValueError:
            pass
    try:
        return datetime.fromtimestamp(p.stat().st_mtime)
    except OSError:
        return None


def _note_path(p: Path) -> Path:
    return p.with_suffix("").with_suffix(".note")


def create(note: str, *, path: Path = CONFIG_PATH, backup_dir: Path | None = None) -> Path | None:
    """Copy the settings file into the backups folder. None if there is no file."""
    src = Path(os.path.realpath(path))
    if not src.exists():
        return None
    d = backup_dir or BACKUP_DIR
    d.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    dest = d / f"alacritty_{now:%Y%m%d_%H%M%S}_{now:%f}.bak.toml"
    n = 0
    while dest.exists():                       # two in the same microsecond
        n += 1
        dest = d / f"alacritty_{now:%Y%m%d_%H%M%S}_{now:%f}{n}.bak.toml"
    shutil.copy2(src, dest)
    _note_path(dest).write_text(note, encoding="utf-8")
    prune(d)
    return dest


def list_all(backup_dir: Path | None = None) -> list[Backup]:
    """Newest first."""
    d = backup_dir or BACKUP_DIR
    if not d.is_dir():
        return []
    out = []
    for p in d.glob("alacritty_*.bak.toml"):
        made = made_at(p)
        if made is None:
            continue
        try:
            note = _note_path(p).read_text(encoding="utf-8").strip()
        except OSError:
            note = ""
        out.append(Backup(p, made, note))
    return sorted(out, key=lambda b: (b.made, b.path.name), reverse=True)


def prune(backup_dir: Path | None = None) -> None:
    for b in list_all(backup_dir)[MAX_BACKUPS:]:
        delete(b)


def delete(b: Backup) -> None:
    b.path.unlink(missing_ok=True)
    b.note_path.unlink(missing_ok=True)


def restore(b: Backup, *, path: Path = CONFIG_PATH, backup_dir: Path | None = None) -> Path | None:
    """Put a backup back, after backing up what is there now. Returns that
    new backup. The backup's text is written exactly as it was saved."""
    text = b.path.read_text(encoding="utf-8")
    made = create("pre-restore", path=path, backup_dir=backup_dir)
    write_atomic(path, text)
    return made


def readable(b: Backup) -> bool:
    return SettingsFile.load(b.path).readable
