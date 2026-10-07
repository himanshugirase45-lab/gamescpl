import pygame
import math
from config import *
import assets

class Entity:
    def __init__(self, body, shape):
        self.body = body
        self.shape = shape
        self.dead = False
        
    def draw(self, surface):
        pass

class Bird(Entity):
    def __init__(self, body, shape, bird_type):
        super().__init__(body, shape)
        self.type = bird_type
        self.image = assets.draw_bird(bird_type)
        self.launched = False
        self.original_mass = body.mass
        self.original_moment = body.moment
        
    def draw(self, surface):
        if self.dead: return
        angle = math.degrees(self.body.angle)
        rotated = pygame.transform.rotate(self.image, -angle)
        rect = rotated.get_rect(center=(int(self.body.position.x), int(self.body.position.y)))
        surface.blit(rotated, rect.topleft)

class Block(Entity):
    def __init__(self, body, shape, width, height, material):
        super().__init__(body, shape)
        self.width = width
        self.height = height
        self.material = material
        self.hp = 100 if material == "wood" else (50 if material == "glass" else 200)
        self.max_hp = self.hp
        
    def draw(self, surface):
        if self.dead: return
        damage = self.max_hp - self.hp
        image = assets.draw_block(self.material, self.width, self.height, damage)
        angle = math.degrees(self.body.angle)
        rotated = pygame.transform.rotate(image, -angle)
        rect = rotated.get_rect(center=(int(self.body.position.x), int(self.body.position.y)))
        surface.blit(rotated, rect.topleft)

class Target(Entity):
    def __init__(self, body, shape, radius):
        super().__init__(body, shape)
        self.radius = radius
        self.hp = 50
        self.max_hp = self.hp
        
    def draw(self, surface):
        if self.dead: return
        damage = self.max_hp - self.hp
        image = assets.draw_enemy("pig", self.radius, damage)
        angle = math.degrees(self.body.angle)
        rotated = pygame.transform.rotate(image, -angle)
        rect = rotated.get_rect(center=(int(self.body.position.x), int(self.body.position.y)))
        surface.blit(rotated, rect.topleft)
