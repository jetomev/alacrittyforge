"""alacritty.toml, read and saved safely (v1.0.0).

0.2.0 rewrote the whole file from a parsed copy, so comments and layout were
lost, a value of None made the save fail, and a file it could not read was
treated as empty, so a save would have replaced it with only the changed
settings. This module fixes all three:

- the file is edited as a document (tomlkit), so everything you wrote by hand
  stays, and only the settings you change are touched;
- a change is a dotted key → value, or ``REMOVE`` to take the setting out
  (Alacritty then uses its own default); nothing else is ever written;
- a file that cannot be read is never saved over;
- a save makes one backup, writes the new text next to the old file, and swaps
  it in only when it is complete (``os.replace``), so a crash leaves either the
  old file or the new one, never half of one. A file that is a link (dotfiles)
  stays a link: the file it points to is the one written.
"""

from __future__ import annotations

import os
import tempfile
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import tomlkit
from tomlkit.items import AoT, InlineTable, String, StringType, Table, Trivia

CONFIG_PATH = Path.home() / ".config" / "alacritty" / "alacritty.toml"


class _Remove:
    def __repr__(self) -> str:
        return "REMOVE"


REMOVE = _Remove()      # a change that takes the setting out of the file
MISSING = object()      # get(): the file doesn't set it


class Unreadable(Exception):
    """The file is not valid TOML; it must not be saved over."""


@dataclass
class SettingsFile:
    path: Path
    text: str = ""
    exists: bool = False
    error: str | None = None            # why it could not be read
    _doc: Any = field(default=None, repr=False)

    # ── reading ──────────────────────────────────────────────────────────
    @classmethod
    def load(cls, path: Path = CONFIG_PATH) -> "SettingsFile":
        path = Path(path)
        if not path.exists():
            return cls(path=path, text="", exists=False, _doc=tomlkit.document())
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as e:
            return cls(path=path, exists=True, error=f"can't be opened: {e.strerror}")
        try:
            doc = tomlkit.parse(text)
            tomllib.loads(text)          # the same rules Alacritty's parser keeps
        except Exception as e:           # tomlkit and tomllib raise their own types
            return cls(path=path, text=text, exists=True, error=_plain_error(e))
        return cls(path=path, text=text, exists=True, _doc=doc)

    @property
    def readable(self) -> bool:
        return self.error is None

    def values(self) -> dict:
        """The whole file as plain Python values."""
        if not self.readable:
            return {}
        return self._doc.unwrap()

    def get(self, key: str, default: Any = MISSING) -> Any:
        node: Any = self.values()
        for part in key.split("."):
            if not isinstance(node, dict) or part not in node:
                return default
            node = node[part]
        return node

    # ── writing ──────────────────────────────────────────────────────────
    def render(self, changes: dict[str, Any]) -> str:
        """The file's text with ``changes`` applied, everything else as it was."""
        if not self.readable:
            raise Unreadable(self.error)
        doc = tomlkit.parse(self.text)
        for key, value in changes.items():
            _apply(doc, key.split("."), value)
        out = tomlkit.dumps(doc)
        tomllib.loads(out)               # never write a file Alacritty can't read
        return out


def _plain_error(e: Exception) -> str:
    msg = str(e).strip().splitlines()[0] if str(e).strip() else type(e).__name__
    return msg[0].upper() + msg[1:] if msg else "not valid TOML"


_SHORT = {"\\": "\\\\", '"': '\\"', "\b": "\\b", "\t": "\\t", "\n": "\\n", "\f": "\\f", "\r": "\\r"}


def _string(value: str) -> Any:
    """A TOML string every reader accepts: tomlkit 0.15 writes Esc as \\e,
    which TOML 1.0 readers (Python's, and possibly Alacritty's) reject."""
    out = []
    for c in value:
        if c in _SHORT:
            out.append(_SHORT[c])
        elif ord(c) < 0x20 or ord(c) == 0x7F:
            out.append(f"\\u{ord(c):04x}")
        else:
            out.append(c)
    return String(StringType.SLB, value, "".join(out), Trivia())


