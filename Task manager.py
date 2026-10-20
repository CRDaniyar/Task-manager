import sys
import json
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QTextEdit, QPushButton, QRadioButton, QCheckBox,
    QVBoxLayout, QHBoxLayout, QGroupBox, QComboBox,
    QMessageBox, QListWidget, QDialog
)
from PyQt6.QtCore import pyqtSignal


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('About program')
        self.resize(320, 200)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        title_label = QLabel('<h2>Task Manager</h2>')
        info_label = QLabel(
            'Автор: Фасхудинов Д.Д.\n'
            'Назначение: Управление задачами.\n\n'
            'Поддерживает сохранение в JSON.'
        )
        info_label.setWordWrap(True)

        btn_close = QPushButton('Закрыть')
        btn_close.clicked.connect(self.accept)

        layout.addWidget(title_label)
        layout.addWidget(info_label)
        layout.addStretch()
        layout.addWidget(btn_close)


class TaskManagerWindow(QMainWindow):
    task_created_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Task Manager')
        self.resize(620, 900)

        self.json_filename = 'tasks.json'
        self.tasks = []

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        name_header_layout = QHBoxLayout()
        name_header_layout.addWidget(QLabel('Task:'))
        self.char_counter_label = QLabel('Название: 0 символов')
        name_header_layout.addStretch()
        name_header_layout.addWidget(self.char_counter_label)
        main_layout.addLayout(name_header_layout)

        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText('Введите название задачи...')
        self.task_input.textChanged.connect(self.on_task_title_changed)
        main_layout.addWidget(self.task_input)

        desc_label = QLabel('Description:')
        main_layout.addWidget(desc_label)

        self.desc_input = QTextEdit()
        self.desc_input.setPlaceholderText('Подробное описание задачи...')
        self.desc_input.setFixedHeight(70)
        main_layout.addWidget(self.desc_input)

        priority_group = QGroupBox('Priority')
        priority_layout = QHBoxLayout(priority_group)

        self.radio_low = QRadioButton('Low')
        self.radio_medium = QRadioButton('Medium')
        self.radio_high = QRadioButton('High')
        self.radio_medium.setChecked(True)

        priority_layout.addWidget(self.radio_low)
        priority_layout.addWidget(self.radio_medium)
        priority_layout.addWidget(self.radio_high)
        priority_layout.addStretch()

        main_layout.addWidget(priority_group)

        options_group = QGroupBox('Options')
        optional_layout = QHBoxLayout(options_group)

        self.check_important = QCheckBox('Important')
        self.check_notify = QCheckBox('Send notification')

        optional_layout.addWidget(self.check_important)
        optional_layout.addWidget(self.check_notify)
        optional_layout.addStretch()

        main_layout.addWidget(options_group)

        btn_layout = QHBoxLayout()
        self.btn_create = QPushButton('Add task')
        self.btn_create.clicked.connect(self.on_create_task)

        self.btn_clear_form = QPushButton('Clear Form')
        self.btn_clear_form.clicked.connect(self.on_clear_form)


        self.btn_delete_last = QPushButton('Delete last')
        self.btn_delete_last.clicked.connect(self.on_delete_last_task)

        btn_layout.addWidget(self.btn_create)
        btn_layout.addWidget(self.btn_clear_form)
        btn_layout.addWidget(self.btn_delete_last)
        main_layout.addLayout(btn_layout)

        status_layout = QHBoxLayout()
        self.status_label = QLabel('Status: Ready')
        self.btn_about = QPushButton('О программе')
        self.btn_about.clicked.connect(self.show_about_dialog)
        self.counter_label = QLabel('Задач: 0')

        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.btn_about)
        status_layout.addWidget(self.counter_label)
        main_layout.addLayout(status_layout)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel('Filter by Priority:'))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(['All', 'Low', 'Medium', 'High'])
        self.filter_combo.currentTextChanged.connect(self.update_task_display)
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()
        main_layout.addLayout(filter_layout)

        self.task_list = QListWidget()
        self.task_list.itemSelectionChanged.connect(self.on_list_selection_changed)
        main_layout.addWidget(self.task_list)

        list_btn_layout = QHBoxLayout()
        self.btn_delete_selected = QPushButton('Delete selected task')
        self.btn_delete_selected.setObjectName('deleteSelectedBtn')
        self.btn_delete_selected.setEnabled(False) 
        self.btn_delete_selected.clicked.connect(self.on_delete_selected_task)

        self.btn_clear_list = QPushButton('Clear list')
        self.btn_clear_list.setObjectName('clearListBtn')
        self.btn_clear_list.clicked.connect(self.on_clear_list)

        list_btn_layout.addWidget(self.btn_delete_selected)
        list_btn_layout.addWidget(self.btn_clear_list)
        main_layout.addLayout(list_btn_layout)

        self.task_created_signal.connect(self.handle_task_created_status)

        self.apply_styles()
        self.load_tasks_from_json()


    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f8fafc;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                color: #1e293b;
            }
            QGroupBox {
                font-weight: bold;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
            QLabel {
                font-weight: 600;
            }
            QLineEdit, QTextEdit, QListWidget, QComboBox {
                background-color: #ffffff;
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 6px 8px;
            }
            QLineEdit:focus, QTextEdit:focus, QListWidget:focus, QComboBox:focus {
                border: 1px solid #2563eb;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e2e8f0;
            }
            QListWidget::item:selected {
                background-color: #dbeafe;
                color: #1e40af;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #2563eb;
                color: #ffffff;
                font-weight: bold;
                border: none;
                border-radius: 6px;
                padding: 7px 14px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
            QPushButton:disabled {
                background-color: #cbd5e1;
                color: #94a3b8;
            }
            QPushButton#deleteSelectedBtn {
                background-color: #f59e0b;
            }
            QPushButton#deleteSelectedBtn:hover {
                background-color: #d97706;
            }
            QPushButton#deleteSelectedBtn:pressed {
                background-color: #b45309;
            }
            QPushButton#deleteSelectedBtn:disabled {
                background-color: #cbd5e1;
                color: #94a3b8;
            }
            QPushButton#clearListBtn {
                background-color: #ef4444;
            }
            QPushButton#clearListBtn:hover {
                background-color: #dc2626;
            }
            QPushButton#clearListBtn:pressed {
                background-color: #b91c1c;
            }
            QPushButton#clearListBtn:disabled {
                background-color: #cbd5e1;
                color: #94a3b8;
            }
        """)

    def on_task_title_changed(self, text: str):
        self.char_counter_label.setText(f'Название: {len(text)} символов')

    def get_selected_priority(self) -> str:
        if self.radio_low.isChecked():
            return 'Low'
        elif self.radio_high.isChecked():
            return 'High'
        return 'Medium'

    def on_list_selection_changed(self):
        has_selection = len(self.task_list.selectedItems()) > 0
        self.btn_delete_selected.setEnabled(has_selection)

    def on_create_task(self):
        title = self.task_input.text().strip()
        desc = self.desc_input.toPlainText().strip()

        if not title:
            QMessageBox.warning(
                self, 
                'Предупреждение', 
                'Название задачи не может быть пустым или состоять только из пробелов!'
            )
            return


        priority = self.get_selected_priority()
        
        options = []
        if self.check_important.isChecked():
            options.append('Important')
        if self.check_notify.isChecked():
            options.append('Send notification')

        task = {
            'title': title,
            'description': desc if desc else 'Без описания',
            'priority': priority,
            'options': ', '.join(options) if options else 'None'
        }

        self.tasks.append(task)
        self.save_tasks_to_json()

        self.task_created_signal.emit(title)

        self.counter_label.setText(f'Задач: {len(self.tasks)}')
        self.update_task_display()
        self.on_clear_form()

    def handle_task_created_status(self, task_title: str):
        self.status_label.setText(f'Status: Создана «{task_title}»')

    def on_delete_selected_task(self):
        current_row = self.task_list.currentRow()
        if current_row < 0:
            return

        filtered = self.get_filtered_tasks()
        target_task = filtered[current_row]

        reply = QMessageBox.question(
            self,
            'Подтверждение удаления',
            f'Вы действительно хотите удалить задачу:\n«{target_task["title"]}»?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.tasks.remove(target_task)
            self.save_tasks_to_json()
            self.status_label.setText(f'Status: Задача «{target_task["title"]}» удалена')
            self.counter_label.setText(f'Задач: {len(self.tasks)}')
            self.update_task_display()
            self.btn_delete_selected.setEnabled(False)

    def on_clear_form(self):
        self.task_input.clear()
        self.desc_input.clear()
        self.radio_medium.setChecked(True)
        self.check_important.setChecked(False)
        self.check_notify.setChecked(False)

    def on_delete_last_task(self):
        if self.tasks:
            removed_task = self.tasks.pop()
            self.save_tasks_to_json()
            self.status_label.setText('Status: Last task deleted')
            self.counter_label.setText(f'Задач: {len(self.tasks)}')
            self.update_task_display()
        else:
            self.status_label.setText('Status: No tasks to delete')

    def on_clear_list(self):
        if not self.tasks:
            return

        reply = QMessageBox.question(
            self,
            'Подтверждение очистки',
            'Вы уверены, что хотите полностью очистить весь список задач?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.tasks.clear()
            self.save_tasks_to_json()
            self.task_list.clear()
            self.status_label.setText('Status: Ready')
            self.counter_label.setText('Задач: 0')

    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec()

    def get_filtered_tasks(self):
        selected_filter = self.filter_combo.currentText()
        return [
            t for t in self.tasks 
            if selected_filter == 'All' or t['priority'] == selected_filter
        ]

    def update_task_display(self):
        self.task_list.clear()
        filtered_tasks = self.get_filtered_tasks()


        for i, task in enumerate(filtered_tasks, 1):
            item_text = (
                f"[{i}] {task['title']}  |  Приоритет: {task['priority']}  |  Опции: {task['options']}\n"
                f"     Описание: {task['description']}"
            )
            self.task_list.addItem(item_text)

        self.btn_delete_selected.setEnabled(len(self.task_list.selectedItems()) > 0)
        self.btn_clear_list.setEnabled(len(self.tasks) > 0)

    def save_tasks_to_json(self):
        try:
            with open(self.json_filename, 'w', encoding='utf-8') as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения в JSON: {e}")

    def load_tasks_from_json(self):
        if os.path.exists(self.json_filename):
            try:
                with open(self.json_filename, 'r', encoding='utf-8') as f:
                    self.tasks = json.load(f)
                self.counter_label.setText(f'Задач: {len(self.tasks)}')
                self.update_task_display()
            except Exception as e:
                print(f"Ошибка чтения JSON: {e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TaskManagerWindow()
    window.show()
    sys.exit(app.exec())
