import pygame
import random
import sys
import os
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


class Portal:
    """Animated portal that appears after boss death. It loops its animation so it remains active."""
    def __init__(self, x, y):
        self.frames = []
        folder = "assets/images/portal_1"
        # load available frames named portal1_frame_1.png ... portal1_frame_N.png
        if os.path.exists(folder):
            files = sorted(f for f in os.listdir(folder) if f.lower().endswith(".png"))
            for filename in files:
                path = os.path.join(folder, filename)
                try:
                    frame = pygame.image.load(path).convert_alpha()
                    frame = pygame.transform.scale(frame, (200, 200))
                    self.frames.append(frame)
                except Exception:
                    pass

        if not self.frames:
            # fallback single placeholder
            surf = pygame.Surface((200, 200), pygame.SRCALPHA)
            pygame.draw.circle(surf, (100, 0, 200, 200), (100, 100), 90)
            self.frames = [surf]

        self.index = 0
        self.image = self.frames[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 80

    def update(self):
        # loop animation continuously so portal stays active
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.index = (self.index + 1) % len(self.frames)
            self.image = self.frames[self.index]

    def draw(self, screen):
        screen.blit(self.image, self.rect)


def prompt_confirm(screen, prompt_text="Proceed to level 2? (Y/N)"):
    """Display a simple Y/N prompt. Return True for Y, False for N."""
    font = pygame.font.Font(None, 36)
    small = pygame.font.Font(None, 28)
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))

    prompt_surf = font.render(prompt_text, True, (255, 255, 255))
    hint = small.render("Press Y to confirm or N to cancel", True, (200, 200, 200))

    while True:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_y:
                    return True
                if ev.key == pygame.K_n:
                    return False

        # Draw overlay + text
        screen.blit(overlay, (0, 0))
        screen.blit(prompt_surf, (WIDTH // 2 - prompt_surf.get_width() // 2, HEIGHT // 2 - 30))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 20))
        pygame.display.flip()


def fade_out(screen, duration=800):
    """Fade out to black over duration (ms)."""
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    start = pygame.time.get_ticks()
    while True:
        now = pygame.time.get_ticks()
        t = now - start
        if t >= duration:
            overlay.set_alpha(255)
            screen.blit(overlay, (0, 0))
            pygame.display.flip()
            break
        alpha = int(255 * (t / duration))
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)


def fade_in(screen, duration=800):
    """Fade from black to scene over duration (ms). Assumes screen currently shows the new scene."""
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill((0, 0, 0))
    start = pygame.time.get_ticks()
    while True:
        now = pygame.time.get_ticks()
        t = now - start
        if t >= duration:
            break
        alpha = int(255 * (1 - (t / duration)))
        overlay.set_alpha(alpha)
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(FPS)


def transition_to_level_2(screen):
    """Transition animation: scroll level 2 map background.
    This function will do a fade-out then scroll the map, then fade in.
    """
    # Try to load map fallback to black if missing
    try:
        map_img = pygame.image.load("assets/images/menu/menu_background/level_2_map.jpg").convert()
        map_img = pygame.transform.scale(map_img, (WIDTH, HEIGHT))
    except Exception:
        map_img = pygame.Surface((WIDTH, HEIGHT))
        map_img.fill((10, 10, 40))

    scroll_speed = 1
    map_y = 0
    transition_start = pygame.time.get_ticks()

    # fade out current screen 
    fade_out(screen, duration=700)

    # Here simply scroll and fade in
    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        map_y = (map_y + scroll_speed) % HEIGHT
        screen.blit(map_img, (0, map_y - HEIGHT))
        screen.blit(map_img, (0, map_y))

        pygame.display.flip()

        # run scroll for 2.5 seconds then fade-in to stop
        if pygame.time.get_ticks() - transition_start > 2500:
            break

    fade_in(screen, duration=700)
    # After transition returns, caller may set up level-2 game stat
    return

def level_2_loop(screen):
    """Level 2 loop with ESC pause menu and smoother behavior."""
    try:
        pygame.mixer.music.load("assets/sounds/space_bg.mp3")
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)
    except Exception:
        pass

    try:
        bg = pygame.image.load("assets/images/menu/menu_background/level_2_map.jpg").convert()
        bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
    except Exception:
        bg = pygame.Surface((WIDTH, HEIGHT))
        bg.fill((20, 20, 60))

    bg_y1, bg_y2 = 0, -HEIGHT
    scroll_speed = 1
    player = Player(WIDTH // 2, HEIGHT - 80)
    stars = [Star() for _ in range(100)]
    running = True

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                choice = pause_menu(screen)
                if choice == "quit_to_menu":
                    pygame.mixer.music.stop()
                    return  # go back to main menu

        # Scroll background 
        bg_y1 += scroll_speed
        bg_y2 += scroll_speed
        if bg_y1 >= HEIGHT:
            bg_y1 = bg_y2 - HEIGHT
        if bg_y2 >= HEIGHT:
            bg_y2 = bg_y1 - HEIGHT

        # Draw both
        screen.blit(bg, (0, bg_y1))
        screen.blit(bg, (0, bg_y2))

        for star in stars:
            star.update()
            star.draw(screen)

        player.handle_input(pygame.key.get_pressed())
        player.update()
        player.draw(screen)

        pygame.display.flip()

    pygame.mixer.music.fadeout(1000)
    return



def game_loop():
    """Main game loop."""
    # start background music for level 1
    try:
        pygame.mixer.music.load("assets/sounds/space_bg.mp3")
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    except Exception:
        pass

    # Background setup
    bg = pygame.image.load("assets/images/space.png").convert()
    bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
    bg_y1, bg_y2, bg_speed = 0, -HEIGHT, 2

    player = Player(WIDTH // 2, HEIGHT - 80)
    bugs = [Bug(random.randint(50, WIDTH - 50), random.randint(-300, -50) - i * 120, random.random() < 0.4) for i in range(6)]
    boss = None
    bugs_destroyed = 0
    stars = [Star() for _ in range(100)]
    explosions = []
    portal = None
    running = True

    while running:
        clock.tick(FPS)

        # Game Over
        if player.health <= 0:
            pygame.mixer.music.stop()
            return game_over_screen(screen)

        # Background Scroll
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

        # Events
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

        # Bugs
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

        # Boss spawn
        if bugs_destroyed >= 3 and boss is None:
            # clear remaining bugs visually
            for bug in bugs[:]:
                explosions.append(Explosion(bug.rect.centerx, bug.rect.centery))
                bugs.remove(bug)
            boss = Level1Boss(WIDTH, HEIGHT)
            bugs_destroyed = 0

        # Boss logic & drawing
        if boss:
            boss.update(player.rect)
            boss.draw(screen)

            # If boss completed death sequence and indicated victory, spawn portal (only once)
            if boss.victory:
                if not portal:
                    portal = Portal(boss.rect.centerx, boss.rect.bottom)
                    # do NOT append explosion or auto-transition; wait for player interaction
                # remove boss so we don't keep calling update on it
                boss = None
                # don't continue, let the rest of the loop handle player/portal
            else:
                # only check boss bullets/interaction if boss still exists 
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

        # Portal handling
        if portal:
            portal.update()
            portal.draw(screen)

            # Check collision with player, prompt only when player intentionally steps into portal
            if player.rect.colliderect(portal.rect):
                # Ask a Y/N confirmation before transitioning
                proceed = prompt_confirm(screen, "Proceed to level 2? (Y/N)")
                if proceed:
                    # fade out current scene, stop music, and run the level 2 transition
                    pygame.mixer.music.fadeout(600)
                    fade_out(screen, duration=600)
                    transition_to_level_2(screen)

                    
                    try:
                        pygame.mixer.music.load("assets/sounds/space_bg.mp3")  # or other level2 music
                        pygame.mixer.music.set_volume(0.3)
                        pygame.mixer.music.play(-1)
                    except Exception:
                        pass

                    # Exit level 1 loop, caller can decide next action
                    return "level2"  
                else:
                    # do nothing, simply continue (player canceled)
                    pass

        # Explosions
        for exp in explosions[:]:
            exp.update()
            exp.draw(screen)
            if exp.finished:
                explosions.remove(exp)

        # Draw UI
        player.draw(screen)
        draw_ui(screen, player)
        pygame.display.flip()

    pygame.mixer.music.stop()
    return


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
            elif result == "level2":
                level_2_loop(screen)  # <-- continue to level 2 here
                continue
        elif choice in ("quit", "exit"):
            pygame.quit()
            sys.exit()
