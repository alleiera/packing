from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox)
from database import get_connection

class ProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Product Management / Ürün Yönetimi")
        self.setMinimumSize(500, 400)
        self.init_ui()
        self.load_products()

    def init_ui(self):
        layout = QVBoxLayout()

        # Form for adding
        form_layout = QHBoxLayout()
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Code / Kod")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Name / Ad")

        form_layout.addWidget(self.code_input)
        form_layout.addWidget(self.name_input)

        btn_add = QPushButton("Add / Ekle")
        btn_add.clicked.connect(self.add_product)
        form_layout.addWidget(btn_add)

        layout.addLayout(form_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Code / Kod", "Name / Ad"])
        layout.addWidget(self.table)

        # Bottom buttons
        btn_layout = QHBoxLayout()
        btn_delete = QPushButton("Delete Selected / Seçileni Sil")
        btn_delete.clicked.connect(self.delete_product)
        btn_layout.addWidget(btn_delete)

        btn_close = QPushButton("Close / Kapat")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_products(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, code, name FROM products")
        rows = cursor.fetchall()
        conn.close()

        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def add_product(self):
        code = self.code_input.text()
        name = self.name_input.text()

        if not code or not name:
            QMessageBox.warning(self, "Error", "Code and Name are required!")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO products (code, name) VALUES (?, ?)", (code, name))
            conn.commit()
            conn.close()
            self.load_products()
            self.code_input.clear()
            self.name_input.clear()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not add product: {e}")

    def delete_product(self):
        selected = self.table.currentRow()
        if selected < 0: return
        product_id = self.table.item(selected, 0).text()
        reply = QMessageBox.question(self, 'Delete', 'Are you sure?', QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
            conn.commit()
            conn.close()
            self.load_products()
