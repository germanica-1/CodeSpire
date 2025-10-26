import pygame
import random
from utils.colors import RED  

class Bug_Level_3:
    def __init__(self, x, y, can_shoot=True):

        ship_image = random.choice([
            "assets/images/Ship1.png",
            "assets/images/Ship2.png",
            "assets/images/Ship3.png"
        ])


        self.image = pygame.image.load(ship_image).convert_alpha()
        self.image = pygame.transform.rotate(self.image, 90)  
        self.image = pygame.transform.scale(self.image, (90, 90))
        self.rect = self.image.get_rect(center=(x, y))

        # Movement
        self.speed_y = random.uniform(1.5, 2.5)
        self.speed_x = random.choice([-1, 1]) * random.uniform(0.7, 1.2)
        self.direction_timer = pygame.time.get_ticks()
        self.direction_change_delay = random.randint(1000, 2000)

        # Shooting setup
        self.can_shoot = can_shoot
        self.bullets = []
        self.bullet_image = pygame.image.load("assets/images/enemyBullet.png").convert_alpha()
        self.bullet_image = pygame.transform.scale(self.bullet_image, (28, 28))
        self.shoot_cooldown = random.randint(500, 1500)
        self.last_shot_time = pygame.time.get_ticks()

        
        try:
            self.shoot_sfx = pygame.mixer.Sound("assets/sounds/player_shoot_1.mp3")
            self.shoot_sfx.set_volume(0.2)
        except Exception:
            self.shoot_sfx = None

    def update(self):
        
        now = pygame.time.get_ticks()
        if now - self.direction_timer > self.direction_change_delay:
            self.speed_x *= -1  
            self.direction_timer = now
            self.direction_change_delay = random.randint(500, 500)

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        
        if self.rect.top > 620:
            self.rect.y = random.randint(-200, -50)
            self.rect.x = random.randint(50, 750)

        if self.rect.left < 0 or self.rect.right > 800:
            self.speed_x *= -1

        
        if self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot_time > self.shoot_cooldown:
                self.shoot()
                self.last_shot_time = current_time
                self.shoot_cooldown = random.randint(1000, 2500)

        for bullet in self.bullets[:]:
            bullet.y += 6
            if bullet.y > 600:
                self.bullets.remove(bullet)

    def shoot(self):
        
        bullet_rect = self.bullet_image.get_rect(center=(self.rect.centerx, self.rect.bottom))
        self.bullets.append(bullet_rect)

        
        if random.random() < 0.2:
            left_bullet = self.bullet_image.get_rect(center=(self.rect.centerx - 20, self.rect.bottom))
            right_bullet = self.bullet_image.get_rect(center=(self.rect.centerx + 20, self.rect.bottom))
            self.bullets.extend([left_bullet, right_bullet])

        if self.shoot_sfx:
            self.shoot_sfx.play()

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        for bullet in self.bullets:
            screen.blit(self.bullet_image, bullet)

