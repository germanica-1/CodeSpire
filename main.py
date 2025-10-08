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
from levels.level_1_boss import Level1Boss


# --- Pygame setup ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CodeSpire")
clock = pygame.time.Clock()
FPS = 60


def draw_ui(screen, player):
    """Draw player health bar and shield icon."""
    font = pygame.font.Font(None, 32)
    health_text = font.render(f"Health: {player.health}/{player.max_health}", True, (255, 0, 0))
    screen.blit(health_text, (10, 10))

    bar_width, bar_height = 150, 20
    fill = (player.health / player.max_health) * bar_width
    pygame.draw.rect(screen, (255, 0, 0), (10, 40, fill, bar_height))
    pygame.draw.rect(screen, (255, 255, 255), (10, 40, bar_width, bar_height), 2)

    if player.has_shield:
        player.draw_shield_icon(screen)


def game_over_screen(screen):
    """Show game over screen."""
    screen.fill(BLACK)
    font_large = pygame.font.Font(None, 72)
    font_medium = pygame.font.Font(None, 36)
    game_over_text = font_large.render("GAME OVER", True, (255, 0, 0))
    retry_text = font_medium.render("Press R to Retry or Q to Quit", True, (255, 255, 255))
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(retry_text, (WIDTH // 2 - retry_text.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()

    while True:
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
    """Explosion animation."""
    def __init__(self, x, y):
        self.frames = [
            pygame.transform.scale(
                pygame.image.load(f"assets/images/Explosions/Explosion3_{i}.png").convert_alpha(), (100, 100)
            )
            for i in range(1, 12)
        ]
        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 50
        self.finished = False

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.index += 1
            if self.index >= len(self.frames):
                self.finished = True
            else:
                self.image = self.frames[self.index]

    def draw(self, screen):
        if not self.finished:
            screen.blit(self.image, self.rect)


def game_loop():
    """Main game loop."""
    pygame.mixer.music.load("assets/sounds/space_bg.mp3")
    pygame.mixer.music.set_volume(0.3)
    pygame.mixer.music.play(-1)

    # Background setup
    bg = pygame.image.load("assets/images/space.png").convert()
    bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
    bg_y1, bg_y2, bg_speed = 0, -HEIGHT, 2

    # Entities
    player = Player(WIDTH // 2, HEIGHT - 80)

    # Bugs
    bugs = []
    for i in range(6):
        can_shoot = random.random() < 0.4
        x, y = random.randint(50, WIDTH - 50), random.randint(-300, -50) - i * 120
        bugs.append(Bug(x, y, can_shoot))

    # Boss
    boss = None
    bugs_destroyed = 0

    stars = [Star() for _ in range(100)]
    explosions = []

    running = True
    while running:
        clock.tick(FPS)

        # --- Game Over Check ---
        if player.health <= 0:
            pygame.mixer.music.stop()
            return game_over_screen(screen)

        # --- Background Scroll ---
        bg_y1 += bg_speed
        bg_y2 += bg_speed
        if bg_y1 >= HEIGHT:
            bg_y1 = -HEIGHT
        if bg_y2 >= HEIGHT:
            bg_y2 = -HEIGHT
        screen.blit(bg, (0, bg_y1))
        screen.blit(bg, (0, bg_y2))

        for star in stars:
            star.update()
            star.draw(screen)

        # --- Events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                choice = pause_menu(screen)
                if choice == "quit_to_menu":
                    pygame.mixer.music.stop()
                    return

        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.update()

        # --- Bug Logic ---
        for bug in bugs[:]:
            bug.update()
            bug.draw(screen)

            player_hitbox = player.rect.inflate(-player.rect.width * 0.4, -player.rect.height * 0.4)
            bug_hitbox = bug.rect.inflate(-bug.rect.width * 0.4, -bug.rect.height * 0.4)

            player_hit = bug_hitbox.colliderect(player_hitbox)
            bullet_hit = any(bug_hitbox.colliderect(b["rect"]) for b in player.bullets)

            if player_hit or bullet_hit:
                correct = ask_question(screen)
                if correct:
                    play_correct()
                    explosions.append(Explosion(bug.rect.centerx, bug.rect.centery))
                    bugs.remove(bug)
                    player.get_shield_chance()
                    bugs_destroyed += 1
                else:
                    play_incorrect()
                    explosions.append(Explosion(bug.rect.centerx, bug.rect.centery))
                    player.take_damage()
                    bugs.remove(bug)

                for b in player.bullets[:]:
                    if bug_hitbox.colliderect(b["rect"]):
                        player.bullets.remove(b)

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

        # --- Spawn Boss after 3 Bugs Destroyed ---
        if bugs_destroyed >= 3 and boss is None:
            # Clear all remaining bugs immediately when condition is met
            for bug in bugs[:]:
                explosions.append(Explosion(bug.rect.centerx, bug.rect.centery))
                bugs.remove(bug)

            boss = Level1Boss(WIDTH, HEIGHT)
            bugs_destroyed = 0  # Reset counter to avoid re-triggering

        if boss:
            boss.update(player.rect)
            boss.draw(screen)

            # After death animation finishes and victory pause done
            if boss.victory:
                explosions.append(Explosion(boss.rect.centerx, boss.rect.centery))
                boss = None


            # Boss bullets hit player
            for b_rect in boss.bullets[:]:
                if player.rect.colliderect(b_rect):
                    boss.bullets.remove(b_rect)
                    correct = ask_question(screen)
                    boss.reset_shooting_rate()
                    if correct:
                        play_correct()
                    else:
                        play_incorrect()
                        player.take_damage()

            # Player bullets hit boss
            for b in player.bullets[:]:
                if boss.rect.colliderect(b["rect"]):
                    player.bullets.remove(b)
                    correct = ask_question(screen)
                    boss.reset_shooting_rate()
                    if correct:
                        play_correct()
                        defeated = boss.hit()
                        if defeated:
                            explosions.append(Explosion(boss.rect.centerx, boss.rect.centery))
                            
                    else:
                        play_incorrect()

        # --- Explosions ---
        for exp in explosions[:]:
            exp.update()
            exp.draw(screen)
            if exp.finished:
                explosions.remove(exp)

        # --- Draw UI + Player ---
        player.draw(screen)
        draw_ui(screen, player)

        pygame.display.flip()

    pygame.mixer.music.stop()


# --- Main Menu Loop ---
if __name__ == "__main__":
    while True:
        choice = menu_loop()
        if choice == "game":
            result = game_loop()
            if result == "retry":
                continue
            elif result == "quit":
                pygame.quit()
                sys.exit()
        elif choice in ("quit", "exit"):
            pygame.quit()
            sys.exit()
