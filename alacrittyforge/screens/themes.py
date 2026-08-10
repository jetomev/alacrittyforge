# ═══════════════════════════════════════════════════════════
#  AlacrittyForge — Themes Screen (v0.2.0 redesign)
#
#  Javier's ruling — the staging flow:
#    · list shows Name + path; the ACTIVE theme always first, yellow,
#      with its ✔ icon; a staged theme wears orange with a 🕓 clock
#    · Preview opens a floating window: palette + file preview, with
#      state-aware buttons — [Active (disabled)|Close] for the live
#      theme, [Activate|Close] otherwise; Activate stages (turns
#      orange, disables) and writes NOTHING
#    · back in the list, an orange clock line under the title says the
#      staged theme awaits Apply Theme — which confirms, backs up, and
#      generates the file
#  Plus the inline-colors model: colors written directly in
#  alacritty.toml appear as the active "(inline colors)" entry, with
#  Save-as-theme to promote them into a real themes/ file.
# ═══════════════════════════════════════════════════════════

from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, Input, Label, ListItem, ListView, Static

from forgekit import ConfirmDialog, ForgeModal, ForgePanelScreen

from ..theme_manager import (
    list_themes, apply_theme, get_theme_raw_text, get_themes_help_text,
    has_inline_colors, save_inline_as_theme, THEMES_DIR,
)
from ..widgets.status import StatusMixin

_ORANGE = "#fab387"
_YELLOW = "#f9e2af"


class ThemePreviewModal(ForgeModal):
    """Floating theme preview with the state-aware Activate flow."""

    BINDINGS = [Binding("escape", "close", "", show=False)]

    def __init__(self, theme: dict, is_active: bool, is_staged: bool) -> None:
        super().__init__()
        self._theme = theme
        self._is_active = is_active
        self._staged = is_staged

    def compose(self) -> ComposeResult:
        t = self._theme
        with Vertical(classes="forge-panel"):
            yield Static(f"Preview — {t['name']}", classes="forge-panel-title")
            with VerticalScroll(classes="forge-panel-body"):
                yield Static(f"[#89b4fa]Path[/]  [#cdd6f4]{t['path']}[/]\n")
                palette = "\n".join(
                    f"  [{c['hex']}]█[/]  [#a6adc8]{c['label']:<28}[/]  "
                    f"[#6c7086]{c['hex']}[/]"
                    for c in t["colors"]
                ) or "[#6c7086]No colors detected in this theme.[/]"
                yield Static(palette)
                raw = get_theme_raw_text(Path(t["path"]))
                lines = raw.splitlines()[:60]
                preview = "\n".join(lines)
                if len(raw.splitlines()) > 60:
                    preview += "\n[#6c7086]… (truncated)[/]"
                yield Static(f"\n[#cba6f7 b]── theme.toml ──[/]\n{preview}")
            with Horizontal(classes="forge-buttons forge-panel-footer"):
                if self._is_active:
                    b = Button("Active", id="btn-state", disabled=True)
                    b.styles.background = _YELLOW
                    b.styles.color = "#1e1e2e"
                    yield b
                else:
                    b = Button("Activate", id="btn-state", variant="primary")
                    if self._staged:
                        b.label = "Staged"
                        b.disabled = True
                        b.styles.background = _ORANGE
                        b.styles.color = "#1e1e2e"
                    yield b
                yield Button("Close", id="btn-close")

    def on_button_pressed(self, e: Button.Pressed) -> None:
        if e.button.id == "btn-state" and not e.button.disabled:
            # Stage it: orange, disabled, nothing written. Close remains.
            self._staged = True
            e.button.label = "Staged"
            e.button.disabled = True
            e.button.styles.background = _ORANGE
            e.button.styles.color = "#1e1e2e"
        elif e.button.id == "btn-close":
            self.dismiss(self._staged)

    def action_close(self) -> None:
        self.dismiss(self._staged)


class SaveInlineModal(ForgeModal):
    """Name prompt for promoting inline colors into a theme file."""

    BINDINGS = [Binding("escape", "cancel", "", show=False)]

    def compose(self) -> ComposeResult:
        with Vertical(classes="forge-panel field-edit"):
            yield Static("Save current colors as a theme", classes="forge-panel-title")
            with VerticalScroll(classes="forge-panel-body"):
                yield Static(
                    "[#a6adc8]The [colors] blocks in your alacritty.toml "
                    f"become a file in {THEMES_DIR}/ — browsable, previewable, "
                    "reusable. Your config is not modified.[/]"
                )
                yield Label("Theme name")
                yield Input(placeholder="my-theme", id="theme-name")
            with Horizontal(classes="forge-buttons forge-panel-footer"):
                yield Button("Save", id="save", variant="primary")
                yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        self.query_one("#theme-name", Input).focus()

    def on_input_submitted(self, e: Input.Submitted) -> None:
        self.dismiss(e.value)

    def on_button_pressed(self, e: Button.Pressed) -> None:
        if e.button.id == "save":
            self.dismiss(self.query_one("#theme-name", Input).value)
        else:
            self.dismiss(None)

    def action_cancel(self) -> None:
        self.dismiss(None)


class ThemesHelpWindow(ForgePanelScreen):
    panel_title = "Themes — installation guide"
    CLOSE_KEYS = ("q", "h")

    def compose_body(self) -> ComposeResult:
        yield Static(get_themes_help_text())


