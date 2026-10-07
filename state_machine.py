import pygame
import pymunk
import math
import random
from config import *
import assets
import ui
from entities import Bird, Block, Target
from physics import create_bird, create_block, create_enemy, create_ground
from level import levels_data
import save_manager

class GameState:
    def __init__(self, manager):
        self.manager = manager
    def handle_events(self, events): pass
    def update(self, dt): pass
    def draw(self, surface): pass

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-100, 100)
        self.vy = random.uniform(-100, 50)
        self.life = 1.0
        self.color = color
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += GRAVITY[1] * 0.5 * dt
        self.life -= dt * 2.0
    def draw(self, surface):
        if self.life > 0:
            alpha = int(255 * self.life)
            s = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (3,3), 3)
            surface.blit(s, (int(self.x), int(self.y)))

class FloatingText:
    def __init__(self, x, y, text, color=(255,255,255)):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = 1.5
    def update(self, dt):
        self.y -= 30 * dt
        self.life -= dt
    def draw(self, surface):
        if self.life > 0:
            font = assets.get_font(28, bold=True)
            t = font.render(self.text, True, self.color)
            t.set_alpha(int(255 * min(1.0, self.life)))
            surface.blit(t, (int(self.x), int(self.y)))

class MainMenu(GameState):
    def __init__(self, manager):
        super().__init__(manager)
        self.bg = assets.generate_background(WIDTH, HEIGHT)
        self.buttons = [
            ui.Button(WIDTH//2 - 100, 300, 200, 60, "Play", lambda: self.manager.change_state(LevelSelect(self.manager))),
            ui.Button(WIDTH//2 - 100, 380, 200, 60, "How to Play", lambda: self.manager.change_state(HowToPlay(self.manager))),
            ui.Button(WIDTH//2 - 100, 460, 200, 60, "Settings", lambda: self.manager.change_state(SettingsMenu(self.manager, self))),
            ui.Button(WIDTH//2 - 100, 540, 200, 60, "Exit", lambda: self.manager.quit())
        ]
        
    def handle_events(self, events):
        for e in events:
            for b in self.buttons:
                b.handle_event(e)
                
    def draw(self, surface):
        surface.blit(self.bg, (0, 0))
        font = assets.get_font(90, bold=True)
        title = font.render("SlingShot Adventure", True, (255, 215, 0))
        shadow = font.render("SlingShot Adventure", True, (150, 50, 0))
        rect = title.get_rect(center=(WIDTH//2, 160))
        surface.blit(shadow, (rect.x+6, rect.y+6))
        surface.blit(title, rect)
        for b in self.buttons:
            b.draw(surface)

class LevelSelect(GameState):
    def __init__(self, manager):
        super().__init__(manager)
        self.bg = assets.generate_background(WIDTH, HEIGHT)
        self.cards = []
        save_data = save_manager.load_save()
        for i in range(1, 6):
            data = save_data['levels'].get(str(i), {})
            def make_action(lvl=i):
                return lambda: self.manager.change_state(PlayingState(self.manager, lvl))
            card = ui.LevelCard(140 + (i-1)*210, 300, 170, 220, i, data, make_action())
            self.cards.append(card)
        self.back_btn = ui.Button(20, 20, 120, 50, "Back", lambda: self.manager.change_state(MainMenu(self.manager)))
        
    def handle_events(self, events):
        for e in events:
            for c in self.cards: c.handle_event(e)
            self.back_btn.handle_event(e)
            
    def draw(self, surface):
        surface.blit(self.bg, (0, 0))
        font = assets.get_font(70, bold=True)
        title = font.render("Select Level", True, WHITE)
        shadow = font.render("Select Level", True, (0, 100, 150))
        t_rect = title.get_rect(center=(WIDTH//2, 120))
        surface.blit(shadow, (t_rect.x+4, t_rect.y+4))
        surface.blit(title, t_rect)
        for c in self.cards: c.draw(surface)
        self.back_btn.draw(surface)

class PlayingState(GameState):
    def __init__(self, manager, level_id):
        super().__init__(manager)
        self.level_id = level_id
        self.level_data = levels_data[level_id]
        
        self.space = pymunk.Space()
        self.space.gravity = GRAVITY
        
        # New collision handler for pymunk 7+ (on_collision)
        self.space.on_collision(1, 2, post_solve=self.collision_handler)
        self.space.on_collision(1, 3, post_solve=self.collision_handler)
        self.space.on_collision(2, 3, post_solve=self.collision_handler)
        self.space.on_collision(2, 2, post_solve=self.collision_handler)
        self.space.on_collision(1, 4, post_solve=self.collision_handler)
        
        self.bg = assets.generate_background(WIDTH, HEIGHT)
        self.slingshot_front = assets.draw_slingshot_front()
        self.slingshot_back = assets.draw_slingshot_back()
        
        create_ground(self.space, WIDTH, HEIGHT)
        
        self.entities = []
        self.blocks = []
        self.targets = []
        self.particles = []
        self.floating_texts = []
        self.screen_shake = 0.0
        
        for b in self.level_data["blocks"]:
            body, shape = create_block(self.space, b["x"], b["y"], b["w"], b["h"], b["type"])
            block = Block(body, shape, b["w"], b["h"], b["type"])
            self.entities.append(block)
            self.blocks.append(block)
            
        for t in self.level_data["targets"]:
            body, shape = create_enemy(self.space, t["x"], t["y"], t["r"])
            target = Target(body, shape, t["r"])
            self.entities.append(target)
            self.targets.append(target)
            
        self.birds_queue = self.level_data["birds"].copy()
        self.current_bird = None
        self.load_next_bird()
        
        self.dragging = False
        self.score = 0
        self.game_over = False
        
        self.hud_pause = ui.Button(WIDTH - 150, 20, 120, 50, "Pause", lambda: self.manager.change_state(PauseMenu(self.manager, self)))
        self.hud_restart = ui.Button(WIDTH - 290, 20, 120, 50, "Restart", lambda: self.manager.change_state(PlayingState(self.manager, self.level_id)))
        self.hud_physics = ui.Button(WIDTH - 430, 20, 120, 50, "Physics", self.toggle_physics)
        
        self.physics_view = False
        self.launch_time = 0
        self.initial_velocity = (0,0)
        self.initial_angle = 0
        self.settle_timer = 0
        
    def toggle_physics(self):
        self.physics_view = not self.physics_view
        
    def collision_handler(self, arbiter, space, data):
        impulse = arbiter.total_impulse
        impact = impulse.length
        if impact > 1000:
            shape_a, shape_b = arbiter.shapes
            damage = impact / 150.0
            for entity in self.entities:
                if entity.shape == shape_a or entity.shape == shape_b:
                    if hasattr(entity, 'hp'):
                        entity.hp -= damage
                        # Create particles on heavy hits
                        if impact > 3000:
                            for _ in range(5):
                                self.particles.append(Particle(entity.body.position.x, entity.body.position.y, (200, 200, 200)))
                            self.screen_shake = min(20.0, self.screen_shake + impact / 1000.0)
                            
                        if entity.hp <= 0 and not entity.dead:
                            entity.dead = True
                            pts = 1000 if isinstance(entity, Target) else 50
                            self.score += pts
                            self.floating_texts.append(FloatingText(entity.body.position.x, entity.body.position.y, f"+{pts}", (255, 255, 100)))
                            # Death particles
                            for _ in range(15):
                                self.particles.append(Particle(entity.body.position.x, entity.body.position.y, (150, 100, 50) if isinstance(entity, Block) else (50, 200, 50)))
        
    def load_next_bird(self):
        if self.birds_queue:
            b_type = self.birds_queue.pop(0)
            body, shape = create_bird(self.space, SLING_X, SLING_Y - 30, b_type)
            self.current_bird = Bird(body, shape, b_type)
            self.current_bird.body.body_type = pymunk.Body.KINEMATIC
            self.entities.append(self.current_bird)
        else:
            self.current_bird = None
            
    def process_deaths(self):
        to_remove = []
        for e in self.entities:
            if e.dead:
                to_remove.append(e)
                try:
                    self.space.remove(e.body, e.shape)
                except KeyError:
                    pass
                if e in self.blocks: self.blocks.remove(e)
                if e in self.targets: self.targets.remove(e)
        for e in to_remove:
            self.entities.remove(e)
            
    def all_settled(self):
        for e in self.entities:
            if not getattr(e, 'launched', True): continue
            if e.body.body_type == pymunk.Body.DYNAMIC:
                if e.body.velocity.length > 5 or abs(e.body.angular_velocity) > 0.5:
                    return False
        return True
        
    def handle_events(self, events):
        for e in events:
            self.hud_pause.handle_event(e)
            self.hud_restart.handle_event(e)
            self.hud_physics.handle_event(e)
            
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_SPACE and self.current_bird and self.current_bird.launched:
                    if self.current_bird.type == "speed":
                        v = self.current_bird.body.velocity
                        self.current_bird.body.velocity = v * 1.8
                        self.current_bird.type = "normal"
                        self.screen_shake += 10.0
                        
            if not self.current_bird or self.current_bird.launched or self.game_over:
                continue
                
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = pygame.mouse.get_pos()
                if math.hypot(mx - SLING_X, my - (SLING_Y - 30)) < 60:
                    self.dragging = True
                    
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                if self.dragging:
                    self.dragging = False
                    self.current_bird.launched = True
                    self.current_bird.body.body_type = pymunk.Body.DYNAMIC
                    self.current_bird.body.mass = self.current_bird.original_mass
                    self.current_bird.body.moment = self.current_bird.original_moment
                    
                    dx = SLING_X - self.current_bird.body.position.x
                    dy = SLING_Y - 30 - self.current_bird.body.position.y
                    
                    self.current_bird.body.velocity = (dx * LAUNCH_POWER_MULTIPLIER, dy * LAUNCH_POWER_MULTIPLIER)
                    
                    self.launch_time = pygame.time.get_ticks()
                    vel = self.current_bird.body.velocity
                    self.initial_velocity = (vel.x, vel.y)
                    self.initial_angle = math.degrees(math.atan2(-vel.y, vel.x))
                    
            elif e.type == pygame.MOUSEMOTION:
                if self.dragging:
                    mx, my = e.pos
                    dx = mx - SLING_X
                    dy = my - (SLING_Y - 30)
                    dist = math.hypot(dx, dy)
                    if dist > SLING_MAX_PULL:
                        angle = math.atan2(dy, dx)
                        mx = SLING_X + math.cos(angle) * SLING_MAX_PULL
                        my = (SLING_Y - 30) + math.sin(angle) * SLING_MAX_PULL
                    self.current_bird.body.position = (mx, my)
                    
    def update(self, dt):
        if self.screen_shake > 0:
            self.screen_shake -= dt * 30
            if self.screen_shake < 0: self.screen_shake = 0
            
        for p in self.particles: p.update(dt)
        self.particles = [p for p in self.particles if p.life > 0]
        
        for ft in self.floating_texts: ft.update(dt)
        self.floating_texts = [ft for ft in self.floating_texts if ft.life > 0]
        
        if not self.game_over:
            for _ in range(PHYSICS_STEPS):
                self.space.step(dt / PHYSICS_STEPS)
            self.process_deaths()
            
            if not self.current_bird or self.current_bird.launched:
                if self.all_settled():
                    self.settle_timer += dt
                    if self.settle_timer > 1.5:
                        if len(self.targets) == 0:
                            unused = len(self.birds_queue)
                            self.score += unused * 2000
                            stars = 3 if unused >= 2 else (2 if unused == 1 else 1)
                            save_manager.unlock_level(self.level_id + 1)
                            save_manager.update_score(self.level_id, self.score, stars)
                            self.manager.change_state(VictoryScreen(self.manager, self.score, stars, unused, self.level_id))
                        elif len(self.birds_queue) == 0:
                            self.manager.change_state(DefeatScreen(self.manager, self.level_id))
                        else:
                            self.load_next_bird()
                            self.settle_timer = 0
                else:
                    self.settle_timer = 0
                    
            for e in self.entities:
                if e.body.position.y > HEIGHT + 100 or e.body.position.x > WIDTH + 500 or e.body.position.x < -500:
                    e.dead = True
                    
    def draw_trajectory(self, surface):
        if self.current_bird and not self.current_bird.launched and self.dragging:
            dx = SLING_X - self.current_bird.body.position.x
            dy = SLING_Y - 30 - self.current_bird.body.position.y
            
            v_x = dx * LAUNCH_POWER_MULTIPLIER
            v_y = dy * LAUNCH_POWER_MULTIPLIER
            
            t = 0
            x = self.current_bird.body.position.x
            y = self.current_bird.body.position.y
            
            for i in range(15):
                t += 0.15
                px = x + v_x * t
                py = y + v_y * t + 0.5 * GRAVITY[1] * t * t
                pygame.draw.circle(surface, (255,255,255,150), (int(px), int(py)), max(2, 6 - i*0.2))
                
    def draw(self, surface):
        shake_x = random.uniform(-self.screen_shake, self.screen_shake)
        shake_y = random.uniform(-self.screen_shake, self.screen_shake)
        
        main_surface = pygame.Surface((WIDTH, HEIGHT))
        main_surface.blit(self.bg, (0, 0))
        
        # Slingshot back
        main_surface.blit(self.slingshot_back, (SLING_X - 25, SLING_Y - 60))
        
        # Rubber band back (to pouch)
        if self.current_bird and not self.current_bird.launched and self.dragging:
            bx, by = int(self.current_bird.body.position.x), int(self.current_bird.body.position.y)
            # Band to left side of pouch
            pygame.draw.line(main_surface, (50,30,10), (SLING_X+15, SLING_Y-50), (bx + 15, by), 6)
                             
        for e in self.entities:
            e.draw(main_surface)
            
        # Pouch and Rubber band front
        if self.current_bird and not self.current_bird.launched and self.dragging:
            bx, by = int(self.current_bird.body.position.x), int(self.current_bird.body.position.y)
            # Pouch (leather strip wrapping the bird)
            pouch_rect = pygame.Rect(bx - 20, by - 10, 40, 20)
            pygame.draw.rect(main_surface, (139, 69, 19), pouch_rect, border_radius=8)
            pygame.draw.rect(main_surface, (80, 40, 10), pouch_rect, 2, border_radius=8)
            
            # Band to right side of pouch
            pygame.draw.line(main_surface, (80,40,15), (SLING_X-15, SLING_Y-45), (bx - 15, by), 8)
                             
        main_surface.blit(self.slingshot_front, (SLING_X - 25, SLING_Y - 60))
        self.draw_trajectory(main_surface)
        
        for p in self.particles: p.draw(main_surface)
        for ft in self.floating_texts: ft.draw(main_surface)
        
        # Apply shake
        surface.blit(main_surface, (shake_x, shake_y))
        
        # HUD Layer
        font = assets.get_font(32, bold=True)
        score_t = font.render(f"SCORE: {self.score}", True, WHITE)
        score_shadow = font.render(f"SCORE: {self.score}", True, BLACK)
        surface.blit(score_shadow, (22, 22))
        surface.blit(score_t, (20, 20))
        
        lvl_t = font.render(self.level_data["name"].upper(), True, WHITE)
        lvl_shadow = font.render(self.level_data["name"].upper(), True, BLACK)
        surface.blit(lvl_shadow, (22, 62))
        surface.blit(lvl_t, (20, 60))
        
        # Draw upcoming birds queue
        for i, b_type in enumerate(self.birds_queue):
            pygame.draw.circle(surface, (150, 150, 150), (50 + i*50, HEIGHT - 50), 20)
            bird_surf = assets.draw_bird(b_type)
            small_bird = pygame.transform.scale(bird_surf, (30, 30))
            surface.blit(small_bird, (35 + i*50, HEIGHT - 65))
            
        self.hud_pause.draw(surface)
        self.hud_restart.draw(surface)
        self.hud_physics.draw(surface)
        
        if self.physics_view:
            pygame.draw.rect(surface, (0,0,0,180), (20, 120, 320, 160), border_radius=10)
            pv_font = assets.get_font(20)
            surf1 = pv_font.render(f"Angle: {self.initial_angle:.1f} deg", True, WHITE)
            v_mag = math.hypot(*self.initial_velocity) / PIXELS_PER_METER
            surf2 = pv_font.render(f"Init Speed: {v_mag:.2f} m/s", True, WHITE)
            curr_t = (pygame.time.get_ticks() - self.launch_time)/1000.0 if (self.current_bird and self.current_bird.launched) else 0
            surf3 = pv_font.render(f"Time: {curr_t:.2f} s", True, WHITE)
            surf4 = pv_font.render(f"Gravity: {GRAVITY[1]/PIXELS_PER_METER:.1f} m/s²", True, WHITE)
            surface.blit(surf1, (35, 130))
            surface.blit(surf2, (35, 165))
            surface.blit(surf3, (35, 200))
            surface.blit(surf4, (35, 235))
