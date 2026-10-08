"""Themes — your themes, a preview in their colours, Adjust colours (v1.0.0).

The list on the left; on the right a small terminal drawn in the selected
theme's colours, then its palette. "Use this theme" stages the change like
any other (F10 saves it). hypeForge's files are locked: usable, never edited;
Adjust colours on one makes a copy. New themes (Adjust colours, Save my
colours, Install) are written by the save, never over an existing file.
"""

from __future__ import annotations

from pathlib import Path

from rich.markup import escape
from rich.text import Text
from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, DataTable, Input, OptionList, Static
from textual.widgets.option_list import Option

from forgekit import FilterPicker, ForgeModal, ForgePanelScreen, glyph

from .. import themes
from ..themes import CATPPUCCIN, NAMES, PALETTE, PRIMARY, Theme

OWN = "__own__"
GET_THEMES = "https://github.com/alacritty/alacritty-theme"


def preview(t: Theme, width: int = 46) -> Text:
    """A tiny terminal session in the theme's colours."""
    bg = t.shown("primary.background")
    fg = t.shown("primary.foreground")
    c = {n: t.shown(f"normal.{n}") for n in NAMES}
    cur = t.colour("cursor.cursor") or fg
    lines = [
        [(" ", fg), ("javier@kognogos", c["green"]), (" ", fg), ("~/Programs", c["blue"]), ("> ls", fg)],
        [(" ", fg), ("alacrittyforge/", c["blue"]), ("  ", fg), ("grubforge/", c["blue"]), ("  ", fg),
         ("run.sh", c["green"])],
        [(" > git status", fg)],
        [("   modified:   README.md", c["red"])],
        [("   new file:   docs/plan.md", c["green"])],
        [("   warning: 2 files not staged", c["yellow"])],
        [(" > ", fg), ("█", cur)],
    ]
    out = Text()
    for i, parts in enumerate(lines):
        n = 0
        for text, colour in parts:
            out.append(text, style=f"{colour} on {bg}")
            n += len(text)
        out.append(" " * max(0, width - n), style=f"on {bg}")
        if i < len(lines) - 1:
            out.append("\n")
    return out


def swatches(t: Theme) -> Text:
    out = Text()
    for row, label in (("normal", "Normal "), ("bright", "Bright ")):
        out.append(label, style="dim")
        for n in NAMES:
            out.append("██", style=t.shown(f"{row}.{n}"))
        if row == "normal":
            out.append("\n")
    return out


