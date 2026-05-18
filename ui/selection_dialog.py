from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QComboBox, QLabel, QAbstractItemView, QLineEdit)
from PyQt6.QtCore import Qt, QEvent
from database import get_connection

class SelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Product and Size / Ürün ve Ölçü Seç")
        self.setMinimumSize(600, 600)
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

        # Search
        self.search_input = QLineEdit(); self.search_input.setPlaceholderText("Search Product / Ürün Ara...")
        self.search_input.returnPressed.connect(self.filter_table)
        self.search_input.installEventFilter(self)
        self.search_input.hide()
        layout.addWidget(self.search_input)

        # Product Table
        layout.addWidget(QLabel("Select Products (Checkboxes or Select Multiple) / Ürünleri Seç:"))
        self.table_products = QTableWidget()
        self.table_products.setColumnCount(3)
        self.table_products.setHorizontalHeaderLabels(["", "Code / Kod", "Name / Ad"])
        self.table_products.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_products.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_products.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_products.setColumnWidth(0, 30)
        self.table_products.installEventFilter(self)
        self.table_products.viewport().installEventFilter(self)
        self.table_products.cellDoubleClicked.connect(self.on_cell_double_clicked)
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
        conn = get_connection(); cursor = conn.cursor()
        cursor.execute("SELECT size_value FROM sizes")
        for (s,) in cursor.fetchall(): self.combo_size.addItem(s)

        cursor.execute("SELECT code, name FROM products")
        rows = cursor.fetchall(); conn.close()
        self.table_products.setRowCount(len(rows))
        for i, row in enumerate(rows):
            chk_item = QTableWidgetItem()
            chk_item.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            chk_item.setCheckState(Qt.CheckState.Unchecked)
            self.table_products.setItem(i, 0, chk_item)
            self.table_products.setItem(i, 1, QTableWidgetItem(row[0]))
            self.table_products.setItem(i, 2, QTableWidgetItem(row[1]))

    def filter_table(self):
        query = self.search_input.text().lower()
        for i in range(self.table_products.rowCount()):
            code = self.table_products.item(i, 1).text().lower()
            name = self.table_products.item(i, 2).text().lower()
            self.table_products.setRowHidden(i, query not in code and query not in name)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyPress:
            if obj == self.search_input and event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.filter_table()
                return True
            if (obj == self.table_products or obj == self.table_products.viewport()) and event.key() == Qt.Key.Key_Space:
                row = self.table_products.currentRow()
                if row >= 0:
                    item = self.table_products.item(row, 0)
                    if item.checkState() == Qt.CheckState.Checked:
                        item.setCheckState(Qt.CheckState.Unchecked)
                    else:
                        item.setCheckState(Qt.CheckState.Checked)
                return True
        return super().eventFilter(obj, event)

    def keyPressEvent(self, event):
        ctrl = event.modifiers() & Qt.KeyboardModifier.ControlModifier
        if ctrl and event.key() == Qt.Key.Key_F:
            if self.search_input.isHidden():
                self.search_input.show()
            self.search_input.setFocus()
        else:
            super().keyPressEvent(event)

    def on_cell_double_clicked(self, row, column):
        self.handle_ok()

    def handle_ok(self):
        size = self.combo_size.currentText()
        has_checked = False

        for i in range(self.table_products.rowCount()):
            item = self.table_products.item(i, 0)
            if item.checkState() == Qt.CheckState.Checked:
                has_checked = True
                code = self.table_products.item(i, 1).text()
                name = self.table_products.item(i, 2).text()
                self.selected_data.append((code, name, size))

        if not has_checked:
            row = self.table_products.currentRow()
            if row >= 0:
                code = self.table_products.item(row, 1).text()
                name = self.table_products.item(row, 2).text()
                self.selected_data.append((code, name, size))

        self.accept()
