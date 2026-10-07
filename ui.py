import pygame
from config import *
import assets

class Button:
    def __init__(self, x, y, width, height, text, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
        self.pressed = False
        self.animation_offset = 0.0
        
    def draw(self, surface):
        if self.hovered:
            self.animation_offset += (5 - self.animation_offset) * 0.2
        else:
            self.animation_offset += (0 - self.animation_offset) * 0.2
            
        y_offset = int(self.animation_offset)
        if self.pressed:
            y_offset = -2
            
        bg_rect = self.rect.copy()
        bg_rect.y -= y_offset
        
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        
        color = (130, 220, 130) if self.hovered else (80, 180, 80)
        
        # Shadow
        pygame.draw.rect(surface, (40, 100, 40), shadow_rect, border_radius=15)
        # Button
        pygame.draw.rect(surface, color, bg_rect, border_radius=15)
        pygame.draw.rect(surface, WHITE, bg_rect, 3, border_radius=15)
        
        font = assets.get_font(32, bold=True)
        text_surf = font.render(self.text, True, WHITE)
        # Text shadow
        text_shadow = font.render(self.text, True, (40, 100, 40))
        
        text_rect = text_surf.get_rect(center=bg_rect.center)
        surface.blit(text_shadow, (text_rect.x+2, text_rect.y+2))
        surface.blit(text_surf, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                self.hovered = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.rect.collidepoint(event.pos) and self.action:
                self.action()
            self.pressed = False

class LevelCard(Button):
    def __init__(self, x, y, width, height, level_id, data, action=None):
        super().__init__(x, y, width, height, f"Level {level_id}", action)
        self.level_id = level_id
        self.data = data
        self.unlocked = data.get('unlocked', False)
        if not self.unlocked:
            self.action = None
            
    def draw(self, surface):
        if self.hovered and self.unlocked:
            self.animation_offset += (5 - self.animation_offset) * 0.2
        else:
            self.animation_offset += (0 - self.animation_offset) * 0.2
            
        y_offset = int(self.animation_offset)
        if self.pressed and self.unlocked:
            y_offset = -2
            
        bg_rect = self.rect.copy()
        bg_rect.y -= y_offset
        
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        
        color = (255, 215, 0) if self.hovered and self.unlocked else ((220, 180, 0) if self.unlocked else (120, 120, 120))
        
        # Shadow
        pygame.draw.rect(surface, (150, 100, 0) if self.unlocked else (80, 80, 80), shadow_rect, border_radius=15)
        # Card
        pygame.draw.rect(surface, color, bg_rect, border_radius=15)
        pygame.draw.rect(surface, WHITE, bg_rect, 4, border_radius=15)
        
        font = assets.get_font(28, bold=True)
        text_surf = font.render(f"Level {self.level_id}", True, WHITE)
        surface.blit(text_surf, (bg_rect.x + 15, bg_rect.y + 15))
        
        if self.unlocked:
            score_font = assets.get_font(20, bold=True)
            score_surf = score_font.render(f"Score: {self.data.get('score', 0)}", True, WHITE)
            surface.blit(score_surf, (bg_rect.x + 15, bg_rect.y + 60))
            
            # Stars
            stars = self.data.get('stars', 0)
            for i in range(3):
                star_color = YELLOW if i < stars else (180, 150, 0)
                pygame.draw.circle(surface, star_color, (bg_rect.x + 35 + i * 40, bg_rect.y + 130), 12)
                pygame.draw.circle(surface, WHITE, (bg_rect.x + 35 + i * 40, bg_rect.y + 130), 12, 2)
        else:
            lock_font = assets.get_font(28, bold=True)
            lock_surf = lock_font.render("LOCKED", True, (200, 50, 50))
            surface.blit(lock_surf, (bg_rect.x + 20, bg_rect.y + 80))
