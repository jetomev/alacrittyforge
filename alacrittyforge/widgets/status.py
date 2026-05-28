"""Shared status-feedback mixin for alacrittyForge screens.

Before v0.1.1 every screen had its own `_update_status(msg)` method that
wrote Rich-tagged text to a status Label and emitted no toast. Action
feedback could be missed — a single line in the corner of a screen that
might be scrolled off on smaller terminals — and fonts.py wrote the same
message to two labels.

This mixin unifies the surface. `_set_status` keeps the persistent
in-screen status line AND fires an app-level notify toast, so important
events surface in both places. Pass `popup=False` for passive mount-time
hints — without it every screen's `on_mount` status call would spray
toasts at launch (the same lesson grubForge G1 captured after G3 landed).

Screens set `STATUS_WIDGET_ID` to the id of their status Label, or leave
it `None` (e.g. the Dashboard, which has no status line — it still gets
the toast on R).

Icons are consolidated to the unicode set used in grubForge for Forge-
suite consistency: ✓ (ok), ● (info), ⚠ (warn), ✗ (error). The
alacrittyForge alpha embedded `✔/✖` inside Rich markup strings at call
sites; the mixin now owns icon choice.
"""

from __future__ import annotations

from textual.widgets import Label

# Catppuccin Mocha colors, keyed by alacrittyForge status level.
_COLOR = {
    "ok":    "#a6e3a1",
    "info":  "#89b4fa",
    "warn":  "#f9e2af",
    "error": "#f38ba8",
}

# Canonical icon set (matches grubForge's StatusMixin).
_ICON = {
    "ok":    "✓",
    "info":  "●",
    "warn":  "⚠",
    "error": "✗",
}

# Map alacrittyForge status levels to Textual notify severities.
_SEVERITY = {
    "ok":    "information",
    "info":  "information",
    "warn":  "warning",
    "error": "error",
}


class StatusMixin:
    """Provides a unified `_set_status(msg, level)` for screen widgets.

    Mix in *before* the Textual widget base so this `_set_status` is the
    one resolved, e.g. `class FontsScreen(StatusMixin, Static)`.
    """

    # Override per screen with the id of its status Label, or leave None.
    STATUS_WIDGET_ID: str | None = None

    def _set_status(
        self,
        msg: str,
        level: str = "info",
        *,
        popup: bool = True,
    ) -> None:
        """Update the in-screen status line and (by default) fire a toast.

        Pass ``popup=False`` for passive mount-time hints so the five
        screens don't spray notifications at app launch.
        """
        color = _COLOR.get(level, "#cdd6f4")
        icon = _ICON.get(level, "●")

        # Persistent in-screen status line, when the screen declares one.
        if self.STATUS_WIDGET_ID:
            try:
                self.query_one(f"#{self.STATUS_WIDGET_ID}", Label).update(
                    f"[{color}]{icon}  {msg}[/{color}]"
                )
            except Exception:
                # Status label not mounted yet (e.g. called during on_mount
                # before compose completes) or absent — the toast still fires.
                pass

        # Transient app-level popup so action feedback is visible regardless
        # of where the status line sits on screen.
        if popup:
            self.app.notify(
                msg,
                severity=_SEVERITY.get(level, "information"),
                timeout=4,
            )
