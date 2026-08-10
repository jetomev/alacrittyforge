# ═══════════════════════════════════════════════════════════
#  AlacrittyForge — Fonts Screen (v0.2.0 redesign)
#
#  Javier's ruling: "exactly like Config and Bindings" — ONE table
#  (Setting / Value / Staged), in-place editing: families open the
#  filterable mono-font picker, styles get dropdowns, numbers get the
#  floating editor. Fixed footer: Apply Edit · Clear Pending · Save
#  Changes (single backup, one bulk write).
# ═══════════════════════════════════════════════════════════

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Label, Static

from forgekit import ConfirmDialog, MenuDropdown

from ..font_manager import get_font_settings, apply_font_settings_bulk
from ..field_options import get_options
from ..widgets.picker import FilterPickerModal
from ..widgets.status import StatusMixin
from .config_editor import FieldEditModal


class FontsScreen(StatusMixin, Static):
    """One-table, in-place editor for Alacritty font settings."""

    STATUS_WIDGET_ID = "fonts-status"
    DEFAULT_FOCUS = "#fonts-table"

    BINDINGS = [
        Binding("e", "edit_selected", "Edit",    show=True),
        Binding("s", "save_changes",  "Save",    show=True),
        Binding("r", "refresh",       "Refresh", show=True),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._settings: list[dict] = []
        self._pending: dict = {}

    def compose(self) -> ComposeResult:
        with Vertical(classes="main-area"):
            yield Label(
                "🔤  Font Settings  (↑↓ navigate · E/Enter edit · S save)",
                classes="section-title",
            )
            yield DataTable(id="fonts-table", cursor_type="row")
            with Horizontal(classes="forge-buttons forge-panel-footer",
                            id="fonts-footer"):
                yield Button("Apply Edit",    id="btn-apply", variant="primary")
                yield Button("Clear Pending", id="btn-clear")
                yield Button("Save Changes",  id="btn-save", variant="primary")
            yield Label("", id="fonts-status")

    def on_mount(self) -> None:
        self._reload_view()
        self._set_status(
            "Select a setting and press E (or Enter) — families open the "
            "font picker.", "info", popup=False,
        )

    def on_show(self) -> None:
        self._reload_view()

    # ── table ─────────────────────────────────────────────────────────

    def _reload_view(self) -> None:
        self._settings = get_font_settings()

        table = self.query_one("#fonts-table", DataTable)
        cursor = table.cursor_row
        table.clear(columns=True)
        table.add_columns("Setting", "Value", "Staged")
        for s in self._settings:
            val = str(s["value"]) if s["value"] not in (None, "") else "—"
            staged = (f"⏳ {self._pending[s['key']]}"
                      if s["key"] in self._pending else "")
            table.add_row(s["label"], val, staged)
        if cursor is not None and 0 <= cursor < len(self._settings):
            try:
                table.move_cursor(row=cursor)
            except Exception:
                pass

    def _selected(self) -> dict | None:
        table = self.query_one("#fonts-table", DataTable)
        idx = table.cursor_row
        if idx is None or idx >= len(self._settings):
            return None
        return self._settings[idx]

    def on_data_table_row_selected(self, e) -> None:
        self.action_edit_selected()

    # ── editing ───────────────────────────────────────────────────────

    def action_edit_selected(self) -> None:
        setting = self._selected()
        if setting is None:
            self._set_status("Select a setting first.", "warn")
            return
        key = setting["key"]
        current = self._pending.get(key, setting["value"])
        current_s = str(current) if current not in (None, "") else ""
        options = get_options(key, current_s or None)

        if options and len(options) > 12:
            self.app.push_screen(
                FilterPickerModal(f"Select — {setting['label']}", options,
                                  current_s),
                lambda choice, k=key: self._stage(k, choice),
            )
        elif options:
            self._open_dropdown(options,
                                lambda choice, k=key: self._stage(k, choice))
        else:
            self.app.push_screen(
                FieldEditModal(setting["label"], current_s,
                               setting.get("description", "")),
                lambda raw, k=key: self._stage(k, raw),
            )

    def _open_dropdown(self, options: list[str], cb) -> None:
        table = self.query_one("#fonts-table", DataTable)
        r = table.region
        row = table.cursor_row or 0
        y_off = 1 + row - int(table.scroll_offset.y)
        y = r.y + max(1, min(y_off, max(1, r.height - 1)))
        try:
            key_w = table.ordered_columns[0].get_render_width(table)
        except Exception:
            key_w = 22
        x = max(r.x, min(r.x + key_w + 1, r.x + r.width - 24))
        items = [(o, str(i + 1) if i < 9 else "", o)
                 for i, o in enumerate(options)]
        self.app.push_screen(MenuDropdown(items, x, y),
                             lambda c: cb(c) if c is not None else None)

    def _stage(self, key: str, raw) -> None:
        if raw is None:
            return
        self._pending[key] = str(raw)
        self._reload_view()
        self._set_status(
            f"Staged: {key} = {raw or '(blank — inherit)'}  "
            f"({len(self._pending)} pending)", "warn",
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
        summary = "\n".join(f"  {k} = {v}" for k, v in self._pending.items())

        def on_confirm(confirmed: bool) -> None:
            if not confirmed:
                self._set_status("Save cancelled.", "info")
                return
            ok, msg = apply_font_settings_bulk(dict(self._pending))
            if ok:
                self._pending = {}
                self._reload_view()
                self._set_status(msg or f"Saved {count} font change(s).", "ok")
            else:
                self._set_status(msg, "error")

        self.app.push_screen(
            ConfirmDialog(
                f"Write {count} font change(s) to alacritty.toml?\n\n{summary}",
                "Save",
            ),
            on_confirm,
        )

    def action_refresh(self) -> None:
        self._reload_view()
        self._set_status("Font settings reloaded from disk.", "info")
