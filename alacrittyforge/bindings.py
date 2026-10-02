"""Keyboard shortcuts, in plain words (v1.0.0).

A shortcut in alacritty.toml is a table in ``keyboard.bindings``: the key,
the modifiers (``"Control|Shift"``), maybe a mode, and what it does: an
``action``, ``chars`` (text typed into the terminal) or a ``command`` (a
program). Every field a shortcut has is kept when it is changed (0.2.0
rebuilt them from four fields and lost ``mode`` and ``command``).

Alacritty's own shortcuts can't be edited, only turned off: a shortcut of
yours on the same keys with the action ``ReceiveChar`` (the key types as
normal) replaces it.
"""

from __future__ import annotations

from typing import Any

from .default_bindings import DEFAULTS

MODS = [("Control", "Ctrl"), ("Shift", "Shift"), ("Alt", "Alt"), ("Super", "Super")]
MOD_WORD = dict(MODS) | {"Command": "Super", "Option": "Alt"}

MODES = [("", "Always"), ("Vi", "Only in vi mode"), ("Search", "Only while searching"),
         ("~Vi", "Except in vi mode")]

# what each action does, said plainly; grouped for the list that picks one
ACTIONS: list[tuple[str, str, str]] = [
    # (action, words, group)
    ("Paste", "Paste", "Text"),
    ("Copy", "Copy", "Text"),
    ("PasteSelection", "Paste what is selected (middle-click paste)", "Text"),
    ("CopySelection", "Copy into the middle-click selection", "Text"),
    ("ClearSelection", "Clear the selection", "Text"),
    ("IncreaseFontSize", "Make the text bigger", "Text"),
    ("DecreaseFontSize", "Make the text smaller", "Text"),
    ("ResetFontSize", "Text size back to normal", "Text"),
    ("ScrollPageUp", "Scroll up a page", "Scrolling"),
    ("ScrollPageDown", "Scroll down a page", "Scrolling"),
    ("ScrollHalfPageUp", "Scroll up half a page", "Scrolling"),
    ("ScrollHalfPageDown", "Scroll down half a page", "Scrolling"),
    ("ScrollLineUp", "Scroll up a line", "Scrolling"),
    ("ScrollLineDown", "Scroll down a line", "Scrolling"),
    ("ScrollToTop", "Scroll to the top", "Scrolling"),
    ("ScrollToBottom", "Scroll to the bottom", "Scrolling"),
    ("ClearHistory", "Forget the lines kept to scroll back", "Scrolling"),
    ("CreateNewWindow", "Open a new window", "Windows"),
    ("SpawnNewInstance", "Open a new Alacritty (separate program)", "Windows"),
    ("ToggleFullscreen", "Full screen on or off", "Windows"),
    ("ToggleMaximized", "Maximized on or off", "Windows"),
    ("Minimize", "Minimize the window", "Windows"),
    ("Hide", "Hide the window", "Windows"),
    ("Quit", "Close Alacritty", "Windows"),
    ("ClearLogNotice", "Clear the message bar", "Windows"),
    ("SearchForward", "Search forward", "Search"),
    ("SearchBackward", "Search backward", "Search"),
    ("ToggleViMode", "Vi mode on or off", "Vi mode"),
    ("ReceiveChar", "Types the key as normal (shortcut off)", "Special"),
    ("None", "Nothing", "Special"),
]
# vi-mode and search-mode actions: named, not explained one by one
VI_ACTIONS = ["Up", "Down", "Left", "Right", "First", "Last", "FirstOccupied", "High", "Middle", "Low",
              "SemanticLeft", "SemanticRight", "SemanticLeftEnd", "SemanticRightEnd", "WordLeft", "WordRight",
              "WordLeftEnd", "WordRightEnd", "Bracket", "ParagraphUp", "ParagraphDown",
              "ToggleNormalSelection", "ToggleLineSelection", "ToggleBlockSelection", "ToggleSemanticSelection",
              "SearchNext", "SearchPrevious", "SearchStart", "SearchEnd", "Open", "CenterAroundViCursor",
              "InlineSearchForward", "InlineSearchBackward", "InlineSearchForwardShort",
              "InlineSearchBackwardShort", "InlineSearchNext", "InlineSearchPrevious",
              "SemanticSearchForward", "SemanticSearchBackward"]
