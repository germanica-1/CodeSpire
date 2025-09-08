import pygame
import random

class Star:
    def __init__(self):
        self.x = random.randint(0, 800)
        self.y = random.randint(0, 600)
        self.speed = random.uniform(0.5, 2)
        self.radius = random.randint(1, 2)

    def update(self):
        self.y += self.speed
        if self.y > 600:
            self.y = 0
            self.x = random.randint(0, 800)

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.radius)
