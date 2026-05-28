# ═══════════════════════════════════════════════════════════
#  AlacrittyForge — Confirm Dialog Widget
#  A reusable confirmation popup used across all screens.
# ═══════════════════════════════════════════════════════════

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import Button, Label
from textual.containers import Vertical, Horizontal


class ConfirmDialog(ModalScreen[bool]):
    """A modal confirmation dialog that returns True (confirm) or False (cancel)."""

    # A5: Esc cancels and Enter confirms — keyboard-only users no longer
    # have to Tab+Space onto a Button to dismiss the dialog.
    BINDINGS = [
        Binding("escape", "cancel",  "Cancel"),
        Binding("enter",  "confirm", "Confirm"),
    ]

    DEFAULT_CSS = """
    ConfirmDialog {
        align: center middle;
    }

    ConfirmDialog > Vertical {
        background: #181825;
        border: solid #cba6f7;
        padding: 2 4;
        width: 60;
        height: auto;
    }

    ConfirmDialog .confirm-title {
        color: #f9e2af;
        text-style: bold;
        text-align: center;
        margin-bottom: 1;
    }

    ConfirmDialog .confirm-message {
        color: #cdd6f4;
        text-align: center;
        margin-bottom: 2;
    }

    ConfirmDialog Horizontal {
        align: center middle;
        height: auto;
    }
    """

    def __init__(self, title: str, message: str) -> None:
        super().__init__()
        self._title = title
        self._message = message

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Label(self._title, classes="confirm-title")
            yield Label(self._message, classes="confirm-message")
            with Horizontal():
                yield Button("✔  Confirm", id="confirm-yes", classes="primary")
                yield Button("✖  Cancel",  id="confirm-no",  classes="danger")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-yes":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_cancel(self) -> None:
        self.dismiss(False)

    def action_confirm(self) -> None:
        self.dismiss(True)