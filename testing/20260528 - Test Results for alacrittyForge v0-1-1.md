# alacrittyForge — v0.1.1 test results

Dogfood results for the v0.1.1 hardening + first-AUR-release cycle. Companion to `20260528 - Test Matrix for alacrittyForge v0-1-1.md`. Verifies all 6 findings (A1–A6) from the v0.1.0 audit are closed.

**Outcome: PASS — shipped v0.1.1-1 (2026-05-28).** GitHub tag `v0.1.1` + release live; AUR `alacrittyforge` at `0.1.1-1` (first AUR submission); Issues #1–#6 closed; milestone v0.1.1 closed.

## Method

Two-layer verification:

1. **Textual `Pilot` automated tests** (headless, run during development) — covered each group as it landed:
   - **G1** pending survives `config → dashboard → config` switch and `action_refresh`; `_load_settings` (full reset) still resets to `{}`. Same for Fonts.
   - **G2** all five screens carry `StatusMixin` with the right `STATUS_WIDGET_ID`; **zero popups fire at startup** (`popup=False` for `on_mount` hints holds); pressing R on each screen toasts the expected message.
   - **G3** `?` opens HelpScreen; second `?` toggles closed (not stack); Esc closes; q closes WITHOUT quitting the app; `?` while modal is up closes via the modal's own binding.
   - **G4** every action screen's `DEFAULT_FOCUS` widget is focused after `action_show_screen`; `pilot.press("r")` fires `action_refresh` on Fonts and Key Bindings with no prior click; `ConfirmDialog` Esc → False, Enter → True.

2. **Real-hardware dogfood** (Javier, local install of the AUR-built artifact). Reported: *"testing worked perfectly."*

## Results by group

### G1 — Pending safety (A1) — PASS
- §1.1 / §1.2 / §1.3 — staging an edit on Config Editor (and Fonts), switching to the Dashboard, and switching back: pending edits **survive**. ✓ (Pilot + dogfood.)
- Post-save still hard-resets via `_load_settings` (`_pending = {}` + reload + announce).

### G2 — Unified feedback surface (A3, A6) — PASS
- §1.4 — action feedback now surfaces in **both** the in-screen status line and a bottom-right toast. ✓
- §1.5 / §1.6 — fonts and keybindings have a single status channel; redundant secondary labels removed. ✓
- §1.7 (regression guard) — **no startup popup spray**. ✓ (Pilot-confirmed: `startup_notifs == []`.)
- §1.8 — unicode icons `✓ ● ⚠ ✗` canonical everywhere.

### G3 — Help modal hardening (A2) — PASS
- §1.9–§1.13 — `?` opens; `?` again toggles closed; Esc closes; q closes without quitting the app; help lists global + per-screen sections. ✓

### G4 — Focus-on-show + ConfirmDialog keys (A4, A5) — PASS
- §1.14 / §1.15 — first keypress on each action screen fires the right action with no prior panel click. ✓
- §1.16 / §1.17 — `ConfirmDialog` Esc cancels, Enter confirms. ✓
- §1.18 — global 1–5 / q / ? still work with a list/table focused on entry.

### Regression — version sync + packaging (1.19–1.22) — PASS
- `alacrittyforge.__version__` = `0.1.1`. ✓
- Man page `.TH` = `v0.1.1`. ✓
- PKGBUILD `check()` printed `alacrittyforge headless mount OK` in the fakeroot build. ✓
- Built `alacrittyforge-0.1.1-1-any.pkg.tar.zst` carries **no `__pycache__`/`.pyc`** (`tar tf` clean). ✓

## Packaging

- This is alacrittyForge's **first AUR submission** — the AUR side was a fresh `git init` + initial commit on master.
- The PKGBUILD's `check()` step adopts grubForge v1.0.3's hardened headless mount (`asyncio.run(app.run_test() ...)`) instead of a bare import smoke. Catches CSS-parse / `on_mount` failures at build time.
- `PYTHONDONTWRITEBYTECODE=1` + defensive `find -name __pycache__ -exec rm` keep the `.pyc` install-conflict class (the v1.0.2 grubForge bug) from recurring.
- AUR index propagation: the search RPC took ~minutes to index the new package after push; the package page and git URL were live immediately (`HTTP 200`).

## Observations / backlog (not v0.1.1 blockers)

- None this cycle. The dogfood was clean. v0.2.0 candidates from the existing roadmap (dropdown selectors, scrollable font picker, hex color picker, backup-restore screen, screenshots) remain as-is.

## Pass criteria

All 1.1–1.18 (the 6 findings + regression guards) verified; 1.19–1.22 version sync + packaging confirmed before tag. **Release approved and shipped.**
