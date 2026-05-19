import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QPushButton,
                             QLabel, QLineEdit, QHeaderView, QTextEdit,
                             QComboBox, QDateEdit, QGridLayout, QFrame, QMenu, QApplication)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QPixmap, QAction
from database import get_connection
from ui.settings_dialog import SettingsDialog
from ui.product_dialog import ProductDialog
from ui.size_dialog import SizeDialog
from ui.selection_dialog import SelectionDialog
from ui.size_selection_dialog import SizeSelectionDialog
from settings_manager import SettingsManager
from calculations import calculate_weights

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Packing List Generator")
        self.setMinimumSize(1100, 900)
        self.current_lang = SettingsManager.get_setting('language', 'tr')
        self.headers_tr = ["Palet No", "Ürün Kodu", "Ürün Adı", "Ölçü", "Metre", "Koli", "Koli Ağ.", "Net Ağ.", "Brut Ağ."]
        self.init_ui()
        self.load_settings()
        self.init_table_rows()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        menu_layout = QHBoxLayout()
        self.btn_products = QPushButton("Products / Ürünler"); self.btn_products.clicked.connect(self.open_products)
        self.btn_sizes = QPushButton("Sizes / Ölçüler"); self.btn_sizes.clicked.connect(self.open_sizes)
        self.btn_settings = QPushButton("Settings / Ayarlar"); self.btn_settings.clicked.connect(self.open_settings)
        self.btn_lang = QPushButton("TR / EN"); self.btn_lang.clicked.connect(self.toggle_language)
        menu_layout.addWidget(self.btn_products); menu_layout.addWidget(self.btn_sizes); menu_layout.addWidget(self.btn_settings)
        menu_layout.addStretch(); menu_layout.addWidget(self.btn_lang)
        main_layout.addLayout(menu_layout)

        header_hbox = QHBoxLayout()
        doc_info_grid = QGridLayout()
        doc_info_grid.addWidget(QLabel("PACKING LIST"), 0, 0, 1, 2)
        doc_info_grid.addWidget(QLabel("Document No:"), 1, 0)
        self.edit_doc_no = QLineEdit(); doc_info_grid.addWidget(self.edit_doc_no, 1, 1)
        doc_info_grid.addWidget(QLabel("Date:"), 2, 0)
        self.edit_date = QDateEdit(QDate.currentDate()); self.edit_date.setCalendarPopup(True); doc_info_grid.addWidget(self.edit_date, 2, 1)
        header_hbox.addLayout(doc_info_grid); header_hbox.addStretch()
        self.lbl_logo = QLabel(); self.lbl_logo.setFixedSize(150, 60); self.lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter); self.lbl_logo.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Plain); header_hbox.addWidget(self.lbl_logo)
        main_layout.addLayout(header_hbox)

        main_layout.addWidget(QLabel("<b>CONSIGNE</b>"))
        con_grid = QGridLayout()
        self.edit_con_company = QLineEdit(); con_grid.addWidget(QLabel("Company:"), 0, 0); con_grid.addWidget(self.edit_con_company, 0, 1)
        self.edit_con_address = QLineEdit(); con_grid.addWidget(QLabel("Address:"), 1, 0); con_grid.addWidget(self.edit_con_address, 1, 1)
        self.edit_con_tel = QLineEdit(); con_grid.addWidget(QLabel("Tel:"), 2, 0); con_grid.addWidget(self.edit_con_tel, 2, 1)
        main_layout.addLayout(con_grid)

        main_layout.addWidget(QLabel("<b>SHIPPER / EXPORTER</b>"))
        ship_grid = QGridLayout()
        self.edit_ship_company = QLineEdit(); ship_grid.addWidget(QLabel("Company:"), 0, 0); ship_grid.addWidget(self.edit_ship_company, 0, 1)
        self.edit_ship_address = QLineEdit(); ship_grid.addWidget(QLabel("Address:"), 1, 0); ship_grid.addWidget(self.edit_ship_address, 1, 1)
        self.edit_ship_tel = QLineEdit(); ship_grid.addWidget(QLabel("Tel:"), 2, 0); ship_grid.addWidget(self.edit_ship_tel, 2, 1)
        main_layout.addLayout(ship_grid)

        main_layout.addWidget(QLabel("<b>REMARKS / EXTRA INFO</b>"))
        extra_grid = QGridLayout()
        self.edit_incoterms = QLineEdit(); extra_grid.addWidget(QLabel("Incoterms:"), 0, 0); extra_grid.addWidget(self.edit_incoterms, 0, 1)
        self.edit_pol = QLineEdit(); extra_grid.addWidget(QLabel("Port of Loading:"), 0, 2); extra_grid.addWidget(self.edit_pol, 0, 3)
        self.edit_pod = QLineEdit(); extra_grid.addWidget(QLabel("Place of Delivery:"), 1, 0); extra_grid.addWidget(self.edit_pod, 1, 1)
        self.edit_origin = QLineEdit(); extra_grid.addWidget(QLabel("Origin Country:"), 1, 2); extra_grid.addWidget(self.edit_origin, 1, 3)
        self.edit_gtip = QLineEdit(); extra_grid.addWidget(QLabel("Gtip Code:"), 2, 0); extra_grid.addWidget(self.edit_gtip, 2, 1)
        main_layout.addLayout(extra_grid)

        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.update_headers()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.itemChanged.connect(self.on_item_changed)
        self.table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        main_layout.addWidget(self.table)

        footer_hbox = QHBoxLayout()
        self.btn_remove_row = QPushButton("- Row Sil"); self.btn_remove_row.clicked.connect(self.remove_row); footer_hbox.addWidget(self.btn_remove_row)
        footer_hbox.addStretch()
        totals_grid = QGridLayout()
        totals_grid.addWidget(QLabel("TOTAL BOX:"), 0, 0); self.lbl_total_boxes = QLabel("0"); totals_grid.addWidget(self.lbl_total_boxes, 0, 1)
        totals_grid.addWidget(QLabel("TOTAL PALLET:"), 1, 0); self.edit_total_pallets = QLineEdit(); self.edit_total_pallets.setFixedWidth(50); self.edit_total_pallets.textChanged.connect(self.update_totals); totals_grid.addWidget(self.edit_total_pallets, 1, 1)
        totals_grid.addWidget(QLabel("NET WEIGHT:"), 2, 0); self.lbl_total_net = QLabel("0.0"); totals_grid.addWidget(self.lbl_total_net, 2, 1)
        totals_grid.addWidget(QLabel("GROSS WEIGHT:"), 3, 0); self.lbl_total_gross = QLabel("0.0"); totals_grid.addWidget(self.lbl_total_gross, 3, 1)
        footer_hbox.addLayout(totals_grid); main_layout.addLayout(footer_hbox)

        exp_layout = QHBoxLayout(); exp_layout.addStretch()
        self.btn_export_pdf = QPushButton("Export PDF"); self.btn_export_pdf.clicked.connect(self.export_pdf)
        self.btn_export_excel = QPushButton("Export Excel"); self.btn_export_excel.clicked.connect(self.export_excel)
        exp_layout.addWidget(self.btn_export_pdf); exp_layout.addWidget(self.btn_export_excel)
        main_layout.addLayout(exp_layout)

    def init_table_rows(self):
        for _ in range(15): self.add_row()

    def update_headers(self):
        self.table.setHorizontalHeaderLabels(self.headers_tr if self.current_lang == "tr" else ["Pallet No", "Code", "Name", "Size", "Meter", "Box", "Box W.", "Net W.", "Gross W."])

    def toggle_language(self):
        self.current_lang = 'en' if self.current_lang == 'tr' else 'tr'
        SettingsManager.save_setting('language', self.current_lang); self.update_headers()

    def add_row(self):
        r = self.table.rowCount(); self.table.insertRow(r)
        for i in range(9): self.table.setItem(r, i, QTableWidgetItem(""))

    def remove_row(self):
        curr = self.table.currentRow()
        if curr >= 0: self.table.removeRow(curr); self.update_totals()

    def on_item_changed(self, item):
        self.table.blockSignals(True)
        r, c = item.row(), item.column()
        if r == self.table.rowCount()-1 and item.text(): self.add_row()
        if c in [5, 8, 0]:
            pallet_no = self.table.item(r, 0).text() if self.table.item(r, 0) else ""
            if pallet_no: self.recalculate_pallet(pallet_no)
            else: self.recalculate_row(r)
            self.update_totals()
        self.table.blockSignals(False)
    def on_cell_double_clicked(self, r, c):
        if c == 3: # Size
            dlg = SizeSelectionDialog(self)
            if dlg.exec(): self.table.setItem(r, 3, QTableWidgetItem(dlg.selected_size))
        elif c in [1, 2]: # Product
            dlg = SelectionDialog(self)
            if dlg.exec():
                self.table.blockSignals(True); curr = r
                for code, name, size in dlg.selected_data:
                    if curr >= self.table.rowCount(): self.add_row()
                    self.table.setItem(curr, 1, QTableWidgetItem(code)); self.table.setItem(curr, 2, QTableWidgetItem(name)); self.table.setItem(curr, 3, QTableWidgetItem(size))
                    curr += 1
                self.table.blockSignals(False); self.update_totals()

    def show_context_menu(self, pos):
        menu = QMenu()
        copy_action = QAction("Copy / Kopyala (Ctrl+C)", self); copy_action.triggered.connect(self.copy_to_clipboard); menu.addAction(copy_action)
        paste_action = QAction("Paste / Yapıştır (Ctrl+V)", self); paste_action.triggered.connect(self.paste_from_clipboard); menu.addAction(paste_action)
        menu.addSeparator()
        delete_action = QAction("Clear Selection / Seçimi Temizle (Delete)", self); delete_action.triggered.connect(self.clear_selected_cells); menu.addAction(delete_action)
        clear_row_action = QAction("Clear Row / Satırı Temizle (Shift+Delete)", self); clear_row_action.triggered.connect(self.clear_current_row); menu.addAction(clear_row_action)
        menu.addSeparator()
        fill_down_action = QAction("Fill Down / Aşağı Kopyala (Ctrl+D)", self); fill_down_action.triggered.connect(self.fill_down); menu.addAction(fill_down_action)
        duplicate_row_action = QAction("Duplicate Row / Satırı Çoğalt", self); duplicate_row_action.triggered.connect(self.duplicate_row); menu.addAction(duplicate_row_action)
        menu.exec(self.table.viewport().mapToGlobal(pos))

    def copy_to_clipboard(self):
        ranges = self.table.selectedRanges()
        if not ranges: return
        rng = ranges[0]
        text = ""
        for r in range(rng.topRow(), rng.bottomRow() + 1):
            row_text = []
            for c in range(rng.leftColumn(), rng.rightColumn() + 1):
                item = self.table.item(r, c)
                row_text.append(item.text() if item else "")
            text += "\t".join(row_text) + "\n"
        QApplication.clipboard().setText(text)

    def paste_from_clipboard(self):
        text = QApplication.clipboard().text()
        if not text: return
        rows = text.strip().split("\n")
        curr_row = self.table.currentRow()
        curr_col = self.table.currentColumn()
        if curr_row < 0 or curr_col < 0: return
        self.table.blockSignals(True)
        for i, row_text in enumerate(rows):
            r = curr_row + i
            if r >= self.table.rowCount(): self.add_row()
            cols = row_text.split("\t")
            for j, val in enumerate(cols):
                c = curr_col + j
                if c < self.table.columnCount():
                    self.table.setItem(r, c, QTableWidgetItem(val))
                    if c in [5, 8, 0]: self.recalculate_row(r)
        self.table.blockSignals(False); self.update_totals()

    def clear_selected_cells(self):
        ranges = self.table.selectedRanges()
        self.table.blockSignals(True)
        for rng in ranges:
            for r in range(rng.topRow(), rng.bottomRow() + 1):
                for c in range(rng.leftColumn(), rng.rightColumn() + 1):
                    self.table.setItem(r, c, QTableWidgetItem(""))
                    if c in [5, 8, 0]: self.recalculate_row(r)
        self.table.blockSignals(False); self.update_totals()

    def clear_current_row(self):
        curr = self.table.currentRow()
        if curr < 0: return
        self.table.blockSignals(True)
        for c in range(9):
            self.table.setItem(curr, c, QTableWidgetItem(""))
        self.recalculate_row(curr)
        self.table.blockSignals(False); self.update_totals()

    def fill_down(self):
        selected_ranges = self.table.selectedRanges()
        if not selected_ranges: return
        self.table.blockSignals(True)
        for rng in selected_ranges:
            top_row = rng.topRow()
            for col in range(rng.leftColumn(), rng.rightColumn() + 1):
                top_val = self.table.item(top_row, col).text() if self.table.item(top_row, col) else ""
                for row in range(top_row + 1, rng.bottomRow() + 1):
                    self.table.setItem(row, col, QTableWidgetItem(top_val))
                    if col in [5, 8, 0]: self.recalculate_row(row)
        self.table.blockSignals(False); self.update_totals()

    def duplicate_row(self):
        curr = self.table.currentRow()
        if curr < 0: return
        self.table.blockSignals(True)
        row_data = [self.table.item(curr, i).text() if self.table.item(curr, i) else "" for i in range(9)]
        target = curr + 1
        if target >= self.table.rowCount(): self.add_row()
        for i, val in enumerate(row_data):
            self.table.setItem(target, i, QTableWidgetItem(val))
        self.recalculate_row(target)
        self.table.blockSignals(False); self.update_totals()

    def keyPressEvent(self, event):
        ctrl = event.modifiers() & Qt.KeyboardModifier.ControlModifier
        shift = event.modifiers() & Qt.KeyboardModifier.ShiftModifier
        if ctrl:
            if event.key() == Qt.Key.Key_C: self.copy_to_clipboard()
            elif event.key() == Qt.Key.Key_V: self.paste_from_clipboard()
            elif event.key() == Qt.Key.Key_D: self.fill_down()
            else: super().keyPressEvent(event)
        elif event.key() == Qt.Key.Key_Delete:
            if shift: self.clear_current_row()
            else: self.clear_selected_cells()
        else: super().keyPressEvent(event)

    def recalculate_pallet(self, pallet_no):
        if not pallet_no: return
        rows = []
        total_boxes = 0
        gross_weight = ""
        for r in range(self.table.rowCount()):
            p_item = self.table.item(r, 0)
            if p_item and p_item.text() == pallet_no:
                rows.append(r)
                b_text = self.table.item(r, 5).text() if self.table.item(r, 5) else "0"
                try: total_boxes += int(b_text)
                except: pass
                g_text = self.table.item(r, 8).text() if self.table.item(r, 8) else ""
                if g_text: gross_weight = g_text

        if rows and total_boxes > 0 and gross_weight:
            bw, nw_total = calculate_weights(gross_weight, total_boxes,
                                            SettingsManager.get_setting('empty_box_weight', 0.5),
                                            SettingsManager.get_setting('empty_pallet_weight', 15.0))
            for r in rows:
                b_text = self.table.item(r, 5).text() if self.table.item(r, 5) else "0"
                try:
                    row_boxes = int(b_text)
                    # row_net = (net_total / total_boxes) * row_boxes
                    row_net = round((nw_total / total_boxes) * row_boxes, 2)
                    self.table.setItem(r, 6, QTableWidgetItem(str(bw)))
                    self.table.setItem(r, 7, QTableWidgetItem(str(row_net)))
                    self.table.setItem(r, 8, QTableWidgetItem(gross_weight))
                except: pass

    def recalculate_row(self, r):
        b, g = self.table.item(r, 5), self.table.item(r, 8)
        if b and g and b.text() and g.text():
            bw, nw = calculate_weights(g.text(), b.text(), SettingsManager.get_setting('empty_box_weight', 0.5), SettingsManager.get_setting('empty_pallet_weight', 15.0))
            self.table.setItem(r, 6, QTableWidgetItem(str(bw))); self.table.setItem(r, 7, QTableWidgetItem(str(nw)))

    def update_totals(self):
        tb, tn, tg = 0, 0.0, 0.0
        for r in range(self.table.rowCount()):
            try:
                b = self.table.item(r, 5).text(); n = self.table.item(r, 7).text(); g = self.table.item(r, 8).text()
                if b: tb += int(b)
                if n: tn += float(n)
                if g: tg += float(g)
            except: pass
        self.lbl_total_boxes.setText(str(tb)); self.lbl_total_net.setText(str(round(tn, 2))); self.lbl_total_gross.setText(str(round(tg, 2)))

    def load_settings(self):
        s = SettingsManager.get_all_settings()
        self.edit_ship_company.setText(s.get('company_name', '')); self.edit_ship_address.setText(s.get('company_address', '')); self.edit_ship_tel.setText(s.get('company_tel', ''))
        self.edit_gtip.setText(s.get('default_gtip', ''))
        lp = s.get('logo_path', '')
        if lp and os.path.exists(lp):
            pix = QPixmap(lp); self.lbl_logo.setPixmap(pix.scaled(self.lbl_logo.size(), Qt.AspectRatioMode.KeepAspectRatio))

    def open_products(self): ProductDialog(self).exec()
    def open_sizes(self): SizeDialog(self).exec()
    def open_settings(self):
        if SettingsDialog(self).exec(): self.load_settings()

    def get_ui_header_info(self):
        return {
            'doc_no': self.edit_doc_no.text(), 'date': self.edit_date.date().toString("dd.MM.yyyy"),
            'con_company': self.edit_con_company.text(), 'con_address': self.edit_con_address.text(), 'con_tel': self.edit_con_tel.text(),
            'ship_company': self.edit_ship_company.text(), 'ship_address': self.edit_ship_address.text(), 'ship_tel': self.edit_ship_tel.text(),
            'incoterms': self.edit_incoterms.text(), 'pol': self.edit_pol.text(), 'pod': self.edit_pod.text(), 'origin': self.edit_origin.text(), 'gtip': self.edit_gtip.text(),
            'total_boxes': self.lbl_total_boxes.text(), 'total_pallets': self.edit_total_pallets.text(), 'total_net': self.lbl_total_net.text(), 'total_gross': self.lbl_total_gross.text(),
            'logo_path': SettingsManager.get_setting('logo_path', '')
        }

    def get_table_items(self):
        items = []
        for r in range(self.table.rowCount()):
            row = [self.table.item(r, c).text() if self.table.item(r, c) else "" for c in range(9)]
            if any(row): items.append(row)
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
    app = QApplication(sys.argv); MainWindow().show(); sys.exit(app.exec())
