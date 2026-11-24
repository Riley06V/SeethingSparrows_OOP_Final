"""The Game manager (Singleton) that owns the window and the screen stack.

Only one window and one clock should ever exist, so ``Game()`` always
returns the same object, like the manager classes in A1-A3.

Screens live on a stack. Full screens replace the top; overlays (pause,
level cleared) are pushed on top and popped off again, so the game under a
pause menu is kept exactly as it was.
"""

from __future__ import annotations

# Any = "any type at all". Used for *args/**kwargs below, which can be anything.
from typing import Any

import pygame

from ui import theme
from ui.screens import Screen


class EmptyScreenStackError(IndexError):
    """Raised when something needs a screen but the stack is empty."""


class Game:
    """Singleton: owns the window, clock and screen stack."""

    # The one shared Game. Starts as None = "not made yet".
    _instance: Game | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> Game:
        """Create the one Game the first time; return it every time after."""
        # __new__ runs BEFORE __init__ and decides which object you get back.
        # First call: build a real object and save it. Every later call:
        # skip building and return the saved one. That's the Singleton.
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False  # __init__ hasn't run yet
        return cls._instance

    def __init__(self) -> None:
        """Open the window once (later calls do nothing)."""
        # Python calls __init__ after EVERY Game(), even when __new__ handed
        # back the existing object. This flag makes the setup run once only,
        # so a second Game() doesn't open a second window or wipe the stack.
        if self._initialized:
            return
        self._initialized: bool = True
        pygame.init()  # switch on every pygame system (display, fonts, ...)
        self.__surface: pygame.Surface = pygame.display.set_mode(
            (theme.WIDTH, theme.HEIGHT)  # open the 1280x720 window
        )
        pygame.display.set_caption(theme.TITLE)  # title bar text
        self.__clock: pygame.time.Clock = pygame.time.Clock()  # keeps a steady FPS
        # The screen stack: a list where the LAST item is the active screen,
        # e.g. [PlayingScreen, PauseScreen] = pause menu over the game.
        self.__stack: list[Screen] = []
        self.__running: bool = False  # True while the main loop is going

    @classmethod
    def reset_instance(cls) -> None:
        """Forget the singleton (used by tests to start fresh)."""
        cls._instance = None  # next Game() builds a brand-new one

    @property
    def surface(self) -> pygame.Surface:
        """The window's drawing surface."""
        return self.__surface

    @property
    def running(self) -> bool:
        """True while the main loop is going."""
        return self.__running

    @property
    def screens(self) -> tuple[Screen, ...]:
        """The stack, bottom first (read-only copy)."""
        # tuple = a list you can't change, so outside code can look but
        # can't edit our stack.
        return tuple(self.__stack)

    @property
    def top(self) -> Screen:
        """The active screen.

        Raises:
            EmptyScreenStackError: if no screen has been shown yet.
        """
        if not self.__stack:
            raise EmptyScreenStackError("no screen on the stack")
        return self.__stack[-1]  # [-1] = the last item = the top of the stack

    def push(self, screen: Screen) -> None:
        """Put a screen on top (used for overlays)."""
        self.__stack.append(screen)

    def pop(self) -> Screen:
        """Remove and return the top screen.

        Raises:
            EmptyScreenStackError: if the stack is empty.
        """
        if not self.__stack:
            raise EmptyScreenStackError("no screen to pop")
        return self.__stack.pop()  # e.g. closing the pause menu

    def replace(self, screen: Screen) -> None:
        """Clear the stack and show only ``screen`` (used for full screens)."""
        self.__stack.clear()
        self.__stack.append(screen)

    def show_main_menu(self) -> None:
        """Go to the main menu."""
        # Imported HERE, inside the method, not at the top of the file:
        # main_menu.py refers back to Game, so importing it at the top would
        # make the two files import each other in a loop.
        from ui.main_menu import MainMenuScreen
        self.replace(MainMenuScreen(self))

    def start_level(self, level: int = 1) -> None:
        """Start playing a level."""
        from ui.playing_screen import PlayingScreen  # same reason as above
        self.replace(PlayingScreen(self, level))

    def quit(self) -> None:
        """Stop the main loop after this frame."""
        self.__running = False

    def visible_screens(self) -> list[Screen]:
        """Screens to draw this frame: the top full screen and overlays above it."""
        # Walk down from the top while screens are overlays, stopping at the
        # first full screen. Everything from there up gets drawn.
        # e.g. [Menu, Playing, Pause(overlay)] -> draw [Playing, Pause]
        start: int = len(self.__stack) - 1
        while start > 0 and self.__stack[start].is_overlay:
            start -= 1
        return self.__stack[max(start, 0):]  # slice from start to the end

    def step(self, events: list[pygame.event.Event], dt: float) -> None:
        """Run one frame: only the top screen gets input; all visible draw."""
        for event in events:
            if event.type == pygame.QUIT:  # the window's X button
                self.quit()
        active: Screen = self.top
        for screen in self.visible_screens():
            if screen is active:
                # The top screen gets the full recipe: input, update, draw.
                screen.frame(events, dt, self.__surface)
            else:
                # Screens under an overlay are only DRAWN, not updated, so
                # the game behind the pause menu stays frozen in place.
                screen.draw(self.__surface)

    def run(self) -> None:
        """Main loop: show the menu, then step until quit."""
        if not self.__stack:
            self.show_main_menu()  # nothing to show yet -> start at the menu
        self.__running = True
        while self.__running:
            # tick(60) waits just long enough to hold 60 FPS, and returns how
            # many milliseconds passed since last frame. / 1000 -> seconds,
            # e.g. 16 ms -> 0.016 s. Physics uses this so speed stays the
            # same even if a frame runs a bit slow.
            dt: float = self.__clock.tick(theme.FPS) / 1000
            self.step(pygame.event.get(), dt)  # everything that happened this frame
            pygame.display.flip()  # show the finished frame on screen
        pygame.quit()  # close the window cleanly
