import pygame
import random
import sys
from entities.player import Player
from entities.bug import Bug
from challenges.challenge_draw import ask_question
from utils.colors import BLACK
from utils.sounds import play_correct, play_incorrect
from utils.stars import Star
from menu.menu import menu_loop, pause_menu  

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
    health_text = font.render(f"Health: {player.health}/{player.max_health}", True, (255, 0, 0))
    screen.blit(health_text, (10, 10))

    # Health Bar
    bar_width = 150
    bar_height = 20
    fill = (player.health / player.max_health) * bar_width
    pygame.draw.rect(screen, (255, 0, 0), (10, 40, fill, bar_height))
    pygame.draw.rect(screen, (255, 255, 255), (10, 40, bar_width, bar_height), 2)

    # Shield Indicator (use icon instead of just text)
    if player.has_shield:
        player.draw_shield_icon(screen)  # <-- draw the icon beside the health bar


def game_over_screen(screen):
    """Display game over screen with retry option"""
    screen.fill(BLACK)
    
    font_large = pygame.font.Font(None, 72)
    font_medium = pygame.font.Font(None, 36)
    
    game_over_text = font_large.render("GAME OVER", True, (255, 0, 0))
    retry_text = font_medium.render("Press R to Retry or Q to Quit", True, (255, 255, 255))
    
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
    screen.blit(retry_text, (WIDTH//2 - retry_text.get_width()//2, HEIGHT//2 + 50))
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "retry"
                elif event.key == pygame.K_q:
                    return "quit"


class Explosion:
    def __init__(self, x, y):
        self.frames = []
        for i in range(1, 12):
            img = pygame.image.load(f"assets/images/Explosions/Explosion3_{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (100, 100))
            self.frames.append(img)

        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.animation_speed = 50
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


def game_loop():
    """Run one play session. Returns when player quits to menu, exits, or game over."""
    # Start/ensure game music is playing only here
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
    player = Player(WIDTH // 2, HEIGHT - 80)

    # Bugs
    num_bugs = 5
    bugs = []
    for i in range(num_bugs):
        can_shoot = random.random() < 0.4
        x = random.randint(50, WIDTH - 50)
        y = random.randint(-300, -50) - i * 120
        bugs.append(Bug(x, y, can_shoot))

    stars = [Star() for _ in range(100)]
    explosions = []

    running = True
    while running:
        clock.tick(FPS)

        # Check if player is dead
        if player.health <= 0:
            pygame.mixer.music.stop()
            choice = game_over_screen(screen)
            return choice  # either "retry" or "quit"

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
                pygame.mixer.music.stop()
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause_choice = pause_menu(screen)
                    if pause_choice == "resume":
                        pass
                    elif pause_choice == "quit_to_menu":
                        pygame.mixer.music.stop()
                        return  # back to menu

        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.update()

        # Bugs update with smaller hitboxes
        for bug in bugs[:]:
            bug.update()
            bug.draw(screen)

            # Smaller hitboxes
            player_hitbox = pygame.Rect(
                player.rect.x + player.rect.width * 0.2,
                player.rect.y + player.rect.height * 0.2,
                player.rect.width * 0.6,
                player.rect.height * 0.6
            )

            bug_hitbox = pygame.Rect(
                bug.rect.x + bug.rect.width * 0.2,
                bug.rect.y + bug.rect.height * 0.2,
                bug.rect.width * 0.6,
                bug.rect.height * 0.6
            )

            # Player or bullet hits bug
            player_hit = bug_hitbox.colliderect(player_hitbox)
            bullet_hit = any(bug_hitbox.colliderect(bullet["rect"]) for bullet in player.bullets)

            if player_hit or bullet_hit:
                correct = ask_question(screen)
                if correct:
                    play_correct()
                    explosions.append(Explosion(bug.rect.centerx, bug.rect.centery))
                    bugs.remove(bug)
                    player.get_shield_chance()
                else:
                    play_incorrect()
                    explosions.append(Explosion(bug.rect.centerx, bug.rect.centery))
                    player.take_damage()
                    bugs.remove(bug)

                # Remove bullets that hit bug
                for bullet in player.bullets[:]:
                    if bug_hitbox.colliderect(bullet["rect"]):
                        player.bullets.remove(bullet)

            # Bug bullets hitting player
            for b_bullet in bug.bullets[:]:
                if player_hitbox.colliderect(b_bullet):
                    bug.bullets.remove(b_bullet)
                    correct = ask_question(screen)
                    if correct:
                        play_correct()
                        player.get_shield_chance()
                    else:
                        play_incorrect()
                        player.take_damage()

        # Explosions
        for explosion in explosions[:]:
            explosion.update()
            explosion.draw(screen)
            if explosion.finished:
                explosions.remove(explosion)

        # Draw Player + UI
        player.draw(screen)
        draw_ui(screen, player)

        pygame.display.flip()

    pygame.mixer.music.stop()


if __name__ == "__main__":
    while True:
        choice = menu_loop()
        if choice == "game":
            result = game_loop()
            if result == "retry":
                continue  # Restart game
            elif result == "quit":
                pygame.quit()
                sys.exit()
        elif choice in ("quit", "exit"):
            pygame.quit()
            sys.exit()
        else:
            continue
