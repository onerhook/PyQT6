# exceptions.py

class PasswordManagerError(Exception):
    """Базовый класс для исключений в менеджере паролей."""
    pass

class DatabaseError(PasswordManagerError):
    """Исключение для ошибок базы данных."""
    pass

class PasswordStrengthError(PasswordManagerError):
    """Исключение для слабых паролей."""
    def __init__(self, message="Пароль слишком слабый."):
        super().__init__(message)
