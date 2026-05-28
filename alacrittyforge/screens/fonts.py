# ═══════════════════════════════════════════════════════════
#  AlacrittyForge — Fonts Screen
#  View and edit all font settings in alacritty.toml.
# ═══════════════════════════════════════════════════════════

from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Label, Static, DataTable, Input, Button
from textual.containers import Vertical, Horizontal, ScrollableContainer

from ..font_manager import (
    get_font_settings, apply_font_setting, list_system_fonts
)
from ..widgets.confirm_dialog import ConfirmDialog
from ..widgets.status import StatusMixin


class FontsScreen(StatusMixin, Static):
    """View and edit Alacritty font settings."""

    STATUS_WIDGET_ID = "fonts-status"
    # G4: focused on show so E/S/R fire on entry without a panel click.
    DEFAULT_FOCUS = "#fonts-table"

    BINDINGS = [
        Binding("e", "edit_selected", "Edit",    show=True),
        Binding("s", "save_changes",  "Save",    show=True),
        Binding("r", "refresh",       "Refresh", show=True),
    ]

    _settings: list[dict] = []
    _selected_index: int = 0
    _pending: dict = {}

    def compose(self) -> ComposeResult:
        with Horizontal():
            # ── Left: font settings table ──
            with Vertical(classes="main-area", id="fonts-left"):
                yield Label(
                    "🔤  Font Settings  (↑↓ navigate  •  E edit)",
                    classes="section-title"
                )
                yield DataTable(id="fonts-table", cursor_type="row")
                yield Label("", id="fonts-status")

            # ── Right: detail + edit panel ──
            with Vertical(classes="detail-panel", id="fonts-right"):
                yield Static(id="font-detail")

                yield Input(
                    placeholder="New value…",
                    id="font-input"
                )
                yield Label("", id="font-validation")

                with Horizontal():
                    yield Button("Apply Edit",    id="btn-apply",  classes="primary")
                    yield Button("Clear Pending", id="btn-clear",  classes="warning")

                yield Label(
                    "Pending edits are saved together when you press S",
                    classes="status-muted"
                )
                # G2 / A6: removed the redundant #font-save-status Label —
                # the unified status goes to #fonts-status (in the left
                # panel) plus a toast. No more dual writes of the same msg.

                # System fonts hint
                yield Label(
                    "── System Fonts ────────────────────",
                    classes="section-title"
                )
                with ScrollableContainer(id="system-fonts-container"):
                    yield Static(id="system-fonts-list")

    def on_mount(self) -> None:
        self._load_settings()
        self._load_system_fonts()

    def on_show(self) -> None:
        # G1 (A1): silent re-read so pending edits aren't clobbered on screen
        # switch. on_show used to call _load_settings(), which resets _pending.
        self._reload_view()

    def _load_settings(self) -> None:
        """Full init — clears pending, reloads, announces. Used by on_mount."""
        self._pending = {}
        self._reload_view()
        # Passive mount-time hint — status line only (G2: avoid startup spray).
        self._set_status("Font settings loaded.", "info", popup=False)

    def _reload_view(self) -> None:
        """Silent re-read from disk. Preserves _pending and selection."""
        self._settings = get_font_settings()

        table = self.query_one("#fonts-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Setting", "Value")

        for s in self._settings:
            val_str = str(s["value"]) if s["value"] not in (None, "") else "—"
            table.add_row(s["label"], val_str)

        # Re-render the detail panel for the current selection so any pending
        # edit stays visible after the reload.
        if self._selected_index < len(self._settings):
            self._show_detail(self._selected_index)

    def _load_system_fonts(self) -> None:
        """List available system fonts in the side panel."""
        fonts = list_system_fonts()
        if not fonts:
            self.query_one("#system-fonts-list", Static).update(
                "[#6c7086]fc-list not available or no fonts found.[/]"
            )
            return

        # Show first 40 fonts to keep it snappy
        display = fonts[:40]
        text = "\n".join(f"  [#a6adc8]{f}[/]" for f in display)
        if len(fonts) > 40:
            text += f"\n  [#6c7086]… and {len(fonts) - 40} more[/]"
        self.query_one("#system-fonts-list", Static).update(text)

    def on_data_table_row_highlighted(
        self, event: DataTable.RowHighlighted
    ) -> None:
        """Update detail panel on row change."""
        if event.cursor_row is None:
            return
        idx = event.cursor_row
        if idx >= len(self._settings):
            return
        self._selected_index = idx
        self._show_detail(idx)

    def _show_detail(self, idx: int) -> None:
        """Render detail panel for selected font setting."""
        if idx >= len(self._settings):
            return

        s = self._settings[idx]
        key   = s["key"]
        value = s["value"]
        desc  = s["description"]
        typ   = s["type"]

        pending_note = ""
        if key in self._pending:
            pending_note = f"\n[yellow]⏳ Pending: {self._pending[key]}[/]"

        detail = (
            f"[bold #cba6f7]{s['label']}[/]\n"
            f"[#6c7086]{key}[/]\n"
            f"\n"
            f"[#89b4fa]Current value:[/]  [#cdd6f4]{value if value not in (None, '') else '(not set)'}[/]"
            f"{pending_note}\n"
            f"\n"
            f"[#89b4fa]Type:[/]  [#a6adc8]{typ}[/]\n"
            f"\n"
            f"[#89b4fa]Description:[/]\n"
            f"[#a6adc8]{desc}[/]\n"
        )
        self.query_one("#font-detail", Static).update(detail)

        # Pre-fill input
        inp = self.query_one("#font-input", Input)
        inp.value = str(value) if value not in (None, "") else ""
        self.query_one("#font-validation", Label).update("")

    def on_input_changed(self, event: Input.Changed) -> None:
        """Live validate input."""
        if self._selected_index >= len(self._settings):
            return
        s   = self._settings[self._selected_index]
        raw = event.value.strip()

        if not raw:
            self.query_one("#font-validation", Label).update("")
            return

        # Simple type check
        typ = s["type"]
        ok, msg = self._validate(raw, typ)
        if ok:
            self.query_one("#font-validation", Label).update(
                "[green]✔  Valid[/]"
            )
        else:
            self.query_one("#font-validation", Label).update(
                f"[red]✖  {msg}[/]"
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-apply":
            self.action_edit_selected()
        elif event.button.id == "btn-clear":
            self._pending = {}
            self._set_status("Pending edits cleared.", "info")

    def action_edit_selected(self) -> None:
        """Stage the current input as a pending edit."""
        if self._selected_index >= len(self._settings):
            self._set_status("Select a setting first.", "warn")
            return

        s   = self._settings[self._selected_index]
        raw = self.query_one("#font-input", Input).value.strip()

        ok, msg = self._validate(raw, s["type"])
        if not ok:
            self._set_status(msg, "error")
            return

        self._pending[s["key"]] = raw
        self._set_status(
            f"Staged: {s['label']} = {raw!r}  ({len(self._pending)} pending)",
            "warn",
        )
        self._show_detail(self._selected_index)

    def action_save_changes(self) -> None:
        """Save all pending edits after confirmation."""
        if not self._pending:
            self._set_status("No pending changes to save.", "warn")
            return

        count = len(self._pending)

        def on_confirm(confirmed: bool) -> None:
            if not confirmed:
                self._set_status("Save cancelled.", "info")
                return

            errors = []
            for key, raw in self._pending.items():
                ok, msg = apply_font_setting(key, raw)
                if not ok:
                    errors.append(msg)

            if errors:
                self._set_status(f"Errors: {' | '.join(errors)}", "error")
            else:
                self._pending = {}
                # _reload_view() so the success status below isn't briefly
                # flashed-over by _load_settings's "Font settings loaded." hint.
                self._reload_view()
                self._set_status(f"Saved {count} font setting(s).", "ok")

        self.app.push_screen(
            ConfirmDialog(
                title="Save Font Settings",
                message=f"Write {count} pending font change(s) to alacritty.toml?"
            ),
            on_confirm
        )

    def action_refresh(self) -> None:
        """Reload from disk — preserves staged pending edits (G1)."""
        self._reload_view()
        self._set_status("Refreshed from disk.", "info")

    def _validate(self, raw: str, typ: str) -> tuple[bool, str]:
        """Quick type validation for display purposes."""
        if typ == "bool":
            if raw.lower() in ("true", "false", "yes", "no", "1", "0"):
                return True, ""
            return False, "Expected true or false"
        if typ == "int":
            try:
                int(raw)
                return True, ""
            except ValueError:
                return False, "Expected a whole number"
        if typ == "float":
            try:
                val = float(raw)
                if val <= 0:
                    return False, "Must be greater than 0"
                return True, ""
            except ValueError:
                return False, "Expected a decimal number (e.g. 12.0)"
        return True, ""

    # _set_status is provided by StatusMixin (v0.1.1 G2 — unified feedback;
    # also closes A6: the old _update_status wrote the same message to both
    # #fonts-status and the now-removed #font-save-status label).