SEARCH_ACTIONS = ["SearchFocusNext", "SearchFocusPrevious", "SearchConfirm", "SearchCancel", "SearchClear",
                  "SearchDeleteWord", "SearchHistoryPrevious", "SearchHistoryNext"]
ACTION_WORDS = {a: w for a, w, _g in ACTIONS}
for _a in VI_ACTIONS:
    ACTION_WORDS.setdefault(_a, f"Vi mode: {_a}")
for _a in SEARCH_ACTIONS:
    ACTION_WORDS.setdefault(_a, f"Search: {_a.removeprefix('Search')}")

# keys a list can offer when pressing them doesn't reach alacrittyForge
NAMED_KEYS = (["Enter", "Tab", "Space", "Backspace", "Delete", "Insert", "Home", "End", "PageUp", "PageDown",
               "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", "Escape"]
              + [f"F{i}" for i in range(1, 25)]
              + ["PrintScreen", "Pause", "ScrollLock", "NumpadEnter", "NumpadAdd", "NumpadSubtract",
                 "NumpadMultiply", "NumpadDivide", "AudioVolumeUp", "AudioVolumeDown", "AudioVolumeMute",
                 "MediaPlayPause", "MediaTrackNext", "MediaTrackPrevious"])
KEY_WORD = {"ArrowUp": "↑", "ArrowDown": "↓", "ArrowLeft": "←", "ArrowRight": "→", "Return": "Enter",
            "Escape": "Esc", "PageUp": "Page Up", "PageDown": "Page Down", "NumpadAdd": "Keypad Plus",
            "NumpadSubtract": "Keypad Minus", "+": "Plus", "-": "Minus", "=": "Equals",
            "Paste": "Paste key", "Copy": "Copy key"}

CHAR_WORDS = {"\x1b": "Esc", "\r": "Enter", "\n": "New line", "\t": "Tab", "\x7f": "Delete", "\x08": "Backspace",
              "\x00": "Ctrl+Space"}


def split_mods(mods: str | None) -> list[str]:
    return [m.strip() for m in (mods or "").split("|") if m.strip()]


def keys_text(b: dict) -> str:
    """'Ctrl+Shift+V', 'Shift+Enter'."""
    parts = [MOD_WORD.get(m, m) for m in split_mods(b.get("mods"))]
    key = str(b.get("key", "?"))
    parts.append(KEY_WORD.get(key, key))
    return "+".join(parts)


def chars_text(chars: str) -> str:
    """Hidden characters named, not printed: '\\x1b\\r' → 'Esc, Enter'."""
    out, plain = [], ""
    for c in chars:
        word = CHAR_WORDS.get(c)
        if word is None and ord(c) < 0x20:
            word = f"Ctrl+{chr(ord(c) + 64)}"
        if word is None:
            plain += c
            continue
        if plain:
            out.append(f'"{plain}"')
            plain = ""
        out.append(word)
    if plain:
        out.append(f'"{plain}"')
    return ", ".join(out)


def does_text(b: dict) -> str:
    """What a shortcut does, in words."""
    if "action" in b:
        return ACTION_WORDS.get(str(b["action"]), str(b["action"]))
    if "chars" in b:
        return f"Types: {chars_text(str(b['chars']))}"
    if "command" in b:
        c = b["command"]
        if isinstance(c, dict):
            c = " ".join([str(c.get("program", ""))] + [str(a) for a in c.get("args", [])])
        return f"Runs: {c}"
    return "Nothing"


MODE_WORDS = {"Vi": "in vi mode", "Search": "while searching", "Alt": "in full-screen programs",
              "AppCursor": "with application cursor keys", "AppKeypad": "with application keypad"}
NOT_WORDS = {"Vi": "not in vi mode", "Search": "not while searching", "Alt": "not in full-screen programs",
             "AppCursor": "without application cursor keys", "AppKeypad": "without application keypad"}


def mode_text(b: dict) -> str:
    """'Vi|~Search' → 'in vi mode, not while searching'. Alt is the screen
    full-screen programs (less, vim) use, not the Alt key."""
    parts = [p.strip() for p in str(b.get("mode", "")).split("|") if p.strip()]
    words = []
    for p in parts:
        if p.startswith("~"):
            words.append(NOT_WORDS.get(p[1:], f"not {p[1:]}"))
        else:
            words.append(MODE_WORDS.get(p, p))
    return ", ".join(words)


