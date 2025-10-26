import random

# List of JavaScript questions and answers
questions_level2 = [
    {"question": "What does JS mean?", "answer": "s"}
]

# Track used questions
used_questions_level2 = []

def get_question_level2():
    """Return a random JavaScript question that hasn't been used yet."""
    global used_questions_level2

    # Get unused questions
    available = [q for q in questions_level2 if q not in used_questions_level2]

    # If all used, reset
    if not available:
        used_questions_level2.clear()
        available = questions_level2.copy()

    # Pick one random unused question
    question = random.choice(available)
    used_questions_level2.append(question)

    return question
