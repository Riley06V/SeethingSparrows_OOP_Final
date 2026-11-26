"""The main menu: Play, Level select, Quit."""

from __future__ import annotations

# TYPE_CHECKING is False when the game runs and True only while mypy checks
# types. Imports under it are for type hints only, which avoids a circular
# import (game.py imports this file, and this file mentions Game).
from typing import TYPE_CHECKING

import pygame

from ui import theme
from ui.background import Background
from ui.buttons import Clickable, Disabled, menu_button
from ui.screens import Screen

if TYPE_CHECKING:  # pragma: no cover - type hints only
    from ui.game import Game


class MainMenuScreen(Screen):
    """Title, three buttons, mouse and keyboard (arrows + Enter) support."""

    # File the menu looks for in assets/backgrounds/. If it's missing, the
    # Background class draws the placeholder sky instead.
    BACKGROUND_FILE: str = "menu.png"

    def __init__(self, game: Game, level_select_ready: bool = False) -> None:
        """Build the title and buttons.

        Args:
            game: the Game manager.
            level_select_ready: until level select exists, its button is
                shown grayed out as 'coming soon'.
        """
        super().__init__(game)  # Screen stores the game for us (self.game)
        self.__background = Background(
            theme.ASSETS_DIR / "backgrounds" / self.BACKGROUND_FILE
        )
        # The title is rendered ONCE here, not every frame (outlines are slow
        # to build). Arguments: text, size 92, fill color, outline color,
        # outline 6 px thick.
        self.__title_top: pygame.Surface = theme.outlined_text(
            "SEETHING", 92, theme.YELLOW, theme.DARK, 6)
        self.__title_bottom: pygame.Surface = theme.outlined_text(
            "SPARROWS", 92, theme.ORANGE, theme.DARK, 6)

        cx: int = theme.WIDTH // 2  # center x of the window: 1280 // 2 = 640
        # Each button: menu_button(label, (center x, center y), (width, height), action)
        # The action is a METHOD passed without () -> the button stores it
        # and calls it later, when clicked.
        level_select: Clickable = menu_button(
            "LEVEL SELECT", (cx, 435), (340, 72), self.open_level_select)
        if not level_select_ready:
            # Decorator in action: wrap the same button to gray it out.
            level_select = Disabled(level_select)
        # Top to bottom. The y values (320, 435, 565) leave room for the
        # "COMING SOON" note under Level select. PLAY is biggest (340x84,
        # font 40) because it's the main action; QUIT is smallest (220x60).
        self.__buttons: list[Clickable] = [
            menu_button("PLAY", (cx, 320), (340, 84), self.play, primary=True, font_size=40),
            level_select,
            menu_button("QUIT", (cx, 565), (220, 60), self.quit, font_size=26),
        ]
        # Which button the keyboard is on: an index into the list above
        # (0 = PLAY, 2 = QUIT), or None when the mouse is being used.
        self.__focus: int | None = None

    @property
    def buttons(self) -> list[Clickable]:
        """The menu's buttons, top to bottom."""
        return list(self.__buttons)  # a copy, so callers can't edit ours

    @property
    def focus(self) -> int | None:
        """Index of the keyboard-focused button, or None."""
        return self.__focus

    def play(self) -> None:
        """Start level 1."""
        self.game.start_level(1)  # the Game swaps this menu for the level

    def open_level_select(self) -> None:
        """Placeholder until the level select screen exists."""

    def quit(self) -> None:
        """Close the game."""
        self.game.quit()

    def move_focus(self, step: int) -> None:
        """Move keyboard focus up/down, skipping disabled buttons.

        step = +1 for Down, -1 for Up.
        """
        # Indexes of buttons that can be used. With Level select disabled,
        # this is [0, 2]: the grayed-out button is never landed on.
        usable: list[int] = [i for i, b in enumerate(self.__buttons) if b.enabled]
        if self.__focus not in usable:
            # Nothing focused yet: Down starts at the top, Up at the bottom.
            self.__focus = usable[0] if step > 0 else usable[-1]
        else:
            assert self.__focus is not None  # promise for mypy
            here: int = usable.index(self.__focus)  # position within `usable`
            # % wraps around: going down from the last button returns to
            # the first one.
            self.__focus = usable[(here + step) % len(usable)]
        # Highlight only the focused button; un-highlight the rest.
        for i, button in enumerate(self.__buttons):
            button.set_focus(i == self.__focus)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Mouse goes to the buttons; arrows/Enter/Esc work too."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_DOWN, pygame.K_s):      # Down arrow or S
                self.move_focus(1)
            elif event.key in (pygame.K_UP, pygame.K_w):      # Up arrow or W
                self.move_focus(-1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE) and self.__focus is not None:
                self.__buttons[self.__focus].click()          # Enter/Space clicks
            elif event.key == pygame.K_ESCAPE:
                self.quit()
            return  # keys are handled; buttons only care about the mouse
        if event.type == pygame.MOUSEMOTION and self.__focus is not None:
            # The player went back to the mouse: drop the keyboard highlight
            # so two buttons aren't lit up at once.
            self.__buttons[self.__focus].set_focus(False)
            self.__focus = None
        # Offer the event to each button; stop once one says it was clicked.
        for button in self.__buttons:
            if button.handle_event(event):
                break

    def update(self, dt: float) -> None:
        """Nothing animates on its own yet."""

    def draw(self, surface: pygame.Surface) -> None:
        """Background, two-line title, buttons."""
        self.__background.draw(surface)  # always first: it covers the old frame
        cx: int = theme.WIDTH // 2
        # get_rect(center=...) = "a rectangle this image's size, centered here".
        # Title line centers at y=80 and y=182 (102 px apart, about one line
        # of 92 px text plus a small gap).
        surface.blit(self.__title_top, self.__title_top.get_rect(center=(cx, 80)))
        surface.blit(self.__title_bottom, self.__title_bottom.get_rect(center=(cx, 182)))
        for button in self.__buttons:
            button.draw(surface)  # each wrapper adds its effect, then draws
