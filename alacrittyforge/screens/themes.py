# ═══════════════════════════════════════════════════════════
#  AlacrittyForge — Themes Screen
#  Browse, preview, and apply Alacritty color themes.
# ═══════════════════════════════════════════════════════════

from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Label, Static, ListView, ListItem, Button
from textual.containers import Vertical, Horizontal, ScrollableContainer

from ..theme_manager import (
    list_themes, apply_theme, get_theme_raw_text, get_themes_help_text
)
from ..widgets.confirm_dialog import ConfirmDialog
from ..widgets.status import StatusMixin


class ThemesScreen(StatusMixin, Static):
    """Browse and apply Alacritty color themes."""

    STATUS_WIDGET_ID = "themes-status"

    BINDINGS = [
        Binding("a",  "apply_theme",    "Apply",   show=True),
        Binding("f5", "refresh",        "Refresh", show=True),
        Binding("h",  "toggle_help",    "Help",    show=True),
    ]

    _themes: list[dict] = []
    _selected_index: int = 0
    _show_help: bool = False

    def compose(self) -> ComposeResult:
        with Horizontal():
            # ── Left: theme list ──
            with Vertical(classes="main-area", id="themes-left"):
                yield Label(
                    "🎨  Themes  (A apply  •  F5 refresh  •  H help)",
                    classes="section-title"
                )
                yield ListView(id="themes-list")
                yield Label("", id="themes-status")

            # ── Right: detail panel ──
            with Vertical(classes="detail-panel", id="themes-right"):
                yield Static(id="theme-detail")

                with Horizontal():
                    yield Button("Apply Theme", id="btn-apply",   classes="primary")
                    yield Button("Refresh",     id="btn-refresh", classes="accent")
                    yield Button("? Help",      id="btn-help",    classes="warning")

                yield Label(
                    "Color Palette",
                    classes="section-title"
                )
                yield Static(id="theme-palette")

                yield Label(
                    "theme.toml Preview",
                    classes="section-title"
                )
                with ScrollableContainer(id="theme-preview-container"):
                    yield Static(id="theme-preview")

    def on_mount(self) -> None:
        self._load_themes()

    def on_show(self) -> None:
        # G2: silent re-read on screen show so we don't spray a "Found N
        # themes" toast every time the user navigates to this tab.
        self._reload_view()

    def _load_themes(self) -> None:
        """Full init — scan themes, populate the list, announce. on_mount only."""
        self._reload_view()
        # Passive mount-time hint — status line only, no startup popup.
        if self._themes:
            self._set_status(
                f"Found {len(self._themes)} theme(s) in ~/.config/alacritty/themes",
                "ok", popup=False,
            )
        else:
            self._set_status(
                "No themes found. Press H for installation help.",
                "warn", popup=False,
            )

    def _reload_view(self) -> None:
        """Silent re-read — populate list, no status emission."""
        self._themes = list_themes()
        lv = self.query_one("#themes-list", ListView)
        lv.clear()

        if not self._themes:
            lv.append(ListItem(Label("  No themes found in ~/.config/alacritty/themes/")))
            self.query_one("#theme-detail", Static).update(
                "[#6c7086]No themes installed.\n\n"
                "Press [bold #89b4fa]H[/] to open the installation guide.[/]"
            )
            return

        for theme in self._themes:
            active_marker = " [green]active[/]" if theme["active"] else ""
            count = len(theme["colors"])
            lv.append(ListItem(
                Label(
                    f"  {theme['name']}{active_marker}\n"
                    f"  [#6c7086]{count} colors detected[/]"
                )
            ))

        # Show first theme detail
        if self._themes:
            self._show_theme_detail(0)

    def on_list_view_highlighted(
        self, event: ListView.Highlighted
    ) -> None:
        """Update detail panel when selection changes."""
        if event.item is None:
            return
        try:
            idx = list(
                self.query_one("#themes-list", ListView).children
            ).index(event.item)
            self._selected_index = idx
            self._show_theme_detail(idx)
        except Exception:
            pass

    def _show_theme_detail(self, idx: int) -> None:
        """Render theme detail, palette, and preview."""
        if idx >= len(self._themes):
            return

        theme = self._themes[idx]
        active_str = (
            "[green]currently active[/]"
            if theme["active"] else ""
        )

        detail = (
            f"[bold #cba6f7]{theme['name']}[/]  {active_str}\n"
            f"\n"
            f"[#89b4fa]Path:  [/][#cdd6f4]{theme['path']}[/]\n"
        )
        self.query_one("#theme-detail", Static).update(detail)

        # Color palette
        palette_lines = []
        for color in theme["colors"]:
            hex_val = color["hex"]
            label   = color["label"]
            swatch  = self._hex_to_markup(hex_val)
            palette_lines.append(
                f"  {swatch}  [#a6adc8]{label:<28}[/]  [#6c7086]{hex_val}[/]"
            )

        palette_text = "\n".join(palette_lines) if palette_lines else (
            "[#6c7086]No colors detected in this theme.[/]"
        )
        self.query_one("#theme-palette", Static).update(palette_text)

        # Raw preview
        raw = get_theme_raw_text(theme["path"])
        # Show first 60 lines only
        lines = raw.splitlines()[:60]
        preview = "\n".join(lines)
        if len(raw.splitlines()) > 60:
            preview += "\n[#6c7086]… (truncated)[/]"
        self.query_one("#theme-preview", Static).update(preview)

    def _hex_to_markup(self, hex_val: str) -> str:
        """Return a colored block character for a hex color."""
        try:
            h = hex_val.lstrip("#")
            if len(h) == 6:
                return f"[{hex_val}]█[/]"
        except Exception:
            pass
        return "▪"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-apply":
            self.action_apply_theme()
        elif event.button.id == "btn-refresh":
            self.action_refresh()
        elif event.button.id == "btn-help":
            self.action_toggle_help()

    def action_apply_theme(self) -> None:
        """Apply the selected theme after confirmation."""
        if not self._themes:
            self._set_status("No themes available.", "warn")
            return

        idx = self._selected_index
        if idx >= len(self._themes):
            return

        theme = self._themes[idx]

        def on_confirm(confirmed: bool) -> None:
            if not confirmed:
                self._set_status("Apply cancelled.", "info")
                return
            ok, msg = apply_theme(theme["path"])
            if ok:
                # _reload_view() (not _load_themes) so the success status
                # below isn't briefly flashed-over by the "Found N themes"
                # passive hint that _load_themes would emit.
                self._reload_view()
                self._set_status(msg, "ok")
            else:
                self._set_status(msg, "error")

        self.app.push_screen(
            ConfirmDialog(
                title="Apply Theme",
                message=f"Apply theme '{theme['name']}' to alacritty.toml?"
            ),
            on_confirm
        )

    def action_refresh(self) -> None:
        """Rescan themes directory."""
        self._reload_view()
        self._set_status("Theme list refreshed.", "info")

    def action_toggle_help(self) -> None:
        """Toggle the installation help overlay."""
        self._show_help = not self._show_help

        if self._show_help:
            help_text = get_themes_help_text()
            self.query_one("#theme-preview", Static).update(help_text)
            self.query_one("#theme-palette", Static).update("")
            self.query_one("#theme-detail", Static).update(
                "[bold #f9e2af]Theme Installation Guide[/]\n"
                "[#6c7086]Press H again to return to theme browser.[/]"
            )
            self._set_status("Showing installation help. Press H to close.", "warn")
        else:
            if self._themes:
                self._show_theme_detail(self._selected_index)
            self._set_status("Returned to theme browser.", "info")

    # _set_status is provided by StatusMixin (v0.1.1 G2 — unified feedback).