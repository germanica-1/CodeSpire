import pygame
import random
import os
from utils.colors import BLUE, GREEN

class Player:
    def __init__(self, x, y):
        # Load player spaceship image
        self.image = pygame.image.load("assets/images/Ship6.png").convert_alpha()
        self.image = pygame.transform.rotate(self.image, 360)
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3.5
        self.score = 0  # <-- Add this lin

        # Health & shield
        self.health = 3
        self.max_health = 3
        self.has_shield = False

        # Shooting system
        self.bullets = []
        self.can_shoot = True
        self.shoot_cooldown = 300
        self.last_shot_time = 0
        self.shoot_sound = pygame.mixer.Sound("assets/sounds/player_shoot_1.mp3")

        # Overheat system
        self.shot_count = 0
        self.max_shots_before_delay = 5
        self.overheat_delay = 3000
        self.overheat_start_time = 0
        self.overheated = False

        # Bullet image
        self.bullet_image = pygame.image.load("assets/images/laserBullet.png").convert_alpha()
        self.bullet_image = pygame.transform.scale(self.bullet_image, (40, 60))

        # Shield images
        self.shield_icon = pygame.image.load("assets/images/shield_icon.png").convert_alpha()
        self.shield_icon = pygame.transform.scale(self.shield_icon, (140, 140))
        self.shield_aura = pygame.image.load("assets/images/shield_aura.png").convert_alpha()
        self.shield_aura = pygame.transform.scale(self.shield_aura, (120, 120))

        #Reload animation setup 
        self.reload_frames = self.load_reload_frames("assets/images/reload_animation")
        self.current_reload_frame = 0
        self.reload_frame_time = 170
        self.last_reload_frame_time = 0

    def load_reload_frames(self, folder_path):
        """Load reload animation frames in correct order (0–5)."""
        frames = []
        for i in range(6):
            filename = f"frame_{i}_delay-0.17s.png"
            path = os.path.join(folder_path, filename)
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (50, 50)) 
                frames.append(img)
        return frames

    def handle_input(self, keys):
        current_time = pygame.time.get_ticks()

        # Movement
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < 800:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < 600:
            self.rect.y += self.speed

        # Overheat cooldown
        if self.overheated:
            if current_time - self.overheat_start_time >= self.overheat_delay:
                self.overheated = False
                self.shot_count = 0
                self.can_shoot = True
                self.current_reload_frame = 0

        # Shooting
        if not self.overheated:
            if keys[pygame.K_SPACE] and self.can_shoot:
                self.shoot()
                self.can_shoot = False
                self.last_shot_time = current_time
                self.shot_count += 1

                if self.shot_count >= self.max_shots_before_delay:
                    self.overheated = True
                    self.overheat_start_time = current_time
                    self.last_reload_frame_time = current_time
                    self.current_reload_frame = 0
                    print("Overheated! Reloading...")

        # Reset cooldown
        if not self.can_shoot and current_time - self.last_shot_time > self.shoot_cooldown:
            self.can_shoot = True

    def shoot(self):
        self.shoot_sound.play()
        bullet_rect = self.bullet_image.get_rect(center=(self.rect.centerx, self.rect.top))
        self.bullets.append({"rect": bullet_rect, "image": self.bullet_image})

    def update(self):
        current_time = pygame.time.get_ticks()

        # Move bullets
        for bullet in self.bullets[:]:
            bullet["rect"].y -= 7
            if bullet["rect"].y < 0:
                self.bullets.remove(bullet)

        # Reload animation
        if self.overheated and self.reload_frames:
            if current_time - self.last_reload_frame_time > self.reload_frame_time:
                self.last_reload_frame_time = current_time
                self.current_reload_frame += 1
                if self.current_reload_frame >= len(self.reload_frames):
                    self.current_reload_frame = 0

    def draw(self, screen):
        # Player
        screen.blit(self.image, self.rect)

        # Shield aura
        if self.has_shield:
            shield_rect = self.shield_aura.get_rect(center=self.rect.center)
            screen.blit(self.shield_aura, shield_rect)

        # Bullets
        for bullet in self.bullets:
            screen.blit(bullet["image"], bullet["rect"])

        # Smaller reload animation above player
        if self.overheated and self.reload_frames:
            frame = self.reload_frames[self.current_reload_frame]
            # lowered the height offset for closer positioning
            frame_rect = frame.get_rect(center=(self.rect.centerx, self.rect.top - 25))
            screen.blit(frame, frame_rect)

    def take_damage(self):
        if self.has_shield:
            self.has_shield = False
            print("Shield used! No damage taken.")
        else:
            self.health -= 1
            print(f"Player damaged! Health: {self.health}")

    def get_shield_chance(self):
        if random.random() < 0.35:
            self.has_shield = True
            print("Shield obtained!")

    def draw_shield_icon(self, screen):
        if self.has_shield:
            screen.blit(self.shield_icon, (120, -25))
