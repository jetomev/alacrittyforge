# Shortcuts

Keys that do something in Alacritty, like **Ctrl+Shift+C** to copy. On the **Shortcuts** screen (press **4**).

Your own shortcuts come first, then Alacritty's own, in grey. Each one says what it does in words ("Make the text bigger"); a shortcut that types hidden characters says which ("Types: Esc, Enter").

## Add a shortcut

1. Press **+** (or **Add a shortcut…**).
2. **The keys:** just press them, for example **Ctrl+Shift+T**. The window shows what it recorded, and whether anything else already uses those keys.
3. **What it does:** **An action** (pick from the list: open a new window, make the text bigger, search…), **Type text** (write **\e** for Esc and **\r** for Enter), or **Run a program** (like `firefox`).
4. **When:** usually **Always**; or only in vi mode, or only while searching.
5. **Add it**, then **F10** to save.

A few keys can't be recorded, because the terminal or alacrittyForge keeps them: **Tab**, **Esc**, and keys your desktop uses. Pick those from the lists under **or pick** instead.

## Change or remove one of yours

Pick it and press **F2** (or **Enter**) to change it, or **Delete** to remove it. Anything else it holds (a mode, a program's options) is kept. Then **F10** to save.

## Alacritty's own shortcuts

They can't be changed, because Alacritty supplies them, but you can **turn one off**: pick it and choose **Turn this one off**; the keys then type as normal. **Turn it back on** undoes that. **Show vi and search keys** lists the shortcuts that only work in vi mode or while searching.

If one of your shortcuts uses the same keys as one of Alacritty's, both happen. alacrittyForge warns you when you add it.

Alacritty name on this page: `keyboard.bindings`.
