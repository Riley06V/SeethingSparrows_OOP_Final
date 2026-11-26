#! /usr/bin/env python3

"""Unit tests for game.py and screens.py."""

__author__ = "Riley Valdez"
__date__ = "2026/11/25"
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Riley Valdez"

import unittest
from unittest.mock import MagicMock, patch

import pygame

from tests.helpers import start_pygame
from ui.game import EmptyScreenStackError, Game
from ui.screens import Screen


class FakeScreen(Screen):
    """Simple screen that just counts what happens to it."""

    def __init__(self, game: Game, overlay: bool = False) -> None:
        super().__init__(game)
        self.overlay = overlay
        self.events = 0
        self.updates = 0
        self.draws = 0

    @property
    def is_overlay(self) -> bool:
        return self.overlay

    def handle_event(self, event: pygame.event.Event) -> None:
        self.events += 1

    def update(self, dt: float) -> None:
        self.updates += 1

    def draw(self, surface: pygame.Surface) -> None:
        self.draws += 1


class TestGame(unittest.TestCase):
    """Tests for the Game singleton and its screen stack."""

    @classmethod
    def setUpClass(cls) -> None:
        start_pygame()

    def setUp(self) -> None:
        Game.reset_instance()  # fresh game every test
        self.game = Game()

    def tearDown(self) -> None:
        Game.reset_instance()

    def test_singleton(self) -> None:
        """Game() always gives back the same game."""
        self.game.push(FakeScreen(self.game))
        self.assertIs(Game(), self.game)
        self.assertEqual(len(Game().screens), 1)  # second Game() didn't wipe it

    def test_window(self) -> None:
        """Window is 1280x720."""
        self.assertEqual(self.game.surface.get_size(), (1280, 720))

    def test_empty_stack(self) -> None:
        """No screens yet means top and pop raise my error."""
        with self.assertRaises(EmptyScreenStackError):
            self.game.top
        with self.assertRaises(EmptyScreenStackError):
            self.game.pop()

    def test_push_pop_replace(self) -> None:
        """Push adds on top, pop takes it off, replace leaves just one."""
        a = FakeScreen(self.game)
        b = FakeScreen(self.game)
        self.game.push(a)
        self.game.push(b)
        self.assertIs(self.game.top, b)
        self.assertIs(self.game.pop(), b)
        self.assertIs(self.game.top, a)
        self.game.replace(b)
        self.assertEqual(self.game.screens, (b,))

    def test_overlay_draws_screen_under_it(self) -> None:
        """Pause-style overlays still show the game under them, but it's frozen."""
        level = FakeScreen(self.game)
        pause = FakeScreen(self.game, overlay=True)
        self.game.push(level)
        self.game.push(pause)
        self.assertEqual(self.game.visible_screens(), [level, pause])
        self.game.step([pygame.event.Event(pygame.KEYDOWN, key=pygame.K_a)], 0.5)
        self.assertEqual((pause.events, pause.updates, pause.draws), (1, 1, 1))
        self.assertEqual((level.events, level.updates, level.draws), (0, 0, 1))

    def test_close_window_quits(self) -> None:
        """Clicking the window X stops the game."""
        self.game.push(FakeScreen(self.game))
        self.game.step([pygame.event.Event(pygame.QUIT)], 0)
        self.assertFalse(self.game.running)

    def test_menu_and_level_helpers(self) -> None:
        """show_main_menu and start_level swap in the right screen (mocked)."""
        with patch("ui.main_menu.MainMenuScreen") as menu:
            self.game.show_main_menu()
            menu.assert_called_once_with(self.game)
        with patch("ui.playing_screen.PlayingScreen") as level:
            self.game.start_level(2)
            level.assert_called_once_with(self.game, 2)

    def test_run_until_quit(self) -> None:
        """run() keeps looping until it sees QUIT (events and display are mocked)."""
        frames = [[], [pygame.event.Event(pygame.QUIT)]]  # frame 1 nothing, frame 2 quit
        with patch("ui.game.pygame.event.get", side_effect=frames), \
                patch("ui.game.pygame.display.flip") as flip, \
                patch("ui.game.pygame.quit"), \
                patch.object(Game, "show_main_menu", lambda g: g.replace(FakeScreen(g))):
            self.game.run()
        self.assertEqual(flip.call_count, 2)
        self.assertFalse(self.game.running)


class TestScreen(unittest.TestCase):
    """Tests for the Screen base class."""

    def test_frame_order(self) -> None:
        """frame() does every event, then update, then draw."""
        screen = FakeScreen(MagicMock())
        events = [pygame.event.Event(pygame.KEYDOWN), pygame.event.Event(pygame.KEYUP)]
        screen.frame(events, 0.1, MagicMock())
        self.assertEqual((screen.events, screen.updates, screen.draws), (2, 1, 1))

    def test_not_overlay_by_default(self) -> None:
        """Normal screens aren't overlays."""
        self.assertFalse(Screen.is_overlay.fget(FakeScreen(MagicMock())))


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
