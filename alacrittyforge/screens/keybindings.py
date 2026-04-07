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


class KeyBindingsScreen(Static):
    """View and manage Alacritty keyboard bindings."""

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

                yield Label("", id="keys-add-status")

    def on_mount(self) -> None:
        self._load_bindings()

    def on_show(self) -> None:
        self._load_bindings()

    def _load_bindings(self) -> None:
        """Load all bindings and populate the table."""
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

        user_count = sum(
            1 for b in self._bindings_data if b.get("source") == "user"
        )
        self._update_status(
            f"[#cdd6f4]{len(self._bindings_data)} bindings total  "
            f"([green]{user_count} user-defined[/]  "
            f"[#6c7086]{len(self._bindings_data) - user_count} defaults[/])[/]"
        )

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
                self._update_add_status("Add cancelled.")
                return
            ok, msg = add_binding(key, mods, action, chars)
            if ok:
                self._update_add_status(f"[green]✔  {msg}[/]")
                self._clear_inputs()
                self._load_bindings()
            else:
                self._update_add_status(f"[red]✖  {msg}[/]")

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
            self._update_add_status("[yellow]Select a binding first.[/]")
            return

        b = self._bindings_data[idx]
        if b.get("source") != "user":
            self._update_add_status(
                "[yellow]Only user-defined bindings can be deleted.[/]"
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
            self._update_add_status("[red]Could not locate binding.[/]")
            return

        key, mods, action = format_binding_display(b)

        def on_confirm(confirmed: bool) -> None:
            if not confirmed:
                self._update_add_status("Delete cancelled.")
                return
            ok, msg = delete_binding(user_idx)
            if ok:
                self._update_add_status(f"[green]✔  {msg}[/]")
                self._load_bindings()
            else:
                self._update_add_status(f"[red]✖  {msg}[/]")

        self.app.push_screen(
            ConfirmDialog(
                title="Delete Binding",
                message=f"Delete binding: {mods+' + ' if mods else ''}{key} → {action}?"
            ),
            on_confirm
        )

    def action_refresh(self) -> None:
        """Reload bindings from disk."""
        self._load_bindings()
        self._update_status("Refreshed.")

    def _clear_inputs(self) -> None:
        """Clear all add-binding input fields."""
        self.query_one("#input-key",   Input).value = ""
        self.query_one("#input-chars", Input).value = ""

    def _update_status(self, msg: str) -> None:
        try:
            self.query_one("#keys-status", Label).update(msg)
        except Exception:
            pass

    def _update_add_status(self, msg: str) -> None:
        try:
            self.query_one("#keys-add-status", Label).update(msg)
        except Exception:
            pass