import pygame
import random
from utils.colors import RED

class Bug:
    def __init__(self, x, y, can_shoot=False):
        # Randomly pick between Ship4.png and Ship5.png
        ship_image = random.choice(["assets/images/Ship4.png", "assets/images/Ship5.png"])

        # Load bug spaceship image
        self.image = pygame.image.load(ship_image).convert_alpha()
        self.image = pygame.transform.rotate(self.image, 90)  # rotate 90° to face down
        self.image = pygame.transform.scale(self.image, (100, 100))  # resize
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2

        # Shooting
        self.can_shoot = can_shoot
        self.bullets = []
        self.shoot_cooldown = random.randint(1000, 3000)  # Random initial interval
        self.last_shot_time = pygame.time.get_ticks()

    def update(self):
        # Move bug downward
        self.rect.y += self.speed
        if self.rect.top > 600:
            self.rect.y = -50
            self.rect.x = random.randint(50, 750)

        # Independent shooting
        if self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot_time > self.shoot_cooldown:
                self.shoot()
                self.last_shot_time = current_time
                # Randomize next shooting interval (1-3 seconds)
                self.shoot_cooldown = random.randint(1000, 3000)

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.y += 5
            if bullet.y > 600:
                self.bullets.remove(bullet)

    def shoot(self):
        # Create a bullet moving downward
        bullet = pygame.Rect(self.rect.centerx-5, self.rect.bottom, 10, 20)
        self.bullets.append(bullet)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        # Draw bullets in red
        for bullet in self.bullets:
            pygame.draw.rect(screen, RED, bullet)
