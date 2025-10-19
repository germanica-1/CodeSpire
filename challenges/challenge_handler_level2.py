import random

# List of .NET questions and answers
questions_level2 = [
    {"question": "What does .NET stand for?", "answer": "Network Enabled Technologies"},
    {"question": "Who developed the .NET Framework?", "answer": "Microsoft"},
    {"question": "What language is commonly used in .NET?", "answer": "C#"},
    {"question": "What does CLR stand for?", "answer": "Common Language Runtime"},
    {"question": "What does CLS stand for?", "answer": "Common Language Specification"},
    {"question": "What does CTS stand for?", "answer": "Common Type System"},
    {"question": "What is the entry point of a C# program?", "answer": "Main"},
    {"question": "What is the file extension of a C# file?", "answer": ".cs"},
    {"question": "What does ASP.NET stand for?", "answer": "Active Server Pages .NET"},
    {"question": "What does ADO.NET stand for?", "answer": "ActiveX Data Objects .NET"},
    {"question": "Which method displays output in C#?", "answer": "Console.WriteLine()"},
    {"question": "Which keyword defines a class?", "answer": "class"},
    {"question": "Which keyword creates an object?", "answer": "new"},
    {"question": "Which data type stores whole numbers?", "answer": "int"},
    {"question": "Which data type stores text?", "answer": "string"},
    {"question": "Which keyword makes a variable constant?", "answer": "const"},
    {"question": "Which symbol is used for single-line comments?", "answer": "//"},
    {"question": "Which keyword is used for inheritance?", "answer": "extends"},
    {"question": "Which keyword defines a method?", "answer": "void"},
    {"question": "Which keyword handles exceptions?", "answer": "try"},
    {"question": "Which keyword exits a loop?", "answer": "break"},
    {"question": "Which collection stores key-value pairs?", "answer": "Dictionary"},
    {"question": "Which keyword defines an interface?", "answer": "interface"},
    {"question": "What is the main purpose of .NET Framework?", "answer": "Run applications"},
    {"question": "What is the latest .NET platform called?", "answer": ".NET Core"},
]

def get_question_level2():
    """Return a random .NET question."""
    return random.choice(questions_level2)
