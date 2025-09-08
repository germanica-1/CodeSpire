import pygame
pygame.mixer.init()

def play_correct():
    sound = pygame.mixer.Sound("assets/sounds/correct.mp3")
    sound.play()

def play_incorrect():
    sound = pygame.mixer.Sound("assets/sounds/incorrect.mp3")
    sound.play()
