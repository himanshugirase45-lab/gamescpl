import pygame
import sys
from config import *
import save_manager

pygame.init()
pygame.display.set_caption("SlingShot Adventure")

# Load settings
save_data = save_manager.load_save()
flags = pygame.SCALED
if save_data['settings']['fullscreen']:
    flags |= pygame.FULLSCREEN
else:
    flags |= pygame.RESIZABLE
    
screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
clock = pygame.time.Clock()

class GameManager:
    def __init__(self):
        from state_machine import MainMenu
        self.state = MainMenu(self)
        self.running = True
        
    def change_state(self, new_state):
        self.state = new_state
        
    def quit(self):
        self.running = False
        
    def run(self):
        # We need to monkey patch the imports in state_machine since we separated menus.py
        import state_machine
        import menus
        state_machine.PauseMenu = menus.PauseMenu
        state_machine.VictoryScreen = menus.VictoryScreen
        state_machine.DefeatScreen = menus.DefeatScreen
        state_machine.SettingsMenu = menus.SettingsMenu
        state_machine.HowToPlay = menus.HowToPlay
        
        while self.running:
            dt = clock.tick(FPS) / 1000.0
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    self.quit()
                    
            self.state.handle_events(events)
            self.state.update(dt)
            self.state.draw(screen)
            pygame.display.flip()

if __name__ == "__main__":
    game = GameManager()
    game.run()
    pygame.quit()
    sys.exit()
