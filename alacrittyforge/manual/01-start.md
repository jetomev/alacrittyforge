# Getting started

alacrittyForge changes the settings of **Alacritty**, your terminal: how its window looks, the font, the cursor, the colours, and its keyboard shortcuts. Alacritty keeps them in one file, `~/.config/alacritty/alacritty.toml`; alacrittyForge edits that file for you, so you never have to.

## The two steps for any change

1. **Change** something: a setting, a theme, a shortcut. Nothing is written yet; the bar at the bottom counts your changes, and each changed setting says **● changed · was: …**.
2. **Save** with **F10**. You see a review of every change (old → new), a backup is made, and the change is written.

That's all: Alacritty notices the saved file and uses the change straight away, in every open window. A few settings say **next time Alacritty opens** or **new windows only**; those wait.

## Moving around

- **Tab** goes to the next field or button, **Shift+Tab** back.
- **Enter** opens a list or presses a button. **Space** flips a switch.
- **1 – 5** go to the screens: Overview, Settings, Themes, Shortcuts, Backups.
- **F1** explains whatever is selected. **?** lists every key. **M** opens this manual.
- **Q** quits. If something isn't saved, alacrittyForge asks first.

## Good to know

- Every save makes one backup first. See [Backups and undo](#backups).
- Your own notes in the file (lines starting with `#`) and its layout are kept; only the settings you change are touched.
- A setting you haven't set shows **not set (…)** with what Alacritty does instead. Picking that same value leaves it unset.
