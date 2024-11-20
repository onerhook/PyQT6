#password_generator.py
import random
import string


class PasswordGenerator:
    def __init__(self, length=12, use_digits=True, use_special_chars=True):
        # делаем параметры настраиваемыми
        self.length = length
        self.use_digits = use_digits
        self.use_special_chars = use_special_chars

    def generate(self):
        """генерирует случайный пароль"""
        characters = string.ascii_letters  # буквы (верхний и нижний регистры)
        if self.use_digits:
            characters += string.digits  # цифры
        if self.use_special_chars:
            characters += string.punctuation  # спецсимволы

        if self.length < 8:
            raise ValueError("Длина пароля должна быть не менее 8 символов.")
        return ''.join(random.choice(characters) for _ in range(self.length))

    @staticmethod
    def is_strong(password):
        """проверяет сложность пароля"""
        if len(password) < 8:
            return False
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in string.punctuation for c in password)
        return all([has_upper, has_lower, has_digit, has_special])

