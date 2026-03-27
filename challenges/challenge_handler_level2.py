import random

# List of JavaScript and Java questions and answers
questions_level2 = [
    # --- JAVASCRIPT (12 questions) ---
    {"question": "JavaScript: What does JS mean?", "answers": ["javascript", "js"]},
    {"question": "JavaScript: How do you show a message?", "answers": ["alert()", "alert"]},
    {"question": "JavaScript: How do you print on console?", "answers": ["console.log()", "console.log", "console log"]},
    {"question": "JavaScript: How do you make a variable?", "answers": ["var"]},
    {"question": "JavaScript: How do you make a constant?", "answers": ["const"]},
    {"question": "JavaScript: How do you make a block variable?", "answers": ["let"]},
    {"question": "JavaScript: What symbol is used for single line comments?", "answers": ["//", "slash slash"]},
    {"question": "JavaScript: What type means true or false?", "answers": ["boolean", "bool"]},
    {"question": "JavaScript: What means nothing?", "answers": ["null"]},
    {"question": "JavaScript: What keyword makes a function?", "answers": ["function"]},
    {"question": "JavaScript: What keyword checks a condition?", "answers": ["if"]},
    {"question": "JavaScript: What loop runs many times?", "answers": ["for"]},

    # --- JAVA (13 questions) ---
    {"question": "Java: What does JVM mean?", "answers": ["java virtual machine", "jvm"]},
    {"question": "Java: How do you print text in Java?", "answers": ["system.out.println()", "println()", "system.out.print", "system out print"]},
    {"question": "Java: What is the main method in Java?", "answers": ["public static void main(string[] args)", "public static void main"]},
    {"question": "Java: What keyword makes a class?", "answers": ["class"]},
    {"question": "Java: What symbol ends a statement?", "answers": [";", "semicolon"]},
    {"question": "Java: What keyword makes a constant?", "answers": ["const"]},
    {"question": "Java: What keyword checks a condition?", "answers": ["if"]},
    {"question": "Java: What loop runs many times?", "answers": ["for"]},
    {"question": "Java: What keyword stops a loop?", "answers": ["break"]},
    {"question": "Java: How do you join two strings?", "answers": ["+", "concatenate", "concatenation"]},
    {"question": "Java: What gives the length of a string?", "answers": ["length()", "length"]},
]

# Track used questions
used_questions_level2 = []

def get_question_level2():
    """Return a random Level 2 question that hasn't been used yet."""
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
