# ═══════════════════════════════════════════════════════════
#  AlacrittyForge — Keybind Manager
#  Reads, displays, and writes keyboard bindings
#  from the [[keyboard.bindings]] section of alacritty.toml
# ═══════════════════════════════════════════════════════════

from .config_manager import load_config, save_config
from .backup_manager import create_backup


# ── Default Alacritty bindings shown for reference ──
DEFAULT_BINDINGS: list[dict] = [
    {"key": "Paste",        "mods": "",             "action": "Paste"},
    {"key": "Copy",         "mods": "",             "action": "Copy"},
    {"key": "L",            "mods": "Control",      "action": "ClearLogNotice"},
    {"key": "L",            "mods": "Control",      "chars":  "\\x0c"},
    {"key": "PageUp",       "mods": "Shift",        "action": "ScrollPageUp"},
    {"key": "PageDown",     "mods": "Shift",        "action": "ScrollPageDown"},
    {"key": "Home",         "mods": "Shift",        "action": "ScrollToTop"},
    {"key": "End",          "mods": "Shift",        "action": "ScrollToBottom"},
    {"key": "Return",       "mods": "Alt",          "action": "ToggleFullscreen"},
    {"key": "N",            "mods": "Control|Shift","action": "SpawnNewInstance"},
    {"key": "Plus",         "mods": "Control",      "action": "IncreaseFontSize"},
    {"key": "Minus",        "mods": "Control",      "action": "DecreaseFontSize"},
    {"key": "Key0",         "mods": "Control",      "action": "ResetFontSize"},
    {"key": "V",            "mods": "Control|Shift","action": "Paste"},
    {"key": "C",            "mods": "Control|Shift","action": "Copy"},
    {"key": "F",            "mods": "Control|Shift","action": "SearchForward"},
    {"key": "B",            "mods": "Control|Shift","action": "SearchBackward"},
]

# ── Available actions for the dropdown ──
AVAILABLE_ACTIONS: list[str] = [
    "Paste",
    "Copy",
    "ClearLogNotice",
    "ScrollPageUp",
    "ScrollPageDown",
    "ScrollToTop",
    "ScrollToBottom",
    "ScrollLineUp",
    "ScrollLineDown",
    "ScrollHalfPageUp",
    "ScrollHalfPageDown",
    "ToggleFullscreen",
    "SpawnNewInstance",
    "IncreaseFontSize",
    "DecreaseFontSize",
    "ResetFontSize",
    "SearchForward",
    "SearchBackward",
    "ClearSelection",
    "ReceiveChar",
    "None",
]

# ── Available modifier keys ──
AVAILABLE_MODS: list[str] = [
    "",
    "Control",
    "Shift",
    "Alt",
    "Super",
    "Control|Shift",
    "Control|Alt",
    "Control|Super",
    "Alt|Shift",
    "Control|Alt|Shift",
]


def get_user_bindings() -> list[dict]:
    """
    Return the [[keyboard.bindings]] list from alacritty.toml.
    Each entry: { key, mods, action } or { key, mods, chars }
    Returns empty list if none defined.
    """
    data = load_config()
    keyboard = data.get("keyboard", {})
    bindings = keyboard.get("bindings", [])
    return bindings if isinstance(bindings, list) else []


def get_all_bindings() -> list[dict]:
    """
    Return combined list: user bindings first, then defaults.
    Each entry gets a 'source' field: 'user' or 'default'.
    """
    user = [dict(b, source="user") for b in get_user_bindings()]
    defaults = [dict(b, source="default") for b in DEFAULT_BINDINGS]
    return user + defaults


def add_binding(key: str, mods: str, action: str = "",
                chars: str = "") -> tuple[bool, str]:
    """
    Add a new keybinding to [[keyboard.bindings]].
    Creates a backup first.
    Returns (success, message).
    """
    if not key.strip():
        return False, "Key cannot be empty."

    if not action.strip() and not chars.strip():
        return False, "Must specify either an action or a chars sequence."

    create_backup(note="pre-keybind-add")
    data = load_config()

    entry: dict = {"key": key.strip()}
    if mods.strip():
        entry["mods"] = mods.strip()
    if action.strip():
        entry["action"] = action.strip()
    elif chars.strip():
        entry["chars"] = chars.strip()

    keyboard = data.setdefault("keyboard", {})
    bindings = keyboard.setdefault("bindings", [])
    bindings.append(entry)

    if save_config(data):
        return True, f"Binding added: {mods} + {key} → {action or chars}"
    return False, "Failed to write config file."


def delete_binding(index: int) -> tuple[bool, str]:
    """
    Delete a user binding by its index in the user bindings list.
    Creates a backup first.
    Returns (success, message).
    """
    create_backup(note="pre-keybind-delete")
    data = load_config()

    keyboard = data.get("keyboard", {})
    bindings = keyboard.get("bindings", [])

    if not isinstance(bindings, list) or index >= len(bindings):
        return False, "Binding index out of range."

    removed = bindings.pop(index)
    data.setdefault("keyboard", {})["bindings"] = bindings

    if save_config(data):
        return True, f"Binding removed: {removed.get('key', '?')}"
    return False, "Failed to write config file."


def update_binding(index: int, key: str, mods: str,
                   action: str = "", chars: str = "") -> tuple[bool, str]:
    """
    Update an existing user binding by index.
    Creates a backup first.
    Returns (success, message).
    """
    if not key.strip():
        return False, "Key cannot be empty."
    if not action.strip() and not chars.strip():
        return False, "Must specify either an action or a chars sequence."

    create_backup(note="pre-keybind-update")
    data = load_config()

    keyboard = data.get("keyboard", {})
    bindings = keyboard.get("bindings", [])

    if not isinstance(bindings, list) or index >= len(bindings):
        return False, "Binding index out of range."

    entry: dict = {"key": key.strip()}
    if mods.strip():
        entry["mods"] = mods.strip()
    if action.strip():
        entry["action"] = action.strip()
    elif chars.strip():
        entry["chars"] = chars.strip()

    bindings[index] = entry
    data.setdefault("keyboard", {})["bindings"] = bindings

    if save_config(data):
        return True, f"Binding updated: {mods} + {key} → {action or chars}"
    return False, "Failed to write config file."


def format_binding_display(binding: dict) -> tuple[str, str, str]:
    """
    Return (key, mods, action_or_chars) strings for display.
    """
    key    = binding.get("key", "")
    mods   = binding.get("mods", "")
    action = binding.get("action", binding.get("chars", ""))
    return key, mods, action