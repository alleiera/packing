import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QLabel, QLineEdit, QHeaderView, QAbstractItemView,
                             QComboBox, QDateEdit, QGridLayout)
from PyQt6.QtCore import Qt, QDate
from database import get_connection
from ui.settings_dialog import SettingsDialog
from ui.product_dialog import ProductDialog
from ui.size_dialog import SizeDialog
from ui.selection_dialog import SelectionDialog
from settings_manager import SettingsManager
from calculations import calculate_weights

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Packing List Generator")
        self.setMinimumSize(1000, 700)
        self.current_lang = SettingsManager.get_setting('language', 'tr')
        self.init_ui()
        self.load_settings()
        self.init_table_rows()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        menu_layout = QHBoxLayout()
        self.btn_products = QPushButton("Products / Ürünler")
        self.btn_products.clicked.connect(self.open_products)
        self.btn_sizes = QPushButton("Sizes / Ölçüler")
        self.btn_sizes.clicked.connect(self.open_sizes)
        self.btn_settings = QPushButton("Settings / Ayarlar")
        self.btn_settings.clicked.connect(self.open_settings)
        self.btn_lang = QPushButton("TR / EN")
        self.btn_lang.clicked.connect(self.toggle_language)

        menu_layout.addWidget(self.btn_products)
        menu_layout.addWidget(self.btn_sizes)
        menu_layout.addWidget(self.btn_settings)
        menu_layout.addStretch()
        menu_layout.addWidget(self.btn_lang)
        main_layout.addLayout(menu_layout)

        header_layout = QGridLayout()
        self.lbl_doc_no = QLabel("Doc No:")
        self.edit_doc_no = QLineEdit()
        self.lbl_date = QLabel("Date:")
        self.edit_date = QDateEdit(QDate.currentDate())
        self.edit_date.setCalendarPopup(True)
        header_layout.addWidget(self.lbl_doc_no, 0, 0)
        header_layout.addWidget(self.edit_doc_no, 0, 1)
        header_layout.addWidget(self.lbl_date, 0, 2)
        header_layout.addWidget(self.edit_date, 0, 3)
        self.lbl_consignee = QLabel("Consignee:")
        self.edit_consignee = QLineEdit()
        header_layout.addWidget(self.lbl_consignee, 1, 0)
        header_layout.addWidget(self.edit_consignee, 1, 1, 1, 3)
        main_layout.addLayout(header_layout)

        self.table = QTableWidget()
        self.headers_tr = ["Ürün Kodu", "Ürün Adı", "Ölçü", "Toplam Metre", "Koli Adeti", "Koli Ağırlığı", "Net Ağırlık", "Bürüt Ağırlık"]
        self.headers_en = ["Product Code", "Product Name", "Size", "Total Meter", "Box Count", "Box Weight", "Net Weight", "Gross Weight"]
        self.table.setColumnCount(len(self.headers_tr))
        self.update_headers()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.itemChanged.connect(self.on_item_changed)
        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        main_layout.addWidget(self.table)

        row_btn_layout = QHBoxLayout()
        self.btn_remove_row = QPushButton("- Remove Row / Satır Sil")
        self.btn_remove_row.clicked.connect(self.remove_row)
        row_btn_layout.addWidget(self.btn_remove_row)
        row_btn_layout.addStretch()
        main_layout.addLayout(row_btn_layout)

        footer_layout = QHBoxLayout()
        self.lbl_total_boxes = QLabel("Total Boxes / Toplam Koli: 0")
        self.edit_total_pallets = QLineEdit()
        self.edit_total_pallets.setPlaceholderText("Pallets")
        self.edit_total_pallets.setFixedWidth(60)
        self.edit_total_pallets.textChanged.connect(self.update_totals)
        footer_layout.addWidget(self.lbl_total_boxes)
        footer_layout.addSpacing(20)
        footer_layout.addWidget(QLabel("Pallets:"))
        footer_layout.addWidget(self.edit_total_pallets)
        footer_layout.addStretch()
        self.btn_export_pdf = QPushButton("Export PDF")
        self.btn_export_pdf.clicked.connect(self.export_pdf)
        self.btn_export_excel = QPushButton("Export Excel")
        self.btn_export_excel.clicked.connect(self.export_excel)
        footer_layout.addWidget(self.btn_export_pdf)
        footer_layout.addWidget(self.btn_export_excel)
        main_layout.addLayout(footer_layout)

    def init_table_rows(self):
        for _ in range(10): self.add_row()

    def update_headers(self):
        headers = self.headers_tr if self.current_lang == 'tr' else self.headers_en
        self.table.setHorizontalHeaderLabels(headers)

    def toggle_language(self):
        self.current_lang = 'en' if self.current_lang == 'tr' else 'tr'
        SettingsManager.save_setting('language', self.current_lang)
        self.update_headers()

    def add_row(self):
        row = self.table.rowCount()
        self.table.insertRow(row)
        for i in range(self.table.columnCount()):
            self.table.setItem(row, i, QTableWidgetItem(""))

    def remove_row(self):
        curr = self.table.currentRow()
        if curr >= 0:
            self.table.removeRow(curr)
            self.update_totals()

    def on_item_changed(self, item):
        self.table.blockSignals(True)
        row = item.row()
        col = item.column()

        # If last row modified, add a new empty row
        if row == self.table.rowCount() - 1 and item.text():
            self.add_row()

        if col in [4, 7]:
            self.recalculate_row(row)
            self.update_totals()
        self.table.blockSignals(False)

    def on_cell_double_clicked(self, row, col):
        # Open selection dialog on double click
        dlg = SelectionDialog(self)
        if dlg.exec():
            selected = dlg.selected_data
            self.table.blockSignals(True)

            # Start filling from current row or first empty row?
            # Let's fill from the clicked row.
            curr_row = row
            for code, name, size in selected:
                if curr_row >= self.table.rowCount():
                    self.add_row()
                self.table.setItem(curr_row, 0, QTableWidgetItem(code))
                self.table.setItem(curr_row, 1, QTableWidgetItem(name))
                self.table.setItem(curr_row, 2, QTableWidgetItem(size))
                curr_row += 1

            if curr_row >= self.table.rowCount():
                self.add_row()

            self.table.blockSignals(False)
            self.update_totals()

    def recalculate_row(self, row):
        boxes_item = self.table.item(row, 4)
        gross_item = self.table.item(row, 7)
        if boxes_item and gross_item and boxes_item.text() and gross_item.text():
            e_box = SettingsManager.get_setting('empty_box_weight', 0.5)
            e_pallet = SettingsManager.get_setting('empty_pallet_weight', 15.0)
            bw, nw = calculate_weights(gross_item.text(), boxes_item.text(), e_box, e_pallet)
            self.table.setItem(row, 5, QTableWidgetItem(str(bw)))
            self.table.setItem(row, 6, QTableWidgetItem(str(nw)))

    def update_totals(self):
        total_boxes = 0
        for r in range(self.table.rowCount()):
            item = self.table.item(r, 4)
            if item and item.text():
                try: total_boxes += int(item.text())
                except: pass
        self.lbl_total_boxes.setText(f"Total Boxes / Toplam Koli: {total_boxes}")

    def open_products(self):
        dlg = ProductDialog(self)
        dlg.exec()

    def open_sizes(self):
        dlg = SizeDialog(self)
        dlg.exec()

    def open_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec(): pass

    def load_settings(self): pass

    def export_pdf(self):
        from export.pdf_exporter import export_to_pdf
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if not file_path: return
        header_info = self.get_ui_header_info()
        items = self.get_table_items()
        export_to_pdf(file_path, header_info, items, self.current_lang)

    def export_excel(self):
        from export.excel_exporter import ExcelExporter
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Excel", "", "Excel Files (*.xlsx)")
        if not file_path: return
        header_info = self.get_ui_header_info()
        items = self.get_table_items()
        ExcelExporter.export(file_path, header_info, items, self.current_lang)

    def get_ui_header_info(self):
        return {
            'doc_no': self.edit_doc_no.text(),
            'date': self.edit_date.date().toString("dd.MM.yyyy"),
            'consignee': self.edit_consignee.text(),
            'total_boxes': self.lbl_total_boxes.text().split(':')[-1].strip(),
            'total_pallets': self.edit_total_pallets.text()
        }

    def get_table_items(self):
        items = []
        for r in range(self.table.rowCount()):
            row_data = []
            has_data = False
            for c in range(self.table.columnCount()):
                it = self.table.item(r, c)
                val = it.text() if it else ""
                if val: has_data = True
                row_data.append(val)
            if has_data:
                items.append(row_data)
        return items

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
