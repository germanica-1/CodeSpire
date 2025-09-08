import pygame
import random

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = random.randint(2, 5)
        self.color = (255, 255, 0)
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-2, 2)
        self.life = 30

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1

    def draw(self, screen):
        if self.life > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
