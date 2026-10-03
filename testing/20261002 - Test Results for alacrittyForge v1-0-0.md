# alacrittyForge v1.0.0: Test Results (2026-10-02)

The matrix carries every result row: `20261002 - Test Matrix for alacrittyForge v1-0-0.md`. This page is the summary.

**Tests: 80** (0.2.0 had none), all passing; **warnings 0**. Also run inside the AUR build and in the four distribution VMs.

| Section | Result |
|---|---|
| §1–§8 safe saving, Overview, Settings, Themes, Shortcuts, Backups, manual, text console / 100 columns | PASS |
| §9 every major distribution: Ubuntu 24.04 (Alacritty 0.13.2), Debian 13 (0.15.1), Fedora 44, openSUSE Tumbleweed (0.17.0) | PASS: each one's own Alacritty read a saved file without a warning, and warned on the wrong names |
| §10 Javier's run, KognogOS VM, package upgrade 0.2.0 → 1.0.0rc1 installed with nog | PASS: 9 saves, one backup each, an exact restore, notes kept — *"a beautiful piece of software"* (Adjust colours and the text console not visible in the log) |

## Findings (all fixed before release, each with an issue)

| ID | Issue | What |
|---|---|---|
| F-1 | #9 | Ubuntu 24.04's Alacritty 0.13 reads older setting names; a theme would silently not apply |
| F-2 | #10 | no monospace font: Alacritty won't start, nothing said why |
| F-3 | #11 | 0.2.0's saving could damage settings (cleared value broke the save, whole-file rewrite lost comments, unreadable file treated as empty, one backup per shortcut change) |
| F-4 | #12 | backups dated with the settings' last edit |
| F-5 | #13 | Textual 8's `Select.BLANK` is `False`: the shortcut window crashed on opening |
| F-6 | #14 | cut off / sideways at 100 columns and 25 lines |
| F-7 | #15 | text read as formatting; Esc printed raw |

## Outside alacrittyForge
- forgekit 0.5.1: number fields take decimals and fit their longest number (released first).
- nog (unverified): `nog install <name> ./file.pkg.tar.zst` in one command did nothing, silently; each alone worked. Noted in nog's TODO.
