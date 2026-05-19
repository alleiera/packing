import sys

with open('ui/main_window.py', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'def on_item_changed(self, item):' in line:
        new_lines.append(line)
        new_lines.append('        self.table.blockSignals(True)\n')
        new_lines.append('        r, c = item.row(), item.column()\n')
        new_lines.append('        if r == self.table.rowCount()-1 and item.text(): self.add_row()\n')
        new_lines.append('        if c in [5, 8, 0]:\n')
        new_lines.append('            pallet_no = self.table.item(r, 0).text() if self.table.item(r, 0) else ""\n')
        new_lines.append('            if pallet_no: self.recalculate_pallet(pallet_no)\n')
        new_lines.append('            else: self.recalculate_row(r)\n')
        new_lines.append('            self.update_totals()\n')
        new_lines.append('        self.table.blockSignals(False)\n')
        new_lines.append('        return\n')
    elif '    def recalculate_row(self, r):' in line:
        # Add recalculate_pallet before recalculate_row
        new_lines.append('''    def recalculate_pallet(self, pallet_no):
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

''')
        new_lines.append(line)
    else:
        # Skip the old on_item_changed implementation lines until the end of the method
        if 'def on_item_changed(self, item):' in "".join(new_lines[-10:]):
             if 'self.table.blockSignals(False)' in line:
                 continue # We already added it
             if 'r, c =' in line or 'if r ==' in line or 'if c in' in line:
                 continue
        new_lines.append(line)

with open('ui/main_window.py', 'w') as f:
    f.writelines(new_lines)
