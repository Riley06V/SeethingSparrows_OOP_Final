#! /usr/bin/env python3

"""Unit tests for theme.py."""

__author__ = "Riley Valdez"
__date__ = "2026/11/25"
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Riley Valdez"

import unittest
from pathlib import Path
from unittest.mock import patch

import pygame

from tests.helpers import start_pygame
from ui import theme


class TestTheme(unittest.TestCase):
    """Tests for the colors, font and outlined text."""

    @classmethod
    def setUpClass(cls) -> None:
        start_pygame()

    def test_window_size(self) -> None:
        """Window is 1280x720."""
        self.assertEqual((theme.WIDTH, theme.HEIGHT), (1280, 720))

    def test_font_file_exists(self) -> None:
        """The font is in assets/fonts."""
        self.assertTrue(theme.FONT_PATH.exists())

    def test_font_is_cached(self) -> None:
        """Asking for the same size twice gives back the same font."""
        self.assertIs(theme.font(30), theme.font(30))

    def test_font_fallback(self) -> None:
        """If the font file is missing it uses pygame's default font."""
        theme.font.cache_clear()
        with patch.object(theme, "FONT_PATH", Path("not/a/real/font.ttf")):
            self.assertIsInstance(theme.font(25), pygame.font.Font)
        theme.font.cache_clear()  # so other tests get the real font again

    def test_plain_text(self) -> None:
        """No outline means just the normal text size."""
        text = theme.outlined_text("HI", 30, theme.WHITE)
        self.assertEqual(text.get_size(), theme.font(30).size("HI"))

    def test_outline_makes_it_bigger(self) -> None:
        """A 4px outline adds 8px to the width and height."""
        w, h = theme.font(30).size("HI")
        text = theme.outlined_text("HI", 30, theme.WHITE, theme.DARK, 4)
        self.assertEqual(text.get_size(), (w + 8, h + 8))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()