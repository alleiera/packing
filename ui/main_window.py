import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QLabel, QLineEdit, QHeaderView, QTextEdit,
                             QComboBox, QDateEdit, QGridLayout, QFrame)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QPixmap
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
        self.setMinimumSize(1100, 850)
        self.current_lang = SettingsManager.get_setting('language', 'tr')
        self.init_ui()
        self.load_settings()
        self.init_table_rows()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Top Buttons
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

        # Header Info Grid
        header_grid = QGridLayout()

        # Left side: Doc Info
        header_grid.addWidget(QLabel("Document No:"), 0, 0)
        self.edit_doc_no = QLineEdit()
        header_grid.addWidget(self.edit_doc_no, 0, 1)

        header_grid.addWidget(QLabel("Date:"), 1, 0)
        self.edit_date = QDateEdit(QDate.currentDate())
        self.edit_date.setCalendarPopup(True)
        header_grid.addWidget(self.edit_date, 1, 1)

        # Logo Area
        self.lbl_logo = QLabel("LOGO")
        self.lbl_logo.setFixedSize(150, 60)
        self.lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_logo.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain)
        header_grid.addWidget(self.lbl_logo, 0, 3, 2, 1)

        main_layout.addLayout(header_grid)

        # Consignee Section
        main_layout.addWidget(QLabel("<b>CONSIGNEE</b>"))
        consignee_layout = QGridLayout()
        consignee_layout.addWidget(QLabel("Company:"), 0, 0)
        self.edit_con_company = QLineEdit()
        consignee_layout.addWidget(self.edit_con_company, 0, 1)

        consignee_layout.addWidget(QLabel("Address:"), 1, 0)
        self.edit_con_address = QLineEdit()
        consignee_layout.addWidget(self.edit_con_address, 1, 1)

        consignee_layout.addWidget(QLabel("Tel:"), 2, 0)
        self.edit_con_tel = QLineEdit()
        consignee_layout.addWidget(self.edit_con_tel, 2, 1)
        main_layout.addLayout(consignee_layout)

        # Shipper Section
        main_layout.addWidget(QLabel("<b>SHIPPER / EXPORTER</b>"))
        shipper_layout = QGridLayout()
        shipper_layout.addWidget(QLabel("Company:"), 0, 0)
        self.edit_ship_company = QLineEdit()
        shipper_layout.addWidget(self.edit_ship_company, 0, 1)

        shipper_layout.addWidget(QLabel("Address:"), 1, 0)
        self.edit_ship_address = QLineEdit()
        shipper_layout.addWidget(self.edit_ship_address, 1, 1)

        shipper_layout.addWidget(QLabel("Tel:"), 2, 0)
        self.edit_ship_tel = QLineEdit()
        shipper_layout.addWidget(self.edit_ship_tel, 2, 1)
        main_layout.addLayout(shipper_layout)

        # Remarks
        main_layout.addWidget(QLabel("<b>REMARKS</b>"))
        self.edit_remarks = QTextEdit()
        self.edit_remarks.setMaximumHeight(60)
        main_layout.addLayout(QVBoxLayout())
        main_layout.addWidget(self.edit_remarks)

        # Table
        self.table = QTableWidget()
        self.headers_tr = ["Ürün Kodu", "Ürün Adı", "Ölçü", "Metre", "Koli", "Koli Ağ.", "Net Ağırlık", "Bürüt Ağırlık"]
        self.headers_en = ["Product Code", "Product Name", "Size", "Meter", "Box", "Box W.", "Net W.", "Gross W."]
        self.table.setColumnCount(len(self.headers_tr))
        self.update_headers()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.itemChanged.connect(self.on_item_changed)
        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        main_layout.addWidget(self.table)

        # Footer
        footer_grid = QGridLayout()
        self.lbl_total_boxes = QLabel("Total Box: 0")
        self.edit_total_pallets = QLineEdit()
        self.edit_total_pallets.setFixedWidth(60)
        self.edit_total_pallets.textChanged.connect(self.update_totals)

        self.lbl_total_net = QLabel("Total Net Weight: 0.0")
        self.lbl_total_gross = QLabel("Total Gross Weight: 0.0")

        footer_grid.addWidget(self.lbl_total_boxes, 0, 0)
        footer_grid.addWidget(QLabel("Total Pallet:"), 0, 1)
        footer_grid.addWidget(self.edit_total_pallets, 0, 2)
        footer_grid.addWidget(self.lbl_total_net, 1, 0)
        footer_grid.addWidget(self.lbl_total_gross, 1, 1)

        self.btn_export_pdf = QPushButton("Export PDF")
        self.btn_export_pdf.clicked.connect(self.export_pdf)
        self.btn_export_excel = QPushButton("Export Excel")
        self.btn_export_excel.clicked.connect(self.export_excel)
        footer_grid.addWidget(self.btn_export_pdf, 0, 3)
        footer_grid.addWidget(self.btn_export_excel, 1, 3)

        main_layout.addLayout(footer_grid)

    def init_table_rows(self):
        for _ in range(15): self.add_row()

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

    def on_item_changed(self, item):
        self.table.blockSignals(True)
        row, col = item.row(), item.column()
        if row == self.table.rowCount() - 1 and item.text(): self.add_row()
        if col in [4, 7]:
            self.recalculate_row(row)
            self.update_totals()
        self.table.blockSignals(False)

    def on_cell_double_clicked(self, row, col):
        dlg = SelectionDialog(self)
        if dlg.exec():
            self.table.blockSignals(True)
            curr_row = row
            for code, name, size in dlg.selected_data:
                if curr_row >= self.table.rowCount(): self.add_row()
                self.table.setItem(curr_row, 0, QTableWidgetItem(code))
                self.table.setItem(curr_row, 1, QTableWidgetItem(name))
                self.table.setItem(curr_row, 2, QTableWidgetItem(size))
                curr_row += 1
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
        total_net = 0.0
        total_gross = 0.0
        for r in range(self.table.rowCount()):
            b_item = self.table.item(r, 4)
            n_item = self.table.item(r, 6)
            g_item = self.table.item(r, 7)
            try:
                if b_item and b_item.text(): total_boxes += int(b_item.text())
                if n_item and n_item.text(): total_net += float(n_item.text())
                if g_item and g_item.text(): total_gross += float(g_item.text())
            except: pass
        self.lbl_total_boxes.setText(f"Total Box: {total_boxes}")
        self.lbl_total_net.setText(f"Total Net Weight: {round(total_net, 2)}")
        self.lbl_total_gross.setText(f"Total Gross Weight: {round(total_gross, 2)}")

    def load_settings(self):
        settings = SettingsManager.get_all_settings()
        self.edit_ship_company.setText(settings.get('company_name', ''))
        self.edit_ship_address.setText(settings.get('company_address', ''))
        self.edit_ship_tel.setText(settings.get('company_tel', ''))
        logo_path = settings.get('logo_path', '')
        if logo_path and os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            self.lbl_logo.setPixmap(pixmap.scaled(self.lbl_logo.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def open_products(self): ProductDialog(self).exec()
    def open_sizes(self): SizeDialog(self).exec()
    def open_settings(self):
        if SettingsDialog(self).exec(): self.load_settings()

    def get_ui_header_info(self):
        return {
            'doc_no': self.edit_doc_no.text(),
            'date': self.edit_date.date().toString("dd.MM.yyyy"),
            'con_company': self.edit_con_company.text(),
            'con_address': self.edit_con_address.text(),
            'con_tel': self.edit_con_tel.text(),
            'ship_company': self.edit_ship_company.text(),
            'ship_address': self.edit_ship_address.text(),
            'ship_tel': self.edit_ship_tel.text(),
            'remarks': self.edit_remarks.toPlainText(),
            'total_boxes': self.lbl_total_boxes.text().split(':')[-1].strip(),
            'total_pallets': self.edit_total_pallets.text(),
            'total_net': self.lbl_total_net.text().split(':')[-1].strip(),
            'total_gross': self.lbl_total_gross.text().split(':')[-1].strip(),
            'logo_path': SettingsManager.get_setting('logo_path', '')
        }

    def get_table_items(self):
        items = []
        for r in range(self.table.rowCount()):
            row_data = [self.table.item(r, c).text() if self.table.item(r, c) else "" for c in range(8)]
            if any(row_data): items.append(row_data)
        return items

    def export_pdf(self):
        from export.pdf_exporter import export_to_pdf
        from PyQt6.QtWidgets import QFileDialog
        fp, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if fp: export_to_pdf(fp, self.get_ui_header_info(), self.get_table_items(), self.current_lang)

    def export_excel(self):
        from export.excel_exporter import ExcelExporter
        from PyQt6.QtWidgets import QFileDialog
        fp, _ = QFileDialog.getSaveFileName(self, "Save Excel", "", "Excel Files (*.xlsx)")
        if fp: ExcelExporter.export(fp, self.get_ui_header_info(), self.get_table_items(), self.current_lang)

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    MainWindow().show()
    sys.exit(app.exec())
