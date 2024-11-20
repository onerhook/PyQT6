#db_handler.py

import sqlite3

class DBHandler:
    def __init__(self, db_name="passwords.db"):
        self.db_name = db_name
        self.create_table()

    def create_table(self):
        """Создает таблицу, если она не существует."""
        query = '''
        CREATE TABLE IF NOT EXISTS passwords (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            note TEXT
        )
        '''
        self.execute_query(query)

    def execute_query(self, query, params=None):
        """Выполняет SQL-запросы."""
        if params is None:
            params = ()
        try:
            connection = sqlite3.connect(self.db_name)
            cursor = connection.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            connection.commit()
            connection.close()
            print(f"Executed query: {query} with params: {params}")  # Debug log
            return result
        except sqlite3.Error as e:
            print(f"Ошибка базы данных: {e}")
            return []
        except Exception as e:
            print(f"Общая ошибка: {e}")
            return []


    def get_passwords(self, filter_text=""):
        """Возвращает пароли с фильтрацией по тексту."""
        query = "SELECT * FROM passwords"
        if filter_text:
            query += f" WHERE name LIKE ? OR username LIKE ?"
            return self.execute_query(query, ('%' + filter_text + '%', '%' + filter_text + '%'))
        return self.execute_query(query)

    def add_password(self, name, username, password, note=""):
        """Добавляет новый пароль в базу данных."""
        query = "INSERT INTO passwords (name, username, password, note) VALUES (?, ?, ?, ?)"
        print(f"Adding password with: {name}, {username}, {password}, {note}")  # Debug log
        self.execute_query(query, (name, username, password, note))


    def delete_password(self, password_id):
        """Удаляет пароль из базы данных по ID."""
        query = "DELETE FROM passwords WHERE id = ?"
        self.execute_query(query, (password_id,))

    def get_all_passwords(self):
        """Получает все пароли."""
        query = "SELECT * FROM passwords"
        return self.execute_query(query)
