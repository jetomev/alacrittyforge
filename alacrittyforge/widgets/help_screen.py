"""alacrittyForge — Help modal screen.

v0.1.1 G3 (A2): the help overlay used to be an inline-nested ModalScreen
class defined inside app.action_show_help, with that method calling
push_screen on every keypress — so pressing ? twice stacked two help
modals on top of each other. The modal bound escape and q to dismiss but
not ?, which is the key that *opened* it.

This is the extracted, dedicated module:
  • the app's action_show_help now toggles (pops if HelpScreen is already
    on top, else pushes), so it can never stack;
  • the modal binds ? itself, so a second ? closes it directly;
  • q is bound here so it shadows the app-level quit while help is up.
"""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import Label
from textual.containers import Vertical


class HelpScreen(ModalScreen):
    """Toggleable, dismissible help overlay."""

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
        Binding("escape",        "close", "Close"),
        Binding("q",             "close", "Close"),
        Binding("question_mark", "close", "Close"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label("⚡ AlacrittyForge — Help", classes="help-title")
            yield Label("── Global ──────────────────────────────", classes="help-section")
            yield Label("  1-5    Switch screens",         classes="help-line")
            yield Label("  R      Refresh current screen", classes="help-line")
            yield Label("  q      Quit",                   classes="help-line")
            yield Label("  ?      Toggle this help",       classes="help-line")
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
            yield Label("  Press Escape, Q, or ? to close", classes="help-section")

    def action_close(self) -> None:
        # Use ModalScreen's proper dismiss API (with None result) instead
        # of manually popping the screen.
        self.dismiss(None)
