import random
from challenges.challenge_data import questions

# Keep track of used questions
used_questions = []

def get_question():
    """Return a random question that hasn't been used yet."""
    global used_questions

    # Get unused questions
    available = [q for q in questions if q not in used_questions]

    # If all have been used, reset the list
    if not available:
        used_questions.clear()
        available = questions.copy()

    # Pick one random unused question
    question = random.choice(available)
    used_questions.append(question)

    return question
