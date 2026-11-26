#! /usr/bin/env python3

"""Little setup helpers that all my UI tests use."""

__author__ = "Riley Valdez"
__date__ = "2026/11/25"
__license__ = "MIT"
__version__ = "0.1.0"
__maintainer__ = "Riley Valdez"

import os

import pygame

# no real window or sound during tests (the container and CI don't have a screen)
# has to overwrite, since docker-compose sets SDL_VIDEODRIVER=x11
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"


def start_pygame() -> None:
    """Open a tiny hidden window so images and fonts can load."""
    pygame.init()
    if pygame.display.get_surface() is None:
        pygame.display.set_mode((1, 1))


def blank_image(size: int = 32) -> pygame.Surface:
    """Return an empty see-through image for fake sprites."""
    return pygame.Surface((size, size), pygame.SRCALPHA)
