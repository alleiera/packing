import sys
from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow
from database import init_db

def main():
    init_db()
    app = QApplication(sys.argv)

    # Simple Modern Styling
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f3f3f3;
        }
        QPushButton {
            background-color: #ffffff;
            border: 1px solid #cccccc;
            padding: 5px 15px;
            border-radius: 2px;
        }
        QPushButton:hover {
            background-color: #e5e5e5;
        }
        QPushButton#btn_save, QPushButton#btn_add {
            background-color: #0078d4;
            color: white;
            border: none;
        }
        QPushButton#btn_save:hover, QPushButton#btn_add:hover {
            background-color: #005a9e;
        }
        QLineEdit, QDateEdit, QComboBox {
            border: 1px solid #cccccc;
            padding: 4px;
            background: white;
        }
        QTableWidget {
            background-color: white;
            alternate-background-color: #f9f9f9;
            gridline-color: #eeeeee;
            border: 1px solid #cccccc;
        }
        QHeaderView::section {
            background-color: #f3f3f3;
            padding: 4px;
            border: 1px solid #eeeeee;
            font-weight: bold;
        }
    """)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
