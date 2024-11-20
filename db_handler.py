#db_handler.py

import sqlite3
import os
from cryptography.fernet import Fernet

class DBHandler:
    def __init__(self, db_name="passwords.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        try:
            with self.conn:
                self.conn.execute('''CREATE TABLE IF NOT EXISTS passwords
                                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                                      title TEXT NOT NULL,
                                      username TEXT NOT NULL,
                                      password TEXT NOT NULL,
                                      note TEXT)''')
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def add_password(self, title, username, password, note):
        try:
            with self.conn:
                self.conn.execute("INSERT INTO passwords (title, username, password, note) VALUES (?, ?, ?, ?)",
                                  (title, username, password, note))
        except sqlite3.Error as e:
            print(f"Error adding password: {e}")

    def get_passwords(self, filter_text=""):
        query = "SELECT id, title, username, password, note FROM passwords"
        if filter_text:
            query += " WHERE title LIKE ? OR username LIKE ?"
            return self.conn.execute(query, (f"%{filter_text}%", f"%{filter_text}%")).fetchall()
        return self.conn.execute(query).fetchall()



    def delete_password(self, password_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM passwords WHERE id = ?", (password_id,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error deleting password: {e}")


    def get_password_by_id(self, password_id):
        try:
            cursor = self.conn.execute("SELECT password FROM passwords WHERE id = ?", (password_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
