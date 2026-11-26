#! /usr/bin/env python3

"""The in-game buttons in the top-left corner (pause and reset)."""

from __future__ import annotations

__author__ = "Riley Valdez"
__date__ = "2026/11/26"
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Riley Valdez"

import pygame

from ui import theme
from ui.buttons import Action, Button, Clickable, HoverGrow, PressDown


class IconButton(Button):
    """A square Button that draws a little symbol instead of text."""

    ICONS: tuple[str, ...] = ("pause", "restart")  # the symbols I know how to draw

    def __init__(self, icon: str, center: tuple[int, int], on_click: Action,
                 size: int = 64) -> None:
        """Make a size x size white button with an icon on it."""
        if icon not in self.ICONS:
            raise ValueError(f"icon must be one of {self.ICONS}")
        super().__init__("", center, (size, size), on_click)  # empty label, the icon goes there
        self.__icon: str = icon

    @property
    def icon(self) -> str:
        """Which symbol this button shows."""
        return self.__icon

    def draw(self, screen: pygame.Surface, scale: float = 1.0, sink: int = 0) -> None:
        """Draw the normal button, then the symbol in the middle."""
        super().draw(screen, scale, sink)
        r = Button.scaled(self.rect, scale, sink)  # same spot the face was drawn at
        cx, cy = r.center
        unit = r.w / 64  # everything below was laid out on a 64px button
        if self.__icon == "pause":
            # two dark bars, 9 wide and 30 tall, with a gap in the middle
            bar_w, bar_h = round(9 * unit), round(30 * unit)
            pygame.draw.rect(screen, theme.DARK, (cx - round(13 * unit), cy - bar_h // 2,
                                                  bar_w, bar_h), border_radius=3)
            pygame.draw.rect(screen, theme.DARK, (cx + round(4 * unit), cy - bar_h // 2,
                                                  bar_w, bar_h), border_radius=3)
        else:
            # restart: most of a circle (an arc), plus a triangle for the arrow tip
            radius = round(17 * unit)
            box = pygame.Rect(cx - radius, cy - radius, radius * 2, radius * 2)
            pygame.draw.arc(screen, theme.DARK, box, 0.6, 5.6, max(round(6 * unit), 1))
            tip_x, tip_y = cx + round(14 * unit), cy - round(12 * unit)
            pygame.draw.polygon(screen, theme.DARK, [
                (tip_x - round(9 * unit), tip_y - round(6 * unit)),
                (tip_x + round(7 * unit), tip_y - round(8 * unit)),
                (tip_x + round(2 * unit), tip_y + round(8 * unit)),
            ])


class Hud:
    """The pause and reset buttons that sit on top of the level."""

    def __init__(self, on_pause: Action, on_reset: Action) -> None:
        """Put reset at the far top-left and pause right next to it."""
        # 64px buttons, 24px in from the edges, 20px apart
        self.__buttons: list[Clickable] = [
            HoverGrow(PressDown(IconButton("restart", (56, 56), on_reset))),
            HoverGrow(PressDown(IconButton("pause", (140, 56), on_pause))),
        ]

    @property
    def buttons(self) -> list[Clickable]:
        """Reset first, then pause."""
        return list(self.__buttons)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Give the event to the buttons. True if one of them got clicked."""
        for button in self.__buttons:
            if button.handle_event(event):
                return True
        return False

    def covers(self, pos: tuple[int, int]) -> bool:
        """True if a point is on one of the HUD buttons."""
        return any(button.contains(pos) for button in self.__buttons)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw both buttons."""
        for button in self.__buttons:
            button.draw(screen)