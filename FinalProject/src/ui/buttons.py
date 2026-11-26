"""Menu buttons (Decorator pattern).

``Button`` draws the chunky orange/white button. Extra behavior is added by
*wrapping* a button instead of subclassing it:

    HoverGrow(PressDown(Button(...)))

Each wrapper has the same interface as a Button (``Clickable``), so the menu
never needs to know which extras a button has. 
"""

from __future__ import annotations


from abc import ABC, abstractmethod
from collections.abc import Callable

import pygame

from ui import theme


Action = Callable[[], None]


class Clickable(ABC):
    """Anything the menu can show, hover, focus and click.

    This is the shared interface. Button AND every decorator follow it, so
    the menu can treat a plain button and a triple-wrapped one the same way.
    """

    @property
    @abstractmethod
    def rect(self) -> pygame.Rect:
        """Where the button sits at normal size."""

    @property
    @abstractmethod
    def label(self) -> str:
        """Text on the button."""

    @property
    @abstractmethod
    def hovered(self) -> bool:
        """True while the mouse is over it or keyboard focus is on it."""

    @property
    @abstractmethod
    def pressed(self) -> bool:
        """True while the mouse button is held down on it."""

    @property
    @abstractmethod
    def enabled(self) -> bool:
        """False for buttons that can't be used yet."""

    @abstractmethod
    def set_focus(self, focused: bool) -> None:
        """Give or take away keyboard focus."""

    @abstractmethod
    def contains(self, pos: tuple[int, int]) -> bool:
        """Whether a screen point is on the button."""

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        """React to a mouse event. True if this event clicked the button."""

    @abstractmethod
    def click(self) -> None:
        """Run the button's action (mouse release or Enter key)."""

    @abstractmethod
    def draw(self, screen: pygame.Surface, scale: float = 1.0, sink: int = 0) -> None:
        """Draw the button, ``scale`` times bigger and ``sink`` px lower.

        scale and sink are how decorators change the look: HoverGrow passes a
        bigger scale, PressDown passes a bigger sink.
        """


