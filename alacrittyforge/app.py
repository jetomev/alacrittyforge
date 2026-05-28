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
from .widgets.help_screen import HelpScreen


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

        try:
            screen = self.query_one(f"#{screen_id}")
        except Exception:
            return

        # Notify the active screen to refresh its data.
        if hasattr(screen, "on_show"):
            try:
                screen.on_show()
            except Exception:
                pass

        # G4 (A4): focus the screen's primary widget so its key bindings
        # (E/S/R on Config Editor, A/F5/H on Themes, E/S/R on Fonts,
        # N/D/R on Key Bindings) fire immediately on screen entry without
        # needing a click into the panel first. ContentSwitcher doesn't
        # move focus on its own; without this, those keys are inert until
        # the user clicks the table/list.
        focus_id = getattr(screen, "DEFAULT_FOCUS", None)
        if focus_id:
            try:
                self.query_one(focus_id).focus()
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
        """Toggle the help overlay.

        A2: previously this always push_screen'd a fresh HelpScreen, so
        pressing ? twice stacked two modals. Now it toggles — if the top
        screen is already a HelpScreen, pop it; otherwise push.
        """
        if isinstance(self.screen, HelpScreen):
            self.pop_screen()
        else:
            self.push_screen(HelpScreen())