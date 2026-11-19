"""Handles slingshot dragging and launching."""

import pygame
import pymunk


class Slingshot:
    """Manages dragging and launching the bird."""

    def __init__(self, space, bird, x, y, max_drag=100, launch_multiplier=10):
        self.space = space
        self.bird = bird
        self.position = pymunk.Vec2d(x, y)

        self.max_drag = max_drag
        self.launch_multiplier = launch_multiplier

        self.dragging = False
        self.launched = False
        self.in_space = True

        # Remove bird from physics until it is launched
        self.space.remove(self.bird.body, self.bird.shape)
        self.in_space = False

    def handle_event(self, event):
        """Handle mouse input for dragging and releasing the bird."""

        if self.launched:
            return

        # Start dragging when clicking on the bird
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = pymunk.Vec2d(*event.pos)
                bird_pos = self.bird.body.position

                if mouse_pos.get_distance(bird_pos) <= self.bird.radius:
                    self.dragging = True

        # Launch when releasing the mouse
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging:
                self.launch()

        # Move bird while dragging
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mouse_pos = pymunk.Vec2d(*event.pos)

                # Calculate pull distance
                pull = mouse_pos - self.position

                # Restrict to within max_drag
                if pull.length > self.max_drag:
                    pull = pull.normalized() * self.max_drag

                # Update bird position
                self.bird.body.position = self.position + pull

    def launch(self):
        """Launch the bird in the opposite direction of the pull."""

        direction = self.position - self.bird.body.position

        self.dragging = False

        # Return bird to anchor if barely pulled
        if direction.length < 5:
            self.bird.body.position = self.position
            return

        # Add bird back to physics simulation
        self.space.add(self.bird.body, self.bird.shape)
        self.in_space = True

        # Calculate launch velocity
        velocity = direction * self.launch_multiplier
        self.bird.body.velocity = velocity
        self.bird.body.activate()

        self.launched = True

    def reset(self):
        """Reset slingshot state."""

        # Remove bird from physics simulation
        if self.in_space:
            self.space.remove(self.bird.body, self.bird.shape)
            self.in_space = False

        self.dragging = False
        self.launched = False

    def draw(self, screen):
        """Draw the slingshot bands."""
