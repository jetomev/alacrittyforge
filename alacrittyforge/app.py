"""alacrittyForge v1.0.0 — the app frame, on forgekit.

The frame is forgekit's (title bar, menu bar, changes bar, hint bar); the
screens are alacrittyForge's. All file work goes through the Session.
Javier's rulings for 1.0.0 (2 Oct 2026, docs/design/v1.0.0-screens.html):

* five screens like grubForge 2.0: Overview, Settings (fonts are its "Text"
  group), Themes, Shortcuts, Backups;
* every Alacritty setting on Linux, in plain words, picked not typed;
* a save keeps your comments and layout, with a review first and one backup;
* no Rebuild step: Alacritty picks a saved change up by itself.
"""

from __future__ import annotations

import os

from rich.markup import escape
from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Static

from forgekit import (
    FORGE_CSS, GPL3_NOTICE, ChangeGroup, ForgeApp, ForgeModal, ForgePanelScreen, ManualScreen, Notice,
    ReviewDialog, load_pages,
)

from . import __version__, backups
from .session import Session
from .settings_file import Unreadable
from .settings_spec import BY_KEY, default_words
from .ui.overview import OverviewScreen
from .ui.settings import SettingsScreen

MANUAL_DIR = os.path.join(os.path.dirname(__file__), "manual")

AF_CSS = FORGE_CSS + """
/* alacrittyForge's own sections, coloured only through forgekit's roles */
#af-groups { width: 20; height: 1fr; border: none; border-right: solid $forge-border; background: $forge-bg; padding: 1 1 0 0; }
#af-settings-right { width: 1fr; height: 1fr; padding: 0 0 0 2; }
#af-groupforms { height: 1fr; }
.af-group { height: 1fr; padding: 0 1 0 0; }
.af-group-title { height: auto; margin: 0 0 1 0; }
#af-about { height: auto; min-height: 4; max-height: 7; padding: 1 0 0 0; color: $forge-text; }
#af-overview { grid-size: 2 2; grid-columns: 1fr 1fr; grid-rows: auto auto; grid-gutter: 1 2; height: auto; padding: 0 2 0 0; }
.af-box { height: auto; border: round $forge-border; border-title-color: $forge-accent; border-title-style: bold; padding: 0 1; }
.af-attention { border: round $forge-warn; border-title-color: $forge-warn; }
.af-box-buttons, .af-task-row { padding: 1 0 0 0; align-horizontal: left; height: auto; }
.forge-buttons.af-task-row Button { margin: 0 2 0 0; width: 1fr; min-width: 0; padding: 0 1; }
.forge-buttons.af-task-row Button:last-child { margin: 0; }
.af-box-buttons Button { margin: 0 2 0 0; }
#ov-attention { height: auto; }
.af-att-head { height: auto; }
.af-att-body { height: auto; padding: 0 0 0 3; margin: 0 0 1 0; }
.af-att-body:last-child { margin: 0; }
.af-soon { padding: 1 2; }
#af-quit-msg { height: auto; padding: 0 0 1 0; }
"""


class QuitDialog(ForgeModal[str | None]):
    """Before you go: unsaved changes."""

    BINDINGS = [Binding("escape", "stay", "", show=False)]

    def __init__(self, heading: str, lines: list[str], buttons: list[tuple[str, str, bool]]) -> None:
        super().__init__()
        self._heading, self._lines, self._buttons = heading, lines, buttons

    def compose(self) -> ComposeResult:
        with Vertical(classes="forge-panel"):
            yield Static("Before you go", classes="forge-panel-title")
            yield Notice(self._heading, self._lines, level="warn", id="af-quit-msg")
            with Horizontal(classes="forge-buttons forge-panel-footer"):
                for label, bid, primary in self._buttons:
                    yield Button(label, id=bid, variant="primary" if primary else "default")
                yield Button("Stay", id="stay")

    def on_mount(self) -> None:
        self.query_one(f"#{self._buttons[0][1]}", Button).focus()

    def on_button_pressed(self, e: Button.Pressed) -> None:
        e.stop()
        self.dismiss(None if e.button.id == "stay" else e.button.id)

    def action_stay(self) -> None:
        self.dismiss(None)


