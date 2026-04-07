# ═══════════════════════════════════════════════════════════
#  AlacrittyForge — Dashboard Screen
#  System overview: config status, active settings, backups.
# ═══════════════════════════════════════════════════════════

from textual.app import ComposeResult
from textual.widgets import Label, Static
from textual.containers import Vertical, Horizontal

from ..config_manager import (
    config_exists, load_config, get_raw_text,
    get_active_theme, get_font_name, get_font_size, get_opacity
)
from ..backup_manager import get_backup_count, BACKUP_DIR, CONFIG_PATH


class DashboardScreen(Static):
    """Home screen showing Alacritty config status and overview."""

    def compose(self) -> ComposeResult:
        with Vertical(classes="main-area"):
            yield Label(
                "AlacrittyForge — System Overview",
                classes="section-title"
            )
            yield _DashboardContent(id="dashboard-content")

    def on_show(self) -> None:
        """Refresh data when screen becomes visible."""
        try:
            self.query_one("#dashboard-content", _DashboardContent).refresh_data()
        except Exception:
            pass


class _DashboardContent(Static):
    """The actual dashboard content, refreshable."""

    def compose(self) -> ComposeResult:
        yield Static(id="dashboard-body")

    def on_mount(self) -> None:
        self.refresh_data()

    def refresh_data(self) -> None:
        """Re-read config and update all displayed values."""
        exists   = config_exists()
        data     = load_config() if exists else {}
        count    = get_backup_count()
        theme    = get_active_theme(data)   if exists else "—"
        font     = get_font_name(data)      if exists else "—"
        size     = get_font_size(data)      if exists else "—"
        opacity  = get_opacity(data)        if exists else "—"

        # Config status
        if exists:
            cfg_status  = "[green]✔  Found[/]"
            cfg_path    = f"[green]{CONFIG_PATH}[/]"
        else:
            cfg_status  = "[red]✖  Not found[/]"
            cfg_path    = "[red]~/.config/alacritty/alacritty.toml[/]"

        # Backup status
        if count == 0:
            bak_str = "[yellow]0  (no backups yet)[/]"
        else:
            bak_str = f"[green]{count}[/]  saved in {BACKUP_DIR}"

        # Theme status
        if theme == "none" or theme == "—":
            theme_str = "[yellow]none (using built-in colors)[/]"
        else:
            theme_str = f"[green]{theme}[/]"

        # Font status
        if font == "default" or font == "—":
            font_str = "[yellow]default (Alacritty built-in)[/]"
        else:
            font_str = f"[green]{font}  {size}pt[/]"

        # Opacity
        try:
            op_val = float(opacity)
            if op_val < 1.0:
                opacity_str = f"[yellow]{opacity}  (transparent)[/]"
            else:
                opacity_str = f"[green]{opacity}  (opaque)[/]"
        except Exception:
            opacity_str = f"[green]{opacity}[/]"

        body = (
            "\n"
            "[bold #cba6f7]── Alacritty Config ──────────────────────────────────[/]\n"
            "\n"
            f"  [#89b4fa]Config file   [/]  {cfg_status}\n"
            f"  [#89b4fa]Path          [/]  {cfg_path}\n"
            "\n"
            "[bold #cba6f7]── Active Settings ───────────────────────────────────[/]\n"
            "\n"
            f"  [#89b4fa]Theme         [/]  {theme_str}\n"
            f"  [#89b4fa]Font          [/]  {font_str}\n"
            f"  [#89b4fa]Opacity       [/]  {opacity_str}\n"
            "\n"
            "[bold #cba6f7]── Backups ────────────────────────────────────────────[/]\n"
            "\n"
            f"  [#89b4fa]Backup count  [/]  {bak_str}\n"
            "\n"
            "[bold #cba6f7]── Quick Actions ─────────────────────────────────────[/]\n"
            "\n"
            "  Press [bold #b4befe]2[/]  to edit Config settings\n"
            "  Press [bold #b4befe]3[/]  to browse and apply Themes\n"
            "  Press [bold #b4befe]4[/]  to manage Fonts\n"
            "  Press [bold #b4befe]5[/]  to manage Key Bindings\n"
            "  Press [bold #b4befe]?[/]  for help\n"
        )

        self.query_one("#dashboard-body", Static).update(body)