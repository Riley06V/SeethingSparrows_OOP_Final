#! /usr/bin/env python3

"""Unit tests for background.py."""

__author__ = "Riley Valdez"
__date__ = "2026/11/25"
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Riley Valdez"

import tempfile
import unittest
from pathlib import Path

import pygame
from hypothesis import given
from hypothesis import strategies as st

from tests.helpers import start_pygame
from ui.background import Background

# random colors for hypothesis, each number 0-255
colors = st.tuples(st.integers(0, 255), st.integers(0, 255), st.integers(0, 255))


class TestBackground(unittest.TestCase):
    """Tests for the picture/placeholder background."""

    @classmethod
    def setUpClass(cls) -> None:
        start_pygame()

    def test_no_picture_uses_placeholder(self) -> None:
        """Missing file means it draws the placeholder instead."""
        bg = Background(Path("nope/menu.png"))
        self.assertFalse(bg.from_file)
        self.assertEqual(bg.surface.get_size(), (1280, 720))

    def test_placeholder_colors(self) -> None:
        """Top of the placeholder is blue sky, bottom is dirt."""
        surf = Background.placeholder((1280, 720), 620)
        self.assertGreater(surf.get_at((640, 2)).b, 200)  # lots of blue up top
        self.assertEqual(surf.get_at((5, 700))[:3], (122, 82, 48))

    def test_real_picture_gets_stretched(self) -> None:
        """A small picture is loaded and stretched to the window size."""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "menu.png"
            pic = pygame.Surface((300, 200))
            pic.fill((10, 200, 30))
            pygame.image.save(pic, str(path))
            bg = Background(path)
        self.assertTrue(bg.from_file)
        self.assertEqual(bg.surface.get_size(), (1280, 720))
        self.assertEqual(bg.surface.get_at((640, 360))[:3], (10, 200, 30))

    def test_draw(self) -> None:
        """draw() copies the background onto the screen."""
        screen = pygame.Surface((1280, 720))
        bg = Background(None)
        bg.draw(screen)
        self.assertEqual(screen.get_at((5, 700)), bg.surface.get_at((5, 700)))

    def test_lerp_ends(self) -> None:
        """t=0 gives the first color, t=1 gives the second."""
        self.assertEqual(Background.lerp((0, 0, 0), (100, 50, 20), 0), (0, 0, 0))
        self.assertEqual(Background.lerp((0, 0, 0), (100, 50, 20), 1), (100, 50, 20))

    @given(colors, colors, st.floats(-1, 2))
    def test_lerp_stays_between(self, a: tuple, b: tuple, t: float) -> None:
        """The blend never goes outside the two colors (even with a bad t)."""
        mix = Background.lerp(a, b, t)
        for i in range(3):
            self.assertTrue(min(a[i], b[i]) <= mix[i] <= max(a[i], b[i]))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
