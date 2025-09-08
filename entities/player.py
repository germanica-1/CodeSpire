import pygame
import random
from utils.colors import BLUE, GREEN

class Player:
    def __init__(self, x, y):
        # Load player spaceship image
        self.image = pygame.image.load("assets/images/Ship6.png").convert_alpha()
        self.image = pygame.transform.rotate(self.image, 360)  # vertical orientation
        self.image = pygame.transform.scale(self.image, (100, 100))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5

        # Health & shield
        self.health = 3
        self.max_health = 3
        self.has_shield = False

        # Shooting
        self.bullets = []  # each bullet will be a dict with rect and image
        self.can_shoot = True
        self.shoot_cooldown = 300
        self.last_shot_time = 0

        # Load bullet image
        self.bullet_image = pygame.image.load("assets/images/laserBullet.png").convert_alpha()
        self.bullet_image = pygame.transform.scale(self.bullet_image, (90, 90))

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

        # Shoot on single key press
        if keys[pygame.K_SPACE] and self.can_shoot:
            self.shoot()
            self.can_shoot = False
            self.last_shot_time = current_time

        # Reset shooting after cooldown
        if not self.can_shoot and current_time - self.last_shot_time > self.shoot_cooldown:
            self.can_shoot = True

    def shoot(self):
        # Create bullet as a dict containing rect and image
        bullet_rect = pygame.Rect(self.rect.centerx-5, self.rect.top-10, 10, 20)
        self.bullets.append({"rect": bullet_rect, "image": self.bullet_image})

    def take_damage(self):
        if self.has_shield:
            self.has_shield = False
            print("Shield used! No damage taken.")
        else:
            self.health -= 1
            print(f"Player damaged! Health: {self.health}")

    def get_shield_chance(self):
        if random.random() < 0.2:
            self.has_shield = True
            print("Shield obtained!")

    def update(self):
        # Move bullets
        for bullet in self.bullets[:]:
            bullet["rect"].y -= 7
            if bullet["rect"].y < 0:
                self.bullets.remove(bullet)

    def draw(self, screen):
        # Draw player
        screen.blit(self.image, self.rect)

        # Draw bullets using image
        for bullet in self.bullets:
            screen.blit(bullet["image"], bullet["rect"])

        # Draw shield indicator
        if self.has_shield:
            pygame.draw.rect(screen, GREEN, self.rect, 3)
