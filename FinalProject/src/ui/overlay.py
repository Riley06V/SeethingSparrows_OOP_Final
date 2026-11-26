#! /usr/bin/env python3

"""Base class for the cards that pop up over the level (pause, cleared, failed)."""

from __future__ import annotations

__author__ = "Riley Valdez"
__date__ = "2026/11/26"
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Riley Valdez"

from typing import TYPE_CHECKING

import pygame

from ui import theme
from ui.buttons import Clickable
from ui.screens import Screen

if TYPE_CHECKING:  # pragma: no cover - type hints only
    from ui.game import Game

CARD: theme.Color = (246, 242, 234)  # off-white card, a bit warmer than pure white


class Overlay(Screen):
    """A dimmed level with a card and a colored title banner on top."""

    CARD_SIZE: tuple[int, int] = (460, 400)

    def __init__(self, game: Game, title: str, banner: theme.Color) -> None:
        """Make the card. Subclasses add their buttons with add_button()."""
        super().__init__(game)
        self.__banner_color: theme.Color = banner
        # outlined white title text, rendered once here instead of every frame
        self.__title: pygame.Surface = theme.outlined_text(title, 52, theme.WHITE, theme.DARK, 4)
        self.__card = pygame.Rect((0, 0), self.CARD_SIZE)
        self.__card.center = (theme.WIDTH // 2, theme.HEIGHT // 2 + 20)  # a little below middle
        self.__buttons: list[Clickable] = []

    @property
    def is_overlay(self) -> bool:
        """Overlays draw on top of the level instead of replacing it."""
        return True

    @property
    def card(self) -> pygame.Rect:
        """Where the card is (copy)."""
        return self.__card.copy()

    @property
    def buttons(self) -> list[Clickable]:
        """The buttons on the card, top to bottom."""
        return list(self.__buttons)

    def add_button(self, button: Clickable) -> None:
        """Put a button on the card."""
        self.__buttons.append(button)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Mouse events go to the buttons."""
        for button in self.__buttons:
            if button.handle_event(event):
                break

    def update(self, dt: float) -> None:
        """Nothing moves on the card."""

    def draw(self, surface: pygame.Surface) -> None:
        """Dim the level, then card, banner, title and buttons."""
        # see-through dark layer over the frozen level (alpha 140 out of 255)
        dim = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        dim.fill((10, 12, 24, 140))
        surface.blit(dim, (0, 0))

        # card: dark outline 5px bigger on each side, plus an 8px drop shadow under it
        pygame.draw.rect(surface, theme.DARK, self.__card.inflate(10, 10).move(0, 8),
                         border_radius=30)
        pygame.draw.rect(surface, theme.DARK, self.__card.inflate(10, 10), border_radius=30)
        pygame.draw.rect(surface, CARD, self.__card, border_radius=26)

        # banner: wider than the card (+60) and centered on its top edge
        banner = pygame.Rect(0, 0, self.__card.w + 60, 96)
        banner.center = (self.__card.centerx, self.__card.top)
        pygame.draw.rect(surface, theme.DARK, banner.inflate(10, 10), border_radius=22)
        pygame.draw.rect(surface, self.__banner_color, banner, border_radius=18)
        surface.blit(self.__title, self.__title.get_rect(center=banner.center))

        for button in self.__buttons:
            button.draw(surface)