class ThemesScreen(Horizontal):
    FORGE_HINTS = [("↑↓", "pick"), ("Enter", "use this theme"), ("A", "adjust colours"), ("I", "install"),
                   ("Tab", "buttons"), ("F10", "save"), ("?", "all keys")]
    BINDINGS = [Binding("a", "adjust", show=False), Binding("i", "install", show=False)]

    def __init__(self, session, **kw) -> None:
        super().__init__(**kw)
        self.session = session
        self.themes_dir = session.themes_dir or themes.THEMES_DIR
        self.items: list[Theme] = []

    def compose(self) -> ComposeResult:
        with Vertical(id="th-left"):
            yield Static("[b $forge-title-accent]Themes[/]", classes="af-group-title")
            ol = OptionList(id="th-list")
            ol.FORGE_HINTS = self.FORGE_HINTS
            yield ol
            yield Static("", id="th-where")
        with VerticalScroll(id="th-right", can_focus=False):
            yield Static("", id="th-title")
            yield Static("", id="th-preview")
            yield Static("", id="th-swatches")
            yield Static("", id="th-info")
            with Horizontal(classes="forge-buttons th-actions"):
                yield Button("Use This Theme", id="th-use", variant="primary")
                yield Button(f"Adjust Colours{glyph('ellipsis')} (a)", id="th-adjust")
            with Horizontal(classes="forge-buttons th-actions"):
                yield Button(f"Save My Colours as a Theme{glyph('ellipsis')}", id="th-saveown")
                yield Button(f"Install a Theme{glyph('ellipsis')} (i)", id="th-install")
                yield Button("Where to Get Themes", id="th-get")

    def on_mount(self) -> None:
        self.refresh_view()

    # ── the list ──────────────────────────────────────────────────────────────
    def active(self) -> Path | None:
        imports = self.session.value("general.import") or []
        for p in imports:
            full = themes._expand(p, self.session.path)
            if self.themes_dir in full.parents:
                return full
        return None

    def refresh_view(self) -> None:
        ol = self.query_one("#th-list", OptionList)
        keep = ol.highlighted
        self.items = []
        own = themes.own_colours(self.session)
        if own:
            self.items.append(Theme("My colours", None, colours=own))
        listed = themes.list_themes(self.themes_dir)
        active = self.active()
        # the theme in use first, then the rest by name
        listed.sort(key=lambda t: (t.path != active, t.name.lower()))
        self.items += listed
        for path, text in self.session.new_files.items():
            if path.parent == self.themes_dir:
                import tomllib
                self.items.append(Theme(path.stem, path, colours=tomllib.loads(text).get("colors", {}),
                                        pending=True))
        active = self.active()
        ol.clear_options()
        for t in self.items:
            label = Text()
            in_use = (t.path is None and own) or (t.path is not None and t.path == active)
            label.append(f"{glyph('default') if in_use else ' '} ", style="bold")
            label.append(t.name)
            if in_use:
                label.append("  in use", style="green")
            if t.pending:
                label.append("  new, not saved", style="yellow")
            elif t.locked:
                label.append(f"  {t.locked_by}", style="dim")
            elif t.error:
                label.append(f"  {t.error}", style="red")
            ol.add_option(Option(label))
        n = len([t for t in self.items if t.path])
        where = str(self.themes_dir).replace(str(Path.home()), "~")
        self.query_one("#th-where", Static).update(f"[$forge-muted]{n} theme{'s' if n != 1 else ''} · {escape(where)}[/]")
        if self.items:
            ol.highlighted = min(keep or 0, len(self.items) - 1)
            self.show(self.items[ol.highlighted])

    def current(self) -> Theme | None:
        ol = self.query_one("#th-list", OptionList)
        if ol.highlighted is None or ol.highlighted >= len(self.items):
            return None
        return self.items[ol.highlighted]

    @on(OptionList.OptionHighlighted, "#th-list")
    def _picked(self, e: OptionList.OptionHighlighted) -> None:
        if 0 <= e.option_index < len(self.items):
            self.show(self.items[e.option_index])

    @on(OptionList.OptionSelected, "#th-list")
    def _chosen(self, e: OptionList.OptionSelected) -> None:
        self.use()

    def show(self, t: Theme) -> None:
        title = self.query_one("#th-title", Static)
        title.update(f"[b $forge-title-accent]{escape(t.name)}[/]  [$forge-muted]· a preview in its colours[/]")
        if t.error:
            self.query_one("#th-preview", Static).update(f"[$forge-error]{escape(t.error)}[/]")
            self.query_one("#th-swatches", Static).update("")
        else:
            self.query_one("#th-preview", Static).update(preview(t))
            self.query_one("#th-swatches", Static).update(swatches(t))
        info = []
        if getattr(self.app, "forge_console", False):
            info.append("A text console shows only 16 colours, so this preview is only a rough guide.")
        if t.path is None:
            info.append("Written in your settings file itself. A theme file you use replaces them.")
        elif t.locked:
            info.append(f"Made by {t.locked_by}, which rewrites it, so it is locked: use it as it is, or "
                        f"press Adjust Colours{glyph('ellipsis')} (a) to make your own copy.")
        elif t.pending:
            info.append("New: it is written when you save (F10).")
        self.query_one("#th-info", Static).update("\n".join(f"[$forge-muted]{escape(x)}[/]" for x in info))
        active = self.active()
        in_use = (t.path is None) or (t.path == active)
        self.query_one("#th-use", Button).disabled = bool(t.error) or in_use or not self.session.readable
        self.query_one("#th-adjust", Button).disabled = bool(t.error) or not self.session.readable
        self.query_one("#th-saveown", Button).display = bool(themes.own_colours(self.session))

    # ── actions ───────────────────────────────────────────────────────────────
    def use(self) -> None:
        t = self.current()
        if t is None or t.error or t.path is None or not self.session.readable:
            return
        for k, v in themes.use_changes(self.session, t.path, self.themes_dir).items():
            self.session.set(k, v)
        self.refresh_view()
        self.app.refresh_state()
        self.app.notify(f"{t.name} is ready to use. Press F10 to save it.", timeout=5)

    def action_adjust(self) -> None:
        t = self.current()
        if t is None or t.error or not self.session.readable:
            return

        def done(colours: dict | None) -> None:
            if colours is None:
                return
            taken = {p.stem for p in self.session.new_files}
            base = "my colours" if t.path is None else t.name.removesuffix(" (mine)")
            name = themes.free_name(base, self.themes_dir, taken)
            path = self.themes_dir / f"{themes.safe_file_name(name)}.toml"
            self.session.add_file(path, themes.theme_text(colours, made_from=t.name))
            for k, v in themes.use_changes(self.session, path, self.themes_dir).items():
                self.session.set(k, v)
            self.refresh_view()
            self.app.refresh_state()
            self.app.notify(f"Saved as {name} when you press F10.", timeout=6)

        self.app.push_screen(AdjustColours(t), done)

    def save_own(self) -> None:
        own = themes.own_colours(self.session)
        if not own:
            return
        taken = {p.stem for p in self.session.new_files}
        name = themes.free_name("my colours", self.themes_dir, taken)
        self.session.add_file(self.themes_dir / f"{themes.safe_file_name(name)}.toml",
                              themes.theme_text(own, made_from="my settings file"))
        self.refresh_view()
        self.app.refresh_state()
        self.app.notify(f"Your colours become the theme {name} when you press F10.", timeout=6)

    def action_install(self) -> None:
        downloads = Path.home() / "Downloads"
        found = sorted(downloads.glob("*.toml")) if downloads.is_dir() else []
        options = [(str(p), p.name) for p in found]

        def done(value: str | None) -> None:
            if not value:
                return
            src = Path(value).expanduser()
            why = themes.check_install(src)
            if why:
                self.app.notify(f"{src.name} {why}.", title="Not installed", severity="warning", timeout=8)
                return
            name = themes.safe_file_name(src.stem)
            dest = self.themes_dir / f"{name}.toml"
            if dest.exists() or dest in self.session.new_files:
                self.app.notify(f"A theme named {name} is already there.", title="Not installed",
                                severity="warning", timeout=8)
                return
            self.session.add_file(dest, src.read_text(encoding="utf-8"))
            self.refresh_view()
            self.app.refresh_state()
            self.app.notify(f"{name} is installed when you press F10.", timeout=6)

        self.app.push_screen(FilterPicker("Install a theme", options, allow_custom=True,
                                          hint="Theme files in Downloads, or type the path of one"), done)

    def on_button_pressed(self, e: Button.Pressed) -> None:
        bid = e.button.id or ""
        if not bid.startswith("th-"):
            return
        e.stop()
        if bid == "th-use":
            self.use()
        elif bid == "th-adjust":
            self.action_adjust()
        elif bid == "th-saveown":
            self.save_own()
        elif bid == "th-install":
            self.action_install()
        elif bid == "th-get":
            self.app.push_screen(WhereToGet())


