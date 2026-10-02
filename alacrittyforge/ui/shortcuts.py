"""Shortcuts — your keyboard shortcuts in words, recorded by pressing the keys (v1.0.0).

Yours first, then Alacritty's own (fixed: they can only be turned off).
Every shortcut says what it does ("Make the text bigger"); hidden characters
are named ("Types: Esc, Enter"). Add and Change open one window: press the
keys to record them (lists as a fallback, for keys the terminal keeps for
itself), pick what it does, and when. Changes wait for Save like any other.
"""

from __future__ import annotations

import copy

from rich.markup import escape
from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, DataTable, Input, Select, Static

from forgekit import CheckList, Choices, ForgeModal, glyph

from .. import bindings as kb
from ..default_bindings import DEFAULTS

KEY = "keyboard.bindings"
ALWAYS = "__always__"


class ShortcutsScreen(Vertical):
    FORGE_HINTS = [("↑↓", "pick"), ("+", "add"), ("F2", "change"), ("Del", "remove"), ("Tab", "buttons"),
                   ("F10", "save"), ("?", "all keys")]
    BINDINGS = [Binding("plus", "add", show=False), Binding("f2", "change", show=False),
                Binding("delete", "remove", show=False)]

    def __init__(self, session, **kw) -> None:
        super().__init__(**kw)
        self.session = session
        self.rows: list[tuple[str, int | dict]] = []    # ("yours", index) or ("alacritty", default)
        self.show_modes = False

    def compose(self) -> ComposeResult:
        yield Static("[b $forge-title-accent]Shortcuts[/]   [$forge-muted]keys that do something in Alacritty, "
                     "yours first[/]", classes="af-group-title")
        t = DataTable(id="sc-table", cursor_type="row", zebra_stripes=False)
        t.FORGE_HINTS = self.FORGE_HINTS
        yield t
        with Horizontal(classes="forge-buttons sc-actions"):
            yield Button(f"Add a shortcut{glyph('ellipsis')}  +", id="sc-add", variant="primary")
            yield Button("Change  F2", id="sc-change")
            yield Button("Remove", id="sc-remove")
            yield Button("Turn this one off", id="sc-off")
        with Horizontal(classes="forge-buttons sc-actions"):
            yield Button("Show vi and search keys", id="sc-modes")

    def on_mount(self) -> None:
        self.query_one("#sc-table", DataTable).add_columns("Keys", "Does", "From")
        self.refresh_view()

    def yours(self) -> list[dict]:
        return list(self.session.value(KEY) or [])

    def refresh_view(self) -> None:
        t = self.query_one("#sc-table", DataTable)
        keep = t.cursor_row
        t.clear()
        self.rows = []
        mine = self.yours()
        for i, b in enumerate(mine):
            t.add_row(kb.keys_text(b), self._does(b), "yours")
            self.rows.append(("yours", i))
        for d in DEFAULTS:
            if d["group"] != "general" and not self.show_modes:
                continue
            off = kb.turned_off(d, mine)
            style = "dim strike" if off else "dim"
            t.add_row(Text(kb.keys_text(d), style=style), Text(self._does(d), style=style),
                      Text("Alacritty, off" if off else "Alacritty", style="dim"))
            self.rows.append(("alacritty", d))
        if self.rows:
            t.move_cursor(row=min(keep or 0, len(self.rows) - 1))
        self.query_one("#sc-modes", Button).label = ("Hide vi and search keys" if self.show_modes
                                                    else "Show vi and search keys")
        self._buttons()

    @staticmethod
    def _does(b: dict) -> str:
        """What it does, and when if not always: one column, so the list fits 100 columns."""
        when = kb.mode_text(b)
        return kb.does_text(b) + (f" ({when})" if when else "")

    def current(self) -> tuple[str, int | dict] | None:
        t = self.query_one("#sc-table", DataTable)
        if t.cursor_row is None or t.cursor_row >= len(self.rows):
            return None
        return self.rows[t.cursor_row]

    @on(DataTable.RowHighlighted, "#sc-table")
    def _moved(self, _e) -> None:
        self._buttons()

    def _buttons(self) -> None:
        cur = self.current()
        ok = self.session.readable
        mine = cur is not None and cur[0] == "yours"
        self.query_one("#sc-change", Button).disabled = not (ok and mine)
        self.query_one("#sc-remove", Button).disabled = not (ok and mine)
        off_btn = self.query_one("#sc-off", Button)
        off_btn.display = cur is not None and cur[0] == "alacritty"
        if cur is not None and cur[0] == "alacritty":
            off_btn.label = "Turn it back on" if kb.turned_off(cur[1], self.yours()) else "Turn this one off"
        off_btn.disabled = not ok

    def _stage(self, new: list[dict]) -> None:
        # none of yours left, and the file had none: no change
        if not new and self.session.original(KEY) is None:
            new = None
        self.session.set(KEY, new)
        self.refresh_view()
        self.app.refresh_state()

    # ── actions ───────────────────────────────────────────────────────────────
    def action_add(self) -> None:
        if not self.session.readable:
            return

        def done(b: dict | None) -> None:
            if b:
                self._stage(self.yours() + [b])
                self.app.notify(f"{kb.keys_text(b)} added. Press F10 to save it.", timeout=5)

        self.app.push_screen(ShortcutDialog(None, self.yours()), done)

    def action_change(self) -> None:
        cur = self.current()
        if cur is None or cur[0] != "yours" or not self.session.readable:
            return
        i = cur[1]
        mine = self.yours()

        def done(b: dict | None) -> None:
            if b:
                mine[i] = b
                self._stage(mine)

        self.app.push_screen(ShortcutDialog(mine[i], mine, index=i), done)

    def action_remove(self) -> None:
        cur = self.current()
        if cur is None or cur[0] != "yours" or not self.session.readable:
            return
        mine = self.yours()
        gone = mine.pop(cur[1])
        self._stage(mine)
        self.app.notify(f"{kb.keys_text(gone)} removed. Press F10 to save, or Discard to keep it.", timeout=6)

    def toggle_off(self) -> None:
        cur = self.current()
        if cur is None or cur[0] != "alacritty" or not self.session.readable:
            return
        d, mine = cur[1], self.yours()
        if kb.turned_off(d, mine):
            mine = [y for y in mine if not (kb.same_keys(d, y) and y.get("action") in ("ReceiveChar", "None"))]
        else:
            mine.append(kb.turn_off(d))
        self._stage(mine)

    def on_button_pressed(self, e: Button.Pressed) -> None:
        bid = e.button.id or ""
        if not bid.startswith("sc-"):
            return
        e.stop()
        {"sc-add": self.action_add, "sc-change": self.action_change, "sc-remove": self.action_remove,
         "sc-off": self.toggle_off}.get(bid, lambda: None)()
        if bid == "sc-modes":
            self.show_modes = not self.show_modes
            self.refresh_view()

    @on(DataTable.RowSelected, "#sc-table")
    def _enter(self, _e) -> None:
        cur = self.current()
        if cur and cur[0] == "yours":
            self.action_change()


