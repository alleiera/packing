from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox)
from database import get_connection

class SizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Size Management / Ölçü Yönetimi")
        self.setMinimumSize(400, 400)
        self.init_ui()
        self.load_sizes()

    def init_ui(self):
        layout = QVBoxLayout()

        form_layout = QHBoxLayout()
        self.size_input = QLineEdit()
        self.size_input.setPlaceholderText("Size / Ölçü (e.g. 22x0.80)")
        form_layout.addWidget(self.size_input)

        btn_add = QPushButton("Add / Ekle")
        btn_add.clicked.connect(self.add_size)
        form_layout.addWidget(btn_add)
        layout.addLayout(form_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["ID", "Size / Ölçü"])
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_delete = QPushButton("Delete / Sil")
        btn_delete.clicked.connect(self.delete_size)
        btn_layout.addWidget(btn_delete)
        btn_close = QPushButton("Close / Kapat")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_sizes(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, size_value FROM sizes")
        rows = cursor.fetchall()
        conn.close()
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def add_size(self):
        val = self.size_input.text()
        if not val: return
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO sizes (size_value) VALUES (?)", (val,))
            conn.commit()
            conn.close()
            self.load_sizes()
            self.size_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_size(self):
        selected = self.table.currentRow()
        if selected < 0: return
        sid = self.table.item(selected, 0).text()
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sizes WHERE id = ?", (sid,))
        conn.commit()
        conn.close()
        self.load_sizes()
