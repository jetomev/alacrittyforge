# ═══════════════════════════════════════════════════════════
#  AlacrittyForge — Field Options Knowledge Base
#
#  v0.2.0 Config redesign (Javier's ruling): values are edited in-place
#  in the table, and every enumerable key gets a DROPDOWN so typos are
#  impossible. This module knows which keys are enumerable and what
#  their valid options are. Keys not listed here (and not booleans)
#  fall back to the free-text editor, still guarded by validate_value().
# ═══════════════════════════════════════════════════════════

from __future__ import annotations

from pathlib import Path

# Enumerable keys → their valid options (Alacritty 0.13+ documented values).
_ENUM_OPTIONS: dict[str, list[str]] = {
    "env.TERM": [
        "alacritty", "xterm-256color", "xterm", "screen-256color",
        "tmux-256color", "linux",
    ],
    "window.decorations": ["Full", "None", "Transparent", "Buttonless"],
    "window.startup_mode": ["Windowed", "Maximized", "Fullscreen"],
    "cursor.style.shape": ["Block", "Underline", "Beam"],
    "cursor.style.blinking": ["Never", "Off", "On", "Always"],
    "font.normal.style": ["Regular", "Bold", "Italic", "Bold Italic"],
    "font.bold.style": ["Bold", "Regular", "Bold Italic"],
    "font.italic.style": ["Italic", "Regular", "Bold Italic"],
    "font.bold_italic.style": ["Bold Italic", "Regular"],
}

# Boolean keys mirror config_manager.validate_value's bool_keys set.
_BOOL_KEYS = {
    "window.blur", "window.dynamic_title", "window.dynamic_padding",
    "window.resize_increments", "font.builtin_box_drawing",
    "selection.save_to_clipboard", "cursor.unfocused_hollow",
    "mouse.hide_when_typing", "general.live_config_reload",
    "general.ipc_socket",
}


def _shells() -> list[str]:
    """Installed login shells from /etc/shells — the no-typos source."""
    try:
        lines = Path("/etc/shells").read_text().splitlines()
        return [l.strip() for l in lines
                if l.strip() and not l.strip().startswith("#")]
    except Exception:
        return []


def get_options(key: str, current=None) -> list[str] | None:
    """Return dropdown options for ``key``, or None for free-text keys.

    The current value is always included (first) so an unusual existing
    setting never becomes unreachable through its own editor.
    """
    opts: list[str] | None = None
    if key in _BOOL_KEYS:
        opts = ["true", "false"]
    elif key in _ENUM_OPTIONS:
        opts = list(_ENUM_OPTIONS[key])
    elif key == "terminal.shell.program" or key == "shell.program":
        shells = _shells()
        opts = shells if shells else None
    elif key.startswith("font.") and key.endswith(".family"):
        # Monospace families from the system (Javier's ruling: mono only).
        from .font_manager import list_system_fonts
        fonts = list_system_fonts()
        opts = fonts if fonts else None

    if opts is None:
        return None
    cur = str(current) if current is not None else ""
    if cur and cur not in opts and cur.lower() not in opts:
        opts.insert(0, cur)
    return opts
