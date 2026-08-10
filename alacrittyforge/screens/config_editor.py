# ═══════════════════════════════════════════════════════════
#  AlacrittyForge — Config Editor Screen (v0.2.0 redesign)
#
#  Javier's ruling: ONE table (Key / Value / Staged), values edited
#  in place — enumerable keys get an anchored DROPDOWN at the cell
#  (typos impossible), free-text keys get a small floating editor.
#  Below the table, a window-style fixed footer (divider + buttons,
#  always visible regardless of scroll): Apply Edit · Clear Pending ·
#  Save Changes. No right panel, no section-hopping to write the file.
# ═══════════════════════════════════════════════════════════

import re

from rich.text import Text

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, DataTable, Input, Label, Static

from forgekit import ConfirmDialog, ForgeModal, MenuDropdown

from ..config_manager import (
    load_config, save_config, get_flat_settings,
    validate_value, set_nested_value,
)
from ..backup_manager import create_backup
from ..field_options import get_options
from ..widgets.picker import FilterPickerModal
from ..widgets.status import StatusMixin

_HEX_RE = re.compile(r"^#[0-9a-fA-F]{6}$")


def _render_value(val: str) -> Text | str:
    """Color values get a live swatch square before the hex (finding #5)."""
    if _HEX_RE.match(val):
        t = Text()
        t.append("■ ", style=val)
        t.append(val)
        return t
    return val


class FieldEditModal(ForgeModal):
    """Small floating editor for free-text keys (kit window language)."""

    BINDINGS = [Binding("escape", "cancel", "", show=False)]

    def __init__(self, key: str, current: str, description: str) -> None:
        super().__init__()
        self._key, self._current, self._desc = key, current, description

    def compose(self) -> ComposeResult:
        with Vertical(classes="forge-panel field-edit"):
            yield Static(f"Edit — {self._key}", classes="forge-panel-title")
            with VerticalScroll(classes="forge-panel-body"):
                if self._desc:
                    yield Static(f"[#a6adc8]{self._desc}[/]")
                yield Label("New value")
                yield Input(value=self._current, id="field-input")
            with Horizontal(classes="forge-buttons forge-panel-footer"):
                yield Button("Stage", id="stage", variant="primary")
                yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        self.query_one("#field-input", Input).focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)

    def on_button_pressed(self, e: Button.Pressed) -> None:
        if e.button.id == "stage":
            self.dismiss(self.query_one("#field-input", Input).value)
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)


