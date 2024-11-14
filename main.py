import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit,
                             QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox)
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
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Title", "Username", "Password", "Note"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.table)

        self.add_button = QPushButton("Add New Password")
        self.add_button.clicked.connect(self.add_password)
        main_layout.addWidget(self.add_button)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        self.load_passwords()

    def load_passwords(self):
        self.table.setRowCount(0)
        passwords = self.db.get_passwords()
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    manager = PasswordManager()
    manager.show()
    sys.exit(app.exec())
