# alacrittyForge — what the package needs

*Measured from the code on 2026-10-11 (Javier: "check all Forge Suite apps for all dependencies needed to build and
run them"), with the Forge Suite's audit, `forge-suite/scripts/needs-audit.py`, and proven by building the
AUR recipe in a clean Arch system (devtools' `makechrootpkg`, tests included). `tests/test_needs.py` reads every import and fails when one isn't listed here, so this page can't fall behind the code.
Arch's `base` packages (bash, coreutils, glibc, sed, grep, util-linux, systemd…) are on every Arch install and
aren't listed.*

## Needs (the recipe's `depends`)

| Package | What uses it | Module / program |
|---|---|---|
| python | everything | — |
| python-textual | the app's screens | textual |
| python-rich | tables and text | rich |
| python-tomlkit | editing alacritty.toml keeping its comments | tomlkit |
| python-forgekit (>= 0.10.0) | the Forge look | forgekit |
| fontconfig | the font list (fc-list) | (program fc-list) |

## Optional (`optdepends`)

| Package | What uses it | Module / program |
|---|---|---|
| alacritty | the terminal whose settings it edits | (program alacritty) |

## The AUR recipe

Matches the AUR recipe 1.1.0-1. Nothing to change.