class ConfigEditorScreen(StatusMixin, Static):
    """Single-table config editor with in-place value editing."""

    STATUS_WIDGET_ID = "status-msg"
    DEFAULT_FOCUS = "#settings-table"

    BINDINGS = [
        Binding("e",     "edit_selected", "Edit",    show=True),
        Binding("s",     "save_changes",  "Save",    show=True),
        Binding("r",     "refresh",       "Refresh", show=True),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._pending: dict = {}
        self._settings: list[dict] = []

    def compose(self) -> ComposeResult:
        with Vertical(classes="main-area"):
            yield Label(
                "🔧  Config Keys  (↑↓ navigate · E/Enter edit · S save)",
                classes="section-title",
            )
            yield DataTable(id="settings-table", cursor_type="row")
            with Horizontal(classes="forge-buttons forge-panel-footer",
                            id="config-footer"):
                yield Button("Apply Edit",    id="btn-apply", variant="primary")
                yield Button("Clear Pending", id="btn-clear")
                yield Button("Save Changes",  id="btn-save", variant="primary")
            yield Label("", id="status-msg")

    def on_mount(self) -> None:
        self._reload_view()
        self._set_status(
            "Select a key and press E (or Enter) to edit its value.",
            "info", popup=False,
        )

    def on_show(self) -> None:
        # Silent re-read (G1) — staged edits survive section switches.
        self._reload_view()

    # ── table ─────────────────────────────────────────────────────────

    def _reload_view(self) -> None:
        data = load_config()
        self._settings = get_flat_settings(data)

        table = self.query_one("#settings-table", DataTable)
        cursor = table.cursor_row
        table.clear(columns=True)
        table.add_columns("Key", "Value", "Staged")

        for s in self._settings:
            val = str(s["value"]) if s["value"] is not None else ""
            if len(val) > 40:
                val = val[:37] + "…"
            if s["key"] in self._pending:
                pend = str(self._pending[s["key"]])
                if _HEX_RE.match(pend):
                    staged = Text("⏳ ")
                    staged.append("■ ", style=pend)
                    staged.append(pend)
                else:
                    staged = f"⏳ {pend}"
            else:
                staged = ""
            table.add_row(s["key"], _render_value(val), staged)

        if cursor is not None and 0 <= cursor < len(self._settings):
            try:
                table.move_cursor(row=cursor)
            except Exception:
                pass

    def _selected_setting(self) -> dict | None:
        table = self.query_one("#settings-table", DataTable)
        idx = table.cursor_row
        if idx is None or idx >= len(self._settings):
            return None
        return self._settings[idx]

    def on_data_table_row_selected(self, e: DataTable.RowSelected) -> None:
        # Enter or click on a row = edit its value in place.
        self.action_edit_selected()

    # ── editing ───────────────────────────────────────────────────────

    def action_edit_selected(self) -> None:
        setting = self._selected_setting()
        if setting is None:
            self._set_status("Select a setting first.", "warn")
            return
        if not setting["editable"]:
            self._set_status(
                "This value is a list or nested table — edit it in the raw "
                "config file.", "warn",
            )
            return

        key = setting["key"]
        current = self._pending.get(key, setting["value"])
        options = get_options(key, current)

        if options and len(options) > 12:
            self.app.push_screen(
                FilterPickerModal(f"Select — {key}", options,
                                  str(current) if current is not None else ""),
                lambda choice, k=key: self._stage(k, choice),
            )
        elif options:
            self._open_dropdown(key, options)
        else:
            self.app.push_screen(
                FieldEditModal(key, str(current) if current is not None else "",
                               setting.get("description", "")),
                lambda raw, k=key: self._stage(k, raw),
            )

    def _open_dropdown(self, key: str, options: list[str]) -> None:
        """Anchored dropdown at the table cursor — the no-typos editor."""
        table = self.query_one("#settings-table", DataTable)
        r = table.region
        row = table.cursor_row or 0
        # header row (1) + row offset − scroll; clamp inside the table.
        y_off = 1 + row - int(table.scroll_offset.y)
        y = r.y + max(1, min(y_off, max(1, r.height - 1)))
        # Anchor at the VALUE column (finding #2), not over the keys.
        try:
            key_w = table.ordered_columns[0].get_render_width(table)
        except Exception:
            key_w = max((len(s["key"]) for s in self._settings), default=20) + 2
        x = max(r.x, min(r.x + key_w + 1, r.x + r.width - 24))
        items = [(opt, str(i + 1) if i < 9 else "", opt)
                 for i, opt in enumerate(options)]
        self.app.push_screen(
            MenuDropdown(items, x, y),
            lambda choice, k=key: self._stage(k, choice),
        )

    def _stage(self, key: str, raw) -> None:
        if raw is None:
            return
        ok, coerced, error = validate_value(key, str(raw))
        if not ok:
            self._set_status(error, "error")
            return
        self._pending[key] = coerced
        self._reload_view()
        self._set_status(
            f"Staged: {key} = {coerced}  ({len(self._pending)} pending)",
            "warn",
        )

    # ── footer actions ────────────────────────────────────────────────

    def on_button_pressed(self, e: Button.Pressed) -> None:
        if e.button.id == "btn-apply":
            self.action_edit_selected()
        elif e.button.id == "btn-clear":
            self._pending = {}
            self._reload_view()
            self._set_status("Pending edits cleared.", "info")
        elif e.button.id == "btn-save":
            self.action_save_changes()

    def action_save_changes(self) -> None:
        if not self._pending:
            self._set_status("No pending changes to save.", "warn")
            return
        count = len(self._pending)

        def on_confirm(confirmed: bool) -> None:
            if not confirmed:
                self._set_status("Save cancelled.", "info")
                return
            create_backup(note="pre-config-edit")
            data = load_config()
            for key, value in self._pending.items():
                set_nested_value(data, key, value)
            if save_config(data):
                self._pending = {}
                self._reload_view()
                self._set_status(
                    f"Saved {count} change(s) to alacritty.toml", "ok",
                )
            else:
                self._set_status("Failed to write config file.", "error")

        summary = "\n".join(
            f"  {k} = {v}" for k, v in list(self._pending.items())[:8]
        )
        if count > 8:
            summary += f"\n  … and {count - 8} more"
        self.app.push_screen(
            ConfirmDialog(
                f"Write {count} pending change(s) to alacritty.toml?\n\n{summary}",
                "Save",
            ),
            on_confirm,
        )

    def action_refresh(self) -> None:
        self._reload_view()
        self._set_status("Refreshed from disk.", "info")
