# alacrittyForge v1.1.0 — Test Matrix

Issues: [#19](https://github.com/jetomev/alacrittyforge/issues/19) (F-8: Help has no number, "1-5 screens" is confusing) and [#20](https://github.com/jetomev/alacrittyforge/issues/20) (`--hypeforge`, button labels as "Save Changes (s)"). Needs forgekit 0.10.0. Each result is read from the run itself, not assumed.

## 1 · Built and checked by Claude (8 Oct 2026)

Automated: **109 tests** (80 at 1.0.0, 29 new in `tests/test_v110.py`), all passing against forgekit 0.10.0 from the Forge Suite repository; **0 warnings** (0 at 1.0.0). Every new test was also run the other way: with its fix taken out, it fails (29 checks, all failed as they should, each on its own assertion; the files were put back each time). forgekit's part was taken out in scratch copies only: without its "open window keeps its keys" lines, as it was before Javier's second run (`810a336`), and with Keys still a window (`d3e8e90`).

| ID | Area | Proven by | Result |
|---|---|---|---|
| 1.1 | Javier's letter rule: Overview **O**, Settings **S**, Themes **T**, Shortcuts **R**, Backups **B**, Help **H**, Quit **Q**; every entry has a letter, all different; the menu names no letters itself (no `acc`); no key of alacrittyForge's own sits on a menu number or Ctrl letter | `MenuLetters` | **PASS** |
| 1.2 | 1-5 reach the five screens, **6 opens Help**, 7 does nothing (Quit has no number) | `test_a_number_reaches_every_entry_help_is_6` | **PASS** |
| 1.3 | Ctrl+O, S, T, R, B reach the screens, Ctrl+H opens Help; Ctrl+B works from inside a text field | `test_ctrl_and_the_underlined_letter_reach_every_entry`, `test_ctrl_letter_works_from_inside_a_field` | **PASS** |
| 1.4 | The bottom bar says **1-6 menu**, never "1-5"; the Keys list says 1-6, Help, and the hypeForge Settings note | `test_the_bottom_bar_says_1_6_menu`, `test_the_keys_list_names_1_6_and_help` | **PASS** |
| 1.5 | Add a Shortcut records Ctrl+O, S, T, R, B, H (forgekit's menu keys don't take them), and nothing moves behind the window; Ctrl+B, S, O in a window's text field switch nothing and leave the text alone | `test_recording_keeps_every_menu_key`, `test_an_open_window_keeps_its_fields_ctrl_keys`, 1.0.0's `test_shortcuts_record_add_and_save_in_words` | **PASS** |
| 1.6a | Help: **6** opens it and lights it; **6** again closes it. **About** and **License** open as pages of the app (no window), Help lit while they show; **Esc** goes back to the page you came from (Themes, in the test) | `HelpMenu` | **PASS** |
| 1.6b | The manual and Keys as pages: **F1** on a setting opens the manual at that setting's page, **M** at its start (and at a page when opened again), **?** the Keys list; no window, Help lit; **Esc** goes back to the page you came from | `HelpPages`, `test_manual.F1` | **PASS** |
| 1.6 | `--hypeforge`: no Quit in the bar; Q and Ctrl+Q do nothing; Help is still 6; when Settings closes it with a change unsaved, **Before you go** asks, and "Quit Without Saving" closes it. Without the option, Q and Ctrl+Q quit | `InsideHypeForgeSettings` | **PASS** |
| 1.7 | The start option: `--hypeforge` and `--hypeForge` both reach the app; `--help` and the man page don't mention it; `--hypeforge --version` still prints the version; `--hypeforgex` is refused; the spelling matches forgekit's | `StartOption` | **PASS** |
| 1.8 | Every button reads "Words In Title Case (k)", listed one by one (screens, changes bar, Before you go, Add a Shortcut, Adjust Colours, the restore and delete windows), including the labels that change (Turn It Back On, Hide Vi and Search Keys) | `ButtonLabels` | **PASS** |
| 1.9 | Every button label fits at 100 columns; the Keys list fits at 100 columns (each line on one row) | 1.0.0's `test_every_button_label_fits_at_100_columns`; a 100×30 screenshot of the Keys list | **PASS** |

Button labels, old → new: Restore the newest backup → **Restore the Newest Backup** · Update them → **Update Them** · Pick a theme → **Pick a Theme** · Change the font → **Change the Font** · Text size → **Text Size** · Back up now (Overview) → **Back Up Now** · Use this theme → **Use This Theme** · Adjust colours… → **Adjust Colours (a)** · Save my colours as a theme… → **Save My Colours as a Theme** · Install a theme…  I → **Install a Theme (i)** · Where to get themes → **Where to Get Themes** · Keep these colours → **Keep These Colours** · Cancel → **Cancel (Esc)** (Adjust Colours, Add a Shortcut) · Add a shortcut…  + → **Add a Shortcut (+)** · Change  F2 → **Change (F2)** · Remove → **Remove (Del)** · Turn this one off / Turn it back on → **Turn This One Off / Turn It Back On** · Show / Hide vi and search keys → **Show / Hide Vi and Search Keys** · Add it / Keep the change → **Add It / Keep the Change** · Restore…  R → **Restore (r)** · Back up now  N (Backups) → **Back Up Now (n)** · Show whole file → **Show Whole File** · Delete…  D → **Delete (d)** · Restore / Delete (the asking windows) → **Restore (y) / Delete (y)** · Save…  F10 (changes bar) → **Save Changes (s)** · Discard → Discard · Save first → **Save First** · Quit without saving → **Quit Without Saving** · Stay → **Stay (Esc)**. The review window's **Save** has no key of its own and stays **Save**; its **Cancel (Esc)**, and **Cancel (n)** in the asking windows, are forgekit's.

## 2 · Javier's run (at the keyboard)

Setup: alacrittyForge 1.1.0 with forgekit 0.10.0, both installed from the locally built packages (`nog install ./…pkg.tar.zst`). Copy `~/.config/alacritty/alacritty.toml` aside first (`testing/RELEASE-CHECKLIST.md`).

### 2a · On its own, in a terminal (`alacrittyforge`)

| ID | Task | EXPECT | Result | Notes |
|---|---|---|---|---|
| 2.1 | `alacrittyforge --version`, then `alacrittyforge --help` | **alacrittyForge 1.1.0**; the usage, with no `--hypeforge` in it | | |
| 2.2 | `alacrittyforge`, look at the bottom bar on the Overview | it reads **1-6 menu** (not "1-5 screens") | | |
| 2.3 | Press **1**, **2**, **3**, **4**, **5**, one after the other | Overview, Settings, Themes, Shortcuts, Backups | | |
| 2.4 | Press **6** | the **Help** menu opens; **Esc** closes it | | the F-8 fix |
| 2.5 | Look at the menu bar, then press **Ctrl+O**, **Ctrl+S**, **Ctrl+T**, **Ctrl+R**, **Ctrl+B**, **Ctrl+H** | underlined: **O**verview, **S**ettings, **T**hemes, Shortcuts with its **r**, **B**ackups, **H**elp; each key goes to its entry; Ctrl+H opens Help | | Javier's letter rule |
| 2.6 | Settings ▸ Window ▸ Window title: click in the field, press **Ctrl+B** | Backups opens (Ctrl + a menu letter works from inside a field) | | |
| 2.6a | Press **6**, look at **Help**, press **6** again | Help is lit while its menu is open; the second 6 closes it | | |
| 2.6b | From Themes: **6**, then **About** | About shows as a page of the app (not a window), Help lit; **Esc** goes back to Themes | | |
| 2.6c | From Backups: **6**, then **License** | License shows as a page, Help lit; **Esc** goes back to Backups | | |
| 2.7 | Press **?** (then **Esc**) | the Keys list: 1-6 (the five screens, then Help), Ctrl+letter, Q / Ctrl+Q with "none inside hypeForge Settings" under it; every line on one row; it shows inside the app, not as a window; Esc goes back | | |
| 2.7a | Settings ▸ Cursor: on Shape press **F1**; in the manual open another page, press **Backspace**, then **Esc** | the manual inside the app at the Cursor page, Help lit; Backspace goes back to the Cursor page; Esc back to Settings | | |
| 2.7b | From Themes press **M**, then **Esc** | the manual at Getting started, inside the app; Esc back to Themes | | |
| 2.8 | Shortcuts: **+**, press **Ctrl+T**, then **Ctrl+S** | the window records each (Ctrl+T, then Ctrl+S); the screen behind stays Shortcuts. **Esc** to cancel | | |
| 2.9 | Look at the buttons on each screen | every one reads like **Back Up Now (n)**: words with capitals, the key in brackets when it has one | | |
| 2.10 | Change something, then **Q** | **Before you go** with **Save First**, **Quit Without Saving**, **Stay (Esc)**; Esc stays | | |
| 2.11 | Smoke: Settings ▸ Text ▸ Size **14**, then **F10**, **Save** | the review, then saved; open Alacritty windows' text grows; one new backup on the Backups screen | | |
| 2.12 | Smoke: Backups ▸ pick the newest, **R** | the asking window starts on **Cancel (n)**, the other button says **Restore (y)**; choose it and Alacritty goes back | | |
| 2.13 | Quit with **Q** (nothing unsaved) | it closes; the closing note and thank-you in the terminal | | |

### 2b · Inside hypeForge Settings (the Terminal page)

| ID | Task | EXPECT | Result | Notes |
|---|---|---|---|---|
| 2.14 | Open hypeForge Settings ▸ Terminal | alacrittyForge, with **no Quit** in its menu bar | | |
| 2.15 | Press **Q**, then **Ctrl+Q** | nothing happens; alacrittyForge stays open | | |
| 2.16 | Press **6**, then **6** again; then **Ctrl+H** | 6 opens Help and 6 again closes it; Ctrl+H opens it (Esc closes it) | | |
| 2.16a | Help ▸ **About**, then **Esc** | About as a page inside the Terminal page, Help lit; Esc goes back | | |
| 2.17 | Press **1** to **5**, and **Ctrl+O, S, T, R, B** | the screens, as outside | | |
| 2.18 | The bottom bar | **1-6 menu** | | |
| 2.19 | Change something, then close it from Settings | **Before you go** asks; **Stay (Esc)** keeps it open, **Quit Without Saving** lets Settings close it | | |
| 2.20 | Nothing unsaved, close it from Settings | it closes at once | | |

Afterwards: put the copied `alacritty.toml` back if anything should not stay.
