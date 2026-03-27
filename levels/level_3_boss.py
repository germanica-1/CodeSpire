import pygame
import os
import random
import math

class Level3Boss:
    def __init__(self, screen_width, screen_height):
        # --- Boss Sprite ---
        self.image = pygame.image.load("assets/images/level_3_boss.gif").convert_alpha()
        self.image = pygame.transform.scale(self.image, (220, 220))
        self.rect = self.image.get_rect(center=(screen_width // 2, 120))

        # --- Health ---
        self.max_health = 15
        self.health = self.max_health
        self.victory = False
        self.dying = False
        self.death_finished = False
        self.death_index = 0
        self.death_speed = 100  # ms per frame
        self.last_death_update = 0
        self.death_done_time = 0

        # --- Movement ---
        self.speed = 2.5
        self.amplitude = 40
        self.angle = 0
        self.base_y = self.rect.y

        # --- Laser ---
        self.laser_frames = []
        self.load_laser_frames()
        self.laser_index = 0
        self.laser_active = False
        self.laser_timer = 0
        self.laser_delay = random.randint(120, 200)
        self.laser_rect = None
        self.current_laser_frame = None

        # --- Laser aiming & timing ---
        self.aim_x = None
        self.warning_time = 80
        self.lock_time = 40
        self.warning_timer = 0
        self.firing = False
        self.pre_fire_delay = 15
        self.laser_linger = 20

        # --- Fade-in effect ---
        self.fade_alpha = 0
        self.fade_in_speed = 4
        self.fade_done = False

        # --- Font (same as Level 2 Boss) ---
        self.font = pygame.font.Font("assets/fonts/BoldPixels.ttf", 28)
        self.name_surface = self.font.render("D'Ace", True, (255, 255, 255))

        self.screen_height = screen_height
        self.charge_flash = False

        # --- Track if laser already hit player this cycle ---
        self.laser_has_hit = False

        # --- Death animation frames ---
        self.death_frames = self.load_death_frames("assets/images/boss_dying/level_3_boss")

    # ----------------------------------------------------
    # Loaders
    # ----------------------------------------------------
    def load_laser_frames(self):
        folder = "assets/images/laserbeam_boss"
        for i in range(12):
            filename = f"frame_{i:02d}_delay-0.05s.png"
            path = os.path.join(folder, filename)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (180, 250))
                self.laser_frames.append(img)

    def load_death_frames(self, folder_path):
        """Load all death animation frames from a folder."""
        frames = []
        if os.path.exists(folder_path):
            for filename in sorted(os.listdir(folder_path)):
                if filename.endswith(".png"):
                    frame = pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()
                    frame = pygame.transform.scale(frame, (180, 180))
                    frames.append(frame)
        return frames

    # ----------------------------------------------------
    # Update
    # ----------------------------------------------------
    def update(self, player_rect):
        """Update boss movement and attack cycle."""
        if self.victory or self.death_finished:
            return

        # --- Death animation logic ---
        if self.dying:
            self.update_death_animation()
            return

        # --- Fade-in ---
        if not self.fade_done:
            self.fade_alpha = min(255, self.fade_alpha + self.fade_in_speed)
            if self.fade_alpha >= 255:
                self.fade_done = True

        # --- Movement ---
        if not self.firing:
            if player_rect.centerx > self.rect.centerx:
                self.rect.x += self.speed
            elif player_rect.centerx < self.rect.centerx:
                self.rect.x -= self.speed

        self.angle += 0.05
        self.rect.y = self.base_y + math.sin(self.angle) * self.amplitude

        # --- Attack cycle ---
        if self.fade_done:
            self.laser_timer += 1

            # Start warning
            if not self.laser_active and self.laser_timer > self.laser_delay:
                self.laser_active = True
                self.warning_timer = 0
                self.aim_x = player_rect.centerx
                self.laser_timer = 0
                self.laser_has_hit = False

            # --- Warning phase ---
            if self.laser_active and not self.firing:
                self.warning_timer += 1

                if self.warning_timer < self.warning_time - self.lock_time:
                    self.aim_x = player_rect.centerx

                if self.warning_timer == self.warning_time - self.lock_time:
                    self.locked_aim_x = self.aim_x

                self.charge_flash = self.warning_timer >= self.warning_time - self.pre_fire_delay

                if self.warning_timer >= self.warning_time:
                    self.firing = True
                    self.laser_index = 0
                    self.linger_timer = 0
                    self.aim_x = self.locked_aim_x

            # --- Firing phase ---
            if self.firing:
                self.laser_index += 0.3
                if self.laser_index >= len(self.laser_frames):
                    self.linger_timer += 1
                    if self.linger_timer > self.laser_linger:
                        self.firing = False
                        self.laser_active = False
                        self.laser_rect = None
                        self.laser_delay = random.randint(160, 250)
                    else:
                        frame = self.laser_frames[-1]
                        rotated = pygame.transform.rotate(frame, 270)
                        beam_height = self.screen_height - self.rect.bottom
                        stretched = pygame.transform.scale(rotated, (rotated.get_width(), int(beam_height)))
                        self.laser_rect = stretched.get_rect(midtop=(self.aim_x, self.rect.bottom))
                        self.current_laser_frame = stretched
                else:
                    frame = self.laser_frames[int(self.laser_index)]
                    rotated = pygame.transform.rotate(frame, 270)
                    beam_height = self.screen_height - self.rect.bottom
                    stretched = pygame.transform.scale(rotated, (rotated.get_width(), int(beam_height)))
                    self.laser_rect = stretched.get_rect(midtop=(self.aim_x, self.rect.bottom))
                    self.current_laser_frame = stretched

    # ----------------------------------------------------
    # Death logic
    # ----------------------------------------------------
    def update_death_animation(self):
        """Play the boss death animation sequence."""
        if not self.death_frames:
            self.victory = True
            return

        now = pygame.time.get_ticks()
        if now - self.last_death_update > self.death_speed:
            self.last_death_update = now
            self.death_index += 1
            if self.death_index >= len(self.death_frames):
                self.death_finished = True
                self.death_index = len(self.death_frames) - 1
                self.death_done_time = pygame.time.get_ticks()
                self.victory = True

    # ----------------------------------------------------
    # Collision
    # ----------------------------------------------------
    def check_laser_hit(self, player_rect):
        """Return True if player hit by laser (only once per shot)."""
        if self.firing and self.laser_rect and not self.laser_has_hit:
            if self.laser_rect.colliderect(player_rect):
                self.laser_has_hit = True
                return True
        return False

    # ----------------------------------------------------
    # Draw
    # ----------------------------------------------------
    def draw(self, screen):
        """Draw boss, laser, and UI."""
        # --- Death animation ---
        if self.dying and self.death_frames:
            screen.blit(self.death_frames[self.death_index], self.rect)
            return

        # --- Normal state ---
        boss_image = self.image.copy()
        boss_image.set_alpha(self.fade_alpha)
        screen.blit(boss_image, self.rect)

        # --- Warning line ---
        if self.fade_done and self.laser_active and not self.firing:
            color = (255, 40, 40) if self.charge_flash else (255, 150, 150)
            pygame.draw.line(
                screen, color,
                (self.aim_x, self.rect.bottom),
                (self.aim_x, self.screen_height),
                6
            )

        # --- Laser beam ---
        if self.fade_done and self.firing and self.laser_rect:
            screen.blit(self.current_laser_frame, self.laser_rect)

        # --- Health bar ---
        if self.fade_alpha > 30 and not self.dying:
            bar_width, bar_height = 300, 20
            x = (screen.get_width() - bar_width) // 2
            y = 70

            bg_surface = pygame.Surface((bar_width, bar_height))
            bg_surface.fill((80, 0, 0))
            bg_surface.set_alpha(self.fade_alpha)
            screen.blit(bg_surface, (x, y))

            fill = (self.health / self.max_health) * bar_width
            fill_surface = pygame.Surface((fill, bar_height))
            fill_surface.fill((255, 0, 0))
            fill_surface.set_alpha(self.fade_alpha)
            screen.blit(fill_surface, (x, y))

            pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 2)

            # Name text
            name_surface = self.name_surface.copy()
            name_surface.set_alpha(self.fade_alpha)
            name_rect = name_surface.get_rect(center=(screen.get_width() // 2, y - 25))
            screen.blit(name_surface, name_rect)

    # ----------------------------------------------------
    # Damage
    # ----------------------------------------------------
    def hit(self):
        """Damage the boss and check for defeat."""
        if self.dying or self.victory:
            return False

        self.health -= 1
        if self.health <= 0:
            self.health = 0
            self.dying = True
            self.last_death_update = pygame.time.get_ticks()
            self.firing = False
            self.laser_active = False
            self.laser_rect = None
            return True
        return False
