# alacrittyForge — v0.1.1 release test matrix

Fix-verification matrix for the v0.1.1 hardening + first-AUR-release cycle. Each check confirms one of the 6 findings (A1–A6) from the v0.1.0 audit is closed, plus regression guards for the new mechanisms.

## How to run

1. Test against a **clean install of alacrittyforge v0.1.1-1 from the AUR** (`yay -S alacrittyforge` post-AUR-push) on an Arch host with `python-textual ≥ 8.2.7`. Launch with `alacrittyforge` (no sudo needed — it's a user-space tool that writes only to `~/.config/alacritty/`).
2. Tick each `[ ]` box as verified.
3. If anything fails, stop and log it in the v0.1.1 Test Results before continuing.

The fixes shipped in four thematic groups (commits `181dbf1` G1, `ad31f45` G2, `c284d23` G3, `38c251c` G4). The matrix is grouped the same way.

---

## 1. v0.1.1 hardening verification

### 1.G1 — Pending safety (A1) — the bug-class fix

- [ ] **1.1** (A1) Open the app. Press **2** (Config Editor). Use ↑↓ to highlight a row (e.g. `window.opacity`). Press **E**, type a new value (e.g. `0.85`), click **Apply Edit** — row shows `⏳ Pending: 0.85` in the detail panel. **Switch to Dashboard (1), then back to Config Editor (2). The pending edit is still there** — row still shows pending. *(Was: silently wiped.)*
- [ ] **1.2** (A1) Repeat 1.1 on **Fonts (4)**: stage an edit, switch away, switch back — pending survives.
- [ ] **1.3** (A1 follow-through) On Config Editor with the pending edit, press **R** (Refresh). Pending is **preserved** (user-initiated R doesn't drop staged edits). Then press **S** → confirm → pending writes to disk and clears.

### 1.G2 — Unified feedback (A3, A6)

- [ ] **1.4** (A3) On any action screen (Config Editor / Themes / Fonts / Key Bindings) trigger a success action (e.g. **R** refresh). Feedback appears as **both** an in-screen status line **and** a bottom-right **toast popup**. *(Was: status-line only — easy to miss.)*
- [ ] **1.5** (A6) On Fonts: stage an edit. The "Staged: …" message appears in the status line at the bottom of the left panel — **not duplicated** in a right-panel label. (The redundant `#font-save-status` label is gone.)
- [ ] **1.6** (A6) On Key Bindings: add a binding. The "Added …" success message appears in the unified channel (line + toast), not in a separate right-panel label.
- [ ] **1.7** (G2 regression guard) Launch the app. **No popups fire before you press anything.** Mount-time hints stay on the status line only. *(Avoids the spray that nearly-bit grubForge G3→G1.)*
- [ ] **1.8** (G2 icons) Status icons are the unicode set `✓ ● ⚠ ✗` — no ASCII drift on any screen.

### 1.G3 — Help modal hardening (A2)

- [ ] **1.9** (A2) Press **?**. A centered help **modal** opens.
- [ ] **1.10** (A2) Press **?** again → it **closes** (toggle, doesn't stack a second modal on top). *(Was: pressed ? twice and the app stacked two modals.)*
- [ ] **1.11** (A2) Open help, press **Esc** → closes.
- [ ] **1.12** (A2) Open help, press **q** → closes **AND the app does NOT quit**. (The modal binds `q` so it shadows the app-level quit while help is up.)
- [ ] **1.13** (A2) The help modal lists global keys, plus per-screen sections for Config Editor / Themes / Fonts / Key Bindings.

### 1.G4 — Focus-on-show + ConfirmDialog keys (A4, A5)

- [ ] **1.14** (A4) Enter the Config Editor via the **2** key. **Without clicking anywhere**, press **R** → the "Refreshed from disk." status line and toast fire immediately. *(Was: inert until a panel click — `ContentSwitcher` doesn't move focus on its own.)*
- [ ] **1.15** (A4) Repeat for Themes (**3** then **F5**), Fonts (**4** then **R**), Key Bindings (**5** then **R**). Each responds to its first keypress without a click.
- [ ] **1.16** (A5) Open any confirmation dialog (e.g. save changes). Press **Esc** → dialog cancels and you return to the screen. *(Was: had to Tab+Space onto Cancel.)*
- [ ] **1.17** (A5) Open a confirmation dialog. Press **Enter** → dialog confirms.
- [ ] **1.18** (A4 regression guard) With a list/table focused on entry (the A4 side-effect), the global keys still work: **1–5** navigate, **q** quits from a normal screen, **?** opens help.

### 1.regression — version sync + Textual compatibility

- [ ] **1.19** `python -c "import alacrittyforge; print(alacrittyforge.__version__)"` prints **0.1.1**.
- [ ] **1.20** Man page `.TH` line reads **v0.1.1**.
- [ ] **1.21** PKGBUILD `check()` headless mount smoke prints `alacrittyforge headless mount OK` during `makepkg`.
- [ ] **1.22** Built package carries **no `__pycache__`/`.pyc`** (`tar tf grubforge-…pkg.tar.zst | grep pyc` is empty). The `PYTHONDONTWRITEBYTECODE=1` + defensive `__pycache__` cleanup in `package()` are in effect.

---

## Pass criteria for v0.1.1 release

- **1.1–1.17** (the 6 findings) must pass.
- **1.7, 1.18** (regression guards) must pass — they protect against the new mechanisms (unified feedback, focus-on-show) introducing fresh breakage.
- **1.19–1.22** must pass before tag.

If 1.1/1.2 fails: G1's `_reload_view` is being skipped or `_load_settings` is still being called from `on_show`. Check `screens/config_editor.py:on_show` and `screens/fonts.py:on_show`.

If 1.7 fails (popups at startup): the `popup=False` parameter on passive mount hints isn't being honored — check `widgets/status.py::StatusMixin._set_status` and the `on_mount` paths.

If 1.10 fails (stacking on `?`): the app's toggle guard in `action_show_help` isn't checking `isinstance(self.screen, HelpScreen)`.

If 1.14/1.15 fails (keys inert): the `DEFAULT_FOCUS` focus call in `App.action_show_screen` isn't being reached, or the id is wrong.

---

## Out of scope

- v0.2.0 feature roadmap (dropdowns, font/color pickers, restore screen, screenshots) — deferred to the next cycle.
- Cross-distribution install verification — primary target is Arch via AUR.
