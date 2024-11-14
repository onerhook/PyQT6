import random
import string

class PasswordGenerator:
    def __init__(self, length=12, include_digits=True, include_symbols=True):
        self.length = length
        self.include_digits = include_digits
        self.include_symbols = include_symbols

    def generate(self):
        characters = string.ascii_letters
        if self.include_digits:
            characters += string.digits
        if self.include_symbols:
            characters += string.punctuation
        return ''.join(random.choice(characters) for _ in range(self.length))
