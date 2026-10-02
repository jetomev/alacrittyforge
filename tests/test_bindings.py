"""Shortcuts in plain words (v1.0.0, step 4). No display needed."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from alacrittyforge import bindings as b  # noqa: E402
from alacrittyforge.default_bindings import DEFAULTS  # noqa: E402

JAVIER = [
    {"key": "V", "mods": "Control|Shift", "action": "Paste"},
    {"key": "C", "mods": "Control|Shift", "action": "Copy"},
    {"key": "+", "mods": "Control", "action": "IncreaseFontSize"},
    {"key": "-", "mods": "Control", "action": "DecreaseFontSize"},
    {"key": "Return", "mods": "Shift", "chars": "\x1b\r"},
]


class InWords(unittest.TestCase):
    def test_keys_read_the_way_people_say_them(self):
        self.assertEqual(b.keys_text(JAVIER[0]), "Ctrl+Shift+V")
        self.assertEqual(b.keys_text(JAVIER[4]), "Shift+Enter")
        self.assertEqual(b.keys_text({"key": "ArrowUp", "mods": "Alt"}), "Alt+↑")

    def test_hidden_characters_are_named_not_printed(self):
        # 0.2.0 printed \x1b raw; it broke its own Shortcuts screenshot
        self.assertEqual(b.does_text(JAVIER[4]), "Types: Esc, Enter")
        self.assertEqual(b.chars_text("\x0c"), "Ctrl+L")
        self.assertEqual(b.chars_text("ls\r"), '"ls", Enter')
        self.assertNotIn("\x1b", b.does_text(JAVIER[4]))

    def test_actions_and_programs_in_words(self):
        self.assertEqual(b.does_text(JAVIER[2]), "Make the text bigger")
        self.assertEqual(b.does_text({"key": "T", "command": {"program": "firefox", "args": ["-new-window"]}}),
                         "Runs: firefox -new-window")
        self.assertEqual(b.does_text({"key": "K", "action": "SemanticLeft"}), "Vi mode: SemanticLeft")


class Modes(unittest.TestCase):
    def test_modes_in_words(self):
        self.assertEqual(b.mode_text({"mode": "Vi|~Search"}), "in vi mode, not while searching")
        self.assertEqual(b.mode_text({"mode": "~Alt"}), "not in full-screen programs")
        self.assertEqual(b.mode_text({}), "")
        self.assertEqual(b.keys_text({"key": "Paste"}), "Paste key")


class Defaults(unittest.TestCase):
    def test_alacrittys_own_are_the_linux_ones(self):
        groups = {d["group"] for d in DEFAULTS}
        self.assertEqual(groups, {"general", "vi", "search"})
        self.assertTrue(any(b.keys_text(d) == "Ctrl+Shift+F" and d.get("action") == "SearchForward"
                            for d in DEFAULTS))
        self.assertFalse(any(d.get("action", "").startswith("SelectTab") for d in DEFAULTS))   # macOS

    def test_clashes_name_what_else_the_keys_do(self):
        self.assertEqual(b.clashes({"key": "T", "mods": "Control|Shift"}, JAVIER), [])
        self.assertIn("yours: Paste", b.clashes({"key": "V", "mods": "Shift|Control"}, JAVIER))
        self.assertIn("Alacritty's: Search forward", b.clashes({"key": "F", "mods": "Control|Shift", "mode": "~Search"}, []))

    def test_turning_one_of_alacrittys_off(self):
        d = next(x for x in DEFAULTS if b.keys_text(x) == "Ctrl+Shift+B")
        off = b.turn_off(d)
        self.assertEqual(off["action"], "ReceiveChar")
        self.assertTrue(b.turned_off(d, [off]))
        self.assertEqual(b.clashes(d, [off]), ["yours: Types the key as normal (shortcut off)"])


class TheReview(unittest.TestCase):
    def test_added_changed_and_removed_in_words(self):
        new = [dict(x) for x in JAVIER]
        new[2]["action"] = "ResetFontSize"                    # changed
        del new[3]                                            # removed
        new.append({"key": "T", "mods": "Control|Shift", "action": "CreateNewWindow"})
        rows = b.diff(JAVIER, new)
        self.assertIn(("Shortcut", "Ctrl+Plus: Make the text bigger", "Ctrl+Plus: Text size back to normal"), rows)
        self.assertIn(("Shortcut removed", "Ctrl+Minus: Make the text smaller", "—"), rows)
        self.assertIn(("Shortcut added", "", "Ctrl+Shift+T: Open a new window"), rows)


class Recording(unittest.TestCase):
    def test_textual_keys_become_alacritty_keys(self):
        self.assertEqual(b.from_key_event("ctrl+shift+t"), {"key": "T", "mods": "Control|Shift"})
        self.assertEqual(b.from_key_event("shift+enter"), {"key": "Enter", "mods": "Shift"})
        self.assertEqual(b.from_key_event("T"), {"key": "T", "mods": "Shift"})
        self.assertEqual(b.from_key_event("f5"), {"key": "F5"})
        self.assertEqual(b.from_key_event("ctrl+plus"), {"key": "+", "mods": "Control"})
        self.assertIsNone(b.from_key_event("shift"))


if __name__ == "__main__":
    unittest.main()
