"""Every setting alacrittyForge shows, in plain words (v1.0.0).

One ``Setting`` per Alacritty key (0.17, Linux): the name a person reads, its
group, the control that sets it, a short explanation, and Alacritty's own
default, so a setting the file doesn't set can say what Alacritty does
instead. Values are kept as Alacritty stores them (numbers, true/false,
words); ``scale`` only changes how a number is shown (opacity 0.9 → 90 %).

macOS-only settings and values are left out. Lists of tables (hints, mouse
shortcuts, extra palette colours) aren't settings here: the file keeps them
untouched. Shortcuts and colours have screens of their own.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

GROUPS = [
    ("window", "Window", "how the terminal window looks"),
    ("text", "Text", "the font and its size"),
    ("cursor", "Cursor", "the blinking mark where you type"),
    ("scroll", "Scrolling & copy", "going back through what scrolled by, and copying"),
    ("bell", "Bell", "what happens when a program rings the bell"),
    ("shell", "Shell & start", "what runs inside the window, and where"),
    ("mouse", "Mouse & links", "the pointer, and opening links from the screen"),
    ("advanced", "Advanced", "less common settings"),
]

# when Alacritty picks a change up, if not right away
NEXT_START = "next time Alacritty opens"
NEW_WINDOWS = "new windows only"


@dataclass
class Setting:
    key: str
    group: str
    label: str
    control: str              # number | switch | choices | list | text | font | style | shell | colour
    help: str
    default: Any = None       # Alacritty's own value when the file doesn't set it
    choices: list = field(default_factory=list)    # (value, label)
    presets: list = field(default_factory=list)    # numbers, in Alacritty's units
    unit: str = ""
    scale: float = 1          # shown = stored × scale
    kind: type = int          # number: int or float
    lo: float | None = None
    hi: float | None = None
    when: str = ""            # NEXT_START / NEW_WINDOWS, shown in the row
    note: str = ""            # the muted line under the row while unchanged


def _yes_no(on: str, off: str = "") -> list:
    return [(True, on), (False, off or f"No")]


SETTINGS: list[Setting] = [
    # ── Window ──
    Setting("window.opacity", "window", "Opacity", "number",
            "How see-through the window's background is. 100 % is solid; lower lets what is "
            "behind the window show through. Text always stays solid.",
            default=1.0, presets=[0.7, 0.8, 0.9, 0.95, 1.0], unit="%", scale=100, kind=float, lo=0, hi=1),
    Setting("window.blur", "window", "Blur behind", "switch",
            "Blur whatever shows through a see-through window, so text stays easy to read.",
            default=False, note="KDE on Wayland only"),
    Setting("window.decorations", "window", "Title bar", "choices",
            "The title bar and borders your desktop draws around the window.",
            default="Full", choices=[("Full", "Full"), ("None", "None")]),
    Setting("window.startup_mode", "window", "Opens as", "choices",
            "How a new Alacritty window opens.",
            default="Windowed", choices=[("Windowed", "Window"), ("Maximized", "Maximized"),
                                         ("Fullscreen", "Full screen")], when=NEXT_START),
    Setting("window.dimensions.columns", "window", "Width when opened", "number",
            "How many characters wide a new window is. 0 lets your desktop decide. "
            "Works only when the height is set too.",
            default=0, presets=[0, 80, 100, 120, 150], unit="characters", lo=0, when=NEXT_START),
    Setting("window.dimensions.lines", "window", "Height when opened", "number",
            "How many lines tall a new window is. 0 lets your desktop decide.",
            default=0, presets=[0, 24, 30, 40, 50], unit="lines", lo=0, when=NEXT_START),
    Setting("window.padding.x", "window", "Padding left and right", "number",
            "Empty space between the text and the window's left and right edges.",
            default=0, presets=[0, 5, 10, 15, 20], unit="px", lo=0),
    Setting("window.padding.y", "window", "Padding top and bottom", "number",
            "Empty space between the text and the window's top and bottom edges.",
            default=0, presets=[0, 5, 10, 15, 20], unit="px", lo=0),
    Setting("window.dynamic_padding", "window", "Even padding", "switch",
            "Spread the space left over around the text evenly, instead of leaving it at "
            "the right and bottom.", default=False),
    Setting("window.title", "window", "Window title", "text",
            "The title a new window starts with.", default="Alacritty"),
    Setting("window.dynamic_title", "window", "Title follows the program", "switch",
            "Let the program running in the window change its title (for example to the "
            "folder you are in).", default=True),

    # ── Text ──
    Setting("font.normal.family", "text", "Font", "font",
            "The font for all text. Only fonts where every letter is the same width "
            "(monospace) are listed, because a terminal needs them.", default="monospace"),
    Setting("font.normal.style", "text", "Style", "style",
            "Which version of the font: Regular, Medium, Light…", default="Regular"),
    Setting("font.size", "text", "Size", "number",
            "How big the text is, in points.",
            default=11.25, presets=[10, 11, 12, 13, 14, 16], unit="pt", kind=float, lo=1),
    Setting("font.bold.family", "text", "Bold text", "font",
            "The font for bold text. Normally the same as the main font.", default=None),
    Setting("font.italic.family", "text", "Italic text", "font",
            "The font for italic text. Normally the same as the main font.", default=None),
    Setting("font.bold_italic.family", "text", "Bold italic text", "font",
            "The font for bold italic text. Normally the same as the main font.", default=None),
    Setting("font.offset.y", "text", "Line spacing", "number",
            "Extra space between lines, in pixels. Can be negative to squeeze lines together.",
            default=0, presets=[-1, 0, 1, 2, 4]),
    Setting("font.offset.x", "text", "Letter spacing", "number",
            "Extra space between letters, in pixels.", default=0, presets=[-1, 0, 1, 2]),
    Setting("font.builtin_box_drawing", "text", "Line drawing", "switch",
            "Draw boxes, lines and powerline shapes with Alacritty's own crisp shapes, "
            "whatever the font.", default=True),
    Setting("colors.draw_bold_text_with_bright_colors", "text", "Bold text in bright colours", "switch",
            "Show bold text in the brighter version of its colour.", default=False),

    # ── Cursor ──
    Setting("cursor.style.shape", "cursor", "Shape", "choices",
            "What the cursor looks like.", default="Block",
            choices=[("Block", "Block"), ("Underline", "Underline"), ("Beam", "Beam")]),
    Setting("cursor.style.blinking", "cursor", "Blinking", "choices",
            "Whether the cursor blinks. \"Off\" and \"On\" are the starting state that a "
            "program may change; \"Never\" and \"Always\" can't be changed by programs.",
            default="Off", choices=[("Never", "Never"), ("Off", "Off"), ("On", "On"), ("Always", "Always")]),
    Setting("cursor.blink_interval", "cursor", "Blink speed", "number",
            "Time between blinks, in milliseconds. Smaller is faster.",
            default=750, presets=[300, 500, 750, 1000], unit="ms", lo=1),
    Setting("cursor.blink_timeout", "cursor", "Stop blinking after", "number",
            "Stop blinking after this many seconds without typing. 0 blinks forever.",
            default=5, presets=[0, 5, 10, 30], unit="s", lo=0),
    Setting("cursor.unfocused_hollow", "cursor", "Hollow when not in use", "switch",
            "Show the cursor as an empty box while another window has the focus.", default=True),
    Setting("cursor.thickness", "cursor", "Thickness", "number",
            "How thick a Beam or Underline cursor is, as a share of a character's width.",
            default=0.15, presets=[0.1, 0.15, 0.2, 0.3], unit="%", scale=100, kind=float, lo=0, hi=1),

    # ── Scrolling & copy ──
    Setting("scrolling.history", "scroll", "Lines kept to scroll back", "number",
            "How many lines that scrolled off the top you can go back to. 0 turns scrolling back off.",
            default=10000, presets=[1000, 10000, 100000], unit="lines", lo=0, hi=100000),
    Setting("scrolling.multiplier", "scroll", "Scroll speed", "number",
            "Lines moved for each step of the mouse wheel.", default=3, presets=[1, 2, 3, 5], unit="lines", lo=1),
    Setting("selection.save_to_clipboard", "scroll", "Copy when you select", "switch",
            "Copy text to the clipboard as soon as you select it, not only with Copy.", default=False),
    Setting("terminal.osc52", "scroll", "Programs may use the clipboard", "list",
            "Whether programs in the window (also over SSH) may copy to your clipboard, or read it.",
            default="OnlyCopy", choices=[("Disabled", "No"), ("OnlyCopy", "Copy only"),
                                         ("OnlyPaste", "Paste only"), ("CopyPaste", "Both")]),

    # ── Bell ──
    Setting("bell.duration", "bell", "Flash the screen", "number",
            "How long the screen flashes when a program rings the bell, in milliseconds. 0 means no flash.",
            default=0, presets=[0, 50, 100, 250], unit="ms", lo=0),
    Setting("bell.color", "bell", "Flash colour", "colour",
            "The colour of the flash.", default="#ffffff"),
    Setting("bell.animation", "bell", "How it fades", "list",
            "How the flash fades out.", default="Linear",
            choices=[("Linear", "Evenly (Linear)"), ("Ease", "Ease"), ("EaseOut", "Ease out"),
                     ("EaseOutSine", "Ease out, gentle (Sine)"), ("EaseOutQuad", "Ease out (Quad)"),
                     ("EaseOutCubic", "Ease out (Cubic)"), ("EaseOutQuart", "Ease out (Quart)"),
                     ("EaseOutQuint", "Ease out (Quint)"), ("EaseOutExpo", "Ease out, fast (Expo)"),
                     ("EaseOutCirc", "Ease out (Circ)")]),

    # ── Shell & start ──
    Setting("terminal.shell", "shell", "Shell", "shell",
            "The program that runs in the window and reads what you type. Normally your login shell.",
            default=None, when=NEW_WINDOWS),
    Setting("general.working_directory", "shell", "Start in folder", "text",
            "The folder a new window starts in. Empty starts where Alacritty was opened from.",
            default=None, when=NEW_WINDOWS),
    Setting("env.TERM", "shell", "Terminal type", "list",
            "What the window tells programs it is. \"alacritty\" is the most exact; "
            "\"xterm-256color\" works with more programs, for example on other computers over SSH.",
            default=None, choices=[("alacritty", "alacritty"), ("xterm-256color", "xterm-256color"),
                                   ("xterm", "xterm"), ("screen-256color", "screen-256color"),
                                   ("tmux-256color", "tmux-256color")], when=NEW_WINDOWS),
    Setting("general.live_config_reload", "shell", "Pick up changes by itself", "switch",
            "Use changes to this file right away, in every open window. When it is off, "
            "changes wait until Alacritty is opened again.", default=True, when=NEXT_START),

    # ── Mouse & links ──
    Setting("mouse.hide_when_typing", "mouse", "Hide the pointer while typing", "switch",
            "Hide the mouse pointer while you type; it comes back when you move the mouse.", default=False),
    Setting("hints.alphabet", "mouse", "Letters for link labels", "list",
            "When you ask Alacritty to show the links on screen (Ctrl+Shift+O), each gets a "
            "short label made from these letters.", default="jfkdls;ahgurieowpq",
            choices=[("jfkdls;ahgurieowpq", "Home row first (jfkdls…)"), ("asdfghjkl", "Home row only (asdf…)"),
                     ("abcdefghijklmnopqrstuvwxyz", "a to z")]),

    # ── Advanced ──
    Setting("window.class.general", "advanced", "Window name for the desktop", "text",
            "The name your desktop's window rules see (on Wayland, the app id).",
            default="Alacritty", when=NEW_WINDOWS),
    Setting("window.class.instance", "advanced", "Window instance name", "text",
            "A second window name, used by some X11 window rules.", default="Alacritty", when=NEW_WINDOWS),
    Setting("window.decorations_theme_variant", "advanced", "Title bar style", "choices",
            "Ask for a dark or light title bar instead of following the desktop.",
            default="None", choices=[("None", "Follow the desktop"), ("Dark", "Dark"), ("Light", "Light")]),
    Setting("window.level", "advanced", "Keep on top", "choices",
            "Keep Alacritty's windows above all others.",
            default="Normal", choices=[("Normal", "No"), ("AlwaysOnTop", "Always on top")]),
    Setting("window.resize_increments", "advanced", "Resize in whole characters", "switch",
            "Grow and shrink the window one character at a time.", default=False),
    Setting("colors.transparent_background_colors", "advanced", "See-through coloured backgrounds", "switch",
            "Make every coloured background see-through with the window, not only the main one.",
            default=False),
    Setting("font.glyph_offset.x", "advanced", "Move letters right", "number",
            "Nudge every letter inside its space, in pixels.", default=0, presets=[-1, 0, 1, 2]),
    Setting("font.glyph_offset.y", "advanced", "Move letters up", "number",
            "Nudge every letter inside its space, in pixels.", default=0, presets=[-1, 0, 1, 2]),
    Setting("selection.semantic_escape_chars", "advanced", "Word separators", "text",
            "Characters that end a word when you double-click to select it.",
            default=",│`|:\"' ()[]{}<>\t"),
    Setting("general.ipc_socket", "advanced", "Allow alacritty msg", "switch",
            "Let the alacritty msg command control open windows (for example to open a new one).",
            default=True, when=NEXT_START),
    Setting("debug.log_level", "advanced", "Log detail", "list",
            "How much Alacritty writes to its log.", default="Warn",
            choices=[("Off", "Off"), ("Error", "Errors"), ("Warn", "Warnings"), ("Info", "Info"),
                     ("Debug", "Debug"), ("Trace", "Everything")]),
    Setting("debug.persistent_logging", "advanced", "Keep the log", "switch",
            "Keep the log file after Alacritty closes.", default=False),
    Setting("debug.renderer", "advanced", "Drawing method", "list",
            "Force a way of drawing. The best one is picked by itself; change only to work around a problem.",
            default="None", choices=[("None", "Best available"), ("glsl3", "glsl3"), ("gles2", "gles2"),
                                     ("gles2pure", "gles2pure")], when=NEXT_START),
    Setting("debug.prefer_egl", "advanced", "Prefer EGL", "switch",
            "Use EGL to draw. May break see-through windows.", default=False, when=NEXT_START),
    Setting("debug.render_timer", "advanced", "Show drawing time", "switch",
            "Show how long each screen update takes.", default=False),
    Setting("debug.highlight_damage", "advanced", "Highlight redrawn areas", "switch",
            "Mark the parts of the screen that are redrawn.", default=False),
    Setting("debug.print_events", "advanced", "Log every event", "switch",
            "Write every window event to the log.", default=False),
]

BY_KEY = {s.key: s for s in SETTINGS}


def shown(s: Setting, value: Any) -> str:
    """A value the way a person reads it ("90 %", "On", "Full screen")."""
    if value is None:
        return "not set"
    if s.control == "switch":
        return "On" if value else "Off"
    if s.choices:
        for v, label in s.choices:
            if v == value:
                return label
        return str(value)
    if s.control == "number":
        n = value * s.scale
        n = int(n) if float(n).is_integer() else round(n, 2)
        return f"{n:,}".replace(",", " ") + (f" {s.unit}" if s.unit else "")
    if s.control == "shell":
        prog = shell_program(value)
        return prog.rsplit("/", 1)[-1] if prog else "your login shell"
    return str(value)


def default_words(s: Setting) -> str:
    """What Alacritty does when the file doesn't set it."""
    if s.control in ("font",) and s.default is None:
        return "the main font"
    if s.control == "shell":
        return "your login shell"
    if s.key == "env.TERM":
        return "alacritty"
    if s.key == "general.working_directory":
        return "where Alacritty was opened from"
    return shown(s, s.default)


def shell_program(value: Any) -> str | None:
    """terminal.shell is either a program, or {program, args}."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return value.get("program")
    return None


def to_store(s: Setting, shown_number: float) -> Any:
    """A number as typed (90 for 90 %) into what Alacritty stores (0.9)."""
    v = shown_number / s.scale
    if s.kind is int:
        return int(round(v))
    return round(float(v), 4)


def problem(s: Setting, value: Any) -> str:
    """Why a value can't be saved, in plain words; "" when it can."""
    if value is None:
        return ""
    if s.control == "number":
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return "needs a number"
        if s.lo is not None and value < s.lo:
            return f"can't be below {shown(s, s.lo)}"
        if s.hi is not None and value > s.hi:
            return f"can't be above {shown(s, s.hi)}"
    if s.control == "colour":
        import re
        if not (isinstance(value, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", value)):
            return "needs a colour like #1e1e2e"
    return ""