class Button(Clickable):
    """The basic chunky button: dark outline, colored top, darker lip."""

    LIP: int = 6      # height in px of the darker "side" under the face (3D look)
    RADIUS: int = 18  # how rounded the corners are, in px

    def __init__(
        self,
        label: str,
        center: tuple[int, int],
        size: tuple[int, int],
        on_click: Action,
        fill: theme.Color = theme.WHITE,
        lip: theme.Color = theme.WHITE_LIP,
        text_color: theme.Color = theme.DARK,
        font_size: int = 30,
    ) -> None:
        """Create a button centered on ``center``."""
        # pygame.Rect((x, y), (width, height)) stores a rectangle. We make it
        # at (0, 0), then move its center to where the button should sit.
        self.__rect = pygame.Rect((0, 0), size)
        self.__rect.center = center
        self.__label: str = label
        self.__on_click: Action = on_click   # the function to run on click
        self.__fill: theme.Color = fill      # face color
        self.__lip: theme.Color = lip        # lip (side) color
        self.__text_color: theme.Color = text_color
        self.__font_size: int = font_size
        # Three on/off switches tracking what the player is doing:
        self.__mouse_over: bool = False  # mouse is on top of the button
        self.__focused: bool = False     # keyboard (arrow keys) picked it
        self.__pressed: bool = False     # mouse button is held down on it

    @property
    def rect(self) -> pygame.Rect:
        """Normal-size rectangle."""
        # .copy() so outside code can't move our real rect by editing it.
        return self.__rect.copy()

    @property
    def label(self) -> str:
        """Button text."""
        return self.__label

    @property
    def hovered(self) -> bool:
        """Mouse over it, or keyboard focus on it."""
        return self.__mouse_over or self.__focused

    @property
    def pressed(self) -> bool:
        """Mouse held down on it."""
        return self.__pressed

    @property
    def enabled(self) -> bool:
        """A plain button is always usable."""
        return True

    def set_focus(self, focused: bool) -> None:
        """Keyboard focus on/off."""
        self.__focused = focused

    def contains(self, pos: tuple[int, int]) -> bool:
        """Point-in-rectangle test."""
        # collidepoint = "is this (x, y) inside the rectangle?"
        return bool(self.__rect.collidepoint(pos))

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Track hover and press; click on release over the button."""
        if event.type == pygame.MOUSEMOTION:
            # Mouse moved: update whether it's on top of us.
            self.__mouse_over = self.contains(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 1 = left button
            # Pressed down: only counts as "pressed" if it started on us.
            self.__pressed = self.contains(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            # Let go: it's a click only if the press STARTED on us and the
            # release is ALSO on us. Dragging off before letting go cancels,
            # like buttons in real apps.
            was_pressed: bool = self.__pressed
            self.__pressed = False
            if was_pressed and self.contains(event.pos):
                self.click()
                return True  # tell the menu "I was clicked"
        return False

    def click(self) -> None:
        """Run the action."""
        self.__on_click()

    @staticmethod
    def scaled(rect: pygame.Rect, scale: float, sink: int) -> pygame.Rect:
        """A copy of rect grown by ``scale`` around its center, moved down ``sink``."""
        # scale=1.06 -> 6% wider and taller. round() because pixels are whole.
        out = pygame.Rect(0, 0, round(rect.w * scale), round(rect.h * scale))
        # Same center as before (so it grows outward evenly), pushed down by sink.
        out.center = (rect.centerx, rect.centery + sink)
        return out

    def draw(self, screen: pygame.Surface, scale: float = 1.0, sink: int = 0) -> None:
        """Shadow, outline, lip, face, shine, label.

        Drawn back-to-front like layers in a paint program: each new shape
        covers part of the one before it.
        """
        r: pygame.Rect = self.scaled(self.__rect, scale, sink)  # where the face goes

        lip_h: int = max(self.LIP - sink, 0)

        # 1) Soft shadow: a see-through black rounded rect slightly bigger
        #    (+10 px) and lower (+8 px) than the button.
        #    (0, 0, 0, 55) = black at alpha 55 out of 255 (about 22% opaque).
        shadow = pygame.Surface((r.w + 10, r.h + 10), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 55), shadow.get_rect(), border_radius=24)
        screen.blit(shadow, (r.x - 5, r.y + 8 + lip_h - sink))

        # 2) Dark outline: two dark rounded rects 4 px bigger on each side
        #    (inflate(8, 8) = 8 px wider and taller in total). One at the
        #    lip's depth, one at the face, so the outline wraps both.
        pygame.draw.rect(screen, theme.DARK, r.inflate(8, 8).move(0, lip_h),
                         border_radius=self.RADIUS + 4)
        pygame.draw.rect(screen, theme.DARK, r.inflate(8, 8), border_radius=self.RADIUS + 4)

        # 3) Lip: the darker copy of the face, shifted down lip_h px. Only its
        #    bottom edge stays visible once the face is drawn over it.
        pygame.draw.rect(screen, self.__lip, r.move(0, lip_h), border_radius=self.RADIUS)

        # 4) Face: the main colored part of the button.
        pygame.draw.rect(screen, self.__fill, r, border_radius=self.RADIUS)

        # 5) Shine: a faint white bar across the top third of the face, so it
        #    looks glossy. (255, 255, 255, 60) = white at about 24% opacity.
        #    max(..., 1) keeps the size at least 1 px so pygame doesn't error.
        shine = pygame.Surface((max(r.w - 24, 1), max(r.h // 3, 1)), pygame.SRCALPHA)
        pygame.draw.rect(shine, (255, 255, 255, 60), shine.get_rect(), border_radius=12)
        screen.blit(shine, (r.x + 12, r.y + 6))  # 12 px in from the sides, 6 px down

        # 6) Label: text scaled with the button, centered on the face.
        text: pygame.Surface = theme.font(round(self.__font_size * scale)).render(
            self.__label, True, self.__text_color
        )
        screen.blit(text, text.get_rect(center=r.center))


class ButtonDecorator(Clickable):
    """Wraps another Clickable and passes everything through by default.

    This is the Decorator pattern's base: every method just forwards to the
    wrapped button. Real decorators below override only the ONE method
    they want to change and inherit the rest of the forwarding.
    """

    def __init__(self, inner: Clickable) -> None:
        """Wrap ``inner``."""
        # One underscore = "protected": subclasses (the decorators) may use it.
        self._inner: Clickable = inner

    @property
    def inner(self) -> Clickable:
        """The wrapped button."""
        return self._inner

    @property
    def rect(self) -> pygame.Rect:
        """Pass through."""
        return self._inner.rect

    @property
    def label(self) -> str:
        """Pass through."""
        return self._inner.label

    @property
    def hovered(self) -> bool:
        """Pass through."""
        return self._inner.hovered

    @property
    def pressed(self) -> bool:
        """Pass through."""
        return self._inner.pressed

    @property
    def enabled(self) -> bool:
        """Pass through."""
        return self._inner.enabled

    def set_focus(self, focused: bool) -> None:
        """Pass through."""
        self._inner.set_focus(focused)

    def contains(self, pos: tuple[int, int]) -> bool:
        """Pass through."""
        return self._inner.contains(pos)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Pass through."""
        return self._inner.handle_event(event)

    def click(self) -> None:
        """Pass through."""
        self._inner.click()

    def draw(self, screen: pygame.Surface, scale: float = 1.0, sink: int = 0) -> None:
        """Pass through."""
        self._inner.draw(screen, scale, sink)


