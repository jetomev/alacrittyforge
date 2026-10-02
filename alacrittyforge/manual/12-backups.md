# Backups and undo

Every save makes **one backup** of your settings file first, however many changes it holds. They go to `~/.config/alacritty/backups/`, and the newest **20** are kept.

- The **Overview** shows how many there are and when the newest was made. **Back up now** makes one whenever you like.
- If your settings file ever can't be read, the Overview offers **Restore the newest backup**. What's there now is backed up first, so nothing is lost.
- Backups made by earlier versions of alacrittyForge are kept and listed too.

To undo a change you just saved, change it back and save again.