class WhereToGet(ForgePanelScreen):
    def __init__(self) -> None:
        super().__init__()
        self.panel_title = "Where to get themes"

    def compose_body(self) -> ComposeResult:
        yield Static(
            "Alacritty's own collection has over a hundred themes, each one file:\n\n"
            f"[b]{GET_THEMES}[/]\n\n"
            "Open a theme there, download its .toml file (the Download raw file button), then come back "
            "and choose [b]Install a Theme… (i)[/]. Files in your Downloads folder are "
            "listed. Only files that change colours, and nothing else, are installed.")


class AdjustColours(ForgeModal[dict | None]):
    """Change single colours; the result becomes your own copy of the theme."""

    BINDINGS = [Binding("escape", "cancel", "", show=False)]

    def __init__(self, theme: Theme) -> None:
        super().__init__()
        self.theme = theme
        import copy
        self.colours = copy.deepcopy(theme.colours)

    def compose(self) -> ComposeResult:
        with Vertical(classes="forge-panel af-adjust"):
            yield Static(f"Adjust colours · {escape(self.theme.name)}", classes="forge-panel-title")
            yield Static("[$forge-muted]Saved as your own copy; the original stays as it is.[/]")
            # the middle scrolls when the screen is short, so the buttons always show
            with VerticalScroll(id="ad-body", can_focus=False):
                t = DataTable(id="ad-table", cursor_type="row", zebra_stripes=False)
                t.FORGE_HINTS = [("↑↓", "pick a colour"), ("Enter", "change it"), ("Tab", "buttons"),
                                 ("Esc", "cancel")]
                yield t
                yield Static("", id="ad-preview")
            with Horizontal(classes="forge-buttons forge-panel-footer"):
                yield Button("Keep These Colours", id="ad-keep", variant="primary")
                yield Button("Cancel (Esc)", id="ad-cancel")

    def on_mount(self) -> None:
        t = self.query_one("#ad-table", DataTable)
        t.add_columns("Colour", "", "Code")
        self._fill()
        t.focus()

    def _theme(self) -> Theme:
        return Theme(self.theme.name, self.theme.path, colours=self.colours)

    def _fill(self) -> None:
        t = self.query_one("#ad-table", DataTable)
        keep = t.cursor_row
        t.clear()
        th = self._theme()
        for key, label in PRIMARY + PALETTE:
            code = th.colour(key)
            shown = th.shown(key)
            # colour and background both the swatch's, so the row highlight can't repaint it
            t.add_row(label, Text("██", style=f"{shown} on {shown}"), code or Text(f"not set ({shown})", style="dim"))
        if keep is not None:
            t.move_cursor(row=keep)
        self.query_one("#ad-preview", Static).update(preview(th, 52))

    def _key(self) -> str:
        return (PRIMARY + PALETTE)[self.query_one("#ad-table", DataTable).cursor_row][0]

    @on(DataTable.RowSelected, "#ad-table")
    def _change(self, e: DataTable.RowSelected) -> None:
        key = self._key()
        th = self._theme()
        seen, options = set(), []
        for k, label in PRIMARY + PALETTE:
            c = th.colour(k)
            if c and c not in seen:
                seen.add(c)
                options.append((c, f"{c}  this theme's {label.lower()}"))
        options += [(c, f"{c}  Catppuccin {n}") for n, c in CATPPUCCIN]

        def done(value: str | None) -> None:
            if not value:
                return
            value = value.strip()
            if not themes.COLOUR_RE.fullmatch(value):
                self.app.notify("A colour is a code like #1e1e2e.", severity="warning")
                return
            group, name = key.split(".")
            self.colours.setdefault(group, {})[name] = value.lower()
            self._fill()

        self.app.push_screen(FilterPicker(dict(PRIMARY + PALETTE)[key], options, current=th.colour(key) or "",
                                          allow_custom=True, hint="Pick a colour, or type a code like #1e1e2e"),
                             done)

    def on_button_pressed(self, e: Button.Pressed) -> None:
        e.stop()
        self.dismiss(self.colours if e.button.id == "ad-keep" else None)

    def action_cancel(self) -> None:
        self.dismiss(None)
