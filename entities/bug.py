import pygame
import random
from utils.colors import RED  # optional, still used for debugging

class Bug:
    def __init__(self, x, y, can_shoot=False):
        # Randomly pick between Ship4.png and Ship5.png
        ship_image = random.choice(["assets/images/Ship4.png", "assets/images/Ship5.png"])

        # Load bug spaceship image
        self.image = pygame.image.load(ship_image).convert_alpha()
        self.image = pygame.transform.rotate(self.image, 90)  # rotate 90° to face down
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2

        # Load enemy bullet image
        self.bullet_image = pygame.image.load("assets/images/enemyBullet.png").convert_alpha()
        self.bullet_image = pygame.transform.scale(self.bullet_image, (30, 30))

        # --- Load SFX ---
        self.shoot_sfx = pygame.mixer.Sound("assets/sounds/player_shoot_1.mp3")
        self.shoot_sfx.set_volume(0.5)  # adjust volume (0.0–1.0)

        # Shooting attributes
        self.can_shoot = can_shoot
        self.bullets = []
        self.shoot_cooldown = random.randint(1000, 3000)
        self.last_shot_time = pygame.time.get_ticks()

    def update(self):
        # Move downward
        self.rect.y += self.speed
        if self.rect.top > 600:
            self.rect.y = -50
            self.rect.x = random.randint(50, 750)

        # Handle shooting
        if self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot_time > self.shoot_cooldown:
                self.shoot()
                self.last_shot_time = current_time
                self.shoot_cooldown = random.randint(1000, 3000)

        # Update bullets
        for bullet_rect in self.bullets[:]:
            bullet_rect.y += 5
            if bullet_rect.y > 600:
                self.bullets.remove(bullet_rect)

    def shoot(self):
        # Create bullet rect (positioned below the bug)
        bullet_rect = self.bullet_image.get_rect(center=(self.rect.centerx, self.rect.bottom))
        self.bullets.append(bullet_rect)

        # --- Play SFX when shooting ---
        self.shoot_sfx.play()

    def draw(self, screen):
        # Draw the bug
        screen.blit(self.image, self.rect)
        # Draw each bullet image
        for bullet_rect in self.bullets:
            screen.blit(self.bullet_image, bullet_rect)
