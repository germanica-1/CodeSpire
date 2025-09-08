import pygame
import random
from entities.player import Player
from entities.bug import Bug
from challenges.challenge_draw import ask_question
from utils.colors import BLACK
from utils.sounds import play_correct, play_incorrect
from utils.stars import Star

# Pygame init
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CodeSpire")
clock = pygame.time.Clock()
FPS = 60

def draw_ui(screen, player):
    font = pygame.font.Font(None, 32)
    
    # Health Text
    health_text = font.render(f"Health: {player.health}/{player.max_health}", True, (255,0,0))
    screen.blit(health_text, (10, 10))
    
    # Health Bar
    bar_width = 150
    bar_height = 20
    fill = (player.health / player.max_health) * bar_width
    pygame.draw.rect(screen, (255,0,0), (10, 40, fill, bar_height))
    pygame.draw.rect(screen, (255,255,255), (10, 40, bar_width, bar_height), 2)

    # Shield Indicator
    if player.has_shield:
        shield_text = font.render("Shield: ACTIVE", True, (0,255,0))
        screen.blit(shield_text, (10, 70))


class Explosion:
    def __init__(self, x, y):
        # Load all explosion frames
        self.frames = []
        for i in range(1, 12):  # Explostion.png → Explostion1.png
            img = pygame.image.load(f"assets/images/Explosions/Explosion3_{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (100, 100))  # match bug size
            self.frames.append(img)

        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.animation_speed = 50  # ms per frame
        self.last_update = pygame.time.get_ticks()
        self.finished = False

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.animation_speed:
            self.last_update = current_time
            self.index += 1
            if self.index < len(self.frames):
                self.image = self.frames[self.index]
            else:
                self.finished = True

    def draw(self, screen):
        if not self.finished:
            screen.blit(self.image, self.rect)


# Background Music
pygame.mixer.music.load("assets/sounds/space_bg.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)

# Scrolling background
bg_image = pygame.image.load("assets/images/space.png").convert()
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))
bg_y1 = 0
bg_y2 = -HEIGHT
bg_speed = 2

# Game Entities
player = Player(WIDTH//2, HEIGHT-80)

# Bugs
num_bugs = 5
bugs = []
for i in range(num_bugs):
    can_shoot = random.random() < 0.4
    x = random.randint(50, WIDTH-50)
    y = random.randint(-300, -50) - i * 120
    bugs.append(Bug(x, y, can_shoot))

stars = [Star() for _ in range(100)]
explosions = []  # EXPLOSION ADDED

running = True
while running:
    clock.tick(FPS)

    # Scrolling background
    bg_y1 += bg_speed
    bg_y2 += bg_speed
    if bg_y1 >= HEIGHT:
        bg_y1 = -HEIGHT
    if bg_y2 >= HEIGHT:
        bg_y2 = -HEIGHT
    screen.blit(bg_image, (0, bg_y1))
    screen.blit(bg_image, (0, bg_y2))

    # Stars
    for star in stars:
        star.update()
        star.draw(screen)

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.handle_input(keys)
    player.update()

    # Bugs update
    for bug in bugs[:]:
        bug.update()
        bug.draw(screen)

        # Collision with player
        player_hit = bug.rect.colliderect(player.rect)
        # Collision with player bullets
        bullet_hit = any(bug.rect.colliderect(bullet["rect"]) for bullet in player.bullets)

        if player_hit or bullet_hit:
            correct = ask_question(screen)
            if correct:
                play_correct()
                explosions.append(Explosion(bug.rect.centerx, bug.rect.centery))  #  EXPLOSION ADDED
                bugs.remove(bug)
                player.get_shield_chance()
            else:
                play_incorrect()
                explosions.append(Explosion(bug.rect.centerx, bug.rect.centery))  #  EXPLOSION ADDED
                player.take_damage()
                bugs.remove(bug)

            # Remove bullets that hit the bug
            for bullet in player.bullets[:]:
                if bug.rect.colliderect(bullet["rect"]):
                    player.bullets.remove(bullet)

        # Bug bullets collision with player
        for b_bullet in bug.bullets[:]:
            if player.rect.colliderect(b_bullet):
                bug.bullets.remove(b_bullet)
                correct = ask_question(screen)
                if correct:
                    play_correct()
                    player.get_shield_chance()
                else:
                    play_incorrect()
                    player.take_damage()

    # Update explosions
    for explosion in explosions[:]:
        explosion.update()
        explosion.draw(screen)
        if explosion.finished:
            explosions.remove(explosion)

    # Draw Player + UI
    player.draw(screen)
    draw_ui(screen, player)

    pygame.display.flip()

pygame.quit()
