from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QFileDialog, QApplication)
from database import get_connection
import pandas as pd

class ProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Product Management / Ürün Yönetimi")
        self.setMinimumSize(600, 550)
        self.init_ui()
        self.load_products()

    def init_ui(self):
        layout = QVBoxLayout()

        # Manual Add Form
        form_layout = QHBoxLayout()
        self.code_input = QLineEdit(); self.code_input.setPlaceholderText("Code / Kod")
        self.name_input = QLineEdit(); self.name_input.setPlaceholderText("Name / Ad")
        btn_add = QPushButton("Add / Ekle"); btn_add.clicked.connect(self.add_product)
        form_layout.addWidget(self.code_input); form_layout.addWidget(self.name_input); form_layout.addWidget(btn_add)
        layout.addLayout(form_layout)

        # Bulk Actions
        bulk_layout = QHBoxLayout()
        btn_import_excel = QPushButton("Import Excel / Excel'den Yükle")
        btn_import_excel.clicked.connect(self.import_from_excel)
        btn_paste_bulk = QPushButton("Paste Bulk / Toplu Yapıştır")
        btn_paste_bulk.clicked.connect(self.import_from_clipboard)
        bulk_layout.addWidget(btn_import_excel); bulk_layout.addWidget(btn_paste_bulk)
        layout.addLayout(bulk_layout)

        # Search
        self.search_input = QLineEdit(); self.search_input.setPlaceholderText("Search / Ara...")
        self.search_input.textChanged.connect(self.filter_table)
        layout.addWidget(self.search_input)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Code / Kod", "Name / Ad"])
        layout.addWidget(self.table)

        # Bottom buttons
        btn_layout = QHBoxLayout()
        btn_delete = QPushButton("Delete Selected / Seçileni Sil"); btn_delete.clicked.connect(self.delete_product)
        btn_close = QPushButton("Close / Kapat"); btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_delete); btn_layout.addWidget(btn_close)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_products(self):
        conn = get_connection(); cursor = conn.cursor()
        cursor.execute("SELECT id, code, name FROM products")
        rows = cursor.fetchall(); conn.close()
        self.table.setRowCount(len(rows))
        for i, row in enumerate(rows):
            for j, val in enumerate(row): self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def filter_table(self):
        query = self.search_input.text().lower()
        for i in range(self.table.rowCount()):
            code = self.table.item(i, 1).text().lower()
            name = self.table.item(i, 2).text().lower()
            self.table.setRowHidden(i, query not in code and query not in name)

    def add_product(self):
        code, name = self.code_input.text(), self.name_input.text()
        if not code or not name: return
        self.save_to_db([(code, name)])
        self.code_input.clear(); self.name_input.clear()

    def import_from_excel(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Excel", "", "Excel Files (*.xlsx *.xls)")
        if not file_path: return
        try:
            df = pd.read_excel(file_path)
            data = df.iloc[:, :2].values.tolist()
            self.save_to_db(data)
            QMessageBox.information(self, "Success", f"Imported {len(data)} products.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not import: {e}")

    def import_from_clipboard(self):
        text = QApplication.clipboard().text()
        if not text: return
        try:
            lines = text.strip().split("\n")
            data = [line.split("\t") for line in lines if "\t" in line]
            if not data: return
            self.save_to_db(data)
            QMessageBox.information(self, "Success", f"Pasted {len(data)} products.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not paste: {e}")

    def save_to_db(self, product_list):
        try:
            conn = get_connection(); cursor = conn.cursor()
            cursor.executemany("INSERT INTO products (code, name) VALUES (?, ?)", product_list)
            conn.commit(); conn.close(); self.load_products()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Database error: {e}")

    def delete_product(self):
        selected = self.table.currentRow()
        if selected < 0: return
        pid = self.table.item(selected, 0).text()
        if QMessageBox.question(self, 'Delete', 'Are you sure?') == QMessageBox.StandardButton.Yes:
            conn = get_connection(); cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id = ?", (pid,))
            conn.commit(); conn.close(); self.load_products()
