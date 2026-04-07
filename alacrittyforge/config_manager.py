# ═══════════════════════════════════════════════════════════
#  AlacrittyForge — Config Manager
#  Reads, parses, validates, and writes alacritty.toml
# ═══════════════════════════════════════════════════════════

from pathlib import Path
from typing import Any
import tomllib
import tomli_w

CONFIG_PATH = Path.home() / ".config" / "alacritty" / "alacritty.toml"

# ── Human-readable descriptions for every known setting ──
SETTING_DESCRIPTIONS: dict[str, str] = {
    # Window
    "window.opacity":               "Background opacity (0.0 = fully transparent, 1.0 = fully opaque)",
    "window.blur":                  "Enable background blur when opacity < 1.0 (true/false)",
    "window.decorations":           "Window decorations: full, none, transparent, buttonless",
    "window.startup_mode":          "Initial window state: Windowed, Maximized, Fullscreen, SimpleFullscreen",
    "window.title":                 "Default window title",
    "window.dynamic_title":         "Update window title to currently running process (true/false)",
    "window.padding.x":             "Horizontal inner padding in pixels",
    "window.padding.y":             "Vertical inner padding in pixels",
    "window.dynamic_padding":       "Spread padding evenly to fill the window (true/false)",
    "window.resize_increments":     "Resize window by character cell increments (true/false)",
    # Scrolling
    "scrolling.history":            "Number of lines saved in scroll history (0 = disabled, max 100000)",
    "scrolling.multiplier":         "Lines scrolled per mouse wheel tick",
    # Font
    "font.normal.family":           "Font family for normal text (e.g. JetBrains Mono)",
    "font.normal.style":            "Font style for normal text (e.g. Regular)",
    "font.bold.family":             "Font family for bold text",
    "font.bold.style":              "Font style for bold text (e.g. Bold)",
    "font.italic.family":           "Font family for italic text",
    "font.italic.style":            "Font style for italic text (e.g. Italic)",
    "font.bold_italic.family":      "Font family for bold italic text",
    "font.bold_italic.style":       "Font style for bold italic text",
    "font.size":                    "Font size in points",
    "font.offset.x":                "Horizontal spacing between characters (pixels)",
    "font.offset.y":                "Vertical spacing between lines (pixels)",
    "font.glyph_offset.x":         "Horizontal glyph offset within cell",
    "font.glyph_offset.y":         "Vertical glyph offset within cell",
    "font.builtin_box_drawing":     "Use built-in box drawing characters (true/false)",
    # Bell
    "bell.animation":               "Bell animation: Ease, EaseOut, EaseOutSine, EaseOutQuad, etc.",
    "bell.duration":                "Bell animation duration in milliseconds",
    "bell.color":                   "Bell flash color in hex (#rrggbb)",
    "bell.command":                 "Command to run when bell rings (program + args)",
    # Selection
    "selection.semantic_escape_chars": "Characters treated as word separators in selection",
    "selection.save_to_clipboard":  "Automatically copy selection to clipboard (true/false)",
    # Cursor
    "cursor.style.shape":           "Cursor shape: Block, Underline, Beam",
    "cursor.style.blinking":        "Cursor blinking: Never, Off, On, Always",
    "cursor.blink_interval":        "Cursor blink interval in milliseconds",
    "cursor.blink_timeout":         "Stop blinking after N seconds of inactivity (0 = never)",
    "cursor.unfocused_hollow":      "Show hollow cursor when window is unfocused (true/false)",
    "cursor.thickness":             "Cursor thickness as fraction of cell width (0.0–1.0)",
    # Terminal
    "terminal.osc52":               "OSC 52 clipboard access: Disabled, OnlyCopy, OnlyPaste, CopyPaste",
    # Mouse
    "mouse.hide_when_typing":       "Hide mouse cursor while typing (true/false)",
    "mouse.bindings":               "Custom mouse button bindings",
    # Hints
    "hints.enabled":                "URL/hint detection configuration",
    # General
    "general.import":               "List of additional config files to import",
    "general.shell":                "Shell program and arguments to launch",
    "general.working_directory":    "Starting working directory (None = inherit from parent)",
    "general.live_config_reload":   "Reload config automatically on file change (true/false)",
    "general.ipc_socket":           "Enable IPC socket for alacritty msg (true/false)",
}


def config_exists() -> bool:
    """Return True if alacritty.toml exists."""
    return CONFIG_PATH.exists()


def load_config() -> dict:
    """
    Load and parse alacritty.toml.
    Returns empty dict if file doesn't exist or can't be parsed.
    """
    if not CONFIG_PATH.exists():
        return {}
    try:
        with open(CONFIG_PATH, "rb") as f:
            return tomllib.load(f)
    except Exception:
        return {}


