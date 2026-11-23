from objects import Object,Ball,Block
from slingshot import Slingshot
import pygame

class Level:

    def __init__(self, object_list, score, bird_q, pig_list) -> None:
        # self.objects = object_list
        # self.score = score
        # self.birds = bird_q
        self.objects = []
        self.score = 0.0
        self.birds = []
        self.pigs = []
        
    
    def add_block(self,block:Block) -> None:
        self.objects.append(block)

    def add_bird(self,bird:Ball) -> None:
        self.birds.append(bird)
        
    def add_pig(self, pig:Ball) -> None:
        self.pigs.append(pig)

    def fill_sling(self):
        pass
    def take_damage():
        pass
    
    def level_score():
        pass

    # def draw_level(self):
    #     WIDTH, HEIGHT = 1280, 720
    #     pygame.init()
    #     screen = pygame.display.set_mode((WIDTH, HEIGHT))
    #     pygame.display.set_caption("Seething Sparrows")
    #     clock = pygame.time.Clock()
    #     running = True
        
    #     while running:
    #         dt = clock.tick(60) / 1000
            
    #         # Event handling
    #         for event in pygame.event.get():
            
    #             if event.type == pygame.QUIT:
    #                 running = False
            
    #             elif event.type == pygame.KEYDOWN:
    #                 if event.key == pygame.K_r:
    #                     # Reset all objects
    #                     self.slingshot.reset()
    #                     for obj in self.objects:
    #                         obj.reset()
    #                     for bird in self.birds:
    #                         bird.reset()
    #                     for pig in self.pigs:
    #                         pig.reset()
            
    #             self.slingshot.handle_event(event)
    #             # Update physics
    #             space.step(dt)
            
    #                 # Rendering
    #             screen.blit(background, (0, 0))
            
    #             slingshot.draw(screen)
    #             for obj in object_list:
    #                 obj.draw(screen)
            
    #             pygame.display.flip()

    def check_terminal(self) -> bool:
        if not self.birds:
            return True
    def reset():
        pass