import pygame
import textwrap

def ask_question(screen, question_func):
    """
    Ask a question on screen, return True if correct, False if wrong/quit.
    Works with flexible answers (list of acceptable answers).
    """
    question_data = question_func()  # get dict from question file
    question = question_data["question"]
    correct_answers = question_data.get("answers", [question_data.get("answer", "")])

    font = pygame.font.Font(None, 36)
    input_font = pygame.font.Font(None, 32)
    user_text = ''
    input_active = True
    clock = pygame.time.Clock()

    # --- Box layout ---
    box_width, box_height = 700, 400
    box_x = (screen.get_width() - box_width) // 2
    box_y = (screen.get_height() - box_height) // 2
    box_rect = pygame.Rect(box_x, box_y, box_width, box_height)

    # --- Text wrapping for question ---
    wrapped_lines = textwrap.wrap(question, width=50)

    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                    user_input = user_text.strip().lower()
                    # --- Ignore empty input ---
                    if not user_input:
                        return False
                    # --- Check flexible answers ---
                    is_correct = any(user_input in ans.lower() for ans in correct_answers)
                    return is_correct
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    user_text += event.unicode

        # --- Dim background ---
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # --- Draw question box ---
        pygame.draw.rect(screen, (50, 50, 120), box_rect, border_radius=16)
        pygame.draw.rect(screen, (255, 255, 255), box_rect, 3, border_radius=16)

        # --- Draw question text ---
        y_offset = box_y + 40
        for line in wrapped_lines:
            q_surf = font.render(line, True, (255, 255, 255))
            screen.blit(q_surf, (box_x + 25, y_offset))
            y_offset += 40

        # --- Draw input text ---
        prompt = input_font.render("Type your answer:", True, (255, 255, 255))
        a_surf = input_font.render(user_text, True, (255, 255, 0))
        screen.blit(prompt, (box_x + 25, box_y + box_height - 90))
        screen.blit(a_surf, (box_x + 25, box_y + box_height - 50))

        pygame.display.flip()
        clock.tick(30)
