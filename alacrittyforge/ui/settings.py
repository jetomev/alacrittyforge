"""Settings — every Alacritty setting as a form with visible controls (v1.0.0).

Groups on the left, the group's settings on the right, and "About this
setting" following the focus — the same form as grubForge 2.0. Known values
are picked: numbers have presets, switches say On/Off, a few choices sit in
one row, longer lists open, and fonts and shells come from this computer.
A setting the file doesn't set shows what Alacritty does instead; picking
that same value leaves it unset. Nothing is written until Save.
"""

from __future__ import annotations

from rich.markup import escape
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import ContentSwitcher, Input, OptionList, Select, Static
from textual.widgets.option_list import Option

from forgekit import Choices, FilterPicker, Notice, NumberPresets, SettingRow, Toggle, glyph

from ..session import font_styles, monospace_families, shells
from ..settings_spec import BY_KEY, GROUPS, SETTINGS, Setting, default_words, shell_program, shown, to_store

UNSET = "__unset__"
OTHER = "__other__"
SELECT_HINTS = [("Enter", "open list"), ("type", "jump to a match"), ("Tab", "next"), ("F1", "help")]


class SettingsScreen(Horizontal):
    def __init__(self, session, **kw) -> None:
        super().__init__(**kw)
        self.session = session
        self.rows: dict[str, SettingRow] = {}

    # ── the lists a Select offers ─────────────────────────────────────────────
    def options_for(self, s: Setting) -> list[tuple[str, str]]:
        """(value, label) for a list setting; the first is "not set" when unset is allowed."""
        cur = self.session.value(s.key)
        opts: list[tuple[str, str]] = []
        if s.control == "font":
            if s.key == "font.normal.family":
                opts.append((UNSET, f"Not set ({default_words(s)})"))
            else:
                opts.append((UNSET, "Same as the main font"))
            if cur:
                opts.append((cur, cur))
            opts.append((OTHER, f"Choose a font{glyph('ellipsis')}"))
        elif s.control == "style":
            fam = self.session.value("font.normal.family") or "monospace"
            opts.append((UNSET, f"Not set ({default_words(s)})"))
            opts += [(st, st) for st in font_styles(fam)]
        elif s.control == "shell":
            opts.append((UNSET, "Not set (your login shell)"))
            opts += [(p, p.rsplit("/", 1)[-1]) for p in shells()]
            opts.append((OTHER, f"Another program{glyph('ellipsis')}"))
            cur = shell_program(cur)
        else:
            opts.append((UNSET, f"Not set ({default_words(s)})"))
            opts += [(v, l) for v, l in s.choices]
        if cur and all(v != cur for v, _l in opts):
            label = cur.rsplit("/", 1)[-1] if s.control == "shell" else str(cur)
            opts.insert(1, (cur, f"{label}  (current)"))
        return opts

    def _select_value(self, s: Setting) -> str:
        cur = self.session.value(s.key)
        if s.control == "shell":
            cur = shell_program(cur)
        return UNSET if cur is None else cur

    # ── building the form ─────────────────────────────────────────────────────
    def compose(self) -> ComposeResult:
        groups = OptionList(*(Option(label, id=gid) for gid, label, _d in GROUPS), id="af-groups")
        groups.FORGE_HINTS = [("↑↓", "choose a group"), ("Tab", "its settings"), ("F10", "save"), ("?", "all keys")]
        yield groups
        with Vertical(id="af-settings-right"):
            if not self.session.readable:
                yield Notice("Your settings file can't be read, so nothing can be changed here",
                             [escape(self.session.file.error or ""),
                              "Restore a backup on the Backups screen, or fix the line and press R."],
                             level="warn", id="af-readonly")
            with ContentSwitcher(initial=f"grp-{GROUPS[0][0]}", id="af-groupforms"):
                for gid, label, desc in GROUPS:
                    with VerticalScroll(id=f"grp-{gid}", classes="af-group", can_focus=False):
                        yield Static(f"[b $forge-title-accent]{label}[/]   [$forge-muted]{escape(desc)}[/]",
                                     classes="af-group-title")
                        for s in SETTINGS:
                            # left out when the installed Alacritty doesn't have it
                            if s.group == gid and self.session.names.has(s.key):
                                row = self._row(s)
                                self.rows[s.key] = row
                                yield row
            yield Static("", id="af-about")

    def _row(self, s: Setting) -> SettingRow:
        disabled = not self.session.readable
        value = self.session.value(s.key)
        current = s.default if value is None else value
        if s.control == "number":
            presets = [(self._num(s, p), self._num(s, p)) for p in s.presets]
            ctrl = NumberPresets(self._num(s, current if current is not None else 0),
                                 [(str(l), v) for l, v in presets], unit=s.unit,
                                 minimum=None if s.lo is None else self._num(s, s.lo),
                                 maximum=None if s.hi is None else self._num(s, s.hi),
                                 decimals=s.kind is float and s.scale == 1, disabled=disabled)
        elif s.control == "switch":
            ctrl = Toggle(bool(current), disabled=disabled)
        elif s.control == "choices":
            ctrl = Choices(s.choices, current, disabled=disabled)
        elif s.control in ("list", "font", "style", "shell"):
            ctrl = Select([(l, v) for v, l in self.options_for(s)], value=self._select_value(s),
                          allow_blank=False, disabled=disabled)
            ctrl.FORGE_HINTS = SELECT_HINTS
        else:   # text, colour
            ctrl = Input(value or "", placeholder=default_words(s), disabled=disabled)
            ctrl.FORGE_HINTS = [("type", "a value"), ("Tab", "next"), ("F1", "help")]
        ctrl.setting_key = s.key
        note = " · ".join(n for n in (s.note, s.when) if n)
        return SettingRow(s.label, ctrl, note=note, help=s.help, setting=s.key, id=f"row-{s.key.replace('.', '-')}")

    @staticmethod
    def _num(s: Setting, stored: float) -> float:
        n = stored * s.scale
        return int(round(n)) if s.kind is int or s.scale != 1 else n

    def row(self, key: str) -> SettingRow:
        return self.rows[key]

    def on_mount(self) -> None:
        self.query_one("#af-groups", OptionList).highlighted = 0
        for key in self.session.pending:
            self._mark(key)
        self._cursors_home()

    def _cursors_home(self) -> None:
        for inp in self.query(Input):
            if not inp.has_focus:
                inp.cursor_position = 0

    # ── moving around ─────────────────────────────────────────────────────────
    @on(OptionList.OptionHighlighted, "#af-groups")
    def _group(self, e: OptionList.OptionHighlighted) -> None:
        self.query_one("#af-groupforms", ContentSwitcher).current = f"grp-{e.option.id}"

    def show_group(self, gid: str) -> None:
        ids = [g for g, _l, _d in GROUPS]
        self.query_one("#af-groups", OptionList).highlighted = ids.index(gid)

    def on_descendant_focus(self, e) -> None:
        row = next((a for a in e.widget.ancestors_with_self if isinstance(a, SettingRow)), None)
        about = self.query_one("#af-about", Static)
        if row is None:
            about.update("")
            return
        s = BY_KEY[row.setting]
        about.update(
            f"[$forge-muted]{'─' * 3} About this setting {'─' * 40}[/]\n"
            f"{escape(s.help)}\n"
            f"[$forge-muted]Alacritty name: {s.key}  ·  when not set: {escape(default_words(s))}"
            f"  ·  F1 opens the manual[/]")

    # ── changes ───────────────────────────────────────────────────────────────
    def _stage(self, key: str, value) -> None:
        s = BY_KEY[key]
        # Alacritty's own value, picked while the file doesn't set it, stays unset
        if self.session.original(key) is None and value is not None and value == s.default \
                and not (isinstance(value, bool) ^ isinstance(s.default, bool)):
            value = None
        self.session.set(key, value)
        self._mark(key)
        self.app.refresh_state()

    def _mark(self, key: str) -> None:
        row = self.rows.get(key)
        if row is None:
            return
        if key in self.session.pending:
            row.mark_changed(self.session.shown(key, self.session.original(key)))
        else:
            row.mark_unchanged()

    @on(NumberPresets.Changed)
    def _number(self, e: NumberPresets.Changed) -> None:
        key = getattr(e.number, "setting_key", None)
        if key:
            e.stop()
            self._stage(key, to_store(BY_KEY[key], e.value))

    @on(Toggle.Changed)
    def _toggle(self, e: Toggle.Changed) -> None:
        key = getattr(e.toggle, "setting_key", None)
        if key:
            e.stop()
            self._stage(key, bool(e.value))

    @on(Choices.Changed)
    def _choices(self, e: Choices.Changed) -> None:
        key = getattr(e.choices, "setting_key", None)
        if key:
            e.stop()
            self._stage(key, e.value)

    @on(Select.Changed)
    def _select(self, e: Select.Changed) -> None:
        key = getattr(e.select, "setting_key", None)
        if key is None:
            return
        e.stop()
        if e.value == OTHER:
            self._other(BY_KEY[key], e.select)
            return
        self._stage(key, None if e.value == UNSET else e.value)
        if key == "font.normal.family":
            self._refresh_styles()

    def _other(self, s: Setting, select: Select) -> None:
        if s.control == "font":
            options = monospace_families() or []
            hint = (f"{len(options)} monospace fonts on this computer; type to filter" if options else
                    "No monospace fonts found on this computer; type a font's name")
            custom = not options
        else:
            options = shells()
            hint = "Shells on this computer, or type the full path of another program"
            custom = True

        def done(value: str | None) -> None:
            if not value:
                with select.prevent(Select.Changed):
                    select.value = self._select_value(s)
                return
            opts = self.options_for(s)
            if all(v != value for v, _l in opts):
                opts.insert(1, (value, value.rsplit("/", 1)[-1] if s.control == "shell" else value))
            with select.prevent(Select.Changed):
                select.set_options([(l, v) for v, l in opts])
                select.value = value
            self._stage(s.key, value)
            if s.key == "font.normal.family":
                self._refresh_styles()

        current = self.session.value(s.key)
        self.app.push_screen(FilterPicker(s.label, options, current=shell_program(current) or "",
                                          allow_custom=custom, hint=hint), done)

    def _refresh_styles(self) -> None:
        """A new font has its own styles."""
        s = BY_KEY["font.normal.style"]
        sel = self.rows[s.key].control
        with sel.prevent(Select.Changed):
            sel.set_options([(l, v) for v, l in self.options_for(s)])
            sel.value = self._select_value(s)

    @on(Input.Changed)
    def _text(self, e: Input.Changed) -> None:
        key = getattr(e.input, "setting_key", None)
        if key:
            e.stop()
            self._stage(key, e.value or None)

    # ── after save / discard / reload ─────────────────────────────────────────
    def sync(self) -> None:
        """Put every control back to the session's values and marks."""
        for key, row in self.rows.items():
            s, ctrl = BY_KEY[key], row.control
            value = self.session.value(key)
            current = s.default if value is None else value
            if isinstance(ctrl, Select):
                with ctrl.prevent(Select.Changed):
                    ctrl.set_options([(l, v) for v, l in self.options_for(s)])
                    ctrl.value = self._select_value(s)
            elif isinstance(ctrl, Toggle):
                ctrl.set_value(bool(current), announce=False)
            elif isinstance(ctrl, NumberPresets):
                ctrl.set_value(self._num(s, current if current is not None else 0), announce=False)
            elif isinstance(ctrl, Choices):
                ctrl.set_value(current, announce=False)
            elif isinstance(ctrl, Input):
                with ctrl.prevent(Input.Changed):
                    ctrl.value = value or ""
            ctrl.disabled = not self.session.readable
            self._mark(key)
        self._cursors_home()
