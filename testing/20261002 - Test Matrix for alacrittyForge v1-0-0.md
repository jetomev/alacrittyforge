# alacrittyForge v1.0.0 — Test Matrix

Design: `docs/design/v1.0.0-screens.html` (Javier's rulings, 2 Oct 2026). Filled section by section as the steps are built. Each result was read from the run itself, not assumed.

## 9 · Every major distribution, the same (Javier, 2 Oct: "check alacritty functionality in all major linux distros, all the same")

Run in the grubForge test VMs (cloud images, UEFI, snapshot `fresh`), as root, with `scripts/vm-distro-check.py`:
1. alacrittyForge's own tests, with the distribution's Python and its tomlkit version;
2. alacrittyForge saves real changes (theme, font size, opacity, cursor, shell, scroll-back), then **that distribution's own Alacritty** starts on the file in Xvfb, and every config warning or error is collected; clean means none;
3. the failing direction: the same Alacritty on a file using the names this version does **not** read must warn, or step 2's "clean" proves nothing.

| ID | Distribution | Alacritty | Python · tomlkit | Tests | Alacritty on alacrittyForge's file | Wrong names caught | Result |
|---|---|---|---|---|---|---|---|
| 9.1 | Ubuntu 24.04 | **0.13.2** | 3.12 · 0.12.4 | 64 pass | clean (writes `import`, `shell` at the top, as 0.13 reads them) | yes: "Unused config key: general" | **PASS** |
| 9.2 | Debian 13 | 0.15.1 | 3.13 · 0.13.2 | 64 pass | clean | yes: "live_config_reload has been deprecated" | **PASS** |
| 9.3 | Fedora 44 | 0.17.0 | 3.14 · 0.13.2 | 64 pass | clean | yes | **PASS** |
| 9.4 | openSUSE Tumbleweed | 0.17.0 | 3.13 · 0.15.1 | 64 pass | clean (after installing a font, F-2) | yes | **PASS** |
| 9.5 | Arch / KognogOS (this desktop) | 0.17.0 | 3.14 · 0.15.1 | 65 pass | — (Javier's run, §10) | — | — |

**Findings from this section** (fixed, with tests):
- **F-1:** distributions ship different Alacritty versions, and 0.14 moved five settings (`import`, `working_directory`, `live_config_reload`, `ipc_socket` → `[general]`; `shell` → `[terminal]`). Writing the new names on Ubuntu 24.04 would make its Alacritty ignore them; a chosen theme would silently not apply. alacrittyForge now reads `alacritty --version`, writes the names the installed version reads, hides settings it lacks (`window.level` before 0.15, compared from each version's own manual page), and the Overview's name check works in whichever direction that version needs. A test caught the first version flagging Ubuntu's correct names as old.
- **F-2:** a minimal openSUSE install has no font at all; Alacritty then refuses to start ("font monospace not found"). The Overview now says so, with the package to install; it says nothing when fonts can't be listed at all, so it never warns falsely.

**Test-environment notes** (the VMs, not alacrittyForge): the cloud images lack the X11 runtime libraries winit loads (libxkbcommon-x11, libXcursor, libXi, libXrandr), so Alacritty first failed with "NotSupported" before even reading its config; Xvfb needs 24-bit colour. A first version of the check counted that failed start as "warned (good)"; it now counts a warning only when Alacritty really ran.
