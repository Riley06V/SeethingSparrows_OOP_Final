#! /usr/bin/env python3

"""Unit tests for main_menu.py."""

__author__ = "Riley Valdez"
__date__ = "2026/11/25"
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Riley Valdez"

import unittest
from unittest.mock import MagicMock

import pygame

from tests.helpers import start_pygame
from ui.buttons import Disabled
from ui.main_menu import MainMenuScreen


def press(key: int) -> pygame.event.Event:
    """Fake a key press."""
    return pygame.event.Event(pygame.KEYDOWN, key=key)


class TestMainMenu(unittest.TestCase):
    """Tests for the main menu (the Game is a mock so nothing really changes)."""

    @classmethod
    def setUpClass(cls) -> None:
        start_pygame()

    def setUp(self) -> None:
        self.game = MagicMock()
        self.menu = MainMenuScreen(self.game)

    def click(self, label: str) -> None:
        """Click the middle of the button with this label."""
        for button in self.menu.buttons:
            if button.label == label:
                pos = button.rect.center
        self.menu.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=1))
        self.menu.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, pos=pos, button=1))

    def test_buttons(self) -> None:
        """Menu has Play, Level select and Quit in that order."""
        labels = [b.label for b in self.menu.buttons]
        self.assertEqual(labels, ["PLAY", "LEVEL SELECT", "QUIT"])

    def test_play(self) -> None:
        """Play starts level 1."""
        self.click("PLAY")
        self.game.start_level.assert_called_once_with(1)

    def test_quit(self) -> None:
        """Quit closes the game."""
        self.click("QUIT")
        self.game.quit.assert_called_once()

    def test_level_select_coming_soon(self) -> None:
        """Level select is grayed out for now."""
        self.assertIsInstance(self.menu.buttons[1], Disabled)

    def test_level_select_ready(self) -> None:
        """Once it's ready the button works."""
        menu = MainMenuScreen(self.game, level_select_ready=True)
        self.assertTrue(menu.buttons[1].enabled)
        menu.open_level_select()  # does nothing yet

    def test_arrow_keys_skip_disabled(self) -> None:
        """Down goes Play -> Quit (skips the gray one) then wraps back to Play."""
        self.menu.handle_event(press(pygame.K_DOWN))
        self.assertEqual(self.menu.focus, 0)
        self.menu.handle_event(press(pygame.K_DOWN))
        self.assertEqual(self.menu.focus, 2)
        self.menu.handle_event(press(pygame.K_s))
        self.assertEqual(self.menu.focus, 0)

    def test_up_starts_at_bottom(self) -> None:
        """First Up press goes to Quit, W goes back up."""
        self.menu.handle_event(press(pygame.K_UP))
        self.assertEqual(self.menu.focus, 2)
        self.menu.handle_event(press(pygame.K_w))
        self.assertEqual(self.menu.focus, 0)

    def test_enter(self) -> None:
        """Enter clicks whatever is focused (nothing if nothing is)."""
        self.menu.handle_event(press(pygame.K_RETURN))
        self.game.start_level.assert_not_called()
        self.menu.handle_event(press(pygame.K_DOWN))
        self.menu.handle_event(press(pygame.K_RETURN))
        self.game.start_level.assert_called_once_with(1)

    def test_escape_quits(self) -> None:
        """Esc on the menu closes the game."""
        self.menu.handle_event(press(pygame.K_ESCAPE))
        self.game.quit.assert_called_once()

    def test_other_key(self) -> None:
        """Random keys do nothing."""
        self.menu.handle_event(press(pygame.K_q))
        self.assertIsNone(self.menu.focus)

    def test_mouse_clears_focus(self) -> None:
        """Moving the mouse turns off the arrow key highlight."""
        self.menu.handle_event(press(pygame.K_DOWN))
        self.menu.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=(5, 5)))
        self.assertIsNone(self.menu.focus)

    def test_draw(self) -> None:
        """Menu draws with the orange Play button in the middle."""
        screen = pygame.Surface((1280, 720))
        self.menu.update(0.016)
        self.menu.draw(screen)
        self.assertEqual(screen.get_at((640, 320))[:3], (242, 140, 40))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()