#! /usr/bin/env python3

"""The playing screen: one level being played, built by Jason's level Factory."""

from __future__ import annotations

__author__ = "Riley Valdez"
__date__ = "2026/11/25"
__license__ = "MIT"
__version__ = "0.3.0"
__maintainer__ = "Riley Valdez"

from typing import TYPE_CHECKING

import pygame
import pymunk

from ui import theme
from ui.hud import Hud
from ui.pause_screen import PauseScreen
from ui.screens import Screen
from level import Level
from level_factory import Factory
from slingshot import Slingshot

if TYPE_CHECKING:  # pragma: no cover - type hints only
    from ui.game import Game


class PlayingScreen(Screen):
    """One level being played."""

    GRAVITY: tuple[float, float] = (0.0, 980.0)  # +y is down on screen, so this pulls down
    SLING_POS: tuple[int, int] = (150, 500)       # where the slingshot holds the bird

    def __init__(self, game: Game, level: int = 1) -> None:
        """Build the physics world and ask the Factory for the level."""
        super().__init__(game)
        self.__level_number: int = level
        self.__space = pymunk.Space()
        self.__space.gravity = self.GRAVITY
        self.__space.sleep_time_threshold = 0.5  # still for 0.5s = asleep (used for the end check)
        self.__add_walls()

        background = pygame.image.load(str(theme.ASSETS_DIR / "background.png")).convert()
        self.__background = pygame.transform.scale(background, (theme.WIDTH, theme.HEIGHT))

        # Jason's Factory makes all the birds, blocks and cats for this level number
        built = Factory().create_level(self.__space, level)
        if built is None:
            raise ValueError(f"level {level} doesn't exist yet")
        self.__level: Level = built
        # Mikel's slingshot takes the list of birds and loads the first one
        self.__slingshot = Slingshot(self.__space, self.__level.birds, *self.SLING_POS)
        self.__finished: bool = False  # True once the level's end check passes
        self.__hud = Hud(self.pause, self.restart)  # pause + reset buttons, top-left

    @property
    def level_number(self) -> int:
        """Which level this is."""
        return self.__level_number

    @property
    def level(self) -> Level:
        """Jason's Level object (birds, blocks, cats)."""
        return self.__level

    @property
    def space(self) -> pymunk.Space:
        """The physics world."""
        return self.__space

    @property
    def slingshot(self) -> Slingshot:
        """The slingshot."""
        return self.__slingshot

    @property
    def finished(self) -> bool:
        """True once the level is over (bird stopped moving)."""
        return self.__finished

    def __add_walls(self) -> None:
        """Static walls around the edges of the window."""
        static_body = pymunk.Body(body_type=pymunk.Body.STATIC)  # never moves
        w, h = theme.WIDTH, theme.HEIGHT
        walls = [
            pymunk.Segment(static_body, (0, h), (w, h), 5),  # floor
            pymunk.Segment(static_body, (0, 0), (w, 0), 5),  # ceiling
            pymunk.Segment(static_body, (0, 0), (0, h), 5),  # left
            pymunk.Segment(static_body, (w, 0), (w, h), 5),  # right
        ]
        for wall in walls:
            wall.friction = 0.5    # how grippy
            wall.elasticity = 0.5  # how bouncy
        self.__space.add(static_body, *walls)

    @property
    def hud(self) -> Hud:
        """The pause and reset buttons."""
        return self.__hud

    def pause(self) -> None:
        """Put the pause card on top. The level stops updating under it."""
        self.game.push(PauseScreen(self.game, self))

    def restart(self) -> None:
        """Put everything back where the level started."""
        self.__slingshot.reset()
        self.__level.reset_stuff()  # Jason's reset for every bird, block and cat
        self.__finished = False

    def handle_event(self, event: pygame.event.Event) -> None:
        """R restarts, Esc pauses, HUD buttons first, then the slingshot."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.restart()
            elif event.key == pygame.K_ESCAPE:
                self.pause()
                return
        if self.__hud.handle_event(event):
            return  # a HUD button got clicked, don't also aim the slingshot
        if event.type == pygame.MOUSEBUTTONDOWN and self.__hud.covers(event.pos):
            return  # pressing on a HUD button shouldn't grab the bird
        self.__slingshot.handle_event(event)

    def update(self, dt: float) -> None:
        """Step the physics, then check if the level is over."""
        self.__space.step(dt)
        if self.__level.check_terminal(self.__space):
            # later this is where the cleared/failed screen gets pushed
            self.__finished = True

    def draw(self, surface: pygame.Surface) -> None:
        """Background, slingshot, everything in the level, then the HUD on top."""
        surface.blit(self.__background, (0, 0))
        self.__slingshot.draw(surface)
        self.__level.draw_level(surface)
        self.__hud.draw(surface)