class FieldHelp(ForgePanelScreen):
    CLOSE_KEYS = ("f1",)

    def __init__(self, title: str, text: str) -> None:
        super().__init__()
        self.panel_title = title
        self._text = text

    def compose_body(self) -> ComposeResult:
        yield Static(self._text)


class Soon(VerticalScroll, can_focus=False):
    """A screen not built yet in this step."""

    def __init__(self, title: str, text: str, **kw) -> None:
        super().__init__(**kw)
        self._title, self._text = title, text

    def compose(self) -> ComposeResult:
        yield Static(f"[b $forge-title-accent]{self._title}[/]\n\n[$forge-muted]{escape(self._text)}[/]",
                     classes="af-soon")


class AlacrittyForgeApp(ForgeApp):
    APP_NAME = f"alacrittyForge {__version__} · Alacritty settings"
    SHOW_HINT_BAR = True
    SHOW_CHANGES_BAR = True
    CSS = AF_CSS
    LICENSE_NOTICE = GPL3_NOTICE
    MENU = [
        {"id": "overview", "title": "Overview", "kind": "section"},
        {"id": "settings", "title": "Settings", "kind": "section", "acc": "e"},
        {"id": "themes", "title": "Themes", "kind": "section"},
        {"id": "shortcuts", "title": "Shortcuts", "kind": "section", "acc": "u"},
        {"id": "backups", "title": "Backups", "kind": "section", "acc": "k"},
        {"id": "help", "title": "Help", "kind": "menu", "items": [
            ("Manual", "m", "manual"), ("Keys", "k", "shortcuts"),
            ("License", "l", "license"), ("About", "a", "about")]},
        {"id": "quit", "title": "Quit", "kind": "action", "action": "quit"},
    ]
    SHORTCUTS = [
        ("Tab / Shift+Tab", "next / previous field or button"),
        ("Enter", "open a list, press a button, confirm"),
        ("Space", "flip a switch"),
        ("↑↓ in a number", "step through its presets"),
        ("Esc", "close a window"),
        ("1-5, Ctrl+letter", "go to a screen (the underlined letter)"),
        ("F10 or S", "save, with a review first"),
        ("R", "read the file again"),
        ("F1", "help on what is selected"),
        ("M", "the manual"),
        ("?", "this list"),
        ("Q or Ctrl+Q", "quit (asks first if something isn't saved)"),
    ]
    HINTS = [("Tab", "next"), ("1-5", "screens"), ("F10", "save"), ("F1", "help"), ("?", "all keys")]
    BINDINGS = [
        Binding("1", "go('overview')", show=False), Binding("2", "go('settings')", show=False),
        Binding("3", "go('themes')", show=False), Binding("4", "go('shortcuts')", show=False),
        Binding("5", "go('backups')", show=False),
        Binding("ctrl+o", "go('overview')", show=False), Binding("ctrl+e", "go('settings')", show=False),
        Binding("ctrl+t", "go('themes')", show=False), Binding("ctrl+u", "go('shortcuts')", show=False),
        Binding("ctrl+k", "go('backups')", show=False),
        Binding("f10", "save", show=False, priority=True), Binding("s", "save", show=False),
        Binding("r", "reload", show=False),
        Binding("f1", "field_help", show=False, priority=True),
        Binding("m", "act('manual')", show=False),
        Binding("question_mark", "act('shortcuts')", show=False),
        Binding("q", "act('quit')", show=False),
    ]

    def __init__(self, session: Session | None = None, **kw) -> None:
        self.session = session or Session.load()
        self.ABOUT = {
            "name": "alacrittyForge", "version": __version__,
            "tagline": "Alacritty's settings, without editing the file by hand",
            "description": "Part of the Forge Suite for KognogOS.",
            "authors": "jetomev (Javier) · Claude (Anthropic), co-developer",
            "license": "GPL-3.0-or-later",
            "links": [("Code", "https://github.com/jetomev/alacrittyforge")],
        }
        super().__init__(**kw)

    def compose_sections(self) -> ComposeResult:
        yield OverviewScreen(self.session, id="sec-overview")
        yield SettingsScreen(self.session, id="sec-settings")
        yield Soon("Themes", "Coming in step 3: your themes with a preview, and Adjust colours.",
                   id="sec-themes")
        yield Soon("Shortcuts", "Coming in step 4: your shortcuts in words, recorded by pressing the keys.",
                   id="sec-shortcuts")
        yield Soon("Backups", "Coming in step 5: why each backup was made, and what restoring it would change.",
                   id="sec-backups")

    def on_mount(self) -> None:
        super().on_mount()
        user = os.environ.get("USER", "")
        live = "Alacritty picks changes up by itself" if self.session.live_reload() else "changes need a restart"
        self.set_title_status(f"{user} · {live}")
        self.refresh_state()

    # ── navigation ───────────────────────────────────────────────────────────
    def action_go(self, section: str) -> None:
        self._switch_section(section)

    def on_section_shown(self, section_id: str) -> None:
        # the file may have changed outside alacrittyForge: read it again;
        # unsaved changes stay
        self.session.reload()
        self.query_one(SettingsScreen).sync()
        self.refresh_state()
        if section_id == "overview":
            self.query_one(OverviewScreen).refresh_view()
        if section_id == "settings":
            self.query_one("#af-groups").focus()

    def on_action(self, action_id: str) -> None:
        if action_id == "manual":
            self.open_manual()

    def open_manual(self, page: str | None = None) -> None:
        pages = load_pages(MANUAL_DIR) if os.path.isdir(MANUAL_DIR) else []
        if not pages:
            self.notify("The manual isn't written yet.", severity="warning")
            return
        self.push_screen(ManualScreen("alacrittyForge manual", pages, start=page))

    def action_field_help(self) -> None:
        from forgekit import SettingRow
        w = self.focused
        row = next((a for a in (w.ancestors_with_self if w else []) if isinstance(a, SettingRow)), None)
        if row is None:
            self.action_act("shortcuts")
            return
        s = BY_KEY[row.setting]
        pages = load_pages(MANUAL_DIR) if os.path.isdir(MANUAL_DIR) else []
        if pages:
            self.open_manual(page=s.group)
            return
        self.push_screen(FieldHelp(s.label, f"{escape(s.help)}\n\n[$forge-muted]Alacritty name: {s.key}"
                                            f"  ·  when not set: {escape(default_words(s))}[/]"))

    # ── state: the changes bar ───────────────────────────────────────────────
    def refresh_state(self) -> None:
        s, bar = self.session, self.changes_bar
        n = s.change_count
        if n:
            bar.show(f"{n} change{'s' if n != 1 else ''} not saved yet", "changed",
                     [("Save…  F10", "af-save", True), ("Discard", "af-discard", False)])
        else:
            bar.hide()

    def on_button_pressed(self, e: Button.Pressed) -> None:
        bid = e.button.id or ""
        if bid == "af-save":
            self.action_save()
        elif bid == "af-discard":
            self.session.discard()
            self.query_one(SettingsScreen).sync()
            self.refresh_state()
            self.notify("Changes discarded. Nothing was written.")
        elif bid == "ov-rename":
            self.session.stage_renames()
            self.refresh_state()
            self.action_save()
        elif bid == "ov-restore":
            self.restore_newest()
        elif bid == "task-font":
            self._switch_section("settings")
            self.query_one(SettingsScreen).show_group("text")
            self.query_one(SettingsScreen).row("font.normal.family").control.focus()
        elif bid == "task-size":
            self._switch_section("settings")
            self.query_one(SettingsScreen).show_group("text")
            self.query_one(SettingsScreen).row("font.size").control.query_one("Input").focus()
        elif bid == "task-theme":
            self._switch_section("themes")
        elif bid == "task-backup":
            self.backup_now()

    # ── save, reload ─────────────────────────────────────────────────────────
    @work(exclusive=True, group="af-write")
    async def action_save(self) -> None:
        s = self.session
        if not s.readable:
            self.notify("Your settings file can't be read, so it isn't saved over. "
                        "Restore a backup, or fix the file and press R.", title="Can't save", severity="warning",
                        timeout=10)
            return
        if not s.pending:
            self.notify("Nothing to save: no changes.")
            return
        problems = s.problems()
        if problems:
            self.notify("\n".join(problems), title="Can't save yet", severity="error", timeout=10)
            return
        path = str(s.path).replace(os.path.expanduser("~"), "~")
        steps = ["A backup of your settings is made",
                 "The changes are written; your comments and layout stay"]
        later = sorted({BY_KEY[k].when for k in s.pending if k in BY_KEY and BY_KEY[k].when})
        if s.live_reload():
            steps.append("Alacritty picks them up right away, in every open window"
                         + (f" ({'; '.join(later)} for some)" if later else ""))
        else:
            steps.append("They show the next time Alacritty opens")
        choice = await self.push_screen_wait(ReviewDialog(
            "Review before saving", [ChangeGroup("Settings", path, s.changes())], steps=steps,
            buttons=[("Save", "save", True)]))
        if choice is None:
            return
        try:
            s.save()
        except Unreadable as e:
            self.notify(f"The file can't be read now ({e}); nothing was written.", title="Not saved",
                        severity="error", timeout=10)
            return
        except OSError as e:
            self.notify(f"{e.strerror or e}. Nothing was changed.", title="Not saved", severity="error", timeout=10)
            return
        self.query_one(SettingsScreen).sync()
        self.refresh_state()
        self.query_one(OverviewScreen).refresh_view()
        self.notify("Saved. Alacritty is using it now." if s.live_reload() else
                    "Saved. It shows the next time Alacritty opens.", title="Saved", timeout=6)

    def backup_now(self) -> None:
        made = backups.create("manual", path=self.session.path, backup_dir=self.session.backup_dir)
        self.query_one(OverviewScreen).refresh_view()
        self.notify("Backup saved." if made else "There is no settings file to back up yet.")

    def restore_newest(self) -> None:
        made = backups.list_all(self.session.backup_dir)
        if not made:
            return
        backups.restore(made[0], path=self.session.path, backup_dir=self.session.backup_dir)
        self.after_file_changed()
        self.notify(f"Restored the backup from {made[0].made:%b %d %H:%M}.", title="Restored")

    def action_reload(self) -> None:
        self.session.reload()
        self.query_one(SettingsScreen).sync()
        self.query_one(OverviewScreen).refresh_view()
        self.refresh_state()
        self.notify("Read the file again. Your unsaved changes are kept.")

    def after_file_changed(self) -> None:
        self.session.reload()
        self.query_one(SettingsScreen).sync()
        self.query_one(OverviewScreen).refresh_view()
        self.refresh_state()

    # ── quitting ─────────────────────────────────────────────────────────────
    def before_quit(self) -> bool:
        s = self.session
        if s.pending:
            n = s.change_count
            self.push_screen(QuitDialog(
                f"{n} change{'s are' if n != 1 else ' is'} not saved",
                ["Quitting now loses them."],
                [("Save first", "save", True), ("Quit without saving", "quit", False)]), self._after_quit_choice)
            return False
        return True

    def _after_quit_choice(self, choice: str | None) -> None:
        if choice == "quit":
            self.exit()
        elif choice == "save":
            self.action_save()
