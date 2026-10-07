import pygame
import math
import random
from config import *

pygame.init()

_cache = {}

def get_font(size, bold=False):
    key = f"font_{size}_{bold}"
    if key not in _cache:
        try:
            _cache[key] = pygame.font.SysFont("segoeui, arial", size, bold=bold)
        except:
            _cache[key] = pygame.font.Font(None, size)
    return _cache[key]

def draw_bird(bird_type):
    key = f"bird_{bird_type}"
    if key in _cache:
        return _cache[key]
    
    surf = pygame.Surface((60, 60), pygame.SRCALPHA)
    center = (30, 30)
    
    if bird_type == "normal":
        color = RED
        radius = 20
        # Shadow
        pygame.draw.circle(surf, (150, 10, 30), center, radius)
        # Body
        pygame.draw.circle(surf, color, (28, 28), radius)
        # Highlight
        pygame.draw.circle(surf, (255, 100, 100), (22, 22), 8)
        # Belly
        pygame.draw.circle(surf, (240, 220, 200), (30, 40), 14)
        # Wings
        pygame.draw.ellipse(surf, (180, 15, 35), (8, 25, 12, 18))
        # Tail feathers
        pygame.draw.polygon(surf, BLACK, [(10, 28), (0, 25), (4, 30), (0, 35), (12, 32)])
        # Beak
        pygame.draw.polygon(surf, (255, 140, 0), [(38, 28), (52, 32), (38, 36)])
        pygame.draw.polygon(surf, YELLOW, [(38, 28), (52, 32), (38, 32)])
        pygame.draw.line(surf, (200, 100, 0), (38, 32), (50, 32), 2)
        # Eyes
        pygame.draw.circle(surf, WHITE, (28, 22), 6)
        pygame.draw.circle(surf, WHITE, (38, 22), 6)
        pygame.draw.circle(surf, BLACK, (30, 22), 2)
        pygame.draw.circle(surf, BLACK, (40, 22), 2)
        # Eyebrows
        pygame.draw.line(surf, BLACK, (22, 16), (32, 19), 3)
        pygame.draw.line(surf, BLACK, (44, 16), (34, 19), 3)
    elif bird_type == "heavy":
        color = (139, 0, 0)
        radius = 25
        pygame.draw.circle(surf, (80, 0, 0), center, radius)
        pygame.draw.circle(surf, color, (28, 28), radius)
        pygame.draw.circle(surf, (200, 180, 160), (30, 45), 16)
        pygame.draw.polygon(surf, YELLOW, [(38, 28), (56, 32), (38, 36)])
        # Eyes
        pygame.draw.circle(surf, WHITE, (25, 20), 5)
        pygame.draw.circle(surf, WHITE, (39, 20), 5)
        pygame.draw.circle(surf, BLACK, (27, 20), 2)
        pygame.draw.circle(surf, BLACK, (41, 20), 2)
        pygame.draw.line(surf, BLACK, (18, 14), (28, 18), 4)
        pygame.draw.line(surf, BLACK, (46, 14), (36, 18), 4)
    elif bird_type == "speed":
        color = (255, 215, 0)
        # Pointy triangle shape
        pygame.draw.polygon(surf, (200, 150, 0), [(10, 15), (50, 30), (10, 45)])
        pygame.draw.polygon(surf, color, [(12, 17), (48, 30), (12, 43)])
        pygame.draw.polygon(surf, (255, 140, 0), [(40, 28), (55, 30), (40, 32)])
        pygame.draw.circle(surf, WHITE, (28, 24), 5)
        pygame.draw.circle(surf, BLACK, (30, 24), 2)
        pygame.draw.line(surf, (200, 0, 0), (22, 18), (32, 21), 3)
        
    _cache[key] = surf
    return surf

def draw_enemy(enemy_type, radius=20, damage=0):
    key = f"enemy_{enemy_type}_{radius}_{damage}"
    if key in _cache:
        return _cache[key]
    
    surf = pygame.Surface((radius*2+20, radius*2+20), pygame.SRCALPHA)
    center = (radius+10, radius+10)
    
    color = (50, 205, 50)
    if damage > 50:
        color = (100, 205, 100) # bruised
        
    pygame.draw.circle(surf, (20, 100, 20), center, radius)
    pygame.draw.circle(surf, color, (center[0]-2, center[1]-2), radius)
    
    # Nose
    pygame.draw.ellipse(surf, (34, 139, 34), (center[0]+radius*0.2, center[1]-radius*0.2, radius*0.8, radius*0.6))
    pygame.draw.circle(surf, (0, 100, 0), (center[0]+radius*0.4, center[1]+radius*0.1), radius*0.1)
    pygame.draw.circle(surf, (0, 100, 0), (center[0]+radius*0.7, center[1]+radius*0.1), radius*0.1)
    
    # Eyes
    if damage > 50:
        # X eyes
        pygame.draw.line(surf, BLACK, (center[0]-radius*0.4, center[1]-radius*0.5), (center[0]-radius*0.1, center[1]-radius*0.2), 3)
        pygame.draw.line(surf, BLACK, (center[0]-radius*0.1, center[1]-radius*0.5), (center[0]-radius*0.4, center[1]-radius*0.2), 3)
        pygame.draw.line(surf, BLACK, (center[0]+radius*0.1, center[1]-radius*0.5), (center[0]+radius*0.4, center[1]-radius*0.2), 3)
        pygame.draw.line(surf, BLACK, (center[0]+radius*0.4, center[1]-radius*0.5), (center[0]+radius*0.1, center[1]-radius*0.2), 3)
    else:
        pygame.draw.circle(surf, WHITE, (center[0]-radius*0.3, center[1]-radius*0.4), radius*0.25)
        pygame.draw.circle(surf, WHITE, (center[0]+radius*0.3, center[1]-radius*0.4), radius*0.25)
        pygame.draw.circle(surf, BLACK, (center[0]-radius*0.2, center[1]-radius*0.4), radius*0.1)
        pygame.draw.circle(surf, BLACK, (center[0]+radius*0.4, center[1]-radius*0.4), radius*0.1)
    
    _cache[key] = surf
    return surf