def same_keys(a: dict, b: dict) -> bool:
    return (str(a.get("key", "")).lower() == str(b.get("key", "")).lower()
            and sorted(split_mods(a.get("mods"))) == sorted(split_mods(b.get("mods")))
            and str(a.get("mode", "")) == str(b.get("mode", "")))


def turned_off(default: dict, yours: list[dict]) -> bool:
    """A default replaced by one of yours on the same keys that types or does nothing."""
    return any(same_keys(default, y) and y.get("action") in ("ReceiveChar", "None") for y in yours)


def clashes(new: dict, yours: list[dict], skip: int | None = None) -> list[str]:
    """What else the same keys already do (yours, then Alacritty's), in words."""
    out = []
    for i, y in enumerate(yours):
        if i != skip and same_keys(new, y):
            out.append(f"yours: {does_text(y)}")
    for d in DEFAULTS:
        if same_keys(new, d) and not turned_off(d, yours):
            out.append(f"Alacritty's: {does_text(d)}")
    return out


def turn_off(default: dict) -> dict:
    """Your shortcut that replaces one of Alacritty's: the key types as normal."""
    b = {"key": default["key"]}
    for f in ("mods", "mode"):
        if default.get(f):
            b[f] = default[f]
    b["action"] = "ReceiveChar"
    return b


def diff(old: list[dict], new: list[dict]) -> list[tuple[str, str, str]]:
    """(label, old, new) for the review."""
    rows = []
    gone = [b for b in old if b not in new]
    added = [b for b in new if b not in old]
    for b in gone:
        match = next((a for a in added if same_keys(a, b)), None)
        if match is not None:
            added.remove(match)
            rows.append(("Shortcut", f"{keys_text(b)}: {does_text(b)}", f"{keys_text(match)}: {does_text(match)}"))
        else:
            rows.append(("Shortcut removed", f"{keys_text(b)}: {does_text(b)}", "—"))
    for b in added:
        word = "Alacritty's turned off" if b.get("action") == "ReceiveChar" else "Shortcut added"
        rows.append((word, "", f"{keys_text(b)}: {does_text(b)}"))
    return rows


# ── pressing keys to record them ─────────────────────────────────────────
# Textual's key names → Alacritty's
TEXTUAL_KEYS = {"enter": "Enter", "tab": "Tab", "space": "Space", "backspace": "Backspace", "delete": "Delete",
                "insert": "Insert", "home": "Home", "end": "End", "pageup": "PageUp", "pagedown": "PageDown",
                "up": "ArrowUp", "down": "ArrowDown", "left": "ArrowLeft", "right": "ArrowRight",
                "escape": "Escape", "plus": "+", "minus": "-", "equals_sign": "=", "comma": ",",
                "full_stop": ".", "slash": "/", "semicolon": ";", "apostrophe": "'", "left_square_bracket": "[",
                "right_square_bracket": "]", "backslash": "\\", "grave_accent": "`"}
TEXTUAL_MODS = {"ctrl": "Control", "shift": "Shift", "alt": "Alt", "meta": "Alt", "super": "Super"}


def from_key_event(key: str, character: str | None = None) -> dict[str, Any] | None:
    """A Textual key name ('ctrl+shift+t', 'shift+enter') → {key, mods}; None
    for a lone modifier."""
    parts = key.split("+")
    name = parts[-1]
    mods = [TEXTUAL_MODS[p] for p in parts[:-1] if p in TEXTUAL_MODS]
    if name in TEXTUAL_MODS:
        return None
    if name in TEXTUAL_KEYS:
        k = TEXTUAL_KEYS[name]
    elif len(name) >= 2 and name[0] == "f" and name[1:].isdigit():
        k = name.upper()
    elif len(name) == 1:
        k = name.upper()
        if name.isupper() and "Shift" not in mods:       # Textual reports Shift+t as "T"
            mods.append("Shift")
    elif character and len(character) == 1 and character.isprintable():
        k = character.upper()
    else:
        return None
    order = [m for m, _w in MODS]
    out: dict[str, Any] = {"key": k}
    if mods:
        out["mods"] = "|".join(sorted(set(mods), key=order.index))
    return out
