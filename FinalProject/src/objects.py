"""Object definitions."""

import math
import pygame
import pymunk


class Object:
    """Base class for all game objects."""

    def __init__(self, space, surface, mass):
        self.mass = mass
        self.space = space

        # Pymunk setup
        self.body = pymunk.Body(mass, 1)  # moment = 1
        self.shape = None  # no defined shape yet

        # Prepare image
        self.base_image = surface.convert_alpha()

        self.initial_state = None  # save initial state for resetting

    def get_initial_state(self):
        """Save initial physics state for resets."""

        self.initial_state = {
            "position": tuple(self.body.position),
            "velocity": tuple(self.body.velocity),
            "angle": self.body.angle,
            "angular_velocity": self.body.angular_velocity
        }

    def reset(self):
        """Restore the object's initial physics state."""

        if self.initial_state is None:
            return

        self.body.position = self.initial_state["position"]
        self.body.velocity = self.initial_state["velocity"]
        self.body.angle = self.initial_state["angle"]
        self.body.angular_velocity = self.initial_state["angular_velocity"]

        # Clear accumulated forces and torque
        self.body.force = (0, 0)
        self.body.torque = 0

        # Wake body
        self.body.activate()

    def draw(self, screen):
        """Draw the object on the screen."""

        rotated_image = pygame.transform.rotate(
            self.base_image,
            math.degrees(-self.body.angle)
        )

        image_rect = rotated_image.get_rect()
        image_rect.center = (
            round(self.body.position.x),
            round(self.body.position.y)
        )

        screen.blit(rotated_image, image_rect)


class Ball(Object):
    """A circular object (birds, pigs)."""

    def __init__(self, space, x, y, v_x, v_y, surface, radius, bounce):
        mass = 1

        super().__init__(space, surface, mass)  # inherit from Object

        # Circular physics setup
        moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body.moment = moment

        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = bounce
        self.shape.friction = 0.5
        self.radius = radius

        # Position and velocity
        self.body.position = (x, y)
        self.body.velocity = (v_x, v_y)

        # Add to physics space
        space.add(self.body, self.shape)  # automatically handles collisions

        # Scale image to match collision geometry
        self.base_image = pygame.transform.scale(
            self.base_image,
            (int(2 * radius), int(2 * radius))
        )

        # Save initial state
        self.get_initial_state()


class Block(Object):
    """A rectangular object (obstacles, blocks)."""

    def __init__(
        self, space, x, y, v_x, v_y, surface, size, bounce
    ):
        mass = 0.5

        super().__init__(space, surface, mass)

        # Rectangular physics setup
        moment = pymunk.moment_for_box(mass, (size, size))
        self.body.moment = moment

        self.shape = pymunk.Poly.create_box(
            self.body, (size, size)
        )
        self.shape.elasticity = bounce
        self.shape.friction = 0.8
        self.size = size

        # Position and velocity
        self.body.position = (x, y)
        self.body.velocity = (v_x, v_y)

        # Add to physics space
        space.add(self.body, self.shape)

        # Scale image to match collision geometry
        self.base_image = pygame.transform.scale(
            self.base_image,
            (int(size), int(size))
        )

        # Save initial state
        self.get_initial_state()
