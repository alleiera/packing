from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QGridLayout, QLabel,
                             QLineEdit, QPushButton, QFileDialog, QHBoxLayout)
from settings_manager import SettingsManager

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings / Ayarlar")
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout()
        grid = QGridLayout()

        self.inputs = {}
        fields = [
            ('company_name', 'Company Name / Şirket Adı:'),
            ('company_address', 'Address / Adres:'),
            ('company_tel', 'Tel:'),
            ('logo_path', 'Logo Path / Logo Yolu:'),
            ('empty_box_weight', 'Empty Box Weight / Boş Koli Ağırlığı:'),
            ('empty_pallet_weight', 'Empty Pallet Weight / Boş Palet Ağırlığı:'),
            ('default_gtip', 'Default GTIP Code / Varsayılan GTIP Kodu:')
        ]

        for i, (key, label) in enumerate(fields):
            grid.addWidget(QLabel(label), i, 0)
            line_edit = QLineEdit()
            grid.addWidget(line_edit, i, 1)
            self.inputs[key] = line_edit

            if key == 'logo_path':
                btn_browse = QPushButton("...")
                btn_browse.clicked.connect(self.browse_logo)
                grid.addWidget(btn_browse, i, 2)

        layout.addLayout(grid)

        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("Save / Kaydet")
        self.btn_save.clicked.connect(self.save_settings)
        self.btn_cancel = QPushButton("Cancel / İptal")
        self.btn_cancel.clicked.connect(self.reject)

        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def browse_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Logo", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.inputs['logo_path'].setText(file_path)

    def load_settings(self):
        settings = SettingsManager.get_all_settings()
        for key, line_edit in self.inputs.items():
            line_edit.setText(settings.get(key, ''))

    def save_settings(self):
        new_settings = {key: line_edit.text() for key, line_edit in self.inputs.items()}
        SettingsManager.save_settings(new_settings)
        self.accept()
