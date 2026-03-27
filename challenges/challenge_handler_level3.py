import random
from challenges.question_data import level3_questions

# Track used Level 3 questions
used_questions_level3 = []

def get_question_level3():
    """Return a random Level 3 question that hasn't been used yet."""
    global used_questions_level3

    # Filter unused questions
    available = [q for q in level3_questions if q not in used_questions_level3]

    # If all used, reset and start again
    if not available:
        used_questions_level3.clear()
        available = level3_questions.copy()

    # Pick a random unused question
    question = random.choice(available)
    used_questions_level3.append(question)

    return question
