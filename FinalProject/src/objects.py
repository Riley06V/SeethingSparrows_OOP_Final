""" Object definitions for Seething Sparrows """
import math
import pygame
import pymunk


class Object:
    """Base class for all physics entities."""
    def __init__(self, space, surface, radius):
        self.radius = radius

        # Pymunk physics setup
        mass = 1
        moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, moment)
        self.shape = pymunk.Circle(self.body, radius)
        space.add(self.body, self.shape)

        # Prepare surface image
        self.base_image = pygame.transform.scale(
            surface.convert_alpha(), (int(2 * radius), int(2 * radius))
        )

    def draw(self, screen):
        """Draws the object using Pymunk's position and rotation smoothly."""
        rotated_image = pygame.transform.rotate(self.base_image, math.degrees(-self.body.angle))
        image_rect = rotated_image.get_rect()
        image_rect.center = (round(self.body.position[0]), round(self.body.position[1]))
        screen.blit(rotated_image, image_rect)


class Ball(Object):
    """A circular object (birds and pigs)."""
    def __init__(self, space, x, y, v_x, v_y, surface, r, bounce):
        super().__init__(space, surface, r)  # calls constructor of parent class
        self.body.position = (x, y)
        self.body.velocity = (v_x, v_y)
        self.shape.elasticity = bounce
        self.shape.friction = 0.5
