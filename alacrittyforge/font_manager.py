# ═══════════════════════════════════════════════════════════
#  AlacrittyForge — Font Manager
#  Reads and writes font settings in alacritty.toml
# ═══════════════════════════════════════════════════════════

from pathlib import Path
import subprocess

from .config_manager import (
    load_config, save_config, get_nested_value, set_nested_value
)
from .backup_manager import create_backup


# ── Font setting definitions ──
FONT_SETTINGS = [
    {
        "key":         "font.normal.family",
        "label":       "Normal Family",
        "description": "Font family for regular text (e.g. JetBrains Mono)",
        "type":        "string",
    },
    {
        "key":         "font.normal.style",
        "label":       "Normal Style",
        "description": "Style for normal text (e.g. Regular)",
        "type":        "string",
    },
    {
        "key":         "font.bold.family",
        "label":       "Bold Family",
        "description": "Font family for bold text (leave blank to inherit)",
        "type":        "string",
    },
    {
        "key":         "font.bold.style",
        "label":       "Bold Style",
        "description": "Style for bold text (e.g. Bold)",
        "type":        "string",
    },
    {
        "key":         "font.italic.family",
        "label":       "Italic Family",
        "description": "Font family for italic text (leave blank to inherit)",
        "type":        "string",
    },
    {
        "key":         "font.italic.style",
        "label":       "Italic Style",
        "description": "Style for italic text (e.g. Italic)",
        "type":        "string",
    },
    {
        "key":         "font.bold_italic.family",
        "label":       "Bold Italic Family",
        "description": "Font family for bold italic text",
        "type":        "string",
    },
    {
        "key":         "font.bold_italic.style",
        "label":       "Bold Italic Style",
        "description": "Style for bold italic text (e.g. Bold Italic)",
        "type":        "string",
    },
    {
        "key":         "font.size",
        "label":       "Size",
        "description": "Font size in points (e.g. 12.0)",
        "type":        "float",
    },
    {
        "key":         "font.offset.x",
        "label":       "Offset X",
        "description": "Extra horizontal spacing between characters in pixels",
        "type":        "int",
    },
    {
        "key":         "font.offset.y",
        "label":       "Offset Y",
        "description": "Extra vertical spacing between lines in pixels",
        "type":        "int",
    },
    {
        "key":         "font.glyph_offset.x",
        "label":       "Glyph Offset X",
        "description": "Horizontal glyph offset within cell",
        "type":        "int",
    },
    {
        "key":         "font.glyph_offset.y",
        "label":       "Glyph Offset Y",
        "description": "Vertical glyph offset within cell",
        "type":        "int",
    },
    {
        "key":         "font.builtin_box_drawing",
        "label":       "Built-in Box Drawing",
        "description": "Use built-in box drawing characters (true/false)",
        "type":        "bool",
    },
]


def get_font_settings() -> list[dict]:
    """
    Return font settings with current values from alacritty.toml.
    Each dict: { key, label, description, type, value }
    """
    data = load_config()
    result = []
    for setting in FONT_SETTINGS:
        value = get_nested_value(data, setting["key"])
        result.append({
            **setting,
            "value": value if value is not None else "",
        })
    return result


def apply_font_setting(key: str, raw_value: str) -> tuple[bool, str]:
    """
    Validate and apply a single font setting.
    Creates a backup first.
    Returns (success, message).
    """
    # Find the setting definition
    definition = next((s for s in FONT_SETTINGS if s["key"] == key), None)
    if not definition:
        return False, f"Unknown font setting: {key}"

    # Coerce value to correct type
    ok, coerced, error = _coerce(raw_value.strip(), definition["type"])
    if not ok:
        return False, error

    create_backup(note=f"pre-font-edit")

    data = load_config()
    set_nested_value(data, key, coerced)

    if save_config(data):
        return True, f"{definition['label']} set to {coerced!r}"
    return False, "Failed to write config file."


def apply_font_settings_bulk(changes: dict[str, str]) -> tuple[bool, str]:
    """
    Apply multiple font settings at once.
    changes: { key: raw_value }
    Creates a single backup before writing.
    Returns (success, message).
    """
    create_backup(note="pre-font-bulk-edit")
    data = load_config()

    errors = []
    for key, raw_value in changes.items():
        definition = next((s for s in FONT_SETTINGS if s["key"] == key), None)
        if not definition:
            errors.append(f"Unknown key: {key}")
            continue
        ok, coerced, error = _coerce(raw_value.strip(), definition["type"])
        if not ok:
            errors.append(f"{key}: {error}")
            continue
        set_nested_value(data, key, coerced)

    if errors:
        return False, "Errors: " + " | ".join(errors)

    if save_config(data):
        return True, f"Applied {len(changes)} font setting(s) successfully."
    return False, "Failed to write config file."


def list_system_fonts() -> list[str]:
    """
    Return a list of font family names available on the system.
    Uses fc-list if available, otherwise returns empty list.
    """
    try:
        # v0.2.0 (Javier's ruling): monospace families only — the full
        # font list is huge and terminals only render mono well anyway.
        result = subprocess.run(
            ["fc-list", ":spacing=mono", "--format=%{family}\\n"],
            capture_output=True, text=True, timeout=5
        )
        fonts = set()
        for line in result.stdout.splitlines():
            for part in line.split(","):
                name = part.strip()
                if name:
                    fonts.add(name)
        return sorted(fonts)
    except Exception:
        return []


def _coerce(raw: str, typ: str) -> tuple[bool, any, str]:
    """Coerce a raw string to the given type. Returns (ok, value, error)."""
    if typ == "bool":
        if raw.lower() in ("true", "yes", "1"):
            return True, True, ""
        elif raw.lower() in ("false", "no", "0"):
            return True, False, ""
        return False, None, "Expected true or false"

    if typ == "int":
        if raw == "":
            return True, None, ""
        try:
            return True, int(raw), ""
        except ValueError:
            return False, None, "Expected a whole number"

    if typ == "float":
        if raw == "":
            return True, None, ""
        try:
            val = float(raw)
            if val <= 0:
                return False, None, "Must be greater than 0"
            return True, val, ""
        except ValueError:
            return False, None, "Expected a decimal number (e.g. 12.0)"

    # string
    if raw == "":
        return True, None, ""
    return True, raw, ""