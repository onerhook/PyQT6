import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit,
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QInputDialog,
                             QHBoxLayout)
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

        # Кнопки для добавления и удаления
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add New Password")
        self.add_button.clicked.connect(self.add_password)
        button_layout.addWidget(self.add_button)

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_password)
        button_layout.addWidget(self.delete_button)

        main_layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        self.load_passwords()

    def load_passwords(self):
        filter_text = self.filter_input.text()
        self.table.setRowCount(0)
        passwords = self.db.get_passwords(filter_text)
        for row_number, row_data in enumerate(passwords):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data[1:]):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))

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
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a password to delete.")
            return

        record_id = self.table.item(selected_row, 0).text()  # ID хранится в первом столбце
        self.db.delete_password(int(record_id))
        self.load_passwords()
        QMessageBox.information(self, "Password Deleted", "The selected password was deleted.")
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = PasswordManager()
    manager.show()
    sys.exit(app.exec())
