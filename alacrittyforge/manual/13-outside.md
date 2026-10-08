# Changes made elsewhere

You can still edit `alacritty.toml` yourself, or with another tool, while alacrittyForge is open.

- alacrittyForge reads the file again every time you switch screens, and when you press **R**. Your unsaved changes stay.
- A save starts from the file as it is on disk at that moment, so a change made elsewhere in the meantime is kept; only the settings in your review are touched.

## If the file can't be read

A mistake in the file (a missing quote, for example) means Alacritty can't read it either; it then uses its own settings. alacrittyForge says so on the **Overview** and **never saves over the file**, so the mistake can't make things worse.

- **Restore the Newest Backup** (on the Overview) puts back the last version that worked. What's there now is backed up first.
- Or fix the line yourself (the Overview names the line and what's wrong), then press **R**.

## Old setting names

Alacritty renamed some settings (for example `shell` became `terminal.shell`). The old names still work, but Alacritty warns every time it starts. The Overview lists them; **Update Them** moves each to its new name, with a review first like any save.

## Settings Alacritty doesn't know

Often a misspelling, like `opactiy`. Alacritty ignores them. The Overview lists them so you can find and fix them.
