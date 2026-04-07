# ═══════════════════════════════════════════════════════════
#  AlacrittyForge — Backup Manager
#  Handles timestamped backups of alacritty.toml
#  Backups stored in ~/.config/alacritty/backups/
# ═══════════════════════════════════════════════════════════

import os
import shutil
from datetime import datetime
from pathlib import Path


BACKUP_DIR = Path.home() / ".config" / "alacritty" / "backups"
CONFIG_PATH = Path.home() / ".config" / "alacritty" / "alacritty.toml"
MAX_BACKUPS = 20


def ensure_backup_dir() -> None:
    """Create backup directory if it doesn't exist."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def create_backup(note: str = "pre-edit") -> Path | None:
    """
    Create a timestamped backup of alacritty.toml.
    Returns the path to the new backup, or None if source doesn't exist.
    """
    ensure_backup_dir()

    if not CONFIG_PATH.exists():
        return None

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_suffix = str(os.getpid())
    filename = f"alacritty_{timestamp}_{random_suffix}.bak.toml"
    dest = BACKUP_DIR / filename

    shutil.copy2(CONFIG_PATH, dest)

    # Write a note file alongside the backup
    note_file = BACKUP_DIR / f"alacritty_{timestamp}_{random_suffix}.note"
    note_file.write_text(note)

    # Prune old backups if over the limit
    _prune_backups()

    return dest


def list_backups() -> list[dict]:
    """
    Return a list of backup dicts, newest first.
    Each dict: { path, filename, date_str, size_kb, note }
    """
    ensure_backup_dir()

    backups = sorted(
        BACKUP_DIR.glob("*.bak.toml"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    result = []
    for i, bak in enumerate(backups):
        size_kb = round(bak.stat().st_size / 1024, 1)
        mtime = datetime.fromtimestamp(bak.stat().st_mtime)
        date_str = mtime.strftime("%Y-%m-%d  %H:%M:%S")

        # Read note if it exists
        note_file = bak.with_suffix("").with_suffix(".note")
        note = note_file.read_text().strip() if note_file.exists() else ""

        result.append({
            "index":    i + 1,
            "path":     bak,
            "filename": bak.name,
            "date_str": date_str,
            "size_kb":  size_kb,
            "note":     note,
        })

    return result


def restore_backup(backup_path: Path) -> bool:
    """
    Restore a backup over the current alacritty.toml.
    Creates a backup of the current config first.
    Returns True on success.
    """
    if not backup_path.exists():
        return False

    # Back up current config before restoring
    create_backup(note="pre-restore")

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(backup_path, CONFIG_PATH)
    return True


def delete_backup(backup_path: Path) -> bool:
    """
    Delete a backup file (and its note file if present).
    Returns True on success.
    """
    if not backup_path.exists():
        return False

    backup_path.unlink()

    note_file = backup_path.with_suffix("").with_suffix(".note")
    if note_file.exists():
        note_file.unlink()

    return True


def get_backup_count() -> int:
    """Return the number of existing backups."""
    ensure_backup_dir()
    return len(list(BACKUP_DIR.glob("*.bak.toml")))


def _prune_backups() -> None:
    """Delete oldest backups if count exceeds MAX_BACKUPS."""
    backups = sorted(
        BACKUP_DIR.glob("*.bak.toml"),
        key=lambda p: p.stat().st_mtime
    )
    while len(backups) > MAX_BACKUPS:
        oldest = backups.pop(0)
        delete_backup(oldest)