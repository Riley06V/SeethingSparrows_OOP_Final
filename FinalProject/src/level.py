from objects import Object,Ball,Block
from slingshot import Slingshot
import pygame

class Level:

    def __init__(self, space, object_list, score, bird_q, pig_list) -> None:
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

    

    def check_terminal(self, space) -> bool:
        if self.birds and self.birds[0].body.is_sleeping:
            print("Bird is asleep - terminal condition met!")
            return True
        return False
        
    def reset_stuff(self) -> None:
    
        for obj in self.objects:
            obj.reset()
        for bird in self.birds:
            bird.reset()
        for pig in self.pigs:
            pig.reset()

    def draw_level(self, screen) -> None:
        for obj in self.objects:
            obj.draw(screen)
        for bird in self.birds:
            bird.draw(screen)
        for pig in self.pigs:
            pig.draw(screen)