class ThemesScreen(StatusMixin, Static):
    """Browse, preview, stage, and apply Alacritty color themes."""

    STATUS_WIDGET_ID = "themes-status"
    DEFAULT_FOCUS = "#themes-list"

    BINDINGS = [
        Binding("p",  "preview",      "Preview", show=True),
        Binding("a",  "apply_staged", "Apply",   show=True),
        Binding("f5", "refresh",      "Refresh", show=True),
        Binding("h",  "help_window",  "Help",    show=True),
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._themes: list[dict] = []
        self._rows: list[dict] = []          # display order incl. inline entry
        self._staged_path: str | None = None

    def compose(self) -> ComposeResult:
        with Vertical(classes="main-area"):
            yield Label(
                "🎨  Themes  (P preview · A apply staged · H help)",
                classes="section-title",
            )
            yield Label("", id="staged-banner")
            yield ListView(id="themes-list")
            with Horizontal(classes="forge-buttons forge-panel-footer",
                            id="themes-footer"):
                yield Button("Preview",               id="btn-preview", variant="primary")
                yield Button("Apply Theme",           id="btn-apply")
                yield Button("Save colors as theme…", id="btn-saveinline")
            yield Label("", id="themes-status")

    def on_mount(self) -> None:
        self._reload_view()
        if self._themes or has_inline_colors():
            self._set_status("Select a theme and press P to preview.", "info",
                             popup=False)
        else:
            self._set_status("No themes found. Press H for installation help.",
                             "warn", popup=False)

    def on_show(self) -> None:
        self._reload_view()

    # ── list ──────────────────────────────────────────────────────────

    def _reload_view(self) -> None:
        self._themes = list_themes()

        rows: list[dict] = []
        if has_inline_colors():
            active_inline = not any(t["active"] for t in self._themes)
            rows.append({
                "kind": "inline",
                "name": "(inline colors — written in alacritty.toml)",
                "path": "~/.config/alacritty/alacritty.toml",
                "active": active_inline,
            })
        for t in self._themes:
            rows.append({"kind": "file", "active": t["active"],
                         "name": t["name"], "path": str(t["path"]),
                         "theme": t})

        # Active first — always.
        rows.sort(key=lambda r: (not r["active"],))
        self._rows = rows

        lv = self.query_one("#themes-list", ListView)
        lv.clear()
        if not rows:
            lv.append(ListItem(Label(
                "  No themes found — press H for the installation guide.")))
        for r in rows:
            if r["active"]:
                mark = f"[{_YELLOW} b]✔ {r['name']}[/]  [{_YELLOW}]· active[/]"
            elif self._staged_path and r.get("path") == self._staged_path:
                mark = f"[{_ORANGE} b]🕓 {r['name']}[/]  [{_ORANGE}]· staged[/]"
            else:
                mark = f"  {r['name']}"
            lv.append(ListItem(Label(f"{mark}\n  [#6c7086]{r['path']}[/]")))

        banner = self.query_one("#staged-banner", Label)
        if self._staged_path:
            name = Path(self._staged_path).stem
            banner.update(
                f"[{_ORANGE}]🕓 Staged: {name} — press A / Apply Theme to "
                f"generate alacritty.toml.[/]"
            )
        else:
            banner.update("")

    def _selected_row(self) -> dict | None:
        lv = self.query_one("#themes-list", ListView)
        idx = lv.index
        if idx is None or idx >= len(self._rows):
            return None
        return self._rows[idx]

    # ── actions ───────────────────────────────────────────────────────

    def on_button_pressed(self, e: Button.Pressed) -> None:
        if e.button.id == "btn-preview":
            self.action_preview()
        elif e.button.id == "btn-apply":
            self.action_apply_staged()
        elif e.button.id == "btn-saveinline":
            self.action_save_inline()

    def on_list_view_selected(self, e: ListView.Selected) -> None:
        self.action_preview()

    def action_preview(self) -> None:
        row = self._selected_row()
        if row is None:
            self._set_status("Select a theme first.", "warn")
            return
        if row["kind"] == "inline":
            self._set_status(
                "These colors live in alacritty.toml itself — use "
                "'Save colors as theme…' to make them a previewable file.",
                "info",
            )
            return

        theme = row["theme"]

        def on_close(staged) -> None:
            if staged and not row["active"]:
                self._staged_path = str(theme["path"])
                self._set_status(
                    f"Staged '{theme['name']}' — Apply Theme writes the file.",
                    "warn",
                )
            self._reload_view()

        self.app.push_screen(
            ThemePreviewModal(
                {**theme, "path": str(theme["path"])},
                is_active=row["active"],
                is_staged=(self._staged_path == str(theme["path"])),
            ),
            on_close,
        )

    def action_apply_staged(self) -> None:
        if not self._staged_path:
            self._set_status(
                "Nothing staged — preview a theme and press Activate first.",
                "warn",
            )
            return
        name = Path(self._staged_path).stem

        def on_confirm(confirmed: bool) -> None:
            if not confirmed:
                self._set_status("Apply cancelled — theme stays staged.", "info")
                return
            ok, msg = apply_theme(Path(self._staged_path))
            if ok:
                self._staged_path = None
                self._reload_view()
                self._set_status(msg, "ok")
            else:
                self._set_status(msg, "error")

        self.app.push_screen(
            ConfirmDialog(
                f"Generate alacritty.toml with theme '{name}'?\n\n"
                "A backup is created first. Inline [colors] blocks are "
                "replaced by the theme import.",
                "Apply",
            ),
            on_confirm,
        )

    def action_save_inline(self) -> None:
        if not has_inline_colors():
            self._set_status("No inline [colors] in alacritty.toml.", "warn")
            return

        def on_name(name) -> None:
            if not name:
                return
            ok, msg = save_inline_as_theme(name)
            self._reload_view()
            self._set_status(msg, "ok" if ok else "error")

        self.app.push_screen(SaveInlineModal(), on_name)

    def action_refresh(self) -> None:
        self._reload_view()
        self._set_status("Theme list refreshed.", "info")

    def action_help_window(self) -> None:
        self.app.push_screen(ThemesHelpWindow())
