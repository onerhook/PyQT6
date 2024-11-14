class PasswordManagerError(Exception):
    """Базовый класс для исключений в менеджере паролей."""
    pass

class DatabaseError(PasswordManagerError):
    """Исключение для ошибок базы данных."""
    pass

class EncryptionError(PasswordManagerError):
    """Исключение для ошибок шифрования и дешифрования."""
    pass
