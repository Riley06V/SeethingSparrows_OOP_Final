#! /usr/bin/env python3

"""The pause card: Resume, Restart, Main menu, Quit game."""

from __future__ import annotations

__author__ = "Riley Valdez"
__date__ = "2026/11/26"
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Riley Valdez"

from typing import TYPE_CHECKING

import pygame

from ui import theme
from ui.buttons import menu_button
from ui.overlay import Overlay

if TYPE_CHECKING:  # pragma: no cover - type hints only
    from ui.game import Game
    from ui.playing_screen import PlayingScreen


class PauseScreen(Overlay):
    """Pushed on top of the level. The level underneath stays frozen."""

    CARD_SIZE: tuple[int, int] = (460, 450)  # a bit taller than the default for 4 buttons

    def __init__(self, game: Game, level: PlayingScreen) -> None:
        """Remember the level (for Restart) and lay out the 4 buttons."""
        super().__init__(game, "PAUSED", theme.ORANGE)
        self.__level: PlayingScreen = level
        cx = theme.WIDTH // 2
        top = self.card.top
        # Resume is the big orange one, the other three are white and a bit smaller
        # (80px apart so the outlines and lips don't touch)
        self.add_button(menu_button("RESUME", (cx, top + 115), (300, 70), self.resume,
                                    primary=True, font_size=34))
        self.add_button(menu_button("RESTART", (cx, top + 205), (260, 56), self.restart,
                                    font_size=26))
        self.add_button(menu_button("MAIN MENU", (cx, top + 285), (260, 56), self.main_menu,
                                    font_size=26))
        self.add_button(menu_button("QUIT GAME", (cx, top + 365), (260, 56), self.quit_game,
                                    font_size=26))

    def resume(self) -> None:
        """Close the card and go back to the level."""
        self.game.pop()

    def restart(self) -> None:
        """Close the card and reset the level."""
        self.game.pop()
        self.__level.restart()

    def main_menu(self) -> None:
        """Leave the level."""
        self.game.show_main_menu()

    def quit_game(self) -> None:
        """Close the whole game."""
        self.game.quit()

    def handle_event(self, event: pygame.event.Event) -> None:
        """Esc resumes, everything else goes to the buttons."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.resume()
            return
        super().handle_event(event)
