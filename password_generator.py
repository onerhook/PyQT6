# password_generator.py

import random
import string

class PasswordGenerator:
    def __init__(self, length=12, use_digits=True, use_special_chars=True):
        self.length = length
        self.use_digits = use_digits
        self.use_special_chars = use_special_chars

    def generate(self):
        characters = string.ascii_letters  # Используем буквы (верхний и нижний регистр)
        
        if self.use_digits:
            characters += string.digits  # Добавляем цифры

        if self.use_special_chars:
            characters += string.punctuation  # Добавляем специальные символы

        # Генерация пароля случайным образом из доступных символов
        password = ''.join(random.choice(characters) for _ in range(self.length))
        
        return password
