import pygame
import os
import random

class Level1Boss:
    def __init__(self, screen_width, screen_height):
        # Load boss image
        self.image = pygame.image.load("assets/images/level_1_boss.gif").convert_alpha()
        self.image = pygame.transform.scale(self.image, (200, 200))
        self.rect = self.image.get_rect(center=(screen_width // 2, -150))

        # Movement
        self.speed_y = 3
        self.follow_speed = 6
        self.target_y = 100
        self.screen_width = screen_width
        self.alive = True
        self.dying = False
        self.victory = False

        # Movement states
        self.original_x = self.rect.centerx
        self.following = True
        self.returning = False
        self.follow_duration = 4000
        self.last_follow_switch = pygame.time.get_ticks()

        # Health
        self.max_health = 4
        self.health = self.max_health

        # Shooting
        self.bullet_image = pygame.image.load("assets/images/enemyBullet.png").convert_alpha()
        self.bullet_image = pygame.transform.scale(self.bullet_image, (30, 30))
        self.bullets = []
        self.shoot_cooldown = 2500
        self.last_shot_time = pygame.time.get_ticks()
        self.paused_until = 0

        # Font and fade
        self.font = pygame.font.Font("assets/fonts/BoldPixels.ttf", 28)
        self.name_surface = self.font.render("D’Aragon", True, (255, 255, 255))
        self.fade_alpha = 0
        self.fade_in_speed = 3
        self.fade_done = False

        # --- Sound Effects ---
        try:
            self.shoot_sound = pygame.mixer.Sound("assets/sounds/player_shoot_1.mp3")
        except:
            self.shoot_sound = None

        # --- Boss Passive Sound (looping background sound) ---
        try:
            self.boss_passive_sound = pygame.mixer.Sound("assets/sounds/boss_sfx/level_1_boss/level_1_boss_passive.mp3")
            self.boss_passive_sound.set_volume(0.4)
        except:
            self.boss_passive_sound = None

        self.sound_playing = False  # Track if the looping sound is active
        self.sound_paused = False   # Track if it’s temporarily paused

        # Death animation
        self.death_frames = self.load_death_frames("assets/images/boss_dying/level_1_boss")
        self.death_index = 0
        self.death_speed = 100
        self.last_death_update = 0
        self.death_finished = False
        self.death_done_time = 0

        # Bullet speeds
        self.bullet_speeds = {}

    # ----------------------------
    #       SOUND CONTROLS
    # ----------------------------
    def play_boss_sound(self):
        """Play looping boss passive sound."""
        if self.boss_passive_sound and not self.sound_playing:
            self.boss_passive_sound.play(loops=-1)
            self.sound_playing = True
            self.sound_paused = False

    def pause_boss_sound(self):
        """Temporarily pause the boss sound."""
        if self.boss_passive_sound and self.sound_playing and not self.sound_paused:
            pygame.mixer.pause()
            self.sound_paused = True

    def resume_boss_sound(self):
        """Resume the boss sound if paused."""
        if self.boss_passive_sound and self.sound_paused:
            pygame.mixer.unpause()
            self.sound_paused = False

    def stop_boss_sound(self):
        """Completely stop the looping boss sound."""
        if self.boss_passive_sound and self.sound_playing:
            self.boss_passive_sound.stop()
            self.sound_playing = False
            self.sound_paused = False

    # ----------------------------
    #     DEATH ANIMATION LOADER
    # ----------------------------
    def load_death_frames(self, folder_path):
        """Load death animation frames from a folder."""
        frames = []
        if not os.path.exists(folder_path):
            print(f"[WARNING] Boss death animation folder not found: {folder_path}")
            return frames

        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith(".png"):
                frame = pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()
                frame = pygame.transform.scale(frame, (200, 200))
                frames.append(frame)
        return frames

    # ----------------------------
    #       SHOOTING CONTROL
    # ----------------------------
    def reset_shooting_rate(self):
        """Pause boss shooting and sound for 3 seconds after question."""
        self.shoot_cooldown = 2000
        self.paused_until = pygame.time.get_ticks() + 3000
        self.pause_boss_sound()  # Pause the looping boss sound during questions

    def update(self, player_rect):
        if self.victory:
            return

        # --- Handle Death Animation ---
        if self.dying:
            self.update_death_animation()
            return

        if not self.alive:
            return

        # --- Move down into position ---
        if self.rect.y < self.target_y:
            self.rect.y += self.speed_y
            return

        # --- Play looping boss sound once on entry ---
        if not self.sound_playing:
            self.play_boss_sound()

        # --- Resume boss sound if pause ended ---
        if pygame.time.get_ticks() > self.paused_until and self.sound_paused:
            self.resume_boss_sound()

        # --- Fade-in bar and name ---
        if not self.fade_done:
            self.fade_alpha = min(255, self.fade_alpha + self.fade_in_speed)
            if self.fade_alpha >= 255:
                self.fade_done = True

        # --- Movement switching ---
        now = pygame.time.get_ticks()
        if now - self.last_follow_switch > self.follow_duration:
            self.following = not self.following
            self.returning = not self.returning
            self.last_follow_switch = now

        # --- Follow or return ---
        if self.following:
            diff = player_rect.centerx - self.rect.centerx
            self.rect.x += int(diff * 0.05)
        elif self.returning:
            diff = self.original_x - self.rect.centerx
            self.rect.x += int(diff * 0.03)

        # Keep within bounds
        self.rect.x = max(0, min(self.rect.x, self.screen_width - self.rect.width))

        # --- Shooting ---
        current_time = pygame.time.get_ticks()
        can_shoot = current_time >= self.paused_until
        if can_shoot and current_time - self.last_shot_time > self.shoot_cooldown:
            if self.health > self.max_health / 2:
                self.shoot_single()
            else:
                self.shoot_double()
            self.last_shot_time = current_time
            self.shoot_cooldown = max(800, self.shoot_cooldown - 100)

        # --- Move bullets ---
        for bullet_rect in self.bullets[:]:
            dx, dy = self.bullet_speeds.get(id(bullet_rect), (0, 10))
            bullet_rect.x += dx
            bullet_rect.y += dy
            if bullet_rect.y > 600 or bullet_rect.x < 0 or bullet_rect.x > self.screen_width:
                self.bullets.remove(bullet_rect)
                self.bullet_speeds.pop(id(bullet_rect), None)

    # ----------------------------
    #       SHOOT METHODS
    # ----------------------------
    def shoot_single(self):
        """Shoot one bullet straight down."""
        bullet_rect = self.bullet_image.get_rect(center=(self.rect.centerx, self.rect.bottom))
        self.bullets.append(bullet_rect)
        self.bullet_speeds[id(bullet_rect)] = (0, 10)
        if self.shoot_sound:
            self.shoot_sound.play()

    def shoot_double(self):
        """Shoot two bullets slightly angled outward."""
        offset = 40
        spread_angle = 4
        left_bullet = self.bullet_image.get_rect(center=(self.rect.centerx - offset, self.rect.bottom))
        right_bullet = self.bullet_image.get_rect(center=(self.rect.centerx + offset, self.rect.bottom))
        self.bullets.extend([left_bullet, right_bullet])
        self.bullet_speeds[id(left_bullet)] = (-spread_angle, 10)
        self.bullet_speeds[id(right_bullet)] = (spread_angle, 10)
        if self.shoot_sound:
            self.shoot_sound.play()

    # ----------------------------
    #      DEATH ANIMATION
    # ----------------------------
    def update_death_animation(self):
        """Handle boss death animation and sound stop."""
        if self.death_finished:
            if self.death_done_time == 0:
                self.death_done_time = pygame.time.get_ticks()
                self.stop_boss_sound()  # stop looping sound
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

    # ----------------------------
    #          DRAW
    # ----------------------------
    def draw(self, screen):
        """Draw boss, health bar, name, and bullets."""
        if self.dying:
            if self.death_frames:
                screen.blit(self.death_frames[self.death_index], self.rect)
            return

        if self.alive:
            screen.blit(self.image, self.rect)

            if self.fade_alpha > 0:
                alpha = self.fade_alpha
                name_surface = self.name_surface.copy()
                name_surface.set_alpha(alpha)

                # Health bar
                bar_width = 300
                bar_height = 20
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

                # Boss name above bar
                name_rect = name_surface.get_rect(center=(self.screen_width // 2, bar_y - 25))
                screen.blit(name_surface, name_rect)

        # Draw bullets
        for bullet_rect in self.bullets:
            screen.blit(self.bullet_image, bullet_rect)

    # ----------------------------
    #         DAMAGE HANDLER
    # ----------------------------
    def hit(self):
        """Handle boss taking damage."""
        self.health -= 1
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.victory = True
            self.dying = True
            self.last_death_update = pygame.time.get_ticks()
            return True
        return False
