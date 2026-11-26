#! /usr/bin/env python3

"""Unit tests for buttons.py."""

__author__ = "Riley Valdez"
__date__ = "2026/11/25"
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Riley Valdez"

import unittest
from unittest.mock import MagicMock

import pygame
from hypothesis import given
from hypothesis import strategies as st

from tests.helpers import start_pygame
from ui import theme
from ui.buttons import (Button, ButtonDecorator, Disabled, HoverGrow,
                        PressDown, menu_button)


def mouse_move(pos: tuple) -> pygame.event.Event:
    """Fake a mouse move."""
    return pygame.event.Event(pygame.MOUSEMOTION, pos=pos)


def mouse_down(pos: tuple, button: int = 1) -> pygame.event.Event:
    """Fake a mouse press."""
    return pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=pos, button=button)


def mouse_up(pos: tuple, button: int = 1) -> pygame.event.Event:
    """Fake a mouse release."""
    return pygame.event.Event(pygame.MOUSEBUTTONUP, pos=pos, button=button)


class TestButton(unittest.TestCase):
    """Tests for the plain Button."""

    @classmethod
    def setUpClass(cls) -> None:
        start_pygame()

    def setUp(self) -> None:
        # 200x60 button centered at (400, 300), so it covers x 300-500, y 270-330
        self.clicked = MagicMock()
        self.button = Button("PLAY", (400, 300), (200, 60), self.clicked)

    def test_setup(self) -> None:
        """Button is where I put it and has its label."""
        self.assertEqual(self.button.rect.center, (400, 300))
        self.assertEqual(self.button.label, "PLAY")
        self.assertTrue(self.button.enabled)

    def test_hover(self) -> None:
        """Hovered only while the mouse is on it."""
        self.button.handle_event(mouse_move((400, 300)))
        self.assertTrue(self.button.hovered)
        self.button.handle_event(mouse_move((10, 10)))
        self.assertFalse(self.button.hovered)

    def test_focus_counts_as_hover(self) -> None:
        """Arrow key focus lights it up too."""
        self.button.set_focus(True)
        self.assertTrue(self.button.hovered)

    def test_click(self) -> None:
        """Press and let go on the button runs the action."""
        self.button.handle_event(mouse_down((400, 300)))
        self.assertTrue(self.button.pressed)
        self.assertTrue(self.button.handle_event(mouse_up((400, 300))))
        self.clicked.assert_called_once()

    def test_drag_off_cancels(self) -> None:
        """Letting go off the button doesn't click it."""
        self.button.handle_event(mouse_down((400, 300)))
        self.assertFalse(self.button.handle_event(mouse_up((10, 10))))
        self.clicked.assert_not_called()

    def test_right_click_does_nothing(self) -> None:
        """Only left click counts."""
        self.button.handle_event(mouse_down((400, 300), 3))
        self.button.handle_event(mouse_up((400, 300), 3))
        self.clicked.assert_not_called()

    @given(st.integers(-500, 1500), st.integers(-500, 1500))
    def test_contains(self, x: int, y: int) -> None:
        """contains() matches the rectangle for any point."""
        inside = 300 <= x < 500 and 270 <= y < 330
        self.assertEqual(self.button.contains((x, y)), inside)

    def test_scaled_keeps_center(self) -> None:
        """Growing the rect keeps the same center, sink moves it down."""
        r = Button.scaled(pygame.Rect(100, 100, 200, 60), 1.5, 4)
        self.assertEqual(r.size, (300, 90))
        self.assertEqual(r.center, (200, 134))

    def test_draw(self) -> None:
        """Drawing puts the button color on the screen."""
        screen = pygame.Surface((800, 600))
        self.button.draw(screen)
        self.assertEqual(screen.get_at((320, 312))[:3], theme.WHITE)


class TestDecorators(unittest.TestCase):
    """Tests for the button decorators."""

    @classmethod
    def setUpClass(cls) -> None:
        start_pygame()

    def setUp(self) -> None:
        self.screen = pygame.Surface((800, 600))
        self.clicked = MagicMock()
        self.button = Button("GO", (400, 300), (200, 60), self.clicked)

    def test_base_decorator_passes_through(self) -> None:
        """The base decorator just hands everything to the real button."""
        wrapped = ButtonDecorator(self.button)
        self.assertIs(wrapped.inner, self.button)
        self.assertEqual(wrapped.label, "GO")
        self.assertEqual(wrapped.rect, self.button.rect)
        self.assertTrue(wrapped.enabled)
        self.assertTrue(wrapped.contains((400, 300)))
        wrapped.set_focus(True)
        self.assertTrue(wrapped.hovered)
        wrapped.handle_event(mouse_down((400, 300)))
        self.assertTrue(wrapped.pressed)
        wrapped.handle_event(mouse_up((400, 300)))
        wrapped.click()
        self.assertEqual(self.clicked.call_count, 2)
        wrapped.draw(self.screen)

    def test_hover_grow(self) -> None:
        """HoverGrow draws bigger only when hovered (fake inner button)."""
        inner = MagicMock(hovered=False)
        HoverGrow(inner, 1.1).draw(self.screen)
        inner.draw.assert_called_with(self.screen, 1.0, 0)
        inner.hovered = True
        HoverGrow(inner, 1.1).draw(self.screen)
        inner.draw.assert_called_with(self.screen, 1.1, 0)

    def test_hover_grow_bad_value(self) -> None:
        """Can't shrink on hover."""
        with self.assertRaises(ValueError):
            HoverGrow(self.button, 0.5)
        self.assertEqual(HoverGrow(self.button).grow, 1.06)

    def test_press_down(self) -> None:
        """PressDown sinks only while pressed (fake inner button)."""
        inner = MagicMock(pressed=True)
        PressDown(inner, 5).draw(self.screen)
        inner.draw.assert_called_with(self.screen, 1.0, 5)

    def test_press_down_bad_value(self) -> None:
        """Depth can't be negative."""
        with self.assertRaises(ValueError):
            PressDown(self.button, -1)
        self.assertEqual(PressDown(self.button).depth, Button.LIP)

    def test_disabled(self) -> None:
        """Disabled buttons ignore clicks and never light up."""
        off = Disabled(self.button)
        self.assertFalse(off.enabled)
        self.assertEqual(off.note, "COMING SOON")
        self.button.set_focus(True)
        self.assertFalse(off.hovered)
        off.handle_event(mouse_down((400, 300)))
        self.assertFalse(off.handle_event(mouse_up((400, 300))))
        off.click()
        self.clicked.assert_not_called()
        off.draw(self.screen)

    def test_menu_button(self) -> None:
        """menu_button wraps the button and primary ones are orange."""
        play = menu_button("PLAY", (400, 300), (200, 60), self.clicked, primary=True)
        self.assertIsInstance(play, HoverGrow)
        play.draw(self.screen)
        self.assertEqual(self.screen.get_at((320, 312))[:3], theme.ORANGE)
        quit_button = menu_button("QUIT", (400, 450), (200, 60), self.clicked)
        quit_button.draw(self.screen)
        self.assertEqual(self.screen.get_at((320, 462))[:3], theme.WHITE)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()