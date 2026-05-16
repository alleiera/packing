from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QComboBox, QLabel, QAbstractItemView)
from PyQt6.QtCore import Qt
from database import get_connection

class SelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Product and Size / Ürün ve Ölçü Seç")
        self.setMinimumSize(600, 500)
        self.selected_data = [] # List of (code, name, size)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()

        # Size Selection
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Select Size / Ölçü Seç:"))
        self.combo_size = QComboBox()
        size_layout.addWidget(self.combo_size)
        layout.addLayout(size_layout)

        # Product Table
        layout.addWidget(QLabel("Select Products (Hold Ctrl for multiple) / Ürünleri Seç:"))
        self.table_products = QTableWidget()
        self.table_products.setColumnCount(2)
        self.table_products.setHorizontalHeaderLabels(["Code / Kod", "Name / Ad"])
        self.table_products.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.table_products.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self.table_products)

        # Buttons
        btn_layout = QHBoxLayout()
        self.btn_ok = QPushButton("Add Selected / Seçilenleri Ekle")
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

        # Load Sizes
        cursor.execute("SELECT size_value FROM sizes")
        for (s,) in cursor.fetchall():
            self.combo_size.addItem(s)

        # Load Products
        cursor.execute("SELECT code, name FROM products")
        rows = cursor.fetchall()
        self.table_products.setRowCount(len(rows))
        for i, row in enumerate(rows):
            self.table_products.setItem(i, 0, QTableWidgetItem(row[0]))
            self.table_products.setItem(i, 1, QTableWidgetItem(row[1]))

        conn.close()

    def handle_ok(self):
        size = self.combo_size.currentText()
        selected_rows = self.table_products.selectedItems()
        # selectedItems gives all cells. We need unique rows.
        rows = set()
        for item in selected_rows:
            rows.add(item.row())

        for r in sorted(list(rows)):
            code = self.table_products.item(r, 0).text()
            name = self.table_products.item(r, 1).text()
            self.selected_data.append((code, name, size))

        self.accept()
