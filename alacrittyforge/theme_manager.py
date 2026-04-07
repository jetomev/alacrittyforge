# ═══════════════════════════════════════════════════════════
#  AlacrittyForge — Theme Manager
#  Scans, previews, and applies Alacritty color themes.
#  Themes are .toml files stored in:
#    ~/.config/alacritty/themes/
# ═══════════════════════════════════════════════════════════

from pathlib import Path
import tomllib

from .config_manager import (
    load_config, save_config, get_nested_value, CONFIG_PATH
)
from .backup_manager import create_backup

THEMES_DIR = Path.home() / ".config" / "alacritty" / "themes"

# ── Well-known color keys we look for in theme files ──
COLOR_KEYS = [
    ("primary",    "background"),
    ("primary",    "foreground"),
    ("normal",     "black"),
    ("normal",     "red"),
    ("normal",     "green"),
    ("normal",     "yellow"),
    ("normal",     "blue"),
    ("normal",     "magenta"),
    ("normal",     "cyan"),
    ("normal",     "white"),
    ("bright",     "red"),
    ("bright",     "green"),
    ("bright",     "blue"),
    ("bright",     "cyan"),
]


def themes_dir_exists() -> bool:
    """Return True if the themes directory exists."""
    return THEMES_DIR.exists()


def list_themes() -> list[dict]:
    """
    Scan THEMES_DIR for .toml files and return a list of theme dicts.
    Each dict: { name, path, colors, active }
    """
    if not THEMES_DIR.exists():
        return []

    theme_files = sorted(THEMES_DIR.glob("*.toml"))
    active = _get_active_theme_name()
    result = []

    for tf in theme_files:
        colors = _extract_colors(tf)
        result.append({
            "name":   tf.stem,
            "path":   tf,
            "colors": colors,
            "active": tf.stem == active,
        })

    return result


def _extract_colors(theme_path: Path) -> list[dict]:
    """
    Parse a theme .toml and extract color swatches.
    Returns list of { label, hex } dicts.
    """
    try:
        with open(theme_path, "rb") as f:
            data = tomllib.load(f)
    except Exception:
        return []

    colors_section = data.get("colors", {})
    result = []

    for section, key in COLOR_KEYS:
        sec = colors_section.get(section, {})
        val = sec.get(key)
        if val:
            # Normalize: some themes use 0xRRGGBB, convert to #rrggbb
            val = _normalize_color(val)
            result.append({
                "label": f"{section}.{key}",
                "hex":   val,
            })

    return result


def _normalize_color(val: str) -> str:
    """Convert 0xRRGGBB or #RRGGBB to #rrggbb."""
    val = str(val).strip()
    if val.startswith("0x") or val.startswith("0X"):
        val = "#" + val[2:]
    if not val.startswith("#"):
        val = "#" + val
    return val.lower()


def _get_active_theme_name() -> str | None:
    """
    Return the stem of the currently imported theme file, or None.
    Looks at general.import in alacritty.toml.
    """
    data = load_config()
    imports = get_nested_value(data, "general.import")
    if not isinstance(imports, list) or not imports:
        return None
    # Return the stem of the first import that lives in our themes dir
    for imp in imports:
        p = Path(imp).expanduser()
        if THEMES_DIR in p.parents or p.parent == THEMES_DIR:
            return p.stem
    return None


def apply_theme(theme_path: Path) -> tuple[bool, str]:
    """
    Apply a theme by setting general.import in alacritty.toml.
    Creates a backup first.
    Returns (success, message).
    """
    if not theme_path.exists():
        return False, f"Theme file not found: {theme_path}"

    create_backup(note=f"pre-theme-{theme_path.stem}")

    data = load_config()

    # Build the import path string — use ~ shorthand
    import_path = str(theme_path).replace(str(Path.home()), "~")

    # Preserve any existing non-theme imports, replace theme import
    existing = get_nested_value(data, "general.import") or []
    if not isinstance(existing, list):
        existing = []

    # Remove any existing theme imports (anything pointing to themes dir)
    themes_str = str(THEMES_DIR).replace(str(Path.home()), "~")
    filtered = [
        imp for imp in existing
        if themes_str not in imp
    ]
    filtered.insert(0, import_path)

    # Set general.import
    data.setdefault("general", {})["import"] = filtered

    if save_config(data):
        return True, f"Theme '{theme_path.stem}' applied successfully."
    return False, "Failed to write config file."


def get_theme_raw_text(theme_path: Path) -> str:
    """Return raw text content of a theme file for preview."""
    if not theme_path.exists():
        return "# Theme file not found"
    return theme_path.read_text()


def get_themes_help_text() -> str:
    """Return the installation help guide text."""
    return """\
── How to Install Alacritty Themes ──────────────────────────

Themes are .toml files stored in:
  ~/.config/alacritty/themes/

Step 1 — Create the themes directory:
  mkdir -p ~/.config/alacritty/themes

Step 2 — Download a theme file, for example:
  cd ~/.config/alacritty/themes
  curl -O https://raw.githubusercontent.com/alacritty/alacritty-theme/master/themes/catppuccin_mocha.toml

Step 3 — Return to AlacrittyForge and press F5 to refresh.
          Your new theme will appear in the list.

Step 4 — Select it and press A to apply.

── Recommended Theme Sources ────────────────────────────────

  Official collection (200+ themes):
  https://github.com/alacritty/alacritty-theme

  Clone the entire collection:
  git clone https://github.com/alacritty/alacritty-theme \\
    ~/.config/alacritty/themes

── Popular Themes ────────────────────────────────────────────

  catppuccin_mocha      Dark, warm pastel
  catppuccin_latte      Light variant
  tokyo-night           Dark blue/purple
  gruvbox_dark          Warm retro dark
  nord                  Arctic cool blues
  dracula               Classic purple dark
  one_dark              Atom-inspired dark
  solarized_dark        Classic balanced dark
  rose-pine             Warm earthy dark

── Notes ─────────────────────────────────────────────────────

  AlacrittyForge applies themes using Alacritty's built-in
  import system. The theme path is added to general.import
  in your alacritty.toml — no values are overwritten.

  To remove a theme, press A on a different theme, or
  manually remove the import line from your config.
"""