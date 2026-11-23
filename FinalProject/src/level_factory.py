# import assets
from typing import Any
from level import Level
from objects import Object,Ball,Block
from slingshot import Slingshot
import pygame
import os

"""level numbern is the parameter

if level number equal __ return instance of level with attributes

may use nested dictonaries"""

class Factory:
    def __init__(self):
        # self.space = space
        # self.birds = birds
        # self.blocks = blocks
        # self.pigs = pigs
        # self.score = score
        # self.background = background
        # self.level_number = level_num
        # self.slingshot = slingshot


        """level parameters are self, object_list, score, bird_q, pig_list"""

    def create_level(self, space, number) -> Level:
        # number = input("enter level number")
        if number == 1:
            print("base level")
            block_list = []
            level_one = Level([],0,[],[])
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            assets_dir = os.path.join(base_dir, "assets")
            bird_image = pygame.image.load(os.path.join(assets_dir, "red_bird.png"))
            block_image = pygame.image.load(os.path.join(assets_dir, "Stone_Box.png"))
            pig_image = pygame.image.load(os.path.join(assets_dir, "SmallCat.png"))
            glass_image = pygame.image.load(os.path.join(assets_dir, "Glass_Crate.png"))
            wood_image = pygame.image.load(os.path.join(assets_dir, "Wood_Box.png"))
            bird = Ball(space, 150, 500, 0, 0, bird_image, radius=20, bounce=0.5)
            bird2 = Ball(space, 15, 50, 0, 0, bird_image, radius=20, bounce=0.5)
            
            stone = Block(space, 500, 450, 0, 0, block_image, size=60, bounce=0.1)
            stone2 = Block(space, 500, 350, 0, 0, block_image, size=60, bounce=0.1)
            stone3 = Block(space, 500, 250, 0, 0, block_image, size=60, bounce=0.1)
            stone4 = Block(space, 500, 150, 0, 0, block_image, size=60, bounce=0.1)

            glass = Block(space, 600, 450, 0, 0, glass_image, size=70, bounce=0.1)
            glass2 = Block(space, 600, 350, 0, 0, glass_image, size=70, bounce=0.1)
            glass3 = Block(space, 600, 325, 0, 0, glass_image, size=70, bounce=0.1)
            glass4 = Block(space, 600, 300, 0, 0, glass_image, size=70, bounce=0.1)
            glass5 = Block(space, 600, 650, 0, 0, glass_image, size=70, bounce=0.1)

            wood = Block(space, 700, 450, 0, 0, wood_image, size=70, bounce=0.1)
            wood2 = Block(space, 700, 350, 0, 0, wood_image, size=70, bounce=0.1)
            wood3 = Block(space, 700, 325, 0, 0, wood_image, size=70, bounce=0.1)
            wood4 = Block(space, 700, 300, 0, 0, wood_image, size=70, bounce=0.1)
            wood5 = Block(space, 700, 275, 0, 0, wood_image, size=70, bounce=0.1)
            wood6 = Block(space, 700, 250, 0, 0, wood_image, size=70, bounce=0.1)
            wood7 = Block(space, 700, 225, 0, 0, wood_image, size=70, bounce=0.1)
            wood8 = Block(space, 700, 200, 0, 0, wood_image, size=70, bounce=0.1)
            fake_pig = Ball(space, 600, 140,0,0,pig_image, radius=20, bounce=0.5)

            block_list = [stone,stone2,stone3,stone4,glass,glass2,glass3,glass4,glass5,wood,wood2,wood3,wood4,wood5,wood6
                          ,wood7,wood8]

            for block in block_list:
                level_one.add_block(block)
            # level_one.add_block(stone)
            # level_one.add_block(stone2)
            # level_one.add_block(stone3)
            # level_one.add_block(stone4)
            level_one.add_bird(bird)
            level_one.add_bird(bird2)
            level_one.add_pig(fake_pig)
            # object_list = [block, block2,block3,block4]
            # bird_list = [bird,bird2]  # list all objects
            # pig_list = [fake_pig]
            
            return level_one
        # is where the hard coded levels are made
        pass

    