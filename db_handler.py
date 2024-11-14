import sqlite3
import os
from cryptography.fernet import Fernet

class DBHandler:
    def __init__(self, db_name="passwords.db", key_file="secret.key"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()
        self.key = self.load_key(key_file)
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

    def load_key(self, key_file):
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key

    def add_password(self, title, username, password, note):
        encrypted_password = self.cipher_suite.encrypt(password.encode())
        with self.conn:
            self.conn.execute("INSERT INTO passwords (title, username, password, note) VALUES (?, ?, ?, ?)",
                              (title, username, encrypted_password, note))

    def get_passwords(self, filter_text=""):
        query = "SELECT id, title, username, password, note FROM passwords"
        if filter_text:
            query += " WHERE title LIKE ? OR username LIKE ?"
            params = (f"%{filter_text}%", f"%{filter_text}%")
        else:
            params = ()
        with self.conn:
            data = self.conn.execute(query, params).fetchall()
            return [(row[0], row[1], row[2], self.cipher_suite.decrypt(row[3]).decode(), row[4]) for row in data]

    def delete_password(self, record_id):
        with self.conn:
            self.conn.execute("DELETE FROM passwords WHERE id = ?", (record_id,))
