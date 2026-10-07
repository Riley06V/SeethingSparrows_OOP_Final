""" First implementations of pygame and pymunk -- Mikel Kratzer 10/6"""
import math
import pygame
# import pymunk

GRAVITY = 980.0  # gravitational constant measured in px/s^2
FRICTION = 0.2  # slowdown by dragging against the ground
DRAG = 0.0005  # air resistance (quadratic)
THRESHOLD = 30  # minimum velocity before stopping
FLOOR = 720  # position of floor
WIDTH, HEIGHT = 1280, 720  # size of window


class Ball():
    """Defines a simple ball."""
    def __init__(self, x, y, v_x, v_y, image, r, bounce):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(v_x, v_y)
        self.radius = r
        self.bounce = bounce
        self.image = pygame.transform.scale(image.convert_alpha(),
                                            (int(2*self.radius), int(2*self.radius)))

    def add_image(self, screen):
        """Adds an image to the ball."""

        # Get the rectangle bounding the image, and lock its center to the circle's center
        image_rect = self.image.get_rect()
        image_rect.center = self.position
        screen.blit(self.image, image_rect)

    def update(self, dt):
        """Updates the ball's position and velocity every second

        Args:
            dt (float): delta time
        """

        # computes air drag and gravity while in the air
        speed = self.velocity.length()  # computes magnitude of velocity
        acceleration = pygame.Vector2(0, GRAVITY) - DRAG * speed * self.velocity
        self.velocity += acceleration * dt
        self.position += self.velocity * dt

        # side walls
        if not self.radius <= self.position.x <= WIDTH - self.radius:
            self.position.x = max(self.radius, min(WIDTH - self.radius, self.position.x))
            self.velocity.x *= -self.bounce

        # ceiling
        if self.position.y - self.radius < 0:
            self.position.y = self.radius
            self.velocity.y *= -self.bounce

        # floor
        if self.position.y + self.radius >= FLOOR:
            self.position.y = FLOOR - self.radius
            if abs(self.velocity.y) < THRESHOLD:
                self.velocity.y = 0
            else:
                self.velocity.y *= -self.bounce

            # friction: shrink toward 0, keep its sign, never overshoot
            slowdown = FRICTION * GRAVITY * dt
            new_speed = max(abs(self.velocity.x) - slowdown, 0)
            self.velocity.x = math.copysign(new_speed, self.velocity.x)

    def draw(self, screen):
        """Draws the ball.

        Args:
            screen (Surface): pygame window
        """
        pygame.draw.circle(screen, (0, 0, 0),
                           (self.position.x, self.position.y), self.radius)


def main():
    """Basic bouncing ball example from pygame"""
    pygame.init()

    background = pygame.image.load("background.png")
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Seething Sparrows")
    clock = pygame.time.Clock()

    image = pygame.image.load("red_bird.png")

    start_x, start_y = 150, 500  # slingshot position
    start_vx, start_vy = 600, -750  # to be adjusted by player in slingshot
    bird = Ball(start_x, start_y, start_vx, start_vy, image, r=20, bounce=0.5)

    running = True

    while running:

        dt = clock.tick(60) / 1000  # target is 60 frames per second

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        bird.update(dt)

        screen.blit(background, (0, 0))  # draw background first
        # pygame.draw.line(screen, (0, 0, 0), (0, FLOOR), (WIDTH, FLOOR), 3)
        # ball.draw(screen)
        bird.add_image(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
