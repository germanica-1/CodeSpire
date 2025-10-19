import random

# List of .NET questions and answers
questions_level2 = [
    {"question": "What does .NET stand for?", "answer": "s"}
]

def get_question_level2():
    """Return a random .NET question."""
    return random.choice(questions_level2)
