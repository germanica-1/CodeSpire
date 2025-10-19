import pygame
import os
import random
import math
from entities.bugs_level_2 import Bug_Level_2


class Level2Boss:
    def __init__(self, screen_width, screen_height):
        # --- Base sprite ---
        self.image = pygame.image.load("assets/images/level_2_boss.gif").convert_alpha()
        self.image = pygame.transform.scale(self.image, (200, 200))
        self.rect = self.image.get_rect(center=(screen_width // 2, -150))

        # --- Movement ---
        self.speed_y = 3
        self.follow_speed = 6
        self.target_y = 120
        self.screen_width = screen_width
        self.alive = True
        self.dying = False
        self.victory = False

        # --- Movement pattern ---
        self.base_x = self.rect.centerx
        self.wave_angle = 0
        self.wave_speed = 0.03
        self.wave_amplitude = 60

        # --- Health ---
        self.max_health = 8
        self.health = self.max_health

        # --- Shooting setup ---
        self.bullet_image = pygame.image.load("assets/images/enemyBullet.png").convert_alpha()
        self.bullet_image = pygame.transform.scale(self.bullet_image, (28, 28))
        self.bullets = []
        self.bullet_speeds = {}
        self.shoot_cooldown = 2200
        self.last_shot_time = pygame.time.get_ticks()
        self.paused_until = 0

        # --- Minions ---
        self.minions = []
        self.last_minion_spawn = 0
        self.minion_spawn_cooldown = 50000  # every 10s

        # --- Name ---
        self.font = pygame.font.Font("assets/fonts/BoldPixels.ttf", 28)
        self.name_surface = self.font.render("D’Aragon", True, (255, 255, 255))
        self.fade_alpha = 0
        self.fade_in_speed = 3
        self.fade_done = False

        # --- Sound Effects ---
        try:
            self.shoot_sound = pygame.mixer.Sound("assets/sounds/player_shoot_1.mp3")
            self.shoot_sound.set_volume(0.4)
        except:
            self.shoot_sound = None

        try:
            self.boss_passive_sound = pygame.mixer.Sound(
                "assets/sounds/boss_sfx/level_1_boss/level_1_boss_passive.mp3"
            )
            self.boss_passive_sound.set_volume(0.4)
        except:
            self.boss_passive_sound = None

        self.sound_playing = False

        # --- Death animation ---
        self.death_frames = self.load_frames("assets/images/boss_dying/level_2_boss")
        self.death_index = 0
        self.death_speed = 100
        self.last_death_update = 0
        self.death_finished = False
        self.death_done_time = 0

    # --------------------------
    #  Frame loaders
    # --------------------------
    def load_frames(self, folder_path):
        frames = []
        if os.path.exists(folder_path):
            for filename in sorted(os.listdir(folder_path)):
                if filename.endswith(".png"):
                    frame = pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()
                    frame = pygame.transform.scale(frame, (200, 200))
                    frames.append(frame)
        return frames

    # --------------------------
    #  Sound control
    # --------------------------
    def play_boss_sound(self):
        if self.boss_passive_sound and not self.sound_playing:
            self.boss_passive_sound.play(loops=-1)
            self.sound_playing = True

    def stop_boss_sound(self):
        if self.boss_passive_sound and self.sound_playing:
            self.boss_passive_sound.stop()
            self.sound_playing = False

    # --------------------------
    #  Shooting
    # --------------------------
    def shoot(self):
        """Complex shooting pattern — increases in difficulty as HP lowers."""
        pattern = 1
        if self.health <= self.max_health // 2:
            pattern = 2
        if self.health <= self.max_health // 3:
            pattern = 3

        if pattern == 1:
            # Basic downward bullet
            bullet_rect = self.bullet_image.get_rect(center=(self.rect.centerx, self.rect.bottom))
            self.bullets.append(bullet_rect)
            self.bullet_speeds[id(bullet_rect)] = (0, 9)
        elif pattern == 2:
            # Spread shot
            angles = [-5, 0, 5]
            for a in angles:
                bullet_rect = self.bullet_image.get_rect(center=(self.rect.centerx, self.rect.bottom))
                self.bullets.append(bullet_rect)
                self.bullet_speeds[id(bullet_rect)] = (a, 10)
        elif pattern == 3:
            # Spiral spread pattern
            for angle in range(-15, 20, 10):
                bullet_rect = self.bullet_image.get_rect(center=(self.rect.centerx, self.rect.bottom))
                self.bullets.append(bullet_rect)
                self.bullet_speeds[id(bullet_rect)] = (angle / 3, 12)

        if self.shoot_sound:
            self.shoot_sound.play()

    def reset_shooting_rate(self):
        """Pause boss for 3 seconds after a question."""
        self.paused_until = pygame.time.get_ticks() + 3000

    # --------------------------
    #  Update + draw
    # --------------------------
    def update(self, player_rect):
        if self.victory:
            return
        if self.dying:
            self.update_death_animation()
            return

        if not self.alive:
            return

        # Entrance phase
        if self.rect.y < self.target_y:
            self.rect.y += self.speed_y
            return

        # Start passive loop sound
        if not self.sound_playing:
            self.play_boss_sound()

        # Fade-in effect
        if not self.fade_done:
            self.fade_alpha = min(255, self.fade_alpha + self.fade_in_speed)
            if self.fade_alpha >= 255:
                self.fade_done = True

        # --- FOLLOW PLAYER MOVEMENT ---
        # Smoothly follow player's x position
        player_x = player_rect.centerx
        direction = player_x - self.rect.centerx
        self.rect.centerx += int(direction * 0.05)  # smaller value = smoother tracking
        self.rect.centerx = max(100, min(self.rect.centerx, self.screen_width - 100))

        # Add slight vertical sway for realism
        self.wave_angle += self.wave_speed
        self.rect.y = self.target_y + int(math.sin(self.wave_angle * 2) * 5)

        # --- Shooting control ---
        now = pygame.time.get_ticks()
        if now > self.paused_until and now - self.last_shot_time > self.shoot_cooldown:
            self.shoot()
            self.last_shot_time = now
            self.shoot_cooldown = max(600, self.shoot_cooldown - 50)  # faster over time

        # --- Move bullets ---
        for bullet_rect in self.bullets[:]:
            dx, dy = self.bullet_speeds.get(id(bullet_rect), (0, 10))
            bullet_rect.x += dx
            bullet_rect.y += dy
            if bullet_rect.y > 600 or bullet_rect.x < 0 or bullet_rect.x > self.screen_width:
                self.bullets.remove(bullet_rect)
                self.bullet_speeds.pop(id(bullet_rect), None)

        # --- Minion spawning ---
        if now - self.last_minion_spawn > self.minion_spawn_cooldown:
            self.spawn_minions()
            self.last_minion_spawn = now
            if self.health <= self.max_health // 2:
                self.minion_spawn_cooldown = 8000
            if self.health <= self.max_health // 3:
                self.minion_spawn_cooldown = 6000

        # --- Update minions ---
        for m in self.minions[:]:
            m.update()
            if m.rect.top > 700:
                self.minions.remove(m)

    # --------------------------
    #  Minions
    # --------------------------
    def spawn_minions(self):
        """Spawn a small number of additional bugs from Level 2."""
        count = random.randint(2, 4)  # fewer minions, max 4
        for _ in range(count):
            x = random.randint(150, self.screen_width - 150)
            y = random.randint(-150, -50)
            minion = Bug_Level_2(x, y)
            self.minions.append(minion)


    # --------------------------
    #  Death
    # --------------------------
    def update_death_animation(self):
        if self.death_finished:
            if self.death_done_time == 0:
                self.death_done_time = pygame.time.get_ticks()
                self.stop_boss_sound()
            elif pygame.time.get_ticks() - self.death_done_time > 3000:
                self.victory = True
            return

        now = pygame.time.get_ticks()
        if now - self.last_death_update > self.death_speed:
            self.last_death_update = now
            self.death_index += 1
            if self.death_index >= len(self.death_frames):
                self.death_finished = True
                self.death_index = len(self.death_frames) - 1

    # --------------------------
    #  Draw
    # --------------------------
    def draw(self, screen):
        if self.dying and self.death_frames:
            screen.blit(self.death_frames[self.death_index], self.rect)
            return

        screen.blit(self.image, self.rect)

        # Health bar + name
        if self.fade_alpha > 0:
            alpha = self.fade_alpha
            bar_width, bar_height = 300, 20
            bar_x = (self.screen_width - bar_width) // 2
            bar_y = 70

            bg_surface = pygame.Surface((bar_width, bar_height))
            bg_surface.fill((80, 0, 0))
            bg_surface.set_alpha(alpha)
            screen.blit(bg_surface, (bar_x, bar_y))

            current_width = int(bar_width * (self.health / self.max_health))
            fill_surface = pygame.Surface((current_width, bar_height))
            fill_surface.fill((255, 0, 0))
            fill_surface.set_alpha(alpha)
            screen.blit(fill_surface, (bar_x, bar_y))
            pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

            name_surface = self.name_surface.copy()
            name_surface.set_alpha(alpha)
            name_rect = name_surface.get_rect(center=(self.screen_width // 2, bar_y - 25))
            screen.blit(name_surface, name_rect)

        # Draw bullets
        for bullet_rect in self.bullets:
            screen.blit(self.bullet_image, bullet_rect)

        # Draw minions
        for m in self.minions:
            m.draw(screen)

    # --------------------------
    #  Damage
    # --------------------------
    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.dying = True
            self.last_death_update = pygame.time.get_ticks()
            return True
        return False