def _to_item(value: Any) -> Any:
    """Plain values into tomlkit items; lists of tables stay one per line."""
    if isinstance(value, str):
        return _string(value)
    if isinstance(value, dict):
        t = tomlkit.inline_table()
        for k, v in value.items():
            t[k] = _to_item(v)
        return t
    if isinstance(value, list):
        arr = tomlkit.array()
        for v in value:
            arr.append(_to_item(v))
        if value and all(isinstance(v, dict) for v in value):
            arr.multiline(True)
        return arr
    return value


def _apply(doc: Any, parts: list[str], value: Any) -> None:
    node = doc
    trail = []
    for part in parts[:-1]:
        trail.append((node, part))
        if part not in node:
            if value is REMOVE:
                return                    # nothing to remove
            # a table that only holds other tables gets no header of its own
            node[part] = tomlkit.table()   # shows no header while it only holds tables
        node = node[part]
        if not isinstance(node, (Table, InlineTable, dict)) or isinstance(node, AoT):
            raise ValueError(f"{'.'.join(parts)}: {part} is not a section")
    last = parts[-1]
    if value is REMOVE:
        if last in node:
            del node[last]
        # take out sections left empty by the removal, innermost first
        for parent, part in reversed(trail):
            child = parent[part]
            if isinstance(child, (Table, InlineTable)) and len(child) == 0:
                del parent[part]
            else:
                break
        return
    node[last] = _to_item(value)


# ── saving ───────────────────────────────────────────────────────────────

@dataclass
class SaveResult:
    path: Path
    backup: Path | None


def write_atomic(path: Path, text: str) -> Path:
    """Write ``text`` to ``path`` (following a link) in one step. Returns the
    real path written."""
    target = Path(os.path.realpath(path))
    target.parent.mkdir(parents=True, exist_ok=True)
    mode = target.stat().st_mode & 0o7777 if target.exists() else 0o644
    fd, tmp = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".new", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, mode)
        os.replace(tmp, target)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    try:                                   # make the rename itself durable
        dfd = os.open(target.parent, os.O_DIRECTORY)
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    except OSError:
        pass
    return target


def save(changes: dict[str, Any], *, path: Path = CONFIG_PATH, note: str = "Before a save",
         backup_dir: Path | None = None) -> SaveResult:
    """Apply ``changes`` to the file as it is on disk now, with one backup first.

    The file is read again here, so a change made elsewhere since grubForge-style
    screens loaded it is kept: only the keys in ``changes`` are touched."""
    from . import backups
    current = SettingsFile.load(path)
    if not current.readable:
        raise Unreadable(current.error)
    text = current.render(changes)
    backup = backups.create(note, path=path, backup_dir=backup_dir) if current.exists else None
    written = write_atomic(path, text)
    return SaveResult(path=written, backup=backup)


# ── settings Alacritty renamed ───────────────────────────────────────────
# Old names still load but warn on every start; `alacritty migrate` moves them.
RENAMED = {
    "import": "general.import",
    "working_directory": "general.working_directory",
    "live_config_reload": "general.live_config_reload",
    "ipc_socket": "general.ipc_socket",
    "shell": "terminal.shell",
    "key_bindings": "keyboard.bindings",
    "mouse_bindings": "mouse.bindings",
    "draw_bold_text_with_bright_colors": "colors.draw_bold_text_with_bright_colors",
}


def old_names(sf: SettingsFile) -> list[tuple[str, str]]:
    """(old, new) for each renamed setting the file still uses."""
    return [(old, new) for old, new in RENAMED.items() if sf.get(old) is not MISSING]


def rename_changes(sf: SettingsFile) -> dict[str, Any]:
    """The changes that move every old name to its new one. Where both are set,
    the new one wins (it is what Alacritty uses) and the old one is dropped."""
    out: dict[str, Any] = {}
    for old, new in old_names(sf):
        if sf.get(new) is MISSING:
            out[new] = sf.get(old)
        out[old] = REMOVE
    return out
