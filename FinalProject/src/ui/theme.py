"""Shared look for every menu and HUD: window size, colors, fonts.

Keeping these in one place means every screen matches, and changing the
style is a one-file edit.
"""

# Lets us write type hints like `pygame.Surface | None` even for classes
# defined later in a file. Every UI file starts with this line.
from __future__ import annotations


from functools import lru_cache
# Path = a file/folder location that works on Windows AND Linux.
# Path objects join with "/" no matter the OS, e.g. folder / "file.png".
from pathlib import Path

import pygame

# ----- Window settings ------------
WIDTH: int = 1280             # window width in pixels (720p widescreen)
HEIGHT: int = 720             # window height in pixels
FPS: int = 60                 # frames per second the game loop aims for
TITLE: str = "Seething Sparrows"  # text in the window's title bar

# ----- Where files live ------------
# __file__ is this file's own location: .../FinalProject/src/ui/theme.py
# .resolve() turns it into the full absolute path.
# .parents[0] = ui/   .parents[1] = src/   .parents[2] = FinalProject/
# So parents[2] / "assets" = .../FinalProject/assets, no matter where
# the game is launched from.
ASSETS_DIR: Path = Path(__file__).resolve().parents[2] / "assets"
# The font file we ship with the game (free to share under its OFL license).
FONT_PATH: Path = ASSETS_DIR / "fonts" / "ArchivoBlack-Regular.ttf"

# ----- Colors ------------------------
Color = tuple[int, int, int]

DARK: Color = (40, 28, 22)          # near-black brown: outlines and dark text
WHITE: Color = (255, 255, 255)      # face of the secondary buttons
WHITE_LIP: Color = (200, 200, 210)  # slightly darker gray-blue: white button's "lip"
ORANGE: Color = (242, 140, 40)      # lots of red, some green, little blue = orange
ORANGE_LIP: Color = (196, 100, 24)  # same orange, every channel ~20% lower = shadow
YELLOW: Color = (255, 214, 64)      # max red + high green = yellow ("SEETHING")
GRAY: Color = (170, 170, 178)       # equal R/G/B = gray; used for disabled buttons
GRAY_LIP: Color = (130, 130, 140)   # darker gray for a disabled button's lip


@lru_cache(maxsize=None)  # remember every font size we've loaded (no limit)
def font(size: int) -> pygame.font.Font:
    """Return the game font at a size (cached, so each size loads once).

    Falls back to pygame's built-in font if the font file is missing.
    """
    # pygame's font system has to be switched on before loading any font.
    # Game() normally does this, but this check lets tests and previews
    # use fonts without opening the whole game first.
    if not pygame.font.get_init():
        pygame.font.init()
    if FONT_PATH.exists():
        # Load our .ttf at this pixel size. str() because pygame wants text.
        return pygame.font.Font(str(FONT_PATH), size)
    # No font file (e.g. someone deleted it): None = pygame's default font,
    # so the game still runs instead of crashing.
    return pygame.font.Font(None, size)


def outlined_text(
    text: str, size: int, color: Color, outline: Color | None = None, width: int = 0
) -> pygame.Surface:
    """Render text, optionally with a solid outline ``width`` pixels thick."""
    face: pygame.font.Font = font(size)
    # render(text, antialias, color) draws the words onto a new image
    # (a Surface). antialias=True smooths the letter edges.
    body: pygame.Surface = face.render(text, True, color)
    # No outline asked for -> just hand back the plain text.
    if outline is None or width <= 0:
        return body
    # Same words again, but in the outline color.
    edge: pygame.Surface = face.render(text, True, outline)
    # Blank see-through canvas, bigger than the text by `width` on EVERY side
    # (hence 2 * width). SRCALPHA = this image supports transparency.
    out = pygame.Surface(
        (body.get_width() + 2 * width, body.get_height() + 2 * width), pygame.SRCALPHA
    )
    # How the outline works: stamp the dark copy many times, nudged a little
    # in every direction (dx left/right, dy up/down). Together the stamps
    # make a thick border around the letters.
    for dx in range(-width, width + 1):
        for dy in range(-width, width + 1):
            # Only use nudges inside a circle (dx² + dy² <= width²) so the
            # outline has rounded corners instead of square ones.
            if dx * dx + dy * dy <= width * width:
                out.blit(edge, (width + dx, width + dy))
    # Finally stamp the real-colored text once, dead center, on top.
    out.blit(body, (width, width))
    return out
