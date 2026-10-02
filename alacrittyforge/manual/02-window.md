# Window

How the terminal window looks. In **Settings ▸ Window**.

## Make the window see-through

1. Open **Settings** (press **2**); **Window** is the first group.
2. On **Opacity**, pick a preset (**70 80 90 95 100**) or type a number. **↑ ↓** step through the presets.
3. Press **F10**, check the review, choose **Save**.

**Blur behind** blurs what shows through, so text stays easy to read. It works only on KDE with Wayland.

## The settings

- **Opacity**: 100 % is solid; lower lets what's behind the window show through. Text always stays solid.
- **Blur behind**: blur what shows through a see-through window.
- **Title bar**: **Full** shows the title bar and borders your desktop draws; **None** hides them.
- **Opens as**: **Window**, **Maximized** or **Full screen**. Takes effect the next time Alacritty opens.
- **Width when opened** and **Height when opened**: the size of a new window, in characters and lines. **0** lets your desktop decide; both must be set for either to work.
- **Padding left and right**, **Padding top and bottom**: empty space between the text and the window's edges, in pixels.
- **Even padding**: spread the space left over evenly around the text.
- **Window title**: the title a new window starts with.
- **Title follows the program**: let the program in the window change the title (for example, to the folder you're in).

Alacritty names on this page: `window.opacity`, `window.blur`, `window.decorations`, `window.startup_mode`, `window.dimensions`, `window.padding`, `window.dynamic_padding`, `window.title`, `window.dynamic_title`.
