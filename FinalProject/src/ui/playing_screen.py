"""The playing screen: the physics game that used to live in main().

This is the game loop from main.py moved into a Screen, unchanged: the same
bird, blocks, walls and slingshot. The HUD (pause/reset buttons) and the
pause, cleared and failed screens build on top of it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame
import pymunk

from ui import theme
# Mikel's classes live in src/ (not in ui/), so these imports have no "ui.".
from objects import Ball, Block, Object
from ui.screens import Screen
from slingshot import Slingshot

if TYPE_CHECKING:  # pragma: no cover - type hints only
    from ui.game import Game


class PlayingScreen(Screen):
    """One level being played."""

    # pymunk gravity is (x, y) in pixels per second². y points DOWN on screen,
    # so +980 pulls things down. (980 ≈ real gravity, 9.8 m/s², if 100 px = 1 m.)
    GRAVITY: tuple[float, float] = (0.0, 980.0)
    # Where the slingshot holds the bird: 150 px from the left, 500 px down.
    SLING_POS: tuple[int, int] = (150, 500)

    def __init__(self, game: Game, level: int = 1) -> None:
        """Build the physics world for ``level``."""
        super().__init__(game)
        self.__level: int = level
        # pymunk.Space = the physics world. Everything that falls, bounces
        # or collides has to be added to it.
        self.__space = pymunk.Space()
        self.__space.gravity = self.GRAVITY
        # Objects that barely move for 0.5 s "fall asleep" and stop being
        # simulated, so a resting tower stops jittering.
        self.__space.sleep_time_threshold = 0.5
        self.__add_walls()

        # Same images Mikel's main.py used. convert() = faster to draw.
        background = pygame.image.load(str(theme.ASSETS_DIR / "background.png")).convert()
        self.__background: pygame.Surface = pygame.transform.scale(
            background, (theme.WIDTH, theme.HEIGHT))  # stretch to fill the window
        bird_image = pygame.image.load(str(theme.ASSETS_DIR / "red_bird.png"))
        block_image = pygame.image.load(str(theme.ASSETS_DIR / "tnt_block.png"))

        # Create objects (different for each level once levels exist).
        # Ball(space, x, y, x speed, y speed, image, radius, bounce)
        # *self.SLING_POS unpacks (150, 500) into the x and y arguments.
        self.__bird = Ball(self.__space, *self.SLING_POS, 0, 0, bird_image,
                           radius=20, bounce=0.5)
        # Two blocks stacked at x=900: one at y=650 (bottom), one at y=550 on top.
        self.__objects: list[Object] = [
            self.__bird,
            Block(self.__space, 900, 650, 0, 0, block_image, size=60, bounce=0.5),
            Block(self.__space, 900, 550, 0, 0, block_image, size=60, bounce=0.5),
        ]
        self.__slingshot = Slingshot(self.__space, self.__bird, *self.SLING_POS)

    @property
    def level(self) -> int:
        """Which level is being played."""
        return self.__level

    @property
    def space(self) -> pymunk.Space:
        """The physics world."""
        return self.__space

    @property
    def bird(self) -> Ball:
        """The bird in the slingshot."""
        return self.__bird

    @property
    def slingshot(self) -> Slingshot:
        """The slingshot holding the bird."""
        return self.__slingshot

    @property
    def objects(self) -> list[Object]:
        """Everything drawn in the level (copy)."""
        return list(self.__objects)

    def __add_walls(self) -> None:
        """Static walls around the window edges."""
        # STATIC body = never moves, no matter what hits it (like bedrock).
        static_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        w, h = theme.WIDTH, theme.HEIGHT
        # Segment(body, start point, end point, thickness): a line-shaped wall.
        walls = [
            pymunk.Segment(static_body, (0, h), (w, h), 5),  # floor (bottom edge, y = 720)
            pymunk.Segment(static_body, (0, 0), (w, 0), 5),  # ceiling (top edge, y = 0)
            pymunk.Segment(static_body, (0, 0), (0, h), 5),  # left wall (x = 0)
            pymunk.Segment(static_body, (w, 0), (w, h), 5),  # right wall (x = 1280)
        ]
        for wall in walls:
            wall.friction = 0.5    # 0 = ice, 1 = very grippy
            wall.elasticity = 0.5  # bounciness: 0 = thud, 1 = bounces forever
        self.__space.add(static_body, *walls)  # *walls = add all four at once

    def restart(self) -> None:
        """Put everything back where the level started."""
        self.__slingshot.reset()  # bird back in the slingshot, not launched
        for obj in self.__objects:
            obj.reset()           # each object returns to its saved start spot

    def handle_event(self, event: pygame.event.Event) -> None:
        """R restarts, Esc goes to the menu, everything else to the slingshot."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.restart()
            elif event.key == pygame.K_ESCAPE:
                # Temporary: back to the menu. The pause overlay replaces this.
                self.game.show_main_menu()
                return  # this screen is gone; don't do anything else with it
        # Mouse events go to Mikel's slingshot (drag, aim, launch).
        self.__slingshot.handle_event(event)

    def update(self, dt: float) -> None:
        """Step the physics."""
        # Move the whole physics world forward by dt seconds: gravity pulls,
        # things fly, collisions bounce.
        self.__space.step(dt)

    def draw(self, surface: pygame.Surface) -> None:
        """Background, slingshot, objects."""
        surface.blit(self.__background, (0, 0))  # first: covers the old frame
        self.__slingshot.draw(surface)
        for obj in self.__objects:
            obj.draw(surface)  # each object draws its own sprite at its position
