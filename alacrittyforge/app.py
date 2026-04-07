# ═══════════════════════════════════════════════════════════
#  AlacrittyForge — Main Application Shell
#  Textual TUI app with sidebar navigation and screen tabs.
# ═══════════════════════════════════════════════════════════

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer, Label, ContentSwitcher
from textual.containers import Horizontal, Vertical

from .screens.dashboard import DashboardScreen
from .screens.config_editor import ConfigEditorScreen
from .screens.themes import ThemesScreen
from .screens.fonts import FontsScreen
from .screens.keybindings import KeyBindingsScreen


class AlacrittyForge(App):
    """AlacrittyForge — A TUI for managing Alacritty configuration."""

    CSS_PATH = "alacrittyforge.css"

    BINDINGS = [
        Binding("1", "show_screen('dashboard')",   "Dashboard",    show=True),
        Binding("2", "show_screen('config')",       "Config",       show=True),
        Binding("3", "show_screen('themes')",       "Themes",       show=True),
        Binding("4", "show_screen('fonts')",        "Fonts",        show=True),
        Binding("5", "show_screen('keybindings')", "Key Bindings", show=True),
        Binding("q", "quit",                        "Quit",         show=True),
        Binding("question_mark", "show_help",       "Help",         show=True),
    ]

    # Track which nav item is active
    _current_screen: str = "dashboard"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)

        with Horizontal():
            # ── Sidebar ──
            with Vertical(classes="sidebar"):
                yield Label("⚡ AlacrittyForge", classes="sidebar-title")
                yield Label("1  🏠  Dashboard",    id="nav-dashboard",   classes="nav-item --active")
                yield Label("2  🔧  Config",        id="nav-config",      classes="nav-item")
                yield Label("3  🎨  Themes",        id="nav-themes",      classes="nav-item")
                yield Label("4  🔤  Fonts",         id="nav-fonts",       classes="nav-item")
                yield Label("5  ⌨   Key Bindings",  id="nav-keybindings", classes="nav-item")

            # ── Main content area ──
            with ContentSwitcher(initial="dashboard", id="content"):
                yield DashboardScreen(id="dashboard")
                yield ConfigEditorScreen(id="config")
                yield ThemesScreen(id="themes")
                yield FontsScreen(id="fonts")
                yield KeyBindingsScreen(id="keybindings")

        yield Footer()

    def action_show_screen(self, screen_id: str) -> None:
        """Switch the visible screen and update sidebar highlight."""
        self._current_screen = screen_id
        self.query_one("#content", ContentSwitcher).current = screen_id
        self._update_nav(screen_id)

        # Notify the active screen to refresh its data
        try:
            screen = self.query_one(f"#{screen_id}")
            if hasattr(screen, "on_show"):
                screen.on_show()
        except Exception:
            pass

    def _update_nav(self, active_id: str) -> None:
        """Update sidebar nav item highlight."""
        nav_ids = [
            "nav-dashboard",
            "nav-config",
            "nav-themes",
            "nav-fonts",
            "nav-keybindings",
        ]
        for nav_id in nav_ids:
            try:
                label = self.query_one(f"#{nav_id}", Label)
                # Remove --active, re-add only for the active one
                classes = set(label.classes)
                classes.discard("--active")
                if nav_id == f"nav-{active_id}":
                    classes.add("--active")
                label.set_classes(" ".join(classes))
            except Exception:
                pass

    def action_show_help(self) -> None:
        """Show a help overlay with all keybindings."""
        from textual.widgets import Label
        from textual.screen import ModalScreen
        from textual.app import ComposeResult
        from textual.containers import Vertical
        from textual.widgets import Button

        class HelpScreen(ModalScreen):
            DEFAULT_CSS = """
            HelpScreen {
                align: center middle;
            }
            HelpScreen > Vertical {
                background: #181825;
                border: solid #cba6f7;
                padding: 2 4;
                width: 70;
                height: auto;
            }
            HelpScreen .help-title {
                color: #cba6f7;
                text-style: bold;
                text-align: center;
                margin-bottom: 1;
            }
            HelpScreen .help-line {
                color: #cdd6f4;
            }
            HelpScreen .help-key {
                color: #89b4fa;
            }
            HelpScreen .help-section {
                color: #f9e2af;
                text-style: bold;
                margin-top: 1;
            }
            """

            BINDINGS = [
                Binding("escape", "dismiss", "Close"),
                Binding("q",      "dismiss", "Close"),
            ]

            def compose(self) -> ComposeResult:
                with Vertical():
                    yield Label("⚡ AlacrittyForge — Help", classes="help-title")
                    yield Label("── Global ──────────────────────────────", classes="help-section")
                    yield Label("  1-5    Switch screens",         classes="help-line")
                    yield Label("  q      Quit",                   classes="help-line")
                    yield Label("  ?      This help screen",       classes="help-line")
                    yield Label("── Config Editor ───────────────────────", classes="help-section")
                    yield Label("  E      Edit selected value",    classes="help-line")
                    yield Label("  S      Save all changes",       classes="help-line")
                    yield Label("  R      Refresh from disk",      classes="help-line")
                    yield Label("── Themes ──────────────────────────────", classes="help-section")
                    yield Label("  A      Apply selected theme",   classes="help-line")
                    yield Label("  F5     Refresh theme list",     classes="help-line")
                    yield Label("  H      Toggle install guide",   classes="help-line")
                    yield Label("── Fonts ───────────────────────────────", classes="help-section")
                    yield Label("  E      Edit selected value",    classes="help-line")
                    yield Label("  S      Save all changes",       classes="help-line")
                    yield Label("  R      Refresh from disk",      classes="help-line")
                    yield Label("── Key Bindings ────────────────────────", classes="help-section")
                    yield Label("  N      New binding",            classes="help-line")
                    yield Label("  D      Delete selected",        classes="help-line")
                    yield Label("  R      Refresh",                classes="help-line")
                    yield Label("── Backup (in Config Editor) ───────────", classes="help-section")
                    yield Label("  Backups created automatically", classes="help-line")
                    yield Label("  before every save.",            classes="help-line")
                    yield Label("", classes="help-line")
                    yield Label("  Press Escape or Q to close",    classes="help-section")

            def action_dismiss(self) -> None:
                self.app.pop_screen()

        self.push_screen(HelpScreen())