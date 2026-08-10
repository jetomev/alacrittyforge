# ═══════════════════════════════════════════════════════════
#  AlacrittyForge — FilterPickerModal
#
#  The long-list answer (Javier's finding #6, v0.2.0 review): dropdowns
#  are perfect until ~a dozen options; beyond that, a floating window
#  with a type-to-filter input and a scrolling list. Used for font
#  families (many mono fonts) and any future long enumerations.
#  Promotion candidate for forgekit when a second app needs it.
# ═══════════════════════════════════════════════════════════

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, OptionList, Static
from textual.widgets.option_list import Option

from forgekit import ForgeModal


class FilterPickerModal(ForgeModal):
    """Floating picker: filter input on top, matching options below.

    Returns the chosen option string, or None on cancel. Enter in the
    filter jumps to the list; Enter on an option picks it.
    """

    BINDINGS = [Binding("escape", "cancel", "", show=False)]

    def __init__(self, title: str, options: list[str],
                 current: str = "") -> None:
        super().__init__()
        self._title = title
        self._options = options
        self._current = current

    def compose(self) -> ComposeResult:
        with Vertical(classes="forge-panel picker-panel"):
            yield Static(self._title, classes="forge-panel-title")
            yield Input(placeholder="Type to filter…", id="picker-filter")
            yield OptionList(id="picker-list")
            with Horizontal(classes="forge-buttons forge-panel-footer"):
                yield Button("Select", id="pick", variant="primary")
                yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        self._refill("")
        self.query_one("#picker-filter", Input).focus()

    def _refill(self, needle: str) -> None:
        ol = self.query_one("#picker-list", OptionList)
        ol.clear_options()
        needle = needle.lower()
        shown = [o for o in self._options if needle in o.lower()]
        for o in shown:
            marker = "  ✔ " if o == self._current else "    "
            ol.add_option(Option(f"{marker}{o}", id=o))
        if shown:
            ol.highlighted = 0

    def on_input_changed(self, e: Input.Changed) -> None:
        if e.input.id == "picker-filter":
            self._refill(e.value)

    def on_input_submitted(self, e: Input.Submitted) -> None:
        self.query_one("#picker-list", OptionList).focus()

    def on_option_list_option_selected(self, e: OptionList.OptionSelected) -> None:
        self.dismiss(e.option.id)

    def _pick_highlighted(self) -> None:
        ol = self.query_one("#picker-list", OptionList)
        if ol.highlighted is not None and ol.option_count:
            self.dismiss(ol.get_option_at_index(ol.highlighted).id)

    def on_button_pressed(self, e: Button.Pressed) -> None:
        if e.button.id == "pick":
            self._pick_highlighted()
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)
