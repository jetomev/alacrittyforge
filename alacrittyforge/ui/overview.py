"""Overview — "is my terminal set up right?" in four boxes (v1.0.0).

Your terminal · Needs attention · Safety · Common tasks, like grubForge's.
Anything that needs attention comes with the button that fixes it.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from rich.markup import escape
from textual.app import ComposeResult
from textual.containers import Grid, Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Static

from forgekit import glyph

from .. import backups
from ..alacritty import shown_version
from ..session import monospace_families


def fonts_missing() -> bool:
    """True only when fonts could be listed and none is monospace (found on a
    minimal openSUSE install, where Alacritty then refuses to start)."""
    found = monospace_families()
    return found is not None and not found


def when(t: dt.datetime | None) -> str:
    if t is None:
        return "never"
    today = dt.date.today()
    day = "today" if t.date() == today else ("yesterday" if t.date() == today - dt.timedelta(days=1)
                                             else f"{t:%b} {t.day}")
    return f"{day} {t:%H:%M}"


def theme_name(session) -> str:
    imports = session.value("general.import") or []
    for p in imports:
        if "/themes/" in str(p):
            return Path(str(p)).stem
    if session.file.get("colors") not in (None, {}) and isinstance(session.file.get("colors"), dict):
        return "my colours (in the settings file)"
    return "Alacritty's own"


class OverviewScreen(VerticalScroll, can_focus=False):
    FORGE_HINTS = [("Tab", "next button"), ("Enter", "do it"), ("1-5", "screens"), ("F1", "help"), ("?", "all keys")]

    def __init__(self, session, **kw) -> None:
        super().__init__(**kw)
        self.session = session

    def compose(self) -> ComposeResult:
        with Grid(id="af-overview"):
            with Vertical(classes="af-box", id="box-terminal"):
                yield Static("", id="ov-terminal")
            with Vertical(classes="af-box af-attention", id="box-attention"):
                yield Vertical(id="ov-attention")
                with Horizontal(classes="forge-buttons af-box-buttons", id="ov-attention-buttons"):
                    yield Button("Restore the newest backup", id="ov-restore", variant="primary")
                    yield Button("Update them", id="ov-rename", variant="primary")
            with Vertical(classes="af-box", id="box-safety"):
                yield Static("", id="ov-safety")
            with Vertical(classes="af-box", id="box-tasks"):
                yield Static("", id="ov-tasks")
                with Horizontal(classes="forge-buttons af-task-row"):
                    yield Button("Pick a theme", id="task-theme")
                    yield Button("Change the font", id="task-font")
                with Horizontal(classes="forge-buttons af-task-row"):
                    yield Button("Text size", id="task-size")
                    yield Button("Back up now", id="task-backup")

    def on_mount(self) -> None:
        for box, title in (("box-terminal", "Your terminal"), ("box-attention", "Needs attention"),
                           ("box-safety", "Safety"), ("box-tasks", "Common tasks")):
            self.query_one(f"#{box}").border_title = title
        self.refresh_view()

    def refresh_view(self) -> None:
        s = self.session
        m = "$forge-muted"
        if s.readable:
            size = s.shown("font.size").replace("not set (", "").rstrip(")")
            font = s.value("font.normal.family") or "monospace"
            opacity = s.value("window.opacity")
            opacity = 1.0 if opacity is None else opacity
            win = ["solid" if opacity >= 1 else f"{round(opacity * 100)}% opaque"]
            if s.value("window.blur"):
                win.append("blurred")
            cols, lines = s.value("window.dimensions.columns"), s.value("window.dimensions.lines")
            if cols and lines:
                win.append(f"{cols}×{lines}")
            shell = s.shown("terminal.shell").replace("not set (", "").rstrip(")")
            n_keys = len(s.value("keyboard.bindings") or [])
            rows = [("Alacritty", shown_version(s.names.version)), ("Theme", theme_name(s)), ("Font", f"{font} · {size}"), ("Window", " · ".join(win)),
                    ("Shell", shell), ("Shortcuts", f"{n_keys} of yours")]
        else:
            rows = [("File", "can't be read")]
        self.query_one("#ov-terminal", Static).update(
            "\n".join(f"[{m}]{k:<10}[/] {escape(v)}" for k, v in rows))

        # needs attention
        warn = f"[b $forge-warn]{glyph('warn')}[/]"
        items: list[tuple[str, str]] = []
        if not s.readable:
            items.append((f"{warn} [b]Your settings file can't be read.[/]",
                          f"{escape(s.file.error or '')}. Alacritty is using its own settings until it is fixed; "
                          "alacrittyForge won't save over it."))
        old = s.old_names()
        if old:
            names = ", ".join(f"{o} → {n}" for o, n in old)
            if s.names.legacy:
                items.append((f"{warn} [b]{len(old)} setting{'s use' if len(old) != 1 else ' uses'} a newer name "
                              "than this Alacritty reads.[/]",
                              f"{escape(names)}. Alacritty {shown_version(s.names.version)} ignores them until "
                              "they're moved."))
            else:
                items.append((f"{warn} [b]{len(old)} setting{'s use' if len(old) != 1 else ' uses'} an old name.[/]",
                              f"{escape(names)}. Alacritty still reads them, but warns every time it starts."))
        unknown = s.unknown_keys()
        if unknown:
            items.append((f"[$forge-info]{glyph('info')}[/] {len(unknown)} setting"
                          f"{'s' if len(unknown) != 1 else ''} Alacritty doesn't know",
                          f"{escape(', '.join(unknown[:4]))}{'…' if len(unknown) > 4 else ''}. It ignores "
                          "them; often a misspelling."))
        if s.readable and fonts_missing():
            items.append((f"{warn} [b]No monospace font is installed.[/]",
                          "Alacritty can't open without one. Install one, for example DejaVu Sans Mono "
                          "(the package is usually called fonts-dejavu or dejavu-fonts)."))
        if s.names.version is None:
            items.append((f"[$forge-info]{glyph('info')}[/] Alacritty isn't installed",
                          "alacrittyForge can still prepare its settings; they'll be used once it is."))
        if s.readable and not s.live_reload():
            items.append((f"[$forge-info]{glyph('info')}[/] Changes wait for a restart",
                          "\"Pick up changes by itself\" is off, so a saved change shows the next time "
                          "Alacritty opens."))
        if not items:
            items.append((f"[$forge-ok]{glyph('ok')} Nothing needs attention.[/]", ""))
        box = self.query_one("#ov-attention", Vertical)
        box.remove_children()
        widgets = []
        for head, body in items:
            widgets.append(Static(head, classes="af-att-head"))
            if body:
                widgets.append(Static(body, classes="af-att-body"))
        box.mount(*widgets)
        restore = not s.readable and bool(backups.list_all(s.backup_dir))
        self.query_one("#ov-restore").display = restore
        self.query_one("#ov-rename").display = bool(old)
        self.query_one("#ov-attention-buttons").display = restore or bool(old)

        made = backups.list_all(s.backup_dir)
        newest = when(made[0].made) if made else "none yet"
        self.query_one("#ov-safety", Static).update("\n".join([
            f"[{m}]{'Backups':<9}[/] {len(made)} · newest {newest}",
            f"[{m}]{'Saving':<9}[/] one backup first; your",
            f"[{m}]{'':<9}[/] comments and layout are kept",
            f"[{m}]{'File':<9}[/] {escape(str(s.path).replace(str(Path.home()), '~'))}",
        ]))
        self.query_one("#ov-tasks", Static).update(f"[{m}]One step to the things people change most.[/]")
