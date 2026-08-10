# Test Matrix & Results — alacrittyForge v0.2.0 (2026-08-10)

**Scope:** the forgekit migration + Javier's in-place editing redesign, developed
over three same-session field-review rounds. Two legs per round: headless pilot
suites + live field testing on Javier's real `~/.config/alacritty/`.

## Leg 1 — headless pilot suites (3, all green at ship)

- **Suite 1 (migration)**: sections 1–5 switch (digits), `?`/`Ctrl+H`/`q`
  shortcuts toggle via kit `CLOSE_KEYS`, Help→About, Config save → kit
  ConfirmDialog (cancelled — nothing written), all sections mount.
- **Suite 2 (redesign round 1)**: field-options knowledge (enums, booleans,
  `/etc/shells`), Dashboard theme-model detection, Config 3-column table +
  dropdown staging + confirm, Themes model-aware rows + save-inline modal +
  help window, Fonts/Bindings mount.
- **Suite 3 (redesign round 2)**: dropdown anchored at the VALUE column
  (measured against the key-column render width), color swatch cells render
  as Rich Text with ■, font family → FilterPickerModal (486 mono families),
  Bindings staged new/edit/delete + mods dropdown + confirm.
- Suites made **theming-model-agnostic** mid-cycle: Javier ran the full
  save-colors-as-theme → stage → apply flow on his real config during
  testing, converting it from inline to import-based — the tests now accept
  both models (a production validation disguised as a test failure).

## Leg 2 — field findings across the three rounds (all closed)

R1: dropdown appeared over the Keys column → anchored at Value column;
font families needed options (mono only per ruling); color values wanted
swatches; long lists needed an alternative → FilterPickerModal;
Bindings "same application as Config" → cell-level staged editor;
theme "shows none" → inline-colors model support + save-as-theme.
R2/R3: verified fixes; Fonts rebuilt on the pattern ("95% done" → done).

## Kit growth driven by this migration

forgekit 0.3.0: F-9 form-widget + DataTable styling promoted into
`FORGE_CSS`; finding #5 resolved via `ForgePanelScreen.CLOSE_KEYS`.
Promotion candidates queued: FilterPickerModal, ListView styling.

## Field verdict

Javier, on the redesigned Config flow: staged, saved, and applied his own
theme (`KognogOS-theme.toml`) end-to-end during review. "Done."
