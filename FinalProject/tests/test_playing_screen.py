#! /usr/bin/env python3

"""Unit tests for playing_screen.py."""

__author__ = "Riley Valdez"
__date__ = "2026/11/25"
__license__ = "MIT"
__version__ = "0.2.0"
__maintainer__ = "Riley Valdez"

import unittest
from unittest.mock import MagicMock, patch

import pygame

from tests.helpers import start_pygame
from ui.playing_screen import PlayingScreen


class TestPlayingScreen(unittest.TestCase):
    """Tests for the game screen (Game is a mock)."""

    @classmethod
    def setUpClass(cls) -> None:
        start_pygame()

    def setUp(self) -> None:
        self.game = MagicMock()
        self.screen = PlayingScreen(self.game, 1)

    def launch(self) -> None:
        """Drag the bird back and let go."""
        x, y = PlayingScreen.SLING_POS
        self.screen.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(x, y), button=1))
        self.screen.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=(x - 60, y + 40)))
        self.screen.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, pos=(x - 60, y + 40),
                                                    button=1))

    def test_level_setup(self) -> None:
        """Level 1 comes from Jason's Factory with birds, blocks and a cat."""
        self.assertEqual(self.screen.level_number, 1)
        self.assertGreater(len(self.screen.level.birds), 0)
        self.assertGreater(len(self.screen.level.objects), 0)
        self.assertGreater(len(self.screen.level.pigs), 0)
        self.assertIs(self.screen.slingshot.bird, self.screen.level.birds[0])

    def test_missing_level(self) -> None:
        """Asking for a level the Factory doesn't have raises an error."""
        with patch("ui.playing_screen.Factory.create_level", return_value=None):
            with self.assertRaises(ValueError):
                PlayingScreen(self.game, 99)

    def test_launch(self) -> None:
        """After launching, the bird is in the physics world and moves."""
        self.launch()
        bird = self.screen.slingshot.bird
        self.assertTrue(self.screen.slingshot.launched)
        self.assertIn(bird.body, self.screen.space.bodies)
        start = bird.body.position
        self.screen.update(0.05)
        self.assertNotEqual(bird.body.position, start)

    def test_level_finishes(self) -> None:
        """Once the level says it's over, finished turns on (Level is mocked)."""
        self.assertFalse(self.screen.finished)
        with patch.object(self.screen.level, "check_terminal", return_value=True):
            self.screen.update(0.016)
        self.assertTrue(self.screen.finished)

    def test_r_resets(self) -> None:
        """R puts the bird back and clears finished."""
        self.launch()
        self.screen.update(0.05)
        with patch.object(self.screen.level, "check_terminal", return_value=True):
            self.screen.update(0.016)
        self.screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
        self.assertEqual(self.screen.slingshot.bird.body.position, PlayingScreen.SLING_POS)
        self.assertFalse(self.screen.slingshot.launched)
        self.assertFalse(self.screen.finished)

    def test_escape_goes_to_menu(self) -> None:
        """Esc goes back to the main menu for now."""
        self.screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
        self.game.show_main_menu.assert_called_once()

    def test_other_key(self) -> None:
        """Other keys don't do anything."""
        self.screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q))
        self.game.show_main_menu.assert_not_called()

    def test_draw(self) -> None:
        """Drawing the level doesn't crash."""
        self.screen.draw(pygame.Surface((1280, 720)))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
