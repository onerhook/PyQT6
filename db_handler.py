import sqlite3
from cryptography.fernet import Fernet

class DBHandler:
    def __init__(self, db_name="passwords.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()
        # Секретный ключ для шифрования
        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)

    def create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS passwords (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    username TEXT,
                    password TEXT,
                    note TEXT
                )
            """)

    def add_password(self, title, username, password, note):
        encrypted_password = self.cipher_suite.encrypt(password.encode())
        with self.conn:
            self.conn.execute("INSERT INTO passwords (title, username, password, note) VALUES (?, ?, ?, ?)",
                              (title, username, encrypted_password, note))

    def get_passwords(self):
        with self.conn:
            data = self.conn.execute("SELECT id, title, username, password, note FROM passwords").fetchall()
            return [(row[0], row[1], row[2], self.cipher_suite.decrypt(row[3]).decode(), row[4]) for row in data]

    def delete_password(self, record_id):
        with self.conn:
            self.conn.execute("DELETE FROM passwords WHERE id = ?", (record_id,))