def save_config(data: dict) -> bool:
    """
    Write a dict back to alacritty.toml using tomli_w.
    Returns True on success.
    """
    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "wb") as f:
            tomli_w.dump(data, f)
        return True
    except Exception:
        return False


def get_flat_settings(data: dict, prefix: str = "") -> list[dict]:
    """
    Flatten nested TOML dict into a list of settings dicts.
    Each dict: { key, value, description, editable }
    """
    result = []
    for k, v in data.items():
        full_key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            result.extend(get_flat_settings(v, prefix=full_key))
        else:
            result.append({
                "key":         full_key,
                "value":       v,
                "description": SETTING_DESCRIPTIONS.get(full_key, ""),
                "editable":    not isinstance(v, (list, dict)),
            })
    return result


def set_nested_value(data: dict, key_path: str, value: Any) -> dict:
    """
    Set a value in a nested dict using a dot-separated key path.
    e.g. set_nested_value(data, "font.size", 13.0)
    """
    keys = key_path.split(".")
    d = data
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    d[keys[-1]] = value
    return data


def get_nested_value(data: dict, key_path: str) -> Any:
    """
    Get a value from a nested dict using a dot-separated key path.
    Returns None if path doesn't exist.
    """
    keys = key_path.split(".")
    d = data
    for k in keys:
        if not isinstance(d, dict) or k not in d:
            return None
        d = d[k]
    return d


def validate_value(key: str, raw: str) -> tuple[bool, Any, str]:
    """
    Validate and coerce a raw string value for a given key.
    Returns (is_valid, coerced_value, error_message).
    """
    raw = raw.strip()

    # Boolean fields
    bool_keys = {
        "window.blur", "window.dynamic_title", "window.dynamic_padding",
        "window.resize_increments", "font.builtin_box_drawing",
        "selection.save_to_clipboard", "cursor.unfocused_hollow",
        "mouse.hide_when_typing", "general.live_config_reload",
        "general.ipc_socket",
    }
    if key in bool_keys:
        if raw.lower() in ("true", "yes", "1"):
            return True, True, ""
        elif raw.lower() in ("false", "no", "0"):
            return True, False, ""
        else:
            return False, None, "Expected true or false"

    # Integer fields
    int_keys = {
        "scrolling.history", "scrolling.multiplier",
        "window.padding.x", "window.padding.y",
        "font.offset.x", "font.offset.y",
        "font.glyph_offset.x", "font.glyph_offset.y",
        "bell.duration", "cursor.blink_interval", "cursor.blink_timeout",
    }
    if key in int_keys:
        try:
            return True, int(raw), ""
        except ValueError:
            return False, None, "Expected a whole number"

    # Float fields
    float_keys = {
        "window.opacity", "font.size", "cursor.thickness",
    }
    if key in float_keys:
        try:
            val = float(raw)
            if key == "window.opacity" and not (0.0 <= val <= 1.0):
                return False, None, "Opacity must be between 0.0 and 1.0"
            if key == "cursor.thickness" and not (0.0 <= val <= 1.0):
                return False, None, "Thickness must be between 0.0 and 1.0"
            if key == "font.size" and val <= 0:
                return False, None, "Font size must be greater than 0"
            return True, val, ""
        except ValueError:
            return False, None, "Expected a decimal number (e.g. 12.0)"

    # Hex color fields
    color_keys = {"bell.color"}
    if key in color_keys:
        if raw.startswith("#") and len(raw) == 7:
            return True, raw, ""
        return False, None, "Expected hex color like #ff0000"

    # Everything else is a string
    return True, raw, ""


def get_raw_text() -> str:
    """Return the raw text content of alacritty.toml."""
    if not CONFIG_PATH.exists():
        return "# alacritty.toml not found"
    return CONFIG_PATH.read_text()


def get_active_theme(data: dict) -> str:
    """Return the currently imported theme filename, if any."""
    imports = get_nested_value(data, "general.import")
    if isinstance(imports, list) and imports:
        return Path(imports[0]).stem
    return "none"


def get_font_name(data: dict) -> str:
    """Return the current font family name."""
    return get_nested_value(data, "font.normal.family") or "default"


def get_font_size(data: dict) -> str:
    """Return the current font size as a string."""
    size = get_nested_value(data, "font.size")
    return str(size) if size is not None else "default"


def get_opacity(data: dict) -> str:
    """Return the current window opacity as a string."""
    opacity = get_nested_value(data, "window.opacity")
    return str(opacity) if opacity is not None else "1.0"