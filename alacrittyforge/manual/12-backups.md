# Backups and undo

Every save makes **one backup** of your settings file first, however many changes it holds. They're kept in `~/.config/alacritty/backups/`; the newest **20** stay. On the **Backups** screen (press **5**).

## See what a backup would bring back

Pick a backup in the list. The box on the right, **Restoring this would change**, lists every difference from today's settings in words, like **Opacity 70 % → 95 %**. When a backup is the same as today, it says so.

Each backup says why it was made: **Before a save**, **Before restoring a backup**, **Before using a theme (…)**, or **Made by you**.

## Restore one

1. Pick it and press **R**, or choose **Restore… (r)**.
2. The window starts on **Cancel (n)**; choose **Restore (y)** to go ahead.

What's there now is backed up first, so a restore can be undone the same way. Alacritty uses the restored settings straight away. If you had unsaved changes, they're dropped.

## Other things you can do

- **Back Up Now (n)**: make a backup whenever you like.
- **Show Whole File**: read the backup exactly as it was saved.
- **Delete… (d)**: delete a backup for good (the window starts on **Cancel (n)**; **Delete (y)** goes ahead).

If your settings file ever can't be read, the **Overview** offers **Restore the Newest Backup** too.

Backups made by earlier versions of alacrittyForge are kept and listed.
