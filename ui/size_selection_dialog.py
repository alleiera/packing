from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget,
                             QPushButton, QLabel)
from database import get_connection

class SizeSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Size / Ölçü Seç")
        self.setMinimumSize(300, 400)
        self.selected_size = ""
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Select Size / Ölçü Seç:"))

        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.handle_ok)
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton("Select / Seç")
        self.btn_ok.clicked.connect(self.handle_ok)
        self.btn_cancel = QPushButton("Cancel / İptal")
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_ok)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_data(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT size_value FROM sizes")
        for (s,) in cursor.fetchall():
            self.list_widget.addItem(s)
        conn.close()

    def handle_ok(self):
        selected = self.list_widget.currentItem()
        if selected:
            self.selected_size = selected.text()
            self.accept()
