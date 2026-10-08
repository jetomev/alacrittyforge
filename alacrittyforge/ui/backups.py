"""Backups — why each was made, and what restoring it would change (v1.0.0).

Newest first. On the right, "Restoring this would change": every setting,
the theme and the shortcuts that differ between the backup and today, in
plain words, before you choose. Restoring backs up what is there now first.
"""

from __future__ import annotations

from rich.markup import escape
from textual import on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, DataTable, Static

from forgekit import ConfirmDialog, ForgePanelScreen, glyph

from .. import backups
from ..settings_file import MISSING, SettingsFile
from ..settings_spec import SETTINGS, shown
from .overview import when


def differences(session, b: backups.Backup) -> list[tuple[str, str, str]] | None:
    """(what, today, in the backup); None when the backup can't be read."""
    old = SettingsFile.load(b.path)
    if not old.readable:
        return None
    names = session.names
    rows = []
    for s in SETTINGS:
        k = names.file_key(s.key)
        now, then = session.file.get(k), old.get(k)
        if now == then:
            continue
        rows.append((s.label, "not set" if now is MISSING else shown(s, now),
                     "not set" if then is MISSING else shown(s, then)))
    from .overview import theme_name

    class _View:              # theme_name() reads value()/file like a session
        def __init__(self, f):
            self.file = f

        def value(self, key):
            v = self.file.get(names.file_key(key))
            return None if v is MISSING else v
    t_now, t_then = theme_name(session), theme_name(_View(old))
    if t_now != t_then:
        rows.insert(0, ("Theme", t_now, t_then))
    k_now = session.file.get("keyboard.bindings")
    k_then = old.get("keyboard.bindings")
    if k_now != k_then:
        n_now = len(k_now) if isinstance(k_now, list) else 0
        n_then = len(k_then) if isinstance(k_then, list) else 0
        rows.append(("Your shortcuts", f"{n_now}", f"{n_then}" + (" (different)" if n_now == n_then else "")))
    return rows


