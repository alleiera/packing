import sys
from PyQt6.QtWidgets import QApplication, QTableWidgetItem, QDialog
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtCore import Qt, QEvent
from ui.selection_dialog import SelectionDialog

app = QApplication(sys.argv)
dialog = SelectionDialog()

# Setup row
dialog.table_products.setRowCount(1)
chk = QTableWidgetItem()
chk.setCheckState(Qt.CheckState.Unchecked)
dialog.table_products.setItem(0, 0, chk)
dialog.table_products.setItem(0, 1, QTableWidgetItem("1000"))
dialog.table_products.setItem(0, 2, QTableWidgetItem("Item"))

dialog.table_products.setCurrentCell(0, 1) # Focus on column 1 (Code)

# Send space directly to the table (which is where the event actually goes when a cell is focused)
event_space = QKeyEvent(QEvent.Type.KeyPress, Qt.Key.Key_Space, Qt.KeyboardModifier.NoModifier)

# Because we are sending it to the table, and the table handles it internally without passing to dialog,
# we need to simulate what happens.
app.sendEvent(dialog.table_products, event_space)

print("Checked after space on column 1 (handled by table):", dialog.table_products.item(0, 0).checkState() == Qt.CheckState.Checked)
