"""Play a joke for the user."""

import random

from app.voice.speak import speak


def joke_command(jokes: dict[str, dict[str, str]]) -> bool:
    """Choose a random joke and speak both the question and answer."""
    joke = random.choice(list(jokes.values()))
    question = joke["question"]
    answer = joke["answer"]

    speak(question + " " + answer)

    return True
