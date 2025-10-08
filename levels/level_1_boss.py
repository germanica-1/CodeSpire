import pygame
import os
import random
import time

class Level1Boss:
    def __init__(self, screen_width, screen_height):
        # Load boss image
        self.image = pygame.image.load("assets/images/level_1_boss.gif").convert_alpha()
        self.image = pygame.transform.scale(self.image, (200, 200))
        self.rect = self.image.get_rect(center=(screen_width // 2, -150))

        # Movement
        self.speed_y = 3
        self.follow_speed = 3
        self.target_y = 100
        self.screen_width = screen_width
        self.alive = True
        self.dying = False
        self.victory = False  # triggers pause after death

        # Movement states
        self.original_x = self.rect.centerx
        self.following = True
        self.returning = False
        self.follow_duration = 3000
        self.last_follow_switch = pygame.time.get_ticks()

        # Health
        self.max_health = 4
        self.health = self.max_health

        # Shooting
        self.bullet_image = pygame.image.load("assets/images/enemyBullet.png").convert_alpha()
        self.bullet_image = pygame.transform.scale(self.bullet_image, (30, 30))
        self.bullets = []
        self.shoot_cooldown = 2000
        self.last_shot_time = pygame.time.get_ticks()
        self.paused_until = 0  # for 3-second pause after question

        # Font and fade effect
        self.font = pygame.font.Font("assets/fonts/BoldPixels.ttf", 28)
        self.name_surface = self.font.render("D’Aragon", True, (255, 255, 255))
        self.fade_alpha = 0
        self.fade_in_speed = 3
        self.fade_done = False

        # Sound
        try:
            self.shoot_sound = pygame.mixer.Sound("assets/sounds/player_shoot_1.mp3")
        except:
            self.shoot_sound = None

        # Death animation
        self.death_frames = self.load_death_frames("assets/images/boss_dying/level_1_boss")
        self.death_index = 0
        self.death_speed = 100  # ms between frames
        self.last_death_update = 0
        self.death_finished = False
        self.death_done_time = 0

    def load_death_frames(self, folder_path):
        """Load all frames from the boss death animation folder."""
        frames = []
        if not os.path.exists(folder_path):
            print(f"[WARNING] Boss death animation folder not found: {folder_path}")
            return frames

        # Load images in correct order
        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith(".png"):
                frame = pygame.image.load(os.path.join(folder_path, filename)).convert_alpha()
                frame = pygame.transform.scale(frame, (200, 200))
                frames.append(frame)
        return frames

    def reset_shooting_rate(self):
        """Pause boss shooting for 3 seconds after question."""
        self.shoot_cooldown = 2000
        self.paused_until = pygame.time.get_ticks() + 3000

    def update(self, player_rect):
        """Boss logic."""
        if self.victory:
            return  # Pause during victory moment

        # Death animation update
        if self.dying:
            self.update_death_animation()
            return

        if not self.alive:
            return

        # Move down to target position (intro)
        if self.rect.y < self.target_y:
            self.rect.y += self.speed_y
            return

        # Fade-in boss name + health bar
        if not self.fade_done:
            self.fade_alpha = min(255, self.fade_alpha + self.fade_in_speed)
            if self.fade_alpha >= 255:
                self.fade_done = True

        # Movement state switching
        now = pygame.time.get_ticks()
        if now - self.last_follow_switch > self.follow_duration:
            self.following = not self.following
            self.returning = not self.returning
            self.last_follow_switch = now

        # Smooth follow
        if self.following:
            diff = player_rect.centerx - self.rect.centerx
            self.rect.x += int(diff * 0.02)
        elif self.returning:
            diff = self.original_x - self.rect.centerx
            self.rect.x += int(diff * 0.015)

        # Keep in screen
        self.rect.x = max(0, min(self.rect.x, self.screen_width - self.rect.width))

        # Shooting logic
        current_time = pygame.time.get_ticks()
        if current_time < self.paused_until:
            return

        if current_time - self.last_shot_time > self.shoot_cooldown:
            self.shoot()
            self.last_shot_time = current_time
            self.shoot_cooldown = max(1200, self.shoot_cooldown - 100)

        # Update bullets
        for bullet_rect in self.bullets[:]:
            bullet_rect.y += 8
            if bullet_rect.y > 600:
                self.bullets.remove(bullet_rect)

    def shoot(self):
        """Shoot bullet."""
        bullet_rect = self.bullet_image.get_rect(center=(self.rect.centerx, self.rect.bottom))
        self.bullets.append(bullet_rect)
        if self.shoot_sound:
            self.shoot_sound.play()

    def update_death_animation(self):
        """Update boss death animation."""
        if self.death_finished:
            # Wait 3 seconds after animation
            if self.death_done_time == 0:
                self.death_done_time = pygame.time.get_ticks()
            elif pygame.time.get_ticks() - self.death_done_time > 3000:
                self.victory = True  # Pause everything
            return

        now = pygame.time.get_ticks()
        if now - self.last_death_update > self.death_speed:
            self.last_death_update = now
            self.death_index += 1
            if self.death_index >= len(self.death_frames):
                self.death_finished = True
                self.death_index = len(self.death_frames) - 1

    def draw(self, screen):
        """Draw boss, health bar, and bullets."""
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

                name_rect = name_surface.get_rect(center=(self.screen_width // 2, bar_y - 25))
                screen.blit(name_surface, name_rect)

        for bullet_rect in self.bullets:
            screen.blit(self.bullet_image, bullet_rect)

    def hit(self):
        """Handle damage."""
        self.health -= 1
        if self.health <= 0:
            self.alive = False
            self.dying = True
            self.last_death_update = pygame.time.get_ticks()
            return True
        return False
