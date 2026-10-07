import pygame
from config import *
import assets
import ui
from state_machine import GameState, PlayingState, MainMenu
import save_manager

class PauseMenu(GameState):
    def __init__(self, manager, bg_state):
        super().__init__(manager)
        self.bg_state = bg_state
        self.buttons = [
            ui.Button(WIDTH//2 - 100, 300, 200, 60, "Resume", lambda: self.manager.change_state(self.bg_state)),
            ui.Button(WIDTH//2 - 100, 380, 200, 60, "Restart", lambda: self.manager.change_state(PlayingState(self.manager, self.bg_state.level_id))),
            ui.Button(WIDTH//2 - 100, 460, 200, 60, "Settings", lambda: self.manager.change_state(SettingsMenu(self.manager, self))),
            ui.Button(WIDTH//2 - 100, 540, 200, 60, "Main Menu", lambda: self.manager.change_state(MainMenu(self.manager)))
        ]
        
    def handle_events(self, events):
        for e in events:
            for b in self.buttons:
                b.handle_event(e)
                
    def draw(self, surface):
        self.bg_state.draw(surface)
        
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0, 150))
        surface.blit(overlay, (0,0))
        
        font = assets.get_font(60, bold=True)
        title = font.render("Paused", True, WHITE)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 150))
        
        for b in self.buttons:
            b.draw(surface)

class VictoryScreen(GameState):
    def __init__(self, manager, score, stars, unused_birds, level_id):
        super().__init__(manager)
        self.bg = assets.generate_background(WIDTH, HEIGHT)
        self.score = score
        self.stars = stars
        self.unused = unused_birds
        self.level_id = level_id
        
        self.buttons = [
            ui.Button(WIDTH//2 - 220, 500, 120, 50, "Replay", lambda: self.manager.change_state(PlayingState(self.manager, self.level_id))),
            ui.Button(WIDTH//2 - 80, 500, 160, 50, "Next Level", lambda: self.manager.change_state(PlayingState(self.manager, self.level_id+1)) if self.level_id < 5 else self.manager.change_state(MainMenu(self.manager))),
            ui.Button(WIDTH//2 + 100, 500, 150, 50, "Main Menu", lambda: self.manager.change_state(MainMenu(self.manager)))
        ]
        
    def handle_events(self, events):
        for e in events:
            for b in self.buttons:
                b.handle_event(e)
                
    def draw(self, surface):
        surface.blit(self.bg, (0, 0))
        font = assets.get_font(70, bold=True)
        title = font.render("Level Complete!" if self.level_id < 5 else "You Win The Game!", True, (255, 215, 0))
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        score_f = assets.get_font(40)
        s_t = score_f.render(f"Score: {self.score}", True, WHITE)
        surface.blit(s_t, (WIDTH//2 - s_t.get_width()//2, 250))
        
        for i in range(3):
            star_color = YELLOW if i < self.stars else DARK_GRAY
            pygame.draw.circle(surface, star_color, (WIDTH//2 - 60 + i * 60, 350), 25)
            
        for b in self.buttons:
            b.draw(surface)

class DefeatScreen(GameState):
    def __init__(self, manager, level_id):
        super().__init__(manager)
        self.bg = assets.generate_background(WIDTH, HEIGHT)
        self.level_id = level_id
        self.buttons = [
            ui.Button(WIDTH//2 - 150, 400, 120, 60, "Retry", lambda: self.manager.change_state(PlayingState(self.manager, self.level_id))),
            ui.Button(WIDTH//2 + 30, 400, 150, 60, "Main Menu", lambda: self.manager.change_state(MainMenu(self.manager)))
        ]
        
    def handle_events(self, events):
        for e in events:
            for b in self.buttons:
                b.handle_event(e)
                
    def draw(self, surface):
        surface.blit(self.bg, (0, 0))
        font = assets.get_font(70, bold=True)
        title = font.render("Level Failed", True, RED)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 150))
        
        for b in self.buttons:
            b.draw(surface)

class SettingsMenu(GameState):
    def __init__(self, manager, prev_state):
        super().__init__(manager)
        self.prev_state = prev_state
        self.bg = assets.generate_background(WIDTH, HEIGHT)
        
        self.data = save_manager.load_save()['settings']
        self.buttons = [
            ui.Button(WIDTH//2 - 100, 250, 200, 50, f"Mute: {'On' if self.data['mute'] else 'Off'}", self.toggle_mute),
            ui.Button(WIDTH//2 - 100, 320, 200, 50, f"Fullscreen: {'On' if self.data['fullscreen'] else 'Off'}", self.toggle_fullscreen),
            ui.Button(WIDTH//2 - 100, 450, 200, 50, "Back", lambda: self.manager.change_state(self.prev_state))
        ]
        
    def toggle_mute(self):
        self.data['mute'] = not self.data['mute']
        self.buttons[0].text = f"Mute: {'On' if self.data['mute'] else 'Off'}"
        save_manager.update_settings(self.data['volume'], self.data['mute'], self.data['fullscreen'])
        
    def toggle_fullscreen(self):
        self.data['fullscreen'] = not self.data['fullscreen']
        self.buttons[1].text = f"Fullscreen: {'On' if self.data['fullscreen'] else 'Off'}"
        save_manager.update_settings(self.data['volume'], self.data['mute'], self.data['fullscreen'])
        if self.data['fullscreen']:
            pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN | pygame.SCALED)
        else:
            pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE | pygame.SCALED)
            
    def handle_events(self, events):
        for e in events:
            for b in self.buttons:
                b.handle_event(e)
                
    def draw(self, surface):
        surface.blit(self.bg, (0, 0))
        font = assets.get_font(60, bold=True)
        title = font.render("Settings", True, BLACK)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        
        for b in self.buttons:
            b.draw(surface)
            
class HowToPlay(GameState):
    def __init__(self, manager):
        super().__init__(manager)
        self.bg = assets.generate_background(WIDTH, HEIGHT)
        self.buttons = [
            ui.Button(WIDTH//2 - 100, 600, 200, 50, "Back", lambda: self.manager.change_state(MainMenu(self.manager)))
        ]
        
    def handle_events(self, events):
        for e in events:
            for b in self.buttons:
                b.handle_event(e)
                
    def draw(self, surface):
        surface.blit(self.bg, (0,0))
        font = assets.get_font(50, bold=True)
        t = font.render("How To Play", True, BLACK)
        surface.blit(t, (WIDTH//2 - t.get_width()//2, 50))
        
        font_s = assets.get_font(24)
        texts = [
            "1. Click and drag the bird on the slingshot to aim.",
            "2. Release to launch and destroy the green targets.",
            "3. Birds:",
            "   - Red: Normal",
            "   - Dark Red: Heavy (good for stone)",
            "   - Yellow: Speed (press SPACE during flight to boost)",
            "4. Destroy all targets to win the level."
        ]
        for i, text in enumerate(texts):
            ts = font_s.render(text, True, BLACK)
            surface.blit(ts, (200, 150 + i*40))
            
        for b in self.buttons:
            b.draw(surface)
