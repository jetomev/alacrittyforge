# ═══════════════════════════════════════════════════════════
#  AlacrittyForge — Config Editor Screen
#  Browse, edit, and save all alacritty.toml settings.
# ═══════════════════════════════════════════════════════════

from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Label, Static, DataTable, Input, Button
from textual.containers import Vertical, Horizontal, ScrollableContainer

from ..config_manager import (
    load_config, save_config, get_flat_settings,
    validate_value, set_nested_value, get_raw_text
)
from ..backup_manager import create_backup
from ..widgets.confirm_dialog import ConfirmDialog


class ConfigEditorScreen(Static):
    """Browse and edit all settings in alacritty.toml."""

    BINDINGS = [
        Binding("e", "edit_selected",  "Edit",    show=True),
        Binding("s", "save_changes",   "Save",    show=True),
        Binding("r", "refresh",        "Refresh", show=True),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._pending: dict = {}
        self._settings: list[dict] = []
        self._selected_key: str = ""

    def compose(self) -> ComposeResult:
        with Horizontal():
            # ── Left: settings table ──
            with Vertical(classes="main-area", id="editor-left"):
                yield Label(
                    "🔧  Config Keys  (↑↓ navigate  •  E edit)",
                    classes="section-title"
                )
                yield DataTable(id="settings-table", cursor_type="row")

                yield Label(
                    "Raw ~/.config/alacritty/alacritty.toml  (read-only preview)",
                    classes="section-title"
                )
                with ScrollableContainer(id="raw-preview-container"):
                    yield Static(id="raw-preview")

            # ── Right: detail + edit panel ──
            with Vertical(classes="detail-panel", id="editor-right"):
                yield Static(id="detail-content")
                yield Label("", id="detail-spacer")
                yield Input(
                    placeholder="New value…",
                    id="edit-input"
                )
                yield Label("", id="validation-msg")

                with Horizontal():
                    yield Button("Apply Edit",    id="btn-apply",  classes="primary")
                    yield Button("Clear Pending", id="btn-clear",  classes="warning")

                yield Label(
                    "Pending edits are saved together when you press S",
                    classes="status-muted"
                )
                yield Label("", id="status-msg")

    def on_mount(self) -> None:
        self._load_settings()

    def on_show(self) -> None:
        self._load_settings()

    def _load_settings(self) -> None:
        """Load settings from disk and populate the table."""
        data = self._data = load_config()
        self._settings = get_flat_settings(data)
        self._pending = {}

        table = self.query_one("#settings-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Key", "Value")

        for s in self._settings:
            val_str = str(s["value"]) if s["value"] is not None else ""
            if len(val_str) > 45:
                val_str = val_str[:42] + "…"
            table.add_row(s["key"], val_str)

        self.query_one("#raw-preview", Static).update(get_raw_text())
        self._update_status("Config loaded. Select a key to view details.")

    def on_data_table_row_highlighted(
        self, event: DataTable.RowHighlighted
    ) -> None:
        if event.cursor_row is None:
            return
        idx = event.cursor_row
        if idx >= len(self._settings):
            return
        setting = self._settings[idx]
        self._selected_key = setting["key"]
        self._update_detail(setting)

    def _update_detail(self, setting: dict) -> None:
        key      = setting["key"]
        value    = setting["value"]
        desc     = setting["description"] or "No description available."
        editable = setting["editable"]

        pending_note = ""
        if key in self._pending:
            pending_note = f"\n[yellow]⏳ Pending: {self._pending[key]}[/]"

        detail = (
            f"[bold #cba6f7]{key}[/]\n"
            f"\n"
            f"[#89b4fa]Current value:[/]  [#cdd6f4]{value}[/]"
            f"{pending_note}\n"
            f"\n"
            f"[#89b4fa]Description:[/]\n"
            f"[#a6adc8]{desc}[/]\n"
        )

        if not editable:
            detail += (
                "\n[#6c7086]This value is a list or nested table.\n"
                "Edit it manually in the raw config.[/]"
            )

        self.query_one("#detail-content", Static).update(detail)

        if editable:
            inp = self.query_one("#edit-input", Input)
            inp.value = str(value) if value is not None else ""
            self.query_one("#validation-msg", Label).update("")

    def on_input_changed(self, event: Input.Changed) -> None:
        if not self._selected_key:
            return
        raw = event.value
        if not raw:
            self.query_one("#validation-msg", Label).update("")
            return
        ok, _, error = validate_value(self._selected_key, raw)
        if ok:
            self.query_one("#validation-msg", Label).update(
                "[green]✔  Valid[/]"
            )
        else:
            self.query_one("#validation-msg", Label).update(
                f"[red]✖  {error}[/]"
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-apply":
            self.action_edit_selected()
        elif event.button.id == "btn-clear":
            self._pending = {}
            self._update_status("Pending edits cleared.")

    def action_edit_selected(self) -> None:
        if not self._selected_key:
            self._update_status("[yellow]Select a setting first.[/]")
            return

        setting = next(
            (s for s in self._settings if s["key"] == self._selected_key),
            None
        )
        if not setting or not setting["editable"]:
            self._update_status(
                "[yellow]This setting cannot be edited here.[/]"
            )
            return

        raw = self.query_one("#edit-input", Input).value
        ok, coerced, error = validate_value(self._selected_key, raw)
        if not ok:
            self._update_status(f"[red]✖  {error}[/]")
            return

        self._pending[self._selected_key] = coerced
        self._update_status(
            f"[yellow]Staged: {self._selected_key} = {coerced}  "
            f"({len(self._pending)} pending)[/]"
        )
        self._update_detail(setting)

    def action_save_changes(self) -> None:
        if not self._pending:
            self._update_status("[yellow]No pending changes to save.[/]")
            return

        count = len(self._pending)

        def on_confirm(confirmed: bool) -> None:
            if not confirmed:
                self._update_status("Save cancelled.")
                return
            create_backup(note="pre-config-edit")
            data = load_config()
            for key, value in self._pending.items():
                set_nested_value(data, key, value)
            if save_config(data):
                self._pending = {}
                self._load_settings()
                self._update_status(
                    f"[green]✔  Saved {count} change(s) to alacritty.toml[/]"
                )
            else:
                self._update_status(
                    "[red]✖  Failed to write config file.[/]"
                )

        self.app.push_screen(
            ConfirmDialog(
                title="Save Changes",
                message=f"Write {count} pending change(s) to alacritty.toml?"
            ),
            on_confirm
        )

    def action_refresh(self) -> None:
        self._load_settings()
        self._update_status("Refreshed from disk.")

    def _update_status(self, msg: str) -> None:
        try:
            self.query_one("#status-msg", Label).update(msg)
        except Exception:
            pass