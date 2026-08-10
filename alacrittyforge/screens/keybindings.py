# ═══════════════════════════════════════════════════════════
#  AlacrittyForge — Key Bindings Screen (v0.2.0 redesign)
#
#  Javier's ruling: "same application as Config" — ONE table, values
#  edited in place per CELL (Key / Mods / Action / Chars), dropdowns
#  where enumerable (Mods list, Action picker) so typos are impossible,
#  staged edits marked ⏳, deletions marked ✖, and a window-style fixed
#  footer: New Binding · Delete · Clear Pending · Save Changes.
#  Only user bindings are editable; Alacritty defaults show read-only.
# ═══════════════════════════════════════════════════════════

from rich.text import Text

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Label, Static

from forgekit import ConfirmDialog, MenuDropdown

from ..keybind_manager import (
    get_user_bindings, get_all_bindings, add_binding, delete_binding,
    update_binding, AVAILABLE_ACTIONS, AVAILABLE_MODS,
)
from ..widgets.picker import FilterPickerModal
from ..widgets.status import StatusMixin
from .config_editor import FieldEditModal

_COLS = ("key", "mods", "action", "chars")


class KeyBindingsScreen(StatusMixin, Static):
    """One-table, cell-edited manager for Alacritty keyboard bindings."""

    STATUS_WIDGET_ID = "keys-status"
    DEFAULT_FOCUS = "#keys-table"

    BINDINGS = [
        Binding("e", "edit_cell",      "Edit",   show=True),
        Binding("n", "new_binding",    "New",    show=True),
        Binding("d", "delete_binding", "Delete", show=True),
        Binding("s", "save_changes",   "Save",   show=True),
        Binding("r", "refresh",        "Refresh", show=True),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._user: list[dict] = []       # user bindings (editable)
        self._defaults: list[dict] = []   # read-only rows
        self._edits: dict[int, dict] = {} # user index -> staged field edits
        self._new: list[dict] = []        # staged new bindings
        self._deletes: set[int] = set()   # staged user-index deletions

    # ── compose ───────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        with Vertical(classes="main-area"):
            yield Label(
                "⌨   Key Bindings  (↑↓←→ navigate · E edit cell · "
                "N new · D delete · S save)",
                classes="section-title",
            )
            yield DataTable(id="keys-table", cursor_type="cell")
            with Horizontal(classes="forge-buttons forge-panel-footer",
                            id="keys-footer"):
                yield Button("New Binding",   id="btn-new", variant="primary")
                yield Button("Delete",        id="btn-delete", variant="error")
                yield Button("Clear Pending", id="btn-clear")
                yield Button("Save Changes",  id="btn-save", variant="primary")
            yield Label("", id="keys-status")

    def on_mount(self) -> None:
        self._reload_view()
        self._set_status(
            f"{len(self._user)} user binding(s), "
            f"{len(self._defaults)} defaults. E edits the cell under the "
            "cursor.", "info", popup=False,
        )

    def on_show(self) -> None:
        self._reload_view()

    # ── table ─────────────────────────────────────────────────────────

    def _staged_count(self) -> int:
        return len(self._edits) + len(self._new) + len(self._deletes)

    def _reload_view(self) -> None:
        allb = get_all_bindings()
        self._user = [b for b in allb if b.get("source") == "user"]
        self._defaults = [b for b in allb if b.get("source") != "user"]

        table = self.query_one("#keys-table", DataTable)
        coord = (table.cursor_row, table.cursor_column)
        table.clear(columns=True)
        table.add_columns("Key", "Mods", "Action", "Chars", "Source")

        def cell(base: str, staged) -> object:
            if staged is not None:
                return Text(f"⏳ {staged}", style="#f9e2af")
            return base

        for i, b in enumerate(self._user):
            ed = self._edits.get(i, {})
            if i in self._deletes:
                row = [Text(f"✖ {b.get('key','')}", style="#f38ba8 strike"),
                       Text(b.get("mods", ""), style="#f38ba8 strike"),
                       Text(b.get("action", ""), style="#f38ba8 strike"),
                       Text(b.get("chars", ""), style="#f38ba8 strike"),
                       Text("delete", style="#f38ba8")]
            else:
                row = [cell(b.get("key", ""),   ed.get("key")),
                       cell(b.get("mods", ""),  ed.get("mods")),
                       cell(b.get("action", ""), ed.get("action")),
                       cell(b.get("chars", ""),  ed.get("chars")),
                       "user"]
            table.add_row(*row)

        for j, b in enumerate(self._new):
            table.add_row(
                Text(f"⏳ {b['key'] or '…'}", style="#fab387"),
                Text(b["mods"], style="#fab387"),
                Text(b["action"], style="#fab387"),
                Text(b["chars"], style="#fab387"),
                Text("new", style="#fab387"),
            )

        for b in self._defaults:
            table.add_row(
                Text(b.get("key", ""), style="#6c7086"),
                Text(b.get("mods", ""), style="#6c7086"),
                Text(b.get("action", b.get("chars", "")), style="#6c7086"),
                "",
                Text("default", style="#6c7086"),
            )

        try:
            if coord[0] is not None:
                table.move_cursor(row=coord[0], column=coord[1] or 0)
        except Exception:
            pass

    def _row_kind(self, row: int) -> tuple[str, int]:
        """Return ("user"|"new"|"default", local_index) for a table row."""
        nu, nn = len(self._user), len(self._new)
        if row < nu:
            return "user", row
        if row < nu + nn:
            return "new", row - nu
        return "default", row - nu - nn

    # ── cell editing ──────────────────────────────────────────────────

    def on_data_table_cell_selected(self, e: DataTable.CellSelected) -> None:
        self.action_edit_cell()

    def action_edit_cell(self) -> None:
        table = self.query_one("#keys-table", DataTable)
        row, col = table.cursor_row, table.cursor_column
        if row is None:
            self._set_status("Select a cell first.", "warn")
            return
        kind, idx = self._row_kind(row)
        if kind == "default":
            self._set_status(
                "Alacritty defaults are read-only — add a user binding with "
                "the same key to override it.", "warn",
            )
            return
        if col is None or col > 3:
            col = 0
        field = _COLS[col]
        if kind == "user" and idx in self._deletes:
            self._set_status("Row is staged for deletion — D to undelete.", "warn")
            return

        current = self._current_value(kind, idx, field)

        if field == "mods":
            self._open_dropdown(row, col,
                                [m if m else "(none)" for m in AVAILABLE_MODS],
                                lambda choice: self._stage(kind, idx, "mods",
                                    "" if choice == "(none)" else choice))
        elif field == "action":
            opts = list(AVAILABLE_ACTIONS)
            if len(opts) > 12:
                self.app.push_screen(
                    FilterPickerModal("Select — action", opts, current),
                    lambda choice: self._stage(kind, idx, "action", choice),
                )
            else:
                self._open_dropdown(row, col, opts,
                    lambda choice: self._stage(kind, idx, "action", choice))
        else:
            desc = ("Key name, e.g. V, Return, F5, PageUp" if field == "key"
                    else "Escape sequence, e.g. \\u001b[1;5D — clears Action")
            self.app.push_screen(
                FieldEditModal(f"binding {field}", current or "", desc),
                lambda raw: self._stage(kind, idx, field, raw),
            )

    def _current_value(self, kind: str, idx: int, field: str) -> str:
        if kind == "new":
            return self._new[idx].get(field, "")
        staged = self._edits.get(idx, {})
        if field in staged:
            return str(staged[field])
        return str(self._user[idx].get(field, ""))

    def _open_dropdown(self, row: int, col: int, options: list[str], cb) -> None:
        table = self.query_one("#keys-table", DataTable)
        r = table.region
        y_off = 1 + row - int(table.scroll_offset.y)
        y = r.y + max(1, min(y_off, max(1, r.height - 1)))
        try:
            x_off = sum(c.get_render_width(table)
                        for c in table.ordered_columns[:col]) + 1
        except Exception:
            x_off = 2 + col * 14
        x = max(r.x, min(r.x + x_off, r.x + r.width - 24))
        items = [(o, str(i + 1) if i < 9 else "", o)
                 for i, o in enumerate(options)]
        self.app.push_screen(MenuDropdown(items, x, y),
                             lambda c: cb(c) if c is not None else None)

    def _stage(self, kind: str, idx: int, field: str, value) -> None:
        if value is None:
            return
        value = str(value)
        if kind == "new":
            self._new[idx][field] = value
            if field == "action" and value:
                self._new[idx]["chars"] = ""
            elif field == "chars" and value:
                self._new[idx]["action"] = ""
        else:
            ed = self._edits.setdefault(idx, {})
            ed[field] = value
            # action and chars are mutually exclusive in Alacritty
            if field == "action" and value:
                ed["chars"] = ""
            elif field == "chars" and value:
                ed["action"] = ""
        self._reload_view()
        self._set_status(
            f"Staged {field} = {value or '(empty)'}  "
            f"({self._staged_count()} pending)", "warn",
        )

    # ── row operations ────────────────────────────────────────────────

    def action_new_binding(self) -> None:
        self._new.append({"key": "", "mods": "", "action": "Paste", "chars": ""})
        self._reload_view()
        table = self.query_one("#keys-table", DataTable)
        try:
            table.move_cursor(row=len(self._user) + len(self._new) - 1, column=0)
        except Exception:
            pass
        self._set_status(
            "New binding staged — edit its Key (E on the cell), then Save.",
            "warn",
        )

    def action_delete_binding(self) -> None:
        table = self.query_one("#keys-table", DataTable)
        row = table.cursor_row
        if row is None:
            self._set_status("Select a binding first.", "warn")
            return
        kind, idx = self._row_kind(row)
        if kind == "default":
            self._set_status("Alacritty defaults cannot be deleted.", "warn")
            return
        if kind == "new":
            self._new.pop(idx)
            self._set_status("Staged new binding removed.", "info")
        else:
            if idx in self._deletes:
                self._deletes.discard(idx)
                self._set_status("Deletion unstaged.", "info")
            else:
                self._deletes.add(idx)
                self._edits.pop(idx, None)
                self._set_status(
                    f"Staged for deletion ({self._staged_count()} pending) — "
                    "Save Changes applies it.", "warn",
                )
        self._reload_view()

    # ── footer actions ────────────────────────────────────────────────

    def on_button_pressed(self, e: Button.Pressed) -> None:
        if e.button.id == "btn-new":
            self.action_new_binding()
        elif e.button.id == "btn-delete":
            self.action_delete_binding()
        elif e.button.id == "btn-clear":
            self._edits, self._new, self._deletes = {}, [], set()
            self._reload_view()
            self._set_status("Pending changes cleared.", "info")
        elif e.button.id == "btn-save":
            self.action_save_changes()

    def action_save_changes(self) -> None:
        if not self._staged_count():
            self._set_status("No pending changes to save.", "warn")
            return

        # Validate staged news/edits before confirming.
        for b in self._new:
            if not b["key"].strip():
                self._set_status("A new binding is missing its Key.", "error")
                return
            if not b["action"].strip() and not b["chars"].strip():
                self._set_status(
                    "A new binding needs an Action or Chars.", "error")
                return

        parts = []
        if self._edits:
            parts.append(f"{len(self._edits)} edit(s)")
        if self._new:
            parts.append(f"{len(self._new)} new")
        if self._deletes:
            parts.append(f"{len(self._deletes)} deletion(s)")
        summary = ", ".join(parts)

        def on_confirm(confirmed: bool) -> None:
            if not confirmed:
                self._set_status("Save cancelled — changes stay staged.", "info")
                return
            errors = []
            # deletions first, highest index first (indices stay valid)
            for idx in sorted(self._deletes, reverse=True):
                ok, msg = delete_binding(idx)
                if not ok:
                    errors.append(msg)
            # edits on surviving indices
            for idx, ed in self._edits.items():
                if idx in self._deletes:
                    continue
                base = dict(self._user[idx])
                base.update(ed)
                ok, msg = update_binding(
                    idx - sum(1 for d in self._deletes if d < idx),
                    base.get("key", ""), base.get("mods", ""),
                    base.get("action", ""), base.get("chars", ""),
                )
                if not ok:
                    errors.append(msg)
            for b in self._new:
                ok, msg = add_binding(b["key"], b["mods"],
                                      b["action"], b["chars"])
                if not ok:
                    errors.append(msg)

            done = self._staged_count() - len(errors)
            self._edits, self._new, self._deletes = {}, [], set()
            self._reload_view()
            if errors:
                self._set_status(
                    f"{done} applied, {len(errors)} failed: {errors[0]}",
                    "error",
                )
            else:
                self._set_status(
                    f"Saved — {summary} written to alacritty.toml.", "ok",
                )

        self.app.push_screen(
            ConfirmDialog(
                f"Write to alacritty.toml: {summary}?\n\n"
                "A backup is created before the changes.",
                "Save",
            ),
            on_confirm,
        )

    def action_refresh(self) -> None:
        self._reload_view()
        self._set_status("Bindings reloaded from disk.", "info")
