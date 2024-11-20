# csv_handler.py
import csv
from db_handler import DBHandler

class CSVHandler:
    def __init__(self, db_handler):
        self.db_handler = db_handler

    def export_to_csv(self, file_name="пароли.csv"):
        """Экспортирует данные из базы данных в CSV-файл."""
        passwords = self.db_handler.get_passwords()
        with open(file_name, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Название", "Логин", "Пароль", "Заметка"])
            writer.writerows(passwords)

    def import_from_csv(self, file_name="пароли.csv"):
        """Импортирует данные из CSV-файла в базу данных."""
        with open(file_name, "r") as file:
            reader = csv.reader(file)
            next(reader)  # Пропустить заголовок
            for row in reader:
                title, username, password, note = row
                self.db_handler.add_password(title, username, password, note)
