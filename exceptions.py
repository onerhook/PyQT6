class PasswordManagerError(Exception):
    """базовый класс для исключений в менеджере паролей"""
    pass


class DatabaseError(PasswordManagerError):
    """исключение для ошибок базы данных"""
    pass


class PasswordStrengthError(PasswordManagerError):
    """исключение для слабых паролей"""

    def __init__(self, message="пароль слишком слабый"):
        super().__init__(message)
