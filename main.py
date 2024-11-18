import sys
import csv
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit,
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QInputDialog,
                             QHBoxLayout, QFileDialog, QDialog, QCheckBox, QSpinBox, QTextEdit)
from PyQt6.QtGui import QGuiApplication, QPalette, QColor
from PyQt6.QtCore import Qt
from db_handler import DBHandler
from password_generator import PasswordGenerator

class PasswordManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DBHandler()
        self.password_generator_settings = {
            "length": 12,
            "use_digits": True,
            "use_special_chars": True
        }
        self.show_passwords = False
        self.dark_theme_enabled = False

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Password Manager")
        self.setGeometry(200, 200, 800, 600)

        main_layout = QVBoxLayout()

        # Filter field
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter by title or username")
        self.filter_input.textChanged.connect(self.load_passwords)
        main_layout.addWidget(self.filter_input)

        # Password table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Title", "Username", "Password", "Note"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.table)

        # Button panel
        button_layout = QHBoxLayout()

        self.add_button = QPushButton("Add Password")
        self.add_button.clicked.connect(self.add_password)
        button_layout.addWidget(self.add_button)

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_password)
        button_layout.addWidget(self.delete_button)

        self.edit_button = QPushButton("Edit Selected")
        self.edit_button.clicked.connect(self.edit_password)
        button_layout.addWidget(self.edit_button)

        self.visibility_button = QPushButton("Show/Hide Passwords")
        self.visibility_button.clicked.connect(self.toggle_password_visibility)
        button_layout.addWidget(self.visibility_button)

        self.settings_button = QPushButton("Password Settings")
        self.settings_button.clicked.connect(self.open_password_settings)
        button_layout.addWidget(self.settings_button)

        self.export_button = QPushButton("Export Passwords")
        self.export_button.clicked.connect(self.export_passwords)
        button_layout.addWidget(self.export_button)

        self.import_button = QPushButton("Import Passwords")
        self.import_button.clicked.connect(self.import_passwords)
        button_layout.addWidget(self.import_button)

        self.theme_button = QPushButton("Toggle Theme")
        self.theme_button.clicked.connect(self.toggle_theme)
        button_layout.addWidget(self.theme_button)

        self.help_button = QPushButton("Help")
        self.help_button.clicked.connect(self.show_help)
        button_layout.addWidget(self.help_button)

        main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.load_passwords()

    def toggle_theme(self):
        palette = QApplication.instance().palette()
        if self.dark_theme_enabled:
            # Revert to default light theme
            QApplication.instance().setPalette(QPalette())
            self.dark_theme_enabled = False
        else:
            # Apply dark theme
            dark_palette = QPalette()
            dark_palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(220, 220, 220))
            dark_palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
            dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(220, 220, 220))
            dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(220, 220, 220))
            dark_palette.setColor(QPalette.ColorRole.Text, QColor(220, 220, 220))
            dark_palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(220, 220, 220))
            dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(220, 220, 220))
            QApplication.instance().setPalette(dark_palette)
            self.dark_theme_enabled = True

    def show_help(self):
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("Help")
        help_dialog.setGeometry(300, 300, 500, 400)

        layout = QVBoxLayout(help_dialog)
        help_text = QTextEdit(help_dialog)
        help_text.setReadOnly(True)
        help_text.setText("""
        Welcome to Password Manager!

        Features:
        - Add, edit, and delete passwords.
        - Filter passwords by title or username.
        - Import/export password data.
        - Toggle between light and dark themes.
        - Configure password generation settings.
        - Securely manage your credentials.

        Buttons:
        - Add Password: Create a new password entry.
        - Delete Selected: Remove the selected password.
        - Show/Hide Passwords: Toggle password visibility.
        - Password Settings: Adjust generator preferences.
        - Toggle Theme: Switch between light and dark themes.
        - Help: View this help dialog.
        """)
        layout.addWidget(help_text)
        help_dialog.setLayout(layout)
        help_dialog.exec()

    def delete_password(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Error", "Please select a row to delete.")
            return

        title = self.table.item(selected_row, 0).text()
        username = self.table.item(selected_row, 1).text()

        confirmation = QMessageBox.question(
            self,
            "Delete Password",
            f"Are you sure you want to delete the password for {title} ({username})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirmation == QMessageBox.StandardButton.Yes:
            self.db.delete_password(title, username)
            self.load_passwords()
            QMessageBox.information(self, "Success", "Password deleted successfully.")


    def open_password_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Password Generator Settings")

        layout = QVBoxLayout(dialog)

        # Password length
        length_label = QLabel("Password Length:")
        layout.addWidget(length_label)

        length_spinbox = QSpinBox()
        length_spinbox.setMinimum(6)
        length_spinbox.setMaximum(32)
        length_spinbox.setValue(self.password_generator_settings["length"])
        layout.addWidget(length_spinbox)

        # Include digits
        digits_checkbox = QCheckBox("Include Digits")
        digits_checkbox.setChecked(self.password_generator_settings["use_digits"])
        layout.addWidget(digits_checkbox)

        # Include special characters
        special_chars_checkbox = QCheckBox("Include Special Characters")
        special_chars_checkbox.setChecked(self.password_generator_settings["use_special_chars"])
        layout.addWidget(special_chars_checkbox)

        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(lambda: self.save_password_settings(dialog, length_spinbox, digits_checkbox, special_chars_checkbox))
        layout.addWidget(save_button)

        dialog.setLayout(layout)
        dialog.exec()

    def save_password_settings(self, dialog, length_spinbox, digits_checkbox, special_chars_checkbox):
        self.password_generator_settings["length"] = length_spinbox.value()
        self.password_generator_settings["use_digits"] = digits_checkbox.isChecked()
        self.password_generator_settings["use_special_chars"] = special_chars_checkbox.isChecked()
        dialog.accept()


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