def draw_block(material, width, height, damage=0):
    key = f"block_{material}_{width}_{height}_{damage}"
    if key in _cache:
        return _cache[key]
        
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    rect = pygame.Rect(0, 0, width, height)
    
    if material == "wood":
        pygame.draw.rect(surf, (100, 50, 10), rect)
        pygame.draw.rect(surf, WOOD_COLOR, (1, 1, width-2, height-2))
        for i in range(1, height//10):
            pygame.draw.line(surf, (160, 82, 45), (0, i*10), (width, i*10), 1)
        if damage > 50:
            pygame.draw.line(surf, (60, 30, 5), (width*0.2, 0), (width*0.5, height*0.5), 2)
            pygame.draw.line(surf, (60, 30, 5), (width*0.5, height*0.5), (width*0.3, height), 2)
    elif material == "glass":
        pygame.draw.rect(surf, (100, 150, 200, 100), rect)
        pygame.draw.rect(surf, (200, 230, 255, 180), rect, 2)
        pygame.draw.line(surf, (255, 255, 255, 200), (width*0.2, height*0.2), (width*0.8, height*0.8), 2)
        if damage > 20:
            pygame.draw.line(surf, (255,255,255, 255), (width*0.1, height*0.5), (width*0.9, height*0.4), 1)
            pygame.draw.line(surf, (255,255,255, 255), (width*0.5, height*0.1), (width*0.4, height*0.9), 1)
    elif material == "stone":
        pygame.draw.rect(surf, (80, 80, 80), rect)
        pygame.draw.rect(surf, STONE_COLOR, (2, 2, width-4, height-4))
        pygame.draw.circle(surf, (105, 105, 105), (width//2, height//2), min(width, height)//3)
        if damage > 100:
            pygame.draw.line(surf, (40, 40, 40), (0, height*0.2), (width, height*0.8), 3)
        
    _cache[key] = surf
    return surf

def draw_slingshot_front():
    key = "slingshot_front"
    if key in _cache: return _cache[key]
    surf = pygame.Surface((40, 150), pygame.SRCALPHA)
    pygame.draw.rect(surf, (100, 50, 10), (10, 50, 20, 100))
    pygame.draw.rect(surf, WOOD_COLOR, (12, 52, 16, 96))
    pygame.draw.line(surf, (100, 50, 10), (20, 50), (5, 10), 12)
    pygame.draw.line(surf, WOOD_COLOR, (20, 50), (5, 10), 8)
    _cache[key] = surf
    return surf

def draw_slingshot_back():
    key = "slingshot_back"
    if key in _cache: return _cache[key]
    surf = pygame.Surface((40, 150), pygame.SRCALPHA)
    pygame.draw.line(surf, (80, 40, 5), (20, 50), (35, 10), 12)
    pygame.draw.line(surf, (120, 70, 20), (20, 50), (35, 10), 8)
    _cache[key] = surf
    return surf

def generate_background(width, height):
    key = f"bg_{width}_{height}"
    if key in _cache: return _cache[key]
    
    surf = pygame.Surface((width, height))
    for y in range(height):
        progress = y / height
        r = int(SKY_BLUE[0] * (1 - progress) + 200 * progress)
        g = int(SKY_BLUE[1] * (1 - progress) + 220 * progress)
        b = int(SKY_BLUE[2] * (1 - progress) + 255 * progress)
        pygame.draw.line(surf, (r, g, b), (0, y), (width, y))
        
    pygame.draw.circle(surf, YELLOW, (width - 200, 150), 70)
    pygame.draw.circle(surf, (255, 255, 200), (width - 200, 150), 70, 4)
    
    # Layered hills
    for i in range(3):
        color = (30 + i*10, 150 + i*20, 50 + i*15)
        offset = i * 40
        pygame.draw.ellipse(surf, color, (-200 + offset*2, height - 250 + offset, 800, 400))
        pygame.draw.ellipse(surf, color, (400 + offset*2, height - 300 + offset, 1000, 500))
    
    # Ground
    ground_rect = pygame.Rect(0, height - 100, width, 100)
    pygame.draw.rect(surf, (40, 120, 30), ground_rect)
    pygame.draw.rect(surf, GROUND_GREEN, (0, height - 100, width, 20))
    
    _cache[key] = surf
    return surf
