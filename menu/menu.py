import pygame
import sys
from utils.colors import WHITE, YELLOW

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CodeSpire Menu")
clock = pygame.time.Clock()
FPS = 60

# Load background image (steady, no scroll)
bg_image = pygame.image.load("assets/images/menu/menu_background/menu_bg.jpg").convert()
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

# Font
title_font = pygame.font.Font("assets/fonts/BoldPixels.ttf", 72)
menu_font = pygame.font.Font("assets/fonts/BoldPixels.ttf", 36)

# Title text
title_surface = title_font.render("CodeSpire", True, YELLOW)
title_rect = title_surface.get_rect(center=(WIDTH // 2, 80))

# Menu options
menu_items = ["Start Game", "Options", "Credits", "Quit"]
selected_index = 0

# --- Sounds ---
select_sfx = pygame.mixer.Sound("assets/sounds/select_sfx.mp3")
select_sfx.set_volume(0.5)

def draw_menu(mouse_pos):
    screen.blit(bg_image, (0, 0))

    # Draw title
    screen.blit(title_surface, title_rect)

    # Draw menu items
    for i, item in enumerate(menu_items):
        if i == selected_index or get_item_rect(i).collidepoint(mouse_pos):
            text = menu_font.render(item, True, YELLOW)
            text = pygame.transform.scale(text, (int(text.get_width() * 1.1), int(text.get_height() * 1.1)))
        else:
            text = menu_font.render(item, True, WHITE)

        rect = text.get_rect(center=(WIDTH // 2, 250 + i * 60))
        screen.blit(text, rect)

def get_item_rect(index):
    """Helper to get the rect of each menu item."""
    text = menu_font.render(menu_items[index], True, WHITE)
    return text.get_rect(center=(WIDTH // 2, 250 + index * 60))

def menu_loop():
    global selected_index
    running = True

    # Start menu music
    pygame.mixer.music.load("assets/sounds/menu_music.mp3")
    pygame.mixer.music.set_volume(5)
    pygame.mixer.music.play(-1)

    last_hover_index = -1  # for hover sound

    while running:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(menu_items)
                    select_sfx.play()
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(menu_items)
                    select_sfx.play()
                elif event.key == pygame.K_RETURN:
                    # play SFX on confirm and return
                    select_sfx.play()
                    return handle_selection(menu_items[selected_index])

            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, item in enumerate(menu_items):
                    if get_item_rect(i).collidepoint(mouse_pos):
                        select_sfx.play()
                        return handle_selection(item)

        # Hover detection with sound (plays once when hover changes)
        hovered_index = -1
        for i, item in enumerate(menu_items):
            if get_item_rect(i).collidepoint(mouse_pos):
                hovered_index = i
        if hovered_index != -1 and hovered_index != last_hover_index:
            select_sfx.play()
        last_hover_index = hovered_index

        draw_menu(mouse_pos)
        pygame.display.flip()

def handle_selection(choice):
    if choice == "Start Game":
        pygame.mixer.music.stop()
        return "game"
    elif choice == "Options":
        print("Options selected")
    elif choice == "Credits":
        print("Credits selected")
    elif choice == "Quit":
        pygame.quit()
        sys.exit()

def pause_menu(screen):
    global selected_index
    running = True

    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))

    pause_items = ["Resume", "Options", "Quit to Menu"]
    selected_index = 0
    last_hover_index = -1

    while running:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(pause_items)
                    select_sfx.play()
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(pause_items)
                    select_sfx.play()
                elif event.key == pygame.K_RETURN:
                    select_sfx.play()
                    choice = pause_items[selected_index]
                    if choice == "Resume":
                        return "resume"
                    elif choice == "Options":
                        print("Options (paused) selected")
                    elif choice == "Quit to Menu":
                        return "quit_to_menu"

            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, item in enumerate(pause_items):
                    rect = get_item_rect(i)
                    rect.centery = 250 + i * 60
                    if rect.collidepoint(mouse_pos):
                        select_sfx.play()
                        if item == "Resume":
                            return "resume"
                        elif item == "Options":
                            print("Options (paused) selected")
                        elif item == "Quit to Menu":
                            return "quit_to_menu"

        # Hover detection with sound (plays once when hovered item changes)
        hovered_index = -1
        for i, item in enumerate(pause_items):
            rect = get_item_rect(i)
            rect.centery = 250 + i * 60
            if rect.collidepoint(mouse_pos):
                hovered_index = i
        if hovered_index != -1 and hovered_index != last_hover_index:
            select_sfx.play()
        last_hover_index = hovered_index

        # Draw overlay
        screen.blit(overlay, (0, 0))

        # Draw pause title
        pause_font = pygame.font.Font("assets/fonts/BoldPixels.ttf", 48)
        pause_title = pause_font.render("Paused", True, YELLOW)
        screen.blit(pause_title, pause_title.get_rect(center=(WIDTH // 2, 150)))

        # Draw pause menu items
        for i, item in enumerate(pause_items):
            if i == selected_index or get_item_rect(i).collidepoint(mouse_pos):
                text = menu_font.render(item, True, YELLOW)
                text = pygame.transform.scale(text, (int(text.get_width() * 1.1), int(text.get_height() * 1.1)))
            else:
                text = menu_font.render(item, True, WHITE)

            rect = text.get_rect(center=(WIDTH // 2, 250 + i * 60))
            screen.blit(text, rect)

        pygame.display.flip()

if __name__ == "__main__":
    choice = menu_loop()
    print(f"Menu choice: {choice}")
