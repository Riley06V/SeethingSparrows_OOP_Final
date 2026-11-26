"""Screen backgrounds: a picture if one is provided, otherwise a drawn placeholder.

Drop a 1280x720 image (e.g. a campus photo) at the given path and it is
used automatically; no code changes needed.
"""

from __future__ import annotations

from pathlib import Path

import pygame

from ui import theme

# ----- Placeholder colors (red, green, blue), each 0-255 ---------------------
SKY_TOP: theme.Color = (120, 185, 240)     # deeper blue at the top of the sky
SKY_BOTTOM: theme.Color = (210, 230, 235)  # pale, almost white near the horizon
HILL: theme.Color = (118, 172, 104)        # front hill: darker green (closer = darker)
HILL_FAR: theme.Color = (140, 190, 124)    # back hills: lighter green (far away = paler)
GRASS: theme.Color = (98, 170, 60)         # bright grass strip on top of the ground
GRASS_DARK: theme.Color = (60, 120, 40)    # thin dark line under the grass (its shadow)
DIRT: theme.Color = (122, 82, 48)          # brown: red highest, blue lowest
CLOUD: theme.Color = (250, 252, 255)       # nearly pure white, tiny bit of blue


class Background:
    """A full-window backdrop. Picture only: no physics."""

    # y pixel where the ground starts. y counts DOWN from the top of the
    # window (0 = top edge, 720 = bottom edge), so 620 = 100 px from the bottom.
    GROUND_Y: int = 620

    def __init__(
        self, image_path: Path | None = None,
        size: tuple[int, int] = (theme.WIDTH, theme.HEIGHT),
    ) -> None:
        """Load ``image_path`` if it exists, otherwise draw the placeholder."""
        # Two underscores = private (name mangling): outside code can't
        # change these by accident. They're read through the properties below.
        self.__size: tuple[int, int] = size
        # True only if a path was given AND that file is really there.
        self.__from_file: bool = image_path is not None and image_path.exists()
        if self.__from_file:
            # mypy can't tell image_path isn't None here, so I promise it.
            assert image_path is not None
            # .convert() changes the picture to the screen's pixel format,
            # which makes drawing it every frame much faster.
            picture: pygame.Surface = pygame.image.load(str(image_path)).convert()
            # Stretch any size photo to fill the window. smoothscale blends
            # pixels (good for photos; pixel art uses plain scale instead).
            self.__surface: pygame.Surface = pygame.transform.smoothscale(picture, size)
        else:
            # No picture yet: draw one with code.
            self.__surface = self.placeholder(size, self.GROUND_Y)

    @property
    def from_file(self) -> bool:
        """True if a picture was loaded, False if using the placeholder."""
        return self.__from_file

    @property
    def surface(self) -> pygame.Surface:
        """The finished backdrop image."""
        return self.__surface

    @staticmethod  # doesn't need `self`: it's pure maths on two colors
    def lerp(a: theme.Color, b: theme.Color, t: float) -> theme.Color:
        """Blend two colors; t=0 gives a, t=1 gives b."""
        # "lerp" = linear interpolation = sliding between two values.
        # t=0 -> all a, t=0.5 -> halfway, t=1 -> all b.
        # min/max clamp t into 0..1 so it never goes past either color.
        t = min(max(t, 0.0), 1.0)
        # For each channel: start at a, then move t of the way toward b.
        # e.g. a=100, b=200, t=0.25 -> 100 + (200-100)*0.25 = 125
        return (
            round(a[0] + (b[0] - a[0]) * t),  # red
            round(a[1] + (b[1] - a[1]) * t),  # green
            round(a[2] + (b[2] - a[2]) * t),  # blue
        )

    @classmethod  # gets the class (cls) so it can call cls.lerp
    def placeholder(cls, size: tuple[int, int], ground_y: int) -> pygame.Surface:
        """Sky gradient, clouds, hills and a grass/dirt ground line."""
        w, h = size  # w = 1280, h = 720 for the normal window
        surf = pygame.Surface(size)

        # SKY: paint the window one 1-pixel-tall row at a time. y / h goes from
        # 0 (top row) to almost 1 (bottom row), so each row is a tiny bit
        # closer to SKY_BOTTOM: a smooth top-to-bottom fade.
        for y in range(h):
            surf.fill(cls.lerp(SKY_TOP, SKY_BOTTOM, y / h), (0, y, w, 1))

        # HILLS: three big circles whose centers sit near or below the bottom
        # of the window, so only their round tops poke up. Positions are
        # fractions of the window (w * 0.95 = 95% of the way across) so they
        # still fit if the window size changes.
        # Each entry: (center x, center y, radius, color). Back hills first,
        # front hill last, so it's drawn on top.
        for cx, cy, r, color in ((w * 0.95, h * 0.96, h * 0.53, HILL_FAR),  # back right
                                 (w * 0.16, h * 0.97, h * 0.58, HILL_FAR),  # back left
                                 (w * 0.64, h, h * 0.72, HILL)):            # big front hill
            pygame.draw.circle(surf, color, (round(cx), round(cy)), round(r))

        # CLOUDS: each cloud = 4 overlapping white circles ("puffs").
        # The outer list = where each cloud sits (fractions of the window),
        # picked to stay clear of the title in the middle-top.
        for cloud_x, cloud_y in ((w * 0.06, h * 0.13), (w * 0.82, h * 0.1), (w * 0.14, h * 0.45)):
            # The inner list = each puff's offset from the cloud's spot, plus
            # its radius: (dx, dy, radius). The middle puff is biggest and
            # sits a little higher (dy = -14), giving the classic cloud bump.
            for dx, dy, puff in ((0, 0, 34), (36, -14, 42), (78, 0, 32), (40, 12, 30)):
                pygame.draw.circle(surf, CLOUD, (round(cloud_x + dx), round(cloud_y + dy)), puff)

        # GROUND: rectangles are (left x, top y, width, height).
        surf.fill(DIRT, (0, ground_y, w, h - ground_y))  # dirt from ground_y to the bottom
        surf.fill(GRASS, (0, ground_y, w, 14))           # 14 px grass strip on top of the dirt
        surf.fill(GRASS_DARK, (0, ground_y + 14, w, 3))  # 3 px shadow line just under the grass
        return surf

    def draw(self, screen: pygame.Surface) -> None:
        """Paint the backdrop over the whole screen."""
        # (0, 0) = top-left corner. The backdrop is window-sized, so it covers
        # everything drawn last frame. Always draw it FIRST, then things on top.
        screen.blit(self.__surface, (0, 0))
