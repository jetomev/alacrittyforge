# Scrolling and copy

Going back through what scrolled by, and copying. In **Settings ▸ Scrolling & copy**.

## The settings

- **Lines kept to scroll back**: how many lines that scrolled off the top you can go back to. **0** turns scrolling back off. At most 100 000.
- **Scroll speed**: lines moved for each step of the mouse wheel.
- **Copy when you select**: copy text as soon as you select it, not only with Copy (**Ctrl+Shift+C**).
- **Programs may use the clipboard**: whether programs in the window, also on other computers over SSH, may copy to your clipboard (**Copy only**, Alacritty's choice), read it (**Paste only**), **Both**, or neither (**No**). Letting them read it lets them see anything you copied.

Alacritty names on this page: `scrolling.history`, `scrolling.multiplier`, `selection.save_to_clipboard`, `terminal.osc52`.
