import csv
from db_handler import DBHandler

class CSVHandler:
    def __init__(self, db_handler):
        self.db_handler = db_handler

    def export_to_csv(self, file_name="passwords.csv"):
        passwords = self.db_handler.get_passwords()
        with open(file_name, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Title", "Username", "Password", "Note"])
            writer.writerows(passwords)

    def import_from_csv(self, file_name="passwords.csv"):
        with open(file_name, "r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                title, username, password, note = row
                self.db_handler.add_password(title, username, password, note)
