""" Main game loop -- Mikel Kratzer 10/6"""
import os
import pygame
import pymunk
from objects import Ball

WIDTH, HEIGHT = 1280, 720


def main():
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

    # Physics space
    space = pymunk.Space()
    space.gravity = (0.0, 980.0)
    
    # Enable sleeping so objects fully freeze and stop creeping when they come to rest
    space.sleep_time_threshold = 0.5

    # Static boundaries to keep everything inside the window
    static_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    walls = [
        pymunk.Segment(static_body, (0, HEIGHT), (WIDTH, HEIGHT), 5),  # Floor
        pymunk.Segment(static_body, (0, 0), (WIDTH, 0), 5),            # Ceiling
        pymunk.Segment(static_body, (0, 0), (0, HEIGHT), 5),           # Left wall
        pymunk.Segment(static_body, (WIDTH, 0), (WIDTH, HEIGHT), 5)    # Right wall
    ]
    for wall in walls:
        wall.friction = 0.5
        wall.elasticity = 0.5
    space.add(static_body, *walls)

    # Initial bird launch configuration
    start_x, start_y = 150, 500
    start_vx, start_vy = 600, -750
    bird = Ball(space, start_x, start_y, start_vx, start_vy, bird_image, r=20, bounce=0.5)

    running = True
    while running:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Reset bird position, velocity, angle, and wake it from sleep
                    bird.body.position = (start_x, start_y)
                    bird.body.velocity = (start_vx, start_vy)
                    bird.body.angular_velocity = 0
                    bird.body.angle = 0
                    bird.body.activate()

        space.step(dt)

        screen.blit(background, (0, 0))
        bird.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
