import random
from challenges.challenge_data import questions

def get_question():
    return random.choice(questions)
