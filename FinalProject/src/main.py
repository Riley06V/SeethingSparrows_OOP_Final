"""Pymunk Ball Simulation."""

import os
import pygame
import pymunk

from objects import Ball, Block

WIDTH, HEIGHT = 1280, 720


def main():
    """Main function."""

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Seething Sparrows")
    clock = pygame.time.Clock()

    # Locate assets folder
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    assets_dir = os.path.join(base_dir, "assets")

    # Load images
    background = pygame.image.load(os.path.join(assets_dir, "background.png")).convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    bird_image = pygame.image.load(os.path.join(assets_dir, "red_bird.png"))
    block_image = pygame.image.load(os.path.join(assets_dir, "tnt_block.png"))

    # Physics space
    space = pymunk.Space()
    space.gravity = (0.0, 980.0)

    # Enable sleeping so objects fully stop
    space.sleep_time_threshold = 0.5

    # Boundaries
    static_body = pymunk.Body(body_type=pymunk.Body.STATIC)

    walls = [
        pymunk.Segment(static_body, (0, HEIGHT), (WIDTH, HEIGHT), 5),  # ceiling
        pymunk.Segment(static_body, (0, 0), (WIDTH, 0), 5),  # floor
        pymunk.Segment(static_body, (0, 0), (0, HEIGHT), 5),  # left wall
        pymunk.Segment(static_body, (WIDTH, 0), (WIDTH, HEIGHT), 5)  # right wall
    ]

    for wall in walls:
        wall.friction = 0.5
        wall.elasticity = 0.5

    space.add(static_body, *walls)

    # Create objects (different for each level)
    bird = Ball(space, 150, 500, 600, -750, bird_image, radius=20, bounce=0.5)
    block = Block(space, 900, 650, 0, 0, block_image, size=60, bounce=0.5)
    block2 = Block(space, 900, 550, 0, 0, block_image, size=60, bounce=0.5)
    object_list = [bird, block, block2]  # list all objects

    running = True

    while running:
        dt = clock.tick(60) / 1000

        # Event handling
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:
                    # Reset all objects
                    for obj in object_list:
                        obj.reset()

        # Update physics
        space.step(dt)

        # Rendering
        screen.blit(background, (0, 0))

        for obj in object_list:
            obj.draw(screen)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