class HoverGrow(ButtonDecorator):
    """Button grows a little while hovered or focused."""

    def __init__(self, inner: Clickable, grow: float = 1.06) -> None:
        """Wrap ``inner``; ``grow`` is the hover size multiplier.

        Raises:
            ValueError: if grow is below 1 (that would shrink the button).
        """
        super().__init__(inner)
        if grow < 1.0:
            raise ValueError("grow must be 1.0 or more")
        self.__grow: float = grow  # 1.06 = 6% bigger while hovered

    @property
    def grow(self) -> float:
        """Hover size multiplier."""
        return self.__grow

    def draw(self, screen: pygame.Surface, scale: float = 1.0, sink: int = 0) -> None:
        """Draw bigger while hovered."""
        # The only change: multiply scale while hovered, then let the
        # wrapped button do the real drawing.
        factor: float = self.__grow if self.hovered else 1.0
        self._inner.draw(screen, scale * factor, sink)


class PressDown(ButtonDecorator):
    """Button face sinks onto its lip while held, like a real key."""

    def __init__(self, inner: Clickable, depth: int = Button.LIP) -> None:
        """Wrap ``inner``; ``depth`` is how far it sinks in pixels.

        Raises:
            ValueError: if depth is negative.
        """
        super().__init__(inner)
        if depth < 0:
            raise ValueError("depth must be 0 or more")
        # Default = the lip height, so a pressed face sits exactly where
        # the lip was: fully pushed in.
        self.__depth: int = depth

    @property
    def depth(self) -> int:
        """Sink distance in pixels."""
        return self.__depth

    def draw(self, screen: pygame.Surface, scale: float = 1.0, sink: int = 0) -> None:
        """Draw lower while pressed."""
        # The only change: add extra sink while the mouse is held down.
        extra: int = self.__depth if self.pressed else 0
        self._inner.draw(screen, scale, sink + extra)


class Disabled(ButtonDecorator):
    """Grays a button out and ignores clicks (e.g. 'coming soon')."""

    def __init__(self, inner: Clickable, note: str = "COMING SOON") -> None:
        """Wrap ``inner`` with a small note underneath."""
        super().__init__(inner)
        self.__note: str = note

    @property
    def note(self) -> str:
        """Small text drawn under the button."""
        return self.__note

    @property
    def enabled(self) -> bool:
        """Never usable."""
        return False  # the menu's arrow keys skip buttons that aren't enabled

    @property
    def hovered(self) -> bool:
        """Never highlights."""
        return False  # so HoverGrow (if wrapped inside) never grows it

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Swallow all mouse events."""
        return False  # don't pass events on: the inner button never gets pressed

    def click(self) -> None:
        """Do nothing."""

    def draw(self, screen: pygame.Surface, scale: float = 1.0, sink: int = 0) -> None:
        """Draw the button, then a gray veil and the note."""
        self._inner.draw(screen, scale, sink)  # the normal button first
        r: pygame.Rect = Button.scaled(self.rect, scale, sink)
        # A see-through gray layer covering the button, its outline (+8) and
        # its lip (+LIP). (*theme.GRAY, 150) unpacks the gray color and adds
        # alpha 150 out of 255 (about 60% opaque).
        veil = pygame.Surface(r.inflate(8, 8 + Button.LIP).size, pygame.SRCALPHA)
        pygame.draw.rect(veil, (*theme.GRAY, 150), veil.get_rect(), border_radius=22)
        screen.blit(veil, (r.x - 4, r.y - 4))  # -4 = half of the outline's +8
        # Small note centered 14 px below the button.
        note: pygame.Surface = theme.font(16).render(self.__note, True, theme.DARK)
        screen.blit(note, note.get_rect(midtop=(r.centerx, r.bottom + 14)))


def menu_button(
    label: str, center: tuple[int, int], size: tuple[int, int], on_click: Action,
    primary: bool = False, font_size: int = 30,
) -> Clickable:
    """Standard menu button: orange if primary, white otherwise, with effects.

    A small factory function, so every screen makes buttons the same way.
    """
    if primary:
        # Main action (PLAY, NEXT LEVEL): orange face, white text.
        base = Button(label, center, size, on_click, theme.ORANGE, theme.ORANGE_LIP,
                      theme.WHITE, font_size)
    else:
        # Everything else: white face, dark text (the default colors).
        base = Button(label, center, size, on_click, font_size=font_size)
    # Wrap inside-out: PressDown first, then HoverGrow around it, so a
    # hovered AND pressed button is both bigger and sunk in.
    return HoverGrow(PressDown(base))
