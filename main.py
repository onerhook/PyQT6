# main.py
import sys
import re
import csv
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLineEdit,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QInputDialog,
    QHBoxLayout, QFileDialog, QDialog, QCheckBox, QSpinBox, QTextEdit, QProgressBar
)
from PyQt6.QtGui import QPalette, QColor
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
        self.setWindowTitle("Менеджер Паролей")
        self.setGeometry(200, 200, 800, 600)

        main_layout = QVBoxLayout()

        # поле фильтрации
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Фильтровать по названию или имени пользователя")
        self.filter_input.textChanged.connect(self.load_passwords)
        main_layout.addWidget(self.filter_input)

        # таблица паролей
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Имя пользователя", "Пароль", "Заметка"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.table)

        # панель кнопок
        button_layout = QHBoxLayout()

        self.add_button = QPushButton("Добавить пароль")
        self.add_button.clicked.connect(self.add_password)
        button_layout.addWidget(self.add_button)

        self.refresh_button = QPushButton("Обновить")
        self.refresh_button.clicked.connect(self.refresh_data)
        button_layout.addWidget(self.refresh_button)

        self.delete_button = QPushButton("Удалить выделенное")
        self.delete_button.clicked.connect(self.delete_password)
        button_layout.addWidget(self.delete_button)

        self.visibility_button = QPushButton("Показать/Скрыть пароли")
        self.visibility_button.clicked.connect(self.toggle_password_visibility)
        button_layout.addWidget(self.visibility_button)

        self.settings_button = QPushButton("Настройки генератора")
        self.settings_button.clicked.connect(self.open_password_settings)
        button_layout.addWidget(self.settings_button)

        self.export_button = QPushButton("Экспорт паролей")
        self.export_button.clicked.connect(self.export_passwords)
        button_layout.addWidget(self.export_button)

        self.import_button = QPushButton("Импорт паролей")
        self.import_button.clicked.connect(self.import_passwords)
        button_layout.addWidget(self.import_button)

        self.theme_button = QPushButton("Сменить тему")
        self.theme_button.clicked.connect(self.toggle_theme)
        button_layout.addWidget(self.theme_button)

        self.help_button = QPushButton("Помощь")
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
            QApplication.instance().setPalette(QPalette())
            self.dark_theme_enabled = False
        else:
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
        help_dialog.setWindowTitle("Помощь")
        help_dialog.setGeometry(300, 300, 500, 400)

        layout = QVBoxLayout(help_dialog)
        help_text = QTextEdit(help_dialog)
        help_text.setReadOnly(True)
        help_text.setText("""\
Добро пожаловать в Менеджер Паролей!

Возможности:
- Добавление и удаление паролей.
- Фильтрация паролей по названию или имени пользователя.
- Импорт/экспорт данных о паролях.
- Смена темы приложения.
- Настройки генерации паролей.
- Удобное управление вашими учетными данными.

Кнопки:
- Добавить пароль: Создать новую запись.
- Удалить выделенное: Удалить выбранный пароль.
- Показать/Скрыть пароли: Переключить видимость паролей.
- Настройки генератора: Изменить параметры генерации.
- Экспорт/Импорт: Сохранить или загрузить данные.
- Сменить тему: Переключить светлую/темную тему.
""")
        layout.addWidget(help_text)
        help_dialog.setLayout(layout)
        help_dialog.exec()

    def delete_password(self):
        # получаем индекс выбранной строки
        selected_row = self.table.currentRow()
        
        # проверяем, что строка выбрана (индекс больше или равен 0)
        if selected_row < 0:
            QMessageBox.warning(self, 'Предупреждение', 'Пожалуйста, выберите строку для удаления.')
            return

        # получаем ID пароля из первой ячейки выбранной строки (предположим, что это ID)
        id_item = self.table.item(selected_row, 0)  # ID должно быть в первой ячейке, если вы его добавляли в таблицу
        if id_item is None:
            QMessageBox.warning(self, 'Ошибка', 'Не удалось найти ID для удаления.')
            return
        
        password_id = int(id_item.text())  # преобразуем в целое число для использования в SQL-запросе

        # создаём объект DBHandler для работы с базой данных
        db_handler = DBHandler()

        # удаляем пароль из базы данных
        try:
            db_handler.delete_password(password_id)  # удаляем пароль по ID из базы данных
            self.table.removeRow(selected_row)  # удаляем строку из таблицы в интерфейсе

            # уведомляем пользователя об успешном удалении
            QMessageBox.information(self, 'Успех', 'Пароль был успешно удалён.')

        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Не удалось удалить пароль: {e}')

    def open_password_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Настройки генератора паролей")

        layout = QVBoxLayout(dialog)

        # длина пароля
        length_label = QLabel("Длина пароля:")
        layout.addWidget(length_label)

        length_spinbox = QSpinBox()
        length_spinbox.setMinimum(6)
        length_spinbox.setMaximum(32)
        length_spinbox.setValue(self.password_generator_settings["length"])
        layout.addWidget(length_spinbox)

        # включить цифры
        digits_checkbox = QCheckBox("Включить цифры")
        digits_checkbox.setChecked(self.password_generator_settings["use_digits"])
        layout.addWidget(digits_checkbox)

        # включить специальные символы
        special_chars_checkbox = QCheckBox("Включить спецсимволы")
        special_chars_checkbox.setChecked(self.password_generator_settings["use_special_chars"])
        layout.addWidget(special_chars_checkbox)

        # сохранить настройки
        save_button = QPushButton("Сохранить")
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
        self.table.setRowCount(0)
        passwords = self.db.get_passwords(self.filter_input.text())
        for row_number, row_data in enumerate(passwords):
            self.table.insertRow(row_number)
            self.table.setItem(row_number, 0, QTableWidgetItem(str(row_data[0])))  # ID
            for column_number, data in enumerate(row_data[1:], start=1):  # начинаем с 1 для остальных колонок
                if column_number == 2 and not self.show_passwords:
                    self.table.setItem(row_number, column_number, QTableWidgetItem("***"))
                else:
                    self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))


    def toggle_password_visibility(self):
        self.show_passwords = not self.show_passwords
        self.load_passwords()

    def add_password(self):
        # выбор способа добавления пароля
        choice, ok = QInputDialog.getItem(
            self,
            "Добавить пароль",
            "Выберите метод добавления пароля:",
            ["Вручную", "Сгенерировать"],
            0, False
        )

        if ok:
            if choice == "Вручную":
                self.add_password_manually()
            else:
                self.add_password_generated()

    def add_password_manually(self):
        """окно для ввода пароля вручную"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить пароль вручную")

        layout = QVBoxLayout(dialog)

        name_input = QLineEdit()
        name_input.setPlaceholderText("Заметка(не обязательно)")
        layout.addWidget(name_input)

        username_input = QLineEdit()
        username_input.setPlaceholderText("Имя пользователя")
        layout.addWidget(username_input)

        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.EchoMode.Password)
        password_input.setPlaceholderText("Пароль")
        layout.addWidget(password_input)

        # прогресс-бар для сложности пароля
        complexity_progress = QProgressBar()
        complexity_progress.setMaximum(5)  # максимальное значение сложности (5 факторов)
        complexity_progress.setValue(0)
        layout.addWidget(complexity_progress)

        password_strength_label = QLabel("Сложность пароля: Низкая")
        layout.addWidget(password_strength_label)

        def update_password_complexity():
            password = password_input.text()
            try:
                complexity = self.evaluate_complexity(password)
                complexity_progress.setValue(complexity)

                # обновляем текст в зависимости от сложности
                if complexity == 0:
                    password_strength_label.setText("Сложность пароля: Очень слабый")
                elif complexity == 1:
                    password_strength_label.setText("Сложность пароля: Слабый")
                elif complexity == 2:
                    password_strength_label.setText("Сложность пароля: Средний")
                elif complexity == 3:
                    password_strength_label.setText("Сложность пароля: Хороший")
                elif complexity == 4 or complexity == 5:
                    password_strength_label.setText("Сложность пароля: Очень сильный")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Ошибка при вычислении сложности пароля: {str(e)}")

        # родключение к сигналу изменения текста в поле пароля
        password_input.textChanged.connect(update_password_complexity)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(lambda: self.save_password_manually(dialog, name_input, username_input, password_input))
        layout.addWidget(save_button)

        dialog.setLayout(layout)
        dialog.exec()

    @staticmethod
    def evaluate_complexity(password):
        """оценка сложности пароля"""
        length_score = len(password) >= 12
        has_uppercase = bool(re.search(r"[A-Z]", password))
        has_lowercase = bool(re.search(r"[a-z]", password))
        has_digit = bool(re.search(r"\d", password))
        has_special = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))

        complexity = 0
        if length_score:
            complexity += 1
        if has_uppercase:
            complexity += 1
        if has_lowercase:
            complexity += 1
        if has_digit:
            complexity += 1
        if has_special:
            complexity += 1

        return complexity


    def add_password_generated(self):
        # окно генерации пароля
        dialog = QDialog(self)
        dialog.setWindowTitle("Генерация пароля")

        layout = QVBoxLayout(dialog)

        password_display = QLineEdit()
        password_display.setPlaceholderText("Сгенерированный пароль")
        password_display.setReadOnly(True)
        layout.addWidget(password_display)

        # поле для ввода имени пользователя
        name_input = QLineEdit()
        name_input.setPlaceholderText("Имя пользователя")
        layout.addWidget(name_input)

        # поле для заметки
        note_input = QTextEdit()
        note_input.setPlaceholderText("Заметка (необязательно)")
        layout.addWidget(note_input)

        # прогресс-бар
        progress_bar = QProgressBar()
        progress_bar.setMaximum(100)
        layout.addWidget(progress_bar)

        generate_button = QPushButton("Сгенерировать")
        generate_button.clicked.connect(lambda: self.generate_password(dialog, password_display, progress_bar))
        layout.addWidget(generate_button)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(lambda: self.save_generated_password(dialog, password_display, name_input, note_input))
        layout.addWidget(save_button)

        dialog.setLayout(layout)
        dialog.exec()

    def generate_password(self, dialog, password_display, progress_bar):
        try:   
            password_length = self.password_generator_settings["length"]
            use_special_chars = self.password_generator_settings["use_special_chars"]
            use_digits = self.password_generator_settings["use_digits"]

            # создаем генератор паролей
            generator = PasswordGenerator(
                length=password_length, 
                use_special_chars=use_special_chars, 
                use_digits=use_digits
            )

            # генерируем пароль
            password = generator.generate()
            password_display.setText(password)  # отображаем пароль
            progress_bar.setValue(100)  # устанавливаем прогресс на 100%
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сгенерировать пароль: {e}")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Произошла неизвестная ошибка: {e}")

    def update_progress(self, progress, password, progress_bar, password_display, generator, timer):
        password = generator.generate_password()
        progress += 1
        progress_bar.setValue(progress)
        password_display.setText(password)

        if progress >= 100:
            timer.stop()
            QMessageBox.information(self, "Генерация завершена", "Пароль сгенерирован.")
            password_display.setText(password)
            generator.stop_generating()  # переменная состояния остановки генерации

    def save_password_manually(self, dialog, name_input, username_input, password_input, note_input=None):
        # перепутаны местами переменные для пароля и имени пользователя
        name = username_input.text().strip()  # имя пользователя
        username = password_input.text().strip()  # пароль
        password = name_input.text().strip()  # название
        note = note_input.text().strip() if note_input else ""  # заметка (если есть)

        # проверка, что обязательные поля заполнены
        if not name or not username or not password:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, заполните все обязательные поля.")
            return

        # сохраняем пароль в базе данных
        self.db.add_password(name, username, password, note)
        
        # закрываем диалоговое окно после сохранения
        dialog.accept()
        self.load_passwords()
        QMessageBox.information(self, "Успешно", "Пароль успешно сохранен.")

    def save_generated_password(self, dialog, password_display, name_input, note_input):
        """Сохраняет сгенерированный пароль в базу данных."""
        try:
            password = password_display.text()  # получаем сгенерированный пароль из виджета
            name = name_input.text().strip()  # получаем имя пользователя
            note = note_input.toPlainText().strip()  # получаем заметку (если есть)

            # проверяем, что все необходимые данные введены
            if not name or not password:
                QMessageBox.warning(dialog, 'Ошибка', 'Заполните все обязательные поля.')
                return

            # жобавляем пароль в базу данных
            self.db.add_password(name, password, note)

            QMessageBox.information(dialog, 'Успех', 'Пароль успешно сохранён.')
            dialog.accept()  # закрываем диалог
        except Exception as e:
            # выводим подробное сообщение об ошибке
            QMessageBox.critical(dialog, 'Ошибка', f'Не удалось сохранить пароль: {e}')
            print(f"Ошибка при сохранении пароля: {e}")  # выводим ошибку в консоль

    def refresh_data(self):
        self.load_passwords()

    def export_passwords(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Экспортировать пароли", "", "CSV Files (*.csv)")
        if file_path:
            try:
                passwords = self.db.get_all_passwords()
                with open(file_path, "w", newline='', encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow(["Название", "Имя пользователя", "Пароль", "Заметка"])
                    for password in passwords:
                        writer.writerow(password)
                QMessageBox.information(self, "Успешно", "Пароли успешно экспортированы.")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось экспортировать пароли: {e}")

    def import_passwords(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Импортировать пароли", "", "CSV Files (*.csv)")
        if file_path:
            try:
                with open(file_path, "r", newline='', encoding="utf-8") as file:
                    reader = csv.reader(file)
                    next(reader)  # пропускаем заголовок
                    for row in reader:
                        if row:  # проверка на пустые строки
                            self.db.save_password(row[0], row[1], row[2], row[3])
                self.load_passwords()
                QMessageBox.information(self, "Успешно", "Пароли успешно импортированы.")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось импортировать пароли: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PasswordManager()
    window.show()
    sys.exit(app.exec())