class BackupsScreen(Horizontal):
    FORGE_HINTS = [("↑↓", "pick"), ("R", "restore"), ("N", "back up now"), ("D", "delete"), ("?", "all keys")]
    BINDINGS = [Binding("n", "new", show=False), Binding("r", "restore", show=False),
                Binding("d", "delete", show=False)]

    def __init__(self, session, **kw) -> None:
        super().__init__(**kw)
        self.session = session
        self.items: list[backups.Backup] = []

    def compose(self) -> ComposeResult:
        with Vertical(id="bk-left"):
            yield Static("[b $forge-title-accent]Backups[/]   [$forge-muted]newest first · last 20 kept[/]",
                         classes="af-group-title")
            t = DataTable(id="bk-table", cursor_type="row", zebra_stripes=False)
            t.FORGE_HINTS = self.FORGE_HINTS
            yield t
            yield Static("", id="bk-where")
            with Horizontal(classes="forge-buttons bk-actions"):
                yield Button(f"Restore (r)", id="bk-restore", variant="primary")
                yield Button("Back Up Now (n)", id="bk-new")
            with Horizontal(classes="forge-buttons bk-actions"):
                yield Button("Show Whole File", id="bk-show")
                yield Button(f"Delete (d)", id="bk-delete")
        with VerticalScroll(id="bk-right", classes="af-box", can_focus=False):
            yield Static("", id="bk-diff")

    def on_mount(self) -> None:
        self.query_one("#bk-right").border_title = "Restoring this would change"
        self.refresh_view()

    def on_resize(self) -> None:
        self.call_after_refresh(self.refresh_view)

    def refresh_view(self) -> None:
        t = self.query_one("#bk-table", DataTable)
        keep = t.cursor_row
        t.clear(columns=True)
        t.add_columns("When", "Why it was made")
        self.items = backups.list_all(self.session.backup_dir)
        # a long reason is cut to the list's width, so the list never scrolls sideways
        room = t.size.width - 2 - 16 - 2 - 2 - 1 if t.size.width else 0
        for b in self.items:
            why = b.why
            if room and len(why) > room:
                why = why[:max(room - 1, 8)].rstrip() + glyph("ellipsis")
            t.add_row(when(b.made), why)
        where = str(self.session.backup_dir or backups.BACKUP_DIR).replace(str(__import__("pathlib").Path.home()), "~")
        n = len(self.items)
        self.query_one("#bk-where", Static).update(
            f"[$forge-muted]{n} backup{'s' if n != 1 else ''} · {escape(where)}[/]")
        if self.items:
            t.move_cursor(row=min(keep or 0, n - 1))
            self._show(self.items[t.cursor_row])
        else:
            self.query_one("#bk-diff", Static).update(
                "[$forge-muted]No backups yet. Every save makes one; [b]Back Up Now (n)[/] makes one any time.[/]")
        for bid in ("#bk-restore", "#bk-show", "#bk-delete"):
            self.query_one(bid, Button).disabled = not self.items

    def current(self) -> backups.Backup | None:
        t = self.query_one("#bk-table", DataTable)
        if not self.items or t.cursor_row is None or t.cursor_row >= len(self.items):
            return None
        return self.items[t.cursor_row]

    @on(DataTable.RowHighlighted, "#bk-table")
    def _moved(self, e: DataTable.RowHighlighted) -> None:
        if 0 <= e.cursor_row < len(self.items):
            self._show(self.items[e.cursor_row])

    def _show(self, b: backups.Backup) -> None:
        diff = differences(self.session, b)
        box = self.query_one("#bk-diff", Static)
        if diff is None:
            box.update(f"[$forge-warn]{glyph('warn')} This backup can't be read, so it can't be compared.[/]")
        elif not diff:
            box.update(f"[$forge-ok]{glyph('ok')} Nothing: it is the same as today's settings.[/]")
        else:
            lines = [f"[$forge-muted]{escape(w)}[/]\n   {escape(now)} [$forge-muted]→[/] "
                     f"[$forge-changed]{escape(then)}[/]" for w, now, then in diff]
            box.update("\n".join(lines))

    # ── actions ───────────────────────────────────────────────────────────────
    @work(exclusive=True, group="af-write")
    async def action_restore(self) -> None:
        b = self.current()
        if b is None:
            return
        lines = [f"Your settings go back to {when(b.made)} ({b.why.lower()}).",
                 "What's there now is backed up first, so this can be undone."]
        if self.session.change_count:
            lines.append("Your unsaved changes are dropped.")
        ok = await self.app.push_screen_wait(ConfirmDialog(
            "[b]Restore this backup?[/]\n\n" + "\n".join(lines), confirm_label="Restore (y)", default_no=True))
        if not ok:
            return
        self.session.discard()
        backups.restore(b, path=self.session.path, backup_dir=self.session.backup_dir)
        self.app.after_file_changed()
        self.app.notify(f"Restored the backup from {when(b.made)}. Alacritty is using it now.", title="Restored")

    def action_new(self) -> None:
        self.app.backup_now()
        self.refresh_view()

    @work(exclusive=True, group="af-write")
    async def action_delete(self) -> None:
        b = self.current()
        if b is None:
            return
        ok = await self.app.push_screen_wait(ConfirmDialog(
            f"[b]Delete this backup?[/]\n\nThe backup from {when(b.made)} ({b.why.lower()}) is deleted for good.",
            confirm_label="Delete (y)", danger=True, default_no=True))
        if ok:
            backups.delete(b)
            self.refresh_view()
            self.app.query_one("#sec-overview").refresh_view()

    def show_file(self) -> None:
        b = self.current()
        if b is None:
            return
        try:
            text = b.path.read_text(encoding="utf-8")
        except OSError as e:
            text = f"(can't be read: {e.strerror})"
        self.app.push_screen(WholeFile(f"Backup from {when(b.made)}", text))

    def on_button_pressed(self, e: Button.Pressed) -> None:
        bid = e.button.id or ""
        if not bid.startswith("bk-"):
            return
        e.stop()
        {"bk-restore": self.action_restore, "bk-new": self.action_new, "bk-show": self.show_file,
         "bk-delete": self.action_delete}[bid]()


class WholeFile(ForgePanelScreen):
    def __init__(self, title: str, text: str) -> None:
        super().__init__()
        self.panel_title = title
        self._text = text

    def compose_body(self) -> ComposeResult:
        # the file's own text, never read as markup (0.2.0 lost "[colors]" lines this way)
        yield Static(escape(self._text))
