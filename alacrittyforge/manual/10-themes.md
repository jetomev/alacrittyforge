# Themes and colours

A **theme** is a set of colours: the background, the text, the cursor, and the 16 colours programs use. On the **Themes** screen (press **3**).

## Use a theme

1. Pick a theme in the list. The right side shows a small terminal in its colours.
2. Press **Enter**, or **Use This Theme**.
3. Press **F10**, check the review, choose **Save**. Every open Alacritty window changes at once.

The theme in use is marked and listed first.

## Themes made by hypeForge

hypeForge writes its own themes (named `hypeforge-…`) and rewrites them when you change the desktop's look. They are **locked**: you can use them, but alacrittyForge never changes them. To change one, use **Adjust Colours (a)**, which makes your own copy.

## Adjust colours

1. Pick a theme and press **A**, or choose **Adjust Colours (a)**.
2. Pick a colour in the list and press **Enter**. Choose one of the theme's own colours, one of Catppuccin's, or type a code like **#1e1e2e**. The small preview follows as you go.
3. **Keep These Colours**. Your copy is named after the theme, like **KognogOS-theme (mine)**, and becomes the theme in use.
4. Press **F10** to save. Nothing is written before that.

The original theme stays as it was.

## Colours written in the settings file

Alacritty can also take colours written straight into the settings file. alacrittyForge lists them as **My colours**. They win over any theme, so using a theme takes them out of the settings file; the review says so, and a backup is made first. **Save My Colours as a Theme** keeps them as a theme file of their own first.

## Get more themes

**Where to Get Themes** points to Alacritty's own collection of over a hundred themes. Download a theme's `.toml` file, then choose **Install a Theme (i)**: files in your Downloads folder are listed, or type the path of one. Only files that change colours, and nothing else, are installed, and never over a theme you already have.

Alacritty names on this page: `general.import` (the theme in use), `colors` (colours in the settings file).
