import random
from app.voice.speak import speak


def joke_command(jokes):
    joke = random.choice(list(jokes.values()))
    question = joke["question"]
    answer = joke["answer"]

    speak(question + " " + answer)

    return True