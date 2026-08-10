# ═══════════════════════════════════════════════════════════
#  AlacrittyForge — Main Application Shell (forgekit era)
#
#  v0.2.0: the sidebar / Header / Footer / HelpScreen chrome is replaced
#  by forgekit.ForgeApp — the shared Forge Suite shell. AlacrittyForge is
#  the suite's second forgekit adopter (after BitlaForge) and the one
#  that pushed form styling (Input/Select/DataTable) into the kit.
#  The five screens and all managers carry over unchanged.
# ═══════════════════════════════════════════════════════════

from textual.binding import Binding

from forgekit import ForgeApp, ShortcutsDialog, FORGE_CSS, GPL3_NOTICE

from . import __version__
from .screens.dashboard import DashboardScreen
from .screens.config_editor import ConfigEditorScreen
from .screens.themes import ThemesScreen
from .screens.fonts import FontsScreen
from .screens.keybindings import KeyBindingsScreen


MENU = [
    {"id": "dashboard",   "title": "Dashboard", "kind": "section"},
    {"id": "config",      "title": "Config",    "kind": "section"},
    {"id": "themes",      "title": "Themes",    "kind": "section"},
    {"id": "fonts",       "title": "Fonts",     "kind": "section"},
    {"id": "keybindings", "title": "Bindings",  "kind": "section"},
    {"id": "help",        "title": "Help",      "kind": "menu", "items": [
        ("Shortcuts", "s", "shortcuts"),
        ("License",   "l", "license"),
        ("About",     "a", "about"),
    ]},
    {"id": "quit",        "title": "Quit",      "kind": "action", "action": "quit"},
]

SHORTCUTS = [
    ("Ctrl+D or 1", "Dashboard"),
    ("Ctrl+C or 2", "Config"),
    ("Ctrl+T or 3", "Themes"),
    ("Ctrl+F or 4", "Fonts"),
    ("Ctrl+B or 5", "Key Bindings"),
    ("R",           "Refresh the current section"),
    ("Ctrl+H or ?", "Toggle this shortcuts window"),
    ("Esc",         "Close the open window"),
    ("Enter / ↑↓",  "Navigate open menus"),
    ("Ctrl+Q or Q", "Quit"),
    ("E / S",       "Config & Fonts: edit selected / save pending"),
    ("A",           "Themes: apply the selected theme"),
    ("H",           "Themes: toggle the install guide"),
    ("N / D",       "Bindings: new binding / delete selected"),
]

ABOUT = {
    "name": "AlacrittyForge",
    "version": __version__,
    "tagline": "A Forge Suite TUI for managing Alacritty terminal configuration.",
    "description": (
        "Browse and edit alacritty.toml, apply color themes, manage fonts "
        "and keyboard bindings — with validation, staged edits, and automatic "
        "backups before every write. User-space only; no root required."
    ),
    "authors": "Javier (jetomev) + Claude (Anthropic)",
    "license": "GPL-3.0-or-later",
    "links": [
        ("GitHub", "https://github.com/jetomev/alacrittyforge"),
        ("AUR",    "https://aur.archlinux.org/packages/alacrittyforge"),
    ],
}

# App-specific styling on top of the forgekit base (forms/DataTable/buttons
# now come from the kit — F-9). What remains: the two-panel layout, ListView
# (promotion candidate when a third app needs lists), and app text classes.
ALAC_CSS = """
.main-area { padding: 0 1 0 0; }
.section-title { color: #cba6f7; text-style: bold; margin-bottom: 1; }

.detail-panel { background: #181825; border: round #313244; padding: 1; margin-left: 1; }
.detail-title { color: #cba6f7; text-style: bold; margin-bottom: 1; }
.detail-key   { color: #89b4fa; }
.detail-value { color: #cdd6f4; }
.detail-muted { color: #6c7086; }
.status-ok    { color: #a6e3a1; }
.status-warn  { color: #f9e2af; }
.status-err   { color: #f38ba8; }
.status-info  { color: #89b4fa; }
.status-muted { color: #6c7086; }

DataTable { background: #1e1e2e; border: solid #313244; }
DataTable > .datatable--hover { background: #2a2a3d; }

ListView { background: #1e1e2e; border: solid #313244; }
ListItem { background: #1e1e2e; color: #cdd6f4; padding: 0 1; }
ListItem:hover { background: #313244; }
ListView > .listview--highlight { background: #45475a; color: #cdd6f4; }

#raw-preview-container, #theme-preview-container, #system-fonts-container {
    background: #181825; border: round #313244; padding: 0 1; height: 1fr;
}
SelectOverlay { background: #313244; border: solid #89b4fa; }
"""


class AlacShortcuts(ShortcutsDialog):
    """Shortcuts window that also closes on ? and q (kit CLOSE_KEYS)."""
    CLOSE_KEYS = ("question_mark", "q")


class AlacrittyForge(ForgeApp):
    """AlacrittyForge — Alacritty configuration TUI, on the forgekit shell."""

    APP_NAME = "⚡ AlacrittyForge"
    MENU = MENU
    SHORTCUTS = SHORTCUTS
    ABOUT = ABOUT
    LICENSE_NAME = "GPL-3.0-or-later"
    LICENSE_NOTICE = GPL3_NOTICE
    CSS = FORGE_CSS + ALAC_CSS

    BINDINGS = [
        # AlacrittyForge muscle memory.
        Binding("1", "activate('dashboard')",   show=False),
        Binding("2", "activate('config')",      show=False),
        Binding("3", "activate('themes')",      show=False),
        Binding("4", "activate('fonts')",       show=False),
        Binding("5", "activate('keybindings')", show=False),
        Binding("q", "activate('quit')",        show=False),
        Binding("question_mark", "toggle_shortcuts", show=False),
        # forgekit-convention menu accelerators.
        Binding("ctrl+d", "activate('dashboard')",   show=False, priority=True),
        Binding("ctrl+c", "activate('config')",      show=False, priority=True),
        Binding("ctrl+t", "activate('themes')",      show=False, priority=True),
        Binding("ctrl+f", "activate('fonts')",       show=False, priority=True),
        Binding("ctrl+b", "activate('keybindings')", show=False, priority=True),
        # Suite ruling (BitlaForge v0.2.1): Ctrl+H toggles Shortcuts directly.
        Binding("ctrl+h", "toggle_shortcuts", show=False, priority=True),
    ]

    def compose_sections(self):
        yield DashboardScreen(id="sec-dashboard")
        yield ConfigEditorScreen(id="sec-config")
        yield ThemesScreen(id="sec-themes")
        yield FontsScreen(id="sec-fonts")
        yield KeyBindingsScreen(id="sec-keybindings")

    def on_section_shown(self, section_id: str) -> None:
        """Refresh-on-show + focus the section's primary widget (G4)."""
        try:
            screen = self.query_one(f"#sec-{section_id}")
        except Exception:
            return
        if hasattr(screen, "on_show"):
            try:
                screen.on_show()
            except Exception:
                pass
        focus_id = getattr(screen, "DEFAULT_FOCUS", None)
        if focus_id:
            try:
                self.query_one(focus_id).focus()
            except Exception:
                pass

    def action_act(self, action_id: str) -> None:
        if action_id == "shortcuts":
            self.push_screen(AlacShortcuts(self.SHORTCUTS))
        else:
            super().action_act(action_id)

    def action_toggle_shortcuts(self) -> None:
        """`?` / Ctrl+H toggles the shortcuts window."""
        if isinstance(self.screen, ShortcutsDialog):
            self.pop_screen()
        else:
            self.push_screen(AlacShortcuts(self.SHORTCUTS))
