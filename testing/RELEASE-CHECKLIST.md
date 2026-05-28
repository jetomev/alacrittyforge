# alacrittyForge release checklist

Pre-flight gates that any cut (alpha or stable) must pass before tag + GitHub release + AUR push. Mirrors the grubForge release discipline; adapted for alacrittyForge's user-space scope (no `/etc` writes, no DEMO/read-only mode).

## Pre-dogfood snapshot — preserve outside the backups dir

alacrittyForge only writes to `~/.config/alacritty/alacritty.toml` (user-space). Still snapshot it so any change made during the dogfood is trivially reversible:

```sh
mkdir -p /tmp/alacrittyforge-pretest
cp -p ~/.config/alacritty/alacritty.toml /tmp/alacrittyforge-pretest/ 2>/dev/null || true
sha256sum ~/.config/alacritty/alacritty.toml > /tmp/alacrittyforge-pretest/alacritty.sha256 2>/dev/null || true
```

The auto-backups in `~/.config/alacritty/backups/` are the second safety net (kept up to 20).

## Async-worker pattern audit — `@work` and `run_worker` must not double-wrap

```sh
grep -rn "@work"      alacrittyforge/
grep -rn "run_worker" alacrittyforge/
grep -rn "run_worker(self\.action_" alacrittyforge/   # MUST be empty
```

The third grep must return zero hits. Any `run_worker(self.action_X())` where `action_X` is `@work`-decorated will throw `WorkerError: Unsupported attempt to run an async worker` on newer Textual versions. (Background: the same bug-class bit grubForge v1.0.0 in two screens.)

## Version sync

Before tagging, all of these must agree on the version string:

- `alacrittyforge/__init__.py` `__version__`
- `README.md` Version badge
- `alacrittyforge.1` `.TH` header
- `~/Programs/aur-alacrittyforge/PKGBUILD` `pkgver` + `pkgrel`
- AUR `.SRCINFO`

## Doc coverage

- README and man page must list every binding in `app.py` `BINDINGS` + every screen `BINDINGS` (excluding `show=False` aliases).
- Help overlay (`widgets/help_screen.py`) must match the bindings actually defined in the codebase. When a screen's `BINDINGS` changes, the help text changes with it.
- Backup retention cap mentioned in the docs must match `MAX_BACKUPS` in `backup_manager.py`.

## Co-author credit

Every release artifact must carry the human + AI credit:

- `~/Programs/aur-alacrittyforge/PKGBUILD` co-developer line
- `README.md` Authors / Credits section
- GitHub release body
- Man page AUTHORS section

## Release-day flow

1. Pre-dogfood snapshot (above).
2. Run the Test Matrix top to bottom; log findings in Test Results.
3. Land hotfix batch closing all in-scope findings (per-group commits, one release tag).
4. Audit greps (above).
5. Version sync (above).
6. Local `makepkg -f` smoke (runs `check()` headless mount).
7. Re-run the regression slice (G1 pending-safety, G3 help-toggle, G4 focus + ConfirmDialog) after any late code changes.
8. `git tag v0.X.Y` + `git push --tags`.
9. GitHub release with notes.
10. README sweep top to bottom (Description, Topics, README sections, Authors, Changelog).
11. Bump AUR PKGBUILD; `updpkgsums`; `makepkg --printsrcinfo > .SRCINFO`.
12. Local `makepkg -si` install smoke (or `sudo pacman -U` on the built artifact).
13. `git push` to `ssh://aur@aur.archlinux.org/alacrittyforge.git`.
14. Verify public install path: `yay -S alacrittyforge` → smoke.
15. Close GitHub Issues + milestone for the cycle.
16. Write end-of-day session log to vault with mandatory `## Next-session handoff (read this first)` section.
