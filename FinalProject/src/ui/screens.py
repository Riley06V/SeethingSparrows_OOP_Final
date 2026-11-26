"""Base class for every screen (State + Template Method patterns).

Each screen (main menu, playing, pause, ...) is one *state* of the game.
``Screen.frame`` is the fixed recipe run every frame: handle input, update,
draw. Subclasses only fill in those three steps (Template Method, A4).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import pygame

if TYPE_CHECKING:  # pragma: no cover - type hints only
    from ui.game import Game


class Screen(ABC):
    """One state of the game, run by the Game manager.

    Only one screen is in control at a time, and the Game
    switches between them.
    """

    def __init__(self, game: Game) -> None:
        """Remember the Game so the screen can ask it to switch screens."""
        self.__game: Game = game

    @property
    def game(self) -> Game:
        """The Game manager running this screen."""
        return self.__game

    @property
    def is_overlay(self) -> bool:
        """Overlays (pause, cleared, failed) draw on top of the screen below.

        False for full screens. Overlay screens will override this to True.
        """
        return False

    def frame(
        self, events: list[pygame.event.Event], dt: float, surface: pygame.Surface
    ) -> None:
        """Run one frame: input -> update -> draw (Template Method).

        This recipe is the same for every screen, so it's written once
        here. Subclasses never override frame(); they fill in the 3 steps.
        """
        for event in events:   # 1) every key press / mouse event this frame
            self.handle_event(event)
        self.update(dt)        # 2) move things forward by dt seconds (~0.016)
        self.draw(surface)     # 3) paint the result

    # The three steps. @abstractmethod = every screen MUST write its own.

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """React to one input event."""

    @abstractmethod
    def update(self, dt: float) -> None:
        """Advance animations/physics by ``dt`` seconds."""

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the screen."""
