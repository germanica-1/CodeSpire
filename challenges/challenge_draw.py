import pygame
from challenges.challenge_handler import get_question

def ask_question(screen):
    """Ask a question on screen, return True if correct, False if wrong/quit"""
    question_data = get_question()
    question = question_data["question"]
    answer = question_data["answer"]

    font = pygame.font.Font(None, 32)
    user_text = ''
    input_active = True
    clock = pygame.time.Clock()

    while input_active:
        screen.fill((0, 0, 0))

        # Render question + user input
        q_surf = font.render(question, True, (255, 255, 255))
        a_surf = font.render(user_text, True, (255, 255, 0))

        screen.blit(q_surf, (50, 200))
        screen.blit(a_surf, (50, 250))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # treat quit as incorrect
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                    return user_text.strip().lower() == answer.lower()
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    user_text += event.unicode

        clock.tick(30)
        