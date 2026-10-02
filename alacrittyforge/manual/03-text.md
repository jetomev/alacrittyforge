# Text and fonts

The font and its size. In **Settings ▸ Text**.

## Change the font

1. Open **Settings** (press **2**), then **Text**.
2. On **Font**, press **Enter** and choose **Choose a font…**. Only monospace fonts are listed (every letter the same width, which a terminal needs). Type part of a name to narrow the list.
3. Pick a **Style** if you like (Regular, Medium, Light…). The list follows the font you chose.
4. Press **F10** and **Save**.

A terminal can only draw its own font, so the list shows font names, not samples. Save, and Alacritty shows the new font at once.

## Make the text bigger or smaller

On **Size**, pick a preset (**10 11 12 13 14 16**) or type any size, like **11.5**. Alacritty's own keys (**Ctrl + +** and **Ctrl + -**) change the size only until the window closes; this setting is what a new window starts with.

## The settings

- **Font**, **Style**, **Size**: the main font, its version, and its size in points.
- **Bold text**, **Italic text**, **Bold italic text**: normally **Same as the main font**; pick another font for any of them if you want.
- **Line spacing** and **Letter spacing**: extra space between lines or letters, in pixels. Negative numbers squeeze them together.
- **Line drawing**: draw boxes, lines and powerline shapes with Alacritty's own crisp shapes, whatever the font.
- **Bold text in bright colours**: show bold text in the brighter version of its colour.

Alacritty names on this page: `font.normal.family`, `font.normal.style`, `font.size`, `font.bold.family`, `font.italic.family`, `font.bold_italic.family`, `font.offset`, `font.builtin_box_drawing`, `colors.draw_bold_text_with_bright_colors`.

## If no fonts are listed

A very small Linux install may have no monospace font at all; then Alacritty can't even open, and the Overview says so. Install one with your package manager, for example DejaVu Sans Mono (usually called `fonts-dejavu` or `dejavu-fonts`).
