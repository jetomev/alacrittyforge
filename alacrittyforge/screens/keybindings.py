# ═══════════════════════════════════════════════════════════
#  AlacrittyForge — Key Bindings Screen
#  View, add, and delete Alacritty keyboard bindings.
# ═══════════════════════════════════════════════════════════

from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Label, Static, DataTable, Input, Button, Select
from textual.containers import Vertical, Horizontal

from ..keybind_manager import (
    get_all_bindings, add_binding, delete_binding,
    format_binding_display, AVAILABLE_ACTIONS, AVAILABLE_MODS
)
from ..widgets.confirm_dialog import ConfirmDialog
from ..widgets.status import StatusMixin


class KeyBindingsScreen(StatusMixin, Static):
    """View and manage Alacritty keyboard bindings."""

    STATUS_WIDGET_ID = "keys-status"

    BINDINGS = [
        Binding("n",  "new_binding",    "New",     show=True),
        Binding("d",  "delete_binding", "Delete",  show=True),
        Binding("r",  "refresh",        "Refresh", show=True),
    ]

    _bindings_data: list[dict] = []
    _selected_index: int = 0

    def compose(self) -> ComposeResult:
        with Horizontal():
            # ── Left: bindings table ──
            with Vertical(classes="main-area", id="keys-left"):
                yield Label(
                    "⌨   Key Bindings  (N new  •  D delete  •  R refresh)",
                    classes="section-title"
                )
                yield DataTable(id="keys-table", cursor_type="row")
                yield Label("", id="keys-status")

            # ── Right: detail + add panel ──
            with Vertical(classes="detail-panel", id="keys-right"):
                yield Static(id="key-detail")

                yield Label(
                    "── Add New Binding ─────────────────",
                    classes="section-title"
                )

                yield Label("Key name  (e.g. V, Return, F5, PageUp)",
                            classes="detail-muted")
                yield Input(placeholder="Key…", id="input-key")

                yield Label("Modifiers", classes="detail-muted")
                yield Select(
                    [(m if m else "(none)", m) for m in AVAILABLE_MODS],
                    id="select-mods",
                    value=""
                )

                yield Label("Action", classes="detail-muted")
                yield Select(
                    [(a, a) for a in AVAILABLE_ACTIONS],
                    id="select-action",
                    value="Paste"
                )

                yield Label("— or — send chars instead of action",
                            classes="detail-muted")
                yield Input(
                    placeholder="Chars (e.g. \\x1b[1;5D)…",
                    id="input-chars"
                )

                with Horizontal():
                    yield Button("Add Binding",  id="btn-add",    classes="primary")
                    yield Button("Clear",        id="btn-clear",  classes="warning")
                    yield Button("Delete",       id="btn-delete", classes="danger")
                # G2 / A6: removed the redundant #keys-add-status Label —
                # add/delete feedback now routes through the unified
                # #keys-status + toast pop.

    def on_mount(self) -> None:
        self._load_bindings()

    def on_show(self) -> None:
        # G2: silent reload — no toast on every screen switch.
        self._reload_view()

    def _load_bindings(self) -> None:
        """Full init — reload, announce. Used by on_mount."""
        self._reload_view()
        user_count = sum(
            1 for b in self._bindings_data if b.get("source") == "user"
        )
        # Passive mount-time hint — status line only.
        self._set_status(
            f"{len(self._bindings_data)} bindings total  "
            f"({user_count} user-defined, "
            f"{len(self._bindings_data) - user_count} defaults)",
            "info", popup=False,
        )

    def _reload_view(self) -> None:
        """Silent reload — populate the table, no status emission."""
        self._bindings_data = get_all_bindings()

        table = self.query_one("#keys-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Source", "Key", "Mods", "Action / Chars")

        for b in self._bindings_data:
            key, mods, action = format_binding_display(b)
            source = b.get("source", "default")
            source_label = (
                "[green]user[/]" if source == "user"
                else "[#6c7086]default[/]"
            )
            table.add_row(source_label, key, mods, action)

    def on_data_table_row_highlighted(
        self, event: DataTable.RowHighlighted
    ) -> None:
        """Update detail panel on selection change."""
        if event.cursor_row is None:
            return
        idx = event.cursor_row
        if idx >= len(self._bindings_data):
            return
        self._selected_index = idx
        self._show_detail(idx)

    def _show_detail(self, idx: int) -> None:
        """Render detail for selected binding."""
        if idx >= len(self._bindings_data):
            return

        b      = self._bindings_data[idx]
        key, mods, action = format_binding_display(b)
        source = b.get("source", "default")

        source_str = (
            "[green]User defined[/]" if source == "user"
            else "[#6c7086]Alacritty default[/]"
        )

        chars_str = ""
        if "chars" in b:
            chars_str = f"\n[#89b4fa]Chars:[/]   [#cdd6f4]{b['chars']}[/]"

        detail = (
            f"[bold #cba6f7]{key}[/]\n"
            f"\n"
            f"[#89b4fa]Source:  [/]{source_str}\n"
            f"[#89b4fa]Mods:    [/][#cdd6f4]{mods if mods else '(none)'}[/]\n"
            f"[#89b4fa]Action:  [/][#cdd6f4]{action}[/]"
            f"{chars_str}\n"
            f"\n"
        )

        if source == "user":
            detail += "[#f9e2af]Press D to delete this binding.[/]"
        else:
            detail += "[#6c7086]Default bindings cannot be deleted.\nAdd a user binding to override.[/]"

        self.query_one("#key-detail", Static).update(detail)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-add":
            self.action_new_binding()
        elif event.button.id == "btn-clear":
            self._clear_inputs()
        elif event.button.id == "btn-delete":
            self.action_delete_binding()

    def action_new_binding(self) -> None:
        """Add a new binding from the input fields."""
        key    = self.query_one("#input-key",    Input).value.strip()
        mods   = self.query_one("#select-mods",  Select).value or ""
        action = self.query_one("#select-action", Select).value or ""
        chars  = self.query_one("#input-chars",  Input).value.strip()

        # If chars is filled, ignore action
        if chars:
            action = ""

        def on_confirm(confirmed: bool) -> None:
            if not confirmed:
                self._set_status("Add cancelled.", "info")
                return
            ok, msg = add_binding(key, mods, action, chars)
            if ok:
                self._clear_inputs()
                # _reload_view() (not _load_bindings) so the success status
                # below isn't briefly flashed-over by the "N bindings total"
                # passive hint that _load_bindings would emit.
                self._reload_view()
                self._set_status(msg, "ok")
            else:
                self._set_status(msg, "error")

        self.app.push_screen(
            ConfirmDialog(
                title="Add Key Binding",
                message=f"Add binding: {mods+' + ' if mods else ''}{key} → {action or chars}?"
            ),
            on_confirm
        )

    def action_delete_binding(self) -> None:
        """Delete the selected user binding."""
        idx = self._selected_index
        if idx >= len(self._bindings_data):
            self._set_status("Select a binding first.", "warn")
            return

        b = self._bindings_data[idx]
        if b.get("source") != "user":
            self._set_status(
                "Only user-defined bindings can be deleted.", "warn",
            )
            return

        # Find its index within user bindings only
        user_bindings = [
            (i, b2) for i, b2 in enumerate(self._bindings_data)
            if b2.get("source") == "user"
        ]
        user_idx = next(
            (i for i, (orig_i, _) in enumerate(user_bindings)
             if orig_i == idx),
            None
        )
        if user_idx is None:
            self._set_status("Could not locate binding.", "error")
            return

        key, mods, action = format_binding_display(b)

        def on_confirm(confirmed: bool) -> None:
            if not confirmed:
                self._set_status("Delete cancelled.", "info")
                return
            ok, msg = delete_binding(user_idx)
            if ok:
                # _reload_view() so the success status isn't briefly flashed-
                # over by the "N bindings total" passive hint.
                self._reload_view()
                self._set_status(msg, "ok")
            else:
                self._set_status(msg, "error")

        self.app.push_screen(
            ConfirmDialog(
                title="Delete Binding",
                message=f"Delete binding: {mods+' + ' if mods else ''}{key} → {action}?"
            ),
            on_confirm
        )

    def action_refresh(self) -> None:
        """Reload bindings from disk."""
        self._reload_view()
        self._set_status("Refreshed.", "info")

    def _clear_inputs(self) -> None:
        """Clear all add-binding input fields."""
        self.query_one("#input-key",   Input).value = ""
        self.query_one("#input-chars", Input).value = ""

    # _set_status is provided by StatusMixin (v0.1.1 G2 — unified feedback;
    # also collapses the prior _update_status / _update_add_status split into
    # one channel: status line + toast).