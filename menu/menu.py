import pygame
import sys
from utils.colors import WHITE, YELLOW

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("CodeSpire Menu")
clock = pygame.time.Clock()
FPS = 60

# --- Load background image ---
bg_image = pygame.image.load("assets/images/menu/menu_background/menu_bg.jpg").convert()
bg_image = pygame.transform.scale(bg_image, (WIDTH, HEIGHT))

# --- Fonts ---
title_font = pygame.font.Font("assets/fonts/BoldPixels.ttf", 72)
menu_font = pygame.font.Font("assets/fonts/BoldPixels.ttf", 36)

# --- Title text ---
title_surface = title_font.render("CodeSpire", True, YELLOW)
title_rect = title_surface.get_rect(center=(WIDTH // 2, 80))

# --- Menu items ---
menu_items = ["Start Game", "Options", "Credits", "Quit"]
selected_index = 0

# --- Sounds ---
select_sfx = pygame.mixer.Sound("assets/sounds/select_sfx.mp3")
select_sfx.set_volume(0.5)

# --- Volume settings (adjustable in options) ---
music_volume = 0.5
sfx_volume = 0.5


# --- Draw main menu ---
def draw_menu(mouse_pos):
    screen.blit(bg_image, (0, 0))
    screen.blit(title_surface, title_rect)

    for i, item in enumerate(menu_items):
        if i == selected_index or get_item_rect(i).collidepoint(mouse_pos):
            text = menu_font.render(item, True, YELLOW)
            text = pygame.transform.scale(text, (int(text.get_width() * 1.1), int(text.get_height() * 1.1)))
        else:
            text = menu_font.render(item, True, WHITE)

        rect = text.get_rect(center=(WIDTH // 2, 250 + i * 60))
        screen.blit(text, rect)


# --- Get rect for menu item ---
def get_item_rect(index):
    text = menu_font.render(menu_items[index], True, WHITE)
    return text.get_rect(center=(WIDTH // 2, 250 + index * 60))


# --- Main menu loop ---
def menu_loop():
    global selected_index
    running = True

    # Start menu music
    pygame.mixer.music.load("assets/sounds/menu_music.mp3")
    pygame.mixer.music.set_volume(music_volume)
    pygame.mixer.music.play(-1)

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
                    selected_index = (selected_index - 1) % len(menu_items)
                    select_sfx.play()
                elif event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(menu_items)
                    select_sfx.play()
                elif event.key == pygame.K_RETURN:
                    select_sfx.play()
                    return handle_selection(menu_items[selected_index])

            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, item in enumerate(menu_items):
                    if get_item_rect(i).collidepoint(mouse_pos):
                        select_sfx.play()
                        return handle_selection(item)

        hovered_index = -1
        for i, item in enumerate(menu_items):
            if get_item_rect(i).collidepoint(mouse_pos):
                hovered_index = i
        if hovered_index != -1 and hovered_index != last_hover_index:
            select_sfx.play()
        last_hover_index = hovered_index

        draw_menu(mouse_pos)
        pygame.display.flip()


# --- Handle menu selection ---
def handle_selection(choice):
    if choice == "Start Game":
        pygame.mixer.music.stop()
        return "game"
    elif choice == "Options":
        options_menu(screen)
    elif choice == "Credits":
        print("Credits selected")
    elif choice == "Quit":
        pygame.quit()
        sys.exit()


# --- Pause menu (during gameplay) ---
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
                        options_menu(screen)
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
                            options_menu(screen)
                        elif item == "Quit to Menu":
                            return "quit_to_menu"

        hovered_index = -1
        for i, item in enumerate(pause_items):
            rect = get_item_rect(i)
            rect.centery = 250 + i * 60
            if rect.collidepoint(mouse_pos):
                hovered_index = i
        if hovered_index != -1 and hovered_index != last_hover_index:
            select_sfx.play()
        last_hover_index = hovered_index

        screen.blit(overlay, (0, 0))
        pause_font = pygame.font.Font("assets/fonts/BoldPixels.ttf", 48)
        pause_title = pause_font.render("Paused", True, YELLOW)
        screen.blit(pause_title, pause_title.get_rect(center=(WIDTH // 2, 150)))

        for i, item in enumerate(pause_items):
            if i == selected_index or get_item_rect(i).collidepoint(mouse_pos):
                text = menu_font.render(item, True, YELLOW)
                text = pygame.transform.scale(text, (int(text.get_width() * 1.1), int(text.get_height() * 1.1)))
            else:
                text = menu_font.render(item, True, WHITE)

            rect = text.get_rect(center=(WIDTH // 2, 250 + i * 60))
            screen.blit(text, rect)

        pygame.display.flip()


# --- Options Menu ---
def options_menu(screen):
    global music_volume, sfx_volume

    running = True
    selected_slider = 0  # 0 = music, 1 = sfx
    sliders = ["Music Volume", "SFX Volume"]

    while running:
        clock.tick(FPS)
        screen.blit(bg_image, (0, 0))

        # Title
        title_font2 = pygame.font.Font("assets/fonts/BoldPixels.ttf", 48)
        title_surface = title_font2.render("Options", True, YELLOW)
        screen.blit(title_surface, title_surface.get_rect(center=(WIDTH // 2, 100)))

        # Draw sliders
        for i, label in enumerate(sliders):
            y_pos = 250 + i * 100
            text_color = YELLOW if i == selected_slider else WHITE
            text = menu_font.render(label, True, text_color)
            screen.blit(text, text.get_rect(center=(WIDTH // 2, y_pos - 40)))

            # Slider bar
            bar_x, bar_y, bar_w, bar_h = WIDTH // 2 - 150, y_pos, 300, 20
            pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 3)

            # Fill depending on current volume
            volume = music_volume if i == 0 else sfx_volume
            fill_w = int(bar_w * volume)
            pygame.draw.rect(screen, YELLOW, (bar_x, bar_y, fill_w, bar_h))

        # Instructions
        small_font = pygame.font.Font("assets/fonts/BoldPixels.ttf", 20)
        info = small_font.render("←/→ adjust • ↑/↓ switch • ESC to return", True, WHITE)
        screen.blit(info, info.get_rect(center=(WIDTH // 2, 500)))

        pygame.display.flip()

        # Input handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_UP:
                    selected_slider = (selected_slider - 1) % len(sliders)
                    select_sfx.play()
                elif event.key == pygame.K_DOWN:
                    selected_slider = (selected_slider + 1) % len(sliders)
                    select_sfx.play()
                elif event.key == pygame.K_LEFT:
                    if selected_slider == 0:
                        music_volume = max(0, music_volume - 0.1)
                        pygame.mixer.music.set_volume(music_volume)
                    else:
                        sfx_volume = max(0, sfx_volume - 0.1)
                        select_sfx.set_volume(sfx_volume)
                        select_sfx.play()
                elif event.key == pygame.K_RIGHT:
                    if selected_slider == 0:
                        music_volume = min(1, music_volume + 0.1)
                        pygame.mixer.music.set_volume(music_volume)
                    else:
                        sfx_volume = min(1, sfx_volume + 0.1)
                        select_sfx.set_volume(sfx_volume)
                        select_sfx.play()


# --- Main entry ---
if __name__ == "__main__":
    choice = menu_loop()
    print(f"Menu choice: {choice}")
