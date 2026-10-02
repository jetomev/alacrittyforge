# Shell and start

What runs inside the window, and where. In **Settings ▸ Shell & start**.

## Use another shell

The **shell** is the program that reads what you type (fish, bash, zsh…). Normally Alacritty starts your login shell.

1. Open **Settings**, then **Shell & start**.
2. On **Shell**, press **Enter** and pick one. The list shows the shells installed on this computer; **Another program…** lets you type the full path of anything else.
3. Press **F10** and **Save**. New windows use it; open windows keep theirs.

If your file gives the shell extra options (like `-l`), they're kept when you change the program.

## The settings

- **Shell**: the program that runs in the window. New windows only.
- **Start in folder**: the folder a new window starts in. Empty starts where Alacritty was opened from.
- **Terminal type**: what the window tells programs it is. **alacritty** is the most exact; **xterm-256color** works with more programs, for example on other computers over SSH.
- **Pick up changes by itself**: use saved changes straight away. When it's off, changes wait until Alacritty is opened again. This one itself takes effect the next time Alacritty opens.

Alacritty names on this page: `terminal.shell`, `general.working_directory`, `env.TERM`, `general.live_config_reload`.