class KeyRecorder(Static, can_focus=True):
    """Press the keys and they're recorded. Tab and Esc keep their usual jobs;
    for those, use the lists."""

    DEFAULT_CLASSES = "sc-recorder"
    FORGE_HINTS = [("keys", "record them"), ("Tab", "next"), ("Esc", "cancel")]

    def __init__(self, dialog: "ShortcutDialog", **kw) -> None:
        super().__init__("", **kw)
        self.dialog = dialog

    def on_mount(self) -> None:
        self.show()

    def show(self) -> None:
        b = self.dialog.keys
        text = kb.keys_text(b) if b.get("key") else ""
        self.update(f" [b]{escape(text)}[/]" if text else " [$forge-muted]press the keys now[/]")

    def on_key(self, event) -> None:
        if event.key in ("tab", "shift+tab", "escape"):
            return
        got = kb.from_key_event(event.key, event.character)
        if got is None:
            return
        event.stop()
        event.prevent_default()
        self.dialog.set_keys(got)


class ShortcutDialog(ForgeModal[dict | None]):
    """Add a shortcut, or change one: the keys, what it does, when."""

    BINDINGS = [Binding("escape", "cancel", "", show=False)]

    def __init__(self, existing: dict | None, yours: list[dict], index: int | None = None) -> None:
        super().__init__()
        self.existing = copy.deepcopy(existing) if existing else None
        self.yours = yours
        self.index = index
        self.keys = {k: v for k, v in (existing or {}).items() if k in ("key", "mods")}
        if existing and "chars" in existing:
            self.kind = "chars"
        elif existing and "command" in existing:
            self.kind = "command"
        else:
            self.kind = "action"

    def compose(self) -> ComposeResult:
        title = "Change a shortcut" if self.existing else "Add a shortcut"
        letters = [chr(c) for c in range(ord("A"), ord("Z") + 1)] + [str(i) for i in range(10)]
        symbols = ["+", "-", "=", ",", ".", "/", ";", "'", "[", "]", "\\", "`"]
        key_opts = [(k, kb.KEY_WORD.get(k, k)) for k in letters + kb.NAMED_KEYS + symbols]
        cur_key = self.keys.get("key")
        if cur_key and all(v != cur_key for v, _l in key_opts):
            key_opts.insert(0, (cur_key, cur_key))
        self._key_opts = key_opts
        mods = kb.split_mods(self.keys.get("mods"))
        ex = self.existing or {}
        actions = [(a, f"{w}") for a, w, _g in kb.ACTIONS]
        actions += [(a, kb.ACTION_WORDS[a]) for a in kb.VI_ACTIONS + kb.SEARCH_ACTIONS]
        with Vertical(classes="forge-panel sc-dialog"):
            yield Static(title, classes="forge-panel-title")
            with VerticalScroll(id="sd-body", can_focus=False):
                yield Static("[b]1  The keys[/]")
                yield KeyRecorder(self, id="sd-record")
                with Horizontal(classes="sd-line"):
                    yield Static("or pick", classes="sd-label")
                    yield Select([(l, v) for v, l in key_opts], value=cur_key or Select.NULL,
                                 prompt="a key", id="sd-key")
                yield CheckList(*[(w, m, m in mods) for m, w in kb.MODS], id="sd-mods")
                yield Static("", id="sd-clash")
                yield Static("[b]2  What it does[/]", classes="sd-step")
                yield Choices([("action", "An action"), ("chars", "Type text"), ("command", "Run a program")],
                              self.kind, id="sd-kind")
                yield Select([(l, v) for v, l in actions], value=str(ex.get("action", "CreateNewWindow")),
                             allow_blank=False, id="sd-action")
                yield Input(self._chars_in(ex.get("chars", "")), placeholder=r"text; \e is Esc, \r is Enter",
                            id="sd-chars")
                yield Input(self._command_in(ex.get("command", "")), placeholder="a program, like firefox",
                            id="sd-command")
                yield Static("", id="sd-preview")
                yield Static("[b]3  When[/]", classes="sd-step")
                # Textual's Select can't hold "" as a value: "always" stands for no mode
                yield Select([(w, v or ALWAYS) for v, w in kb.MODES], value=str(ex.get("mode") or ALWAYS),
                             allow_blank=False, id="sd-mode")
            with Horizontal(classes="forge-buttons forge-panel-footer"):
                yield Button("Keep the change" if self.existing else "Add it", id="sd-ok", variant="primary")
                yield Button("Cancel", id="sd-cancel")

    def on_mount(self) -> None:
        self._show_kind()
        self._update()
        self.query_one("#sd-record").focus()
        # focusing the recorder scrolled its heading out of view
        self.call_after_refresh(self.query_one("#sd-body").scroll_home, animate=False)

    @staticmethod
    def _chars_in(chars: str) -> str:
        return (chars.replace("\\", "\\\\").replace("\x1b", r"\e").replace("\r", r"\r").replace("\n", r"\n")
                .replace("\t", r"\t"))

    @staticmethod
    def _chars_out(text: str) -> str:
        out, i = [], 0
        table = {"e": "\x1b", "r": "\r", "n": "\n", "t": "\t", "\\": "\\"}
        while i < len(text):
            if text[i] == "\\" and i + 1 < len(text) and text[i + 1] in table:
                out.append(table[text[i + 1]])
                i += 2
            else:
                out.append(text[i])
                i += 1
        return "".join(out)

    @staticmethod
    def _command_in(c) -> str:
        if isinstance(c, dict):
            return " ".join([str(c.get("program", ""))] + [str(a) for a in c.get("args", [])])
        return str(c or "")

    def set_keys(self, got: dict) -> None:
        self.keys = got
        sel = self.query_one("#sd-key", Select)
        with sel.prevent(Select.Changed):
            if all(v != got["key"] for v, _l in self._key_opts):
                self._key_opts.insert(0, (got["key"], got["key"]))
                sel.set_options([(l, v) for v, l in self._key_opts])
            sel.value = got["key"]
        cl = self.query_one("#sd-mods", CheckList)
        cl.deselect_all()
        for m in kb.split_mods(got.get("mods")):
            cl.select(m)
        self.query_one("#sd-record", KeyRecorder).show()
        self._update()

    @on(Select.Changed, "#sd-key")
    def _key_picked(self, e: Select.Changed) -> None:
        if e.value is not Select.NULL:
            self.keys["key"] = e.value
            self.query_one("#sd-record", KeyRecorder).show()
            self._update()

    @on(CheckList.SelectedChanged, "#sd-mods")
    def _mods_picked(self, e) -> None:
        sel = e.selection_list.selected
        order = [m for m, _w in kb.MODS]
        if sel:
            self.keys["mods"] = "|".join(sorted(sel, key=order.index))
        else:
            self.keys.pop("mods", None)
        self.query_one("#sd-record", KeyRecorder).show()
        self._update()

    @on(Choices.Changed, "#sd-kind")
    def _kind(self, e: Choices.Changed) -> None:
        self.kind = e.value
        self._show_kind()
        self._update()

    def _show_kind(self) -> None:
        self.query_one("#sd-action").display = self.kind == "action"
        self.query_one("#sd-chars").display = self.kind == "chars"
        self.query_one("#sd-command").display = self.kind == "command"

    @on(Input.Changed)
    @on(Select.Changed, "#sd-action, #sd-mode")
    def _changed(self, _e) -> None:
        self._update()

    def result(self) -> dict | None:
        if not self.keys.get("key"):
            return None
        b = copy.deepcopy(self.existing) if self.existing else {}
        for f in ("key", "mods", "mode", "action", "chars", "command"):
            b.pop(f, None)
        b["key"] = self.keys["key"]
        if self.keys.get("mods"):
            b["mods"] = self.keys["mods"]
        mode = self.query_one("#sd-mode", Select).value
        if mode and mode != ALWAYS:
            b["mode"] = mode
        if self.kind == "action":
            b["action"] = self.query_one("#sd-action", Select).value
        elif self.kind == "chars":
            text = self._chars_out(self.query_one("#sd-chars", Input).value)
            if not text:
                return None
            b["chars"] = text
        else:
            words = self.query_one("#sd-command", Input).value.split()
            if not words:
                return None
            b["command"] = words[0] if len(words) == 1 else {"program": words[0], "args": words[1:]}
        return b

    def _update(self) -> None:
        b = self.result()
        clash = self.query_one("#sd-clash", Static)
        if not self.keys.get("key"):
            clash.update("")
        else:
            probe = dict(self.keys)
            mode = self.query_one("#sd-mode", Select).value
            if mode and mode != ALWAYS:
                probe["mode"] = mode
            others = kb.clashes(probe, self.yours, skip=self.index)
            if others:
                clash.update(f"[$forge-warn]{glyph('warn')} {escape(kb.keys_text(self.keys))} already: "
                             f"{escape('; '.join(others))}. Yours would do both.[/]")
            else:
                clash.update(f"[$forge-ok]{glyph('ok')} free: nothing else uses {escape(kb.keys_text(self.keys))}[/]")
        prev = self.query_one("#sd-preview", Static)
        prev.update(f"[$forge-muted]{escape(kb.does_text(b))}[/]" if b and self.kind != "action" else "")
        self.query_one("#sd-ok", Button).disabled = b is None

    def on_button_pressed(self, e: Button.Pressed) -> None:
        e.stop()
        self.dismiss(self.result() if e.button.id == "sd-ok" else None)

    def action_cancel(self) -> None:
        self.dismiss(None)
