import sys
import csv
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit,
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QInputDialog,
                             QHBoxLayout, QFileDialog)
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import Qt
import sqlite3
from db_handler import DBHandler
from password_generator import PasswordGenerator

class PasswordManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DBHandler()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Password Manager")
        self.setGeometry(200, 200, 600, 400)
        self.show_passwords = False  # Переменная для отслеживания видимости паролей

        main_layout = QVBoxLayout()

        # Поле для фильтрации
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter by title or username")
        self.filter_input.textChanged.connect(self.load_passwords)
        main_layout.addWidget(self.filter_input)

        # Таблица для отображения паролей
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Title", "Username", "Password", "Note"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.table)

        # Кнопки для управления
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add New Password")
        self.add_button.clicked.connect(self.add_password)
        button_layout.addWidget(self.add_button)

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_password)
        button_layout.addWidget(self.delete_button)

        self.copy_button = QPushButton("Copy Password")
        self.copy_button.clicked.connect(self.copy_password)
        button_layout.addWidget(self.copy_button)

        self.edit_button = QPushButton("Edit Selected")
        self.edit_button.clicked.connect(self.edit_password)
        button_layout.addWidget(self.edit_button)

        self.visibility_button = QPushButton("Show/Hide Passwords")
        self.visibility_button.clicked.connect(self.toggle_password_visibility)
        button_layout.addWidget(self.visibility_button)

        main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        self.load_passwords()


    def load_passwords(self):
        filter_text = self.filter_input.text()
        self.table.setRowCount(0)
        passwords = self.db.get_passwords(filter_text)  # Предполагается, что результат содержит ID
        
        for row_number, row_data in enumerate(passwords):
            self.table.insertRow(row_number)

            # Добавляем ID в скрытую колонку (нулевой индекс)
            id_item = QTableWidgetItem(str(row_data[0]))  # ID
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Делает ID только для чтения
            self.table.setItem(row_number, 0, id_item)

            # Добавляем остальные данные
            for column_number, data in enumerate(row_data[1:], start=1):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        
        self.table.setColumnHidden(0, True)  # Скрываем колонку ID


    def add_password(self):
        title, ok = QInputDialog.getText(self, "Title", "Enter title:")
        if not ok or not title:
            return

        username, ok = QInputDialog.getText(self, "Username", "Enter username:")
        if not ok:
            return

        generator = PasswordGenerator()
        password = generator.generate()

        note, ok = QInputDialog.getText(self, "Note", "Enter note (optional):")
        if not ok:
            note = ""

        self.db.add_password(title, username, password, note)
        self.load_passwords()
        QMessageBox.information(self, "Password Added", f"Generated password: {password}")

    def delete_password(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Delete Error", "Please select a password to delete.")
            return

        password_id = self.table.item(row, 0).text()  # Получаем ID пароля (первая колонка)
        try:
            self.db.delete_password(password_id)
            self.load_passwords()
            QMessageBox.information(self, "Password Deleted", "The password has been deleted.")
        except Exception as e:
            QMessageBox.warning(self, "Delete Error", f"Error while deleting password: {e}")

    def copy_password(self):
        try:
            row = self.table.currentRow()  # Текущая выделенная строка
            if row == -1:
                QMessageBox.warning(self, "Copy Error", "Please select a password to copy.")
                return

            # Получаем ID из первой колонки
            password_id_item = self.table.item(row, 0)
            if not password_id_item:
                QMessageBox.warning(self, "Copy Error", "Could not retrieve the password ID.")
                return

            password_id = int(password_id_item.text())  # Преобразуем ID в число

            # Получаем пароль из базы данных
            password = self.db.get_password_by_id(password_id)
            if not password:
                QMessageBox.warning(self, "Copy Error", "Password not found in the database.")
                return

            # Копируем пароль в буфер обмена
            QGuiApplication.clipboard().setText(password)
            QMessageBox.information(self, "Password Copied", "Password has been copied to clipboard.")

        except ValueError:
            QMessageBox.critical(self, "Error", "Invalid password ID.")
        except Exception as e:
            QMessageBox.critical(self, "Unexpected Error", f"An unexpected error occurred:\n{str(e)}")



    def toggle_password_visibility(self):
        if self.show_passwords:
            self.show_passwords = False
            self.load_passwords()
        else:
            self.show_passwords = True
            self.load_passwords()
            
    def edit_password(self):
        row = self.table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Edit Error", "Please select a password to edit.")
            return

        # Получаем текущие значения
        password_id = self.table.item(row, 0).text()
        title = self.table.item(row, 0).text()
        username = self.table.item(row, 1).text()
        password = self.table.item(row, 2).text()
        note = self.table.item(row, 3).text()

        # Диалоги для ввода новых данных
        new_title, ok = QInputDialog.getText(self, "Edit Title", "Enter new title:", text=title)
        if not ok or not new_title:
            return

        new_username, ok = QInputDialog.getText(self, "Edit Username", "Enter new username:", text=username)
        if not ok:
            return

        new_password, ok = QInputDialog.getText(self, "Edit Password", "Enter new password:", text=password)
        if not ok:
            return

        new_note, ok = QInputDialog.getText(self, "Edit Note", "Enter new note:", text=note)
        if not ok:
            new_note = ""

        # Обновляем запись в базе данных
        self.db.update_password(password_id, new_title, new_username, new_password, new_note)
        self.load_passwords()
        QMessageBox.information(self, "Password Updated", "Password has been updated successfully.")


    def load_passwords(self):
        filter_text = self.filter_input.text()
        self.table.setRowCount(0)
        passwords = self.db.get_passwords(filter_text)
        for row_number, row_data in enumerate(passwords):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data[1:]):
                if column_number == 2 and not self.show_passwords:
                    self.table.setItem(row_number, column_number, QTableWidgetItem("***"))
                else:
                    self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

    # Функция экспорта паролей в CSV
    def export_passwords(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", "CSV Files (*.csv)")
        if not file_name:
            return

        passwords = self.db.get_passwords("")
        try:
            with open(file_name, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Title", "Username", "Password", "Note"])
                for password in passwords:
                    writer.writerow(password[1:])
            QMessageBox.information(self, "Export Complete", "Passwords have been exported successfully.")
        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"Error while exporting passwords: {e}")

    # Функция импорта паролей из CSV
    def import_passwords(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "CSV Files (*.csv)")
        if not file_name:
            return

        try:
            with open(file_name, mode='r', encoding='utf-8') as file:
                reader = csv.reader(file)
                next(reader)  # Пропускаем заголовок
                for row in reader:
                    if len(row) == 4:
                        title, username, password, note = row
                        self.db.add_password(title, username, password, note)
            self.load_passwords()
            QMessageBox.information(self, "Import Complete", "Passwords have been imported successfully.")
        except Exception as e:
            QMessageBox.warning(self, "Import Error", f"Error while importing passwords: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = PasswordManager()
    manager.show()
    sys.exit(app.exec())
