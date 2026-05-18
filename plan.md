1.  **Update `ui/main_window.py` columns:**
    *   Change total columns from 8 to 9.
    *   Add "Palet No" (Pallet No) as the first column in headers (`headers_tr` and `headers_en`).
    *   Update column indices in the code (`4 -> 5` for Koli, `7 -> 8` for Brut Ağ., etc.).
2.  **Add Grouping & Spanning Logic (`update_spans_and_calculations`):**
    *   Iterate over the table and group consecutive rows with the same, non-empty "Palet No".
    *   Calculate the total boxes for the group.
    *   Read the "Brut Ağ." (Gross Weight) from the first row of the group.
    *   Calculate "Koli Ağ." and "Net Ağ." based on total boxes and group's gross weight.
    *   Set the "Net Ağ." on the first row of the group and apply a row span to visually merge "Net Ağ." and "Brut Ağ." cells for the entire group.
    *   Set "Koli Ağ." for all rows within the group.
3.  **Update Event Handlers:**
    *   Modify `on_item_changed`, `remove_row`, `paste_from_clipboard`, `clear_selected_cells`, `clear_current_row`, `fill_down`, and `duplicate_row` to trigger `self.update_spans_and_calculations()` instead of the old `recalculate_row()`.
4.  **Update `export_to_pdf` and `export_excel`:**
    *   Update the header arrays in `export/pdf_exporter.py` and `export/excel_exporter.py` to include the "Palet No" column so exports reflect the new layout.
    *   Update column widths in `pdf_exporter.py` to accommodate the 9th column.
5.  **Pre-commit checks:**
    *   Ensure proper testing, verifications, review, and reflection are done using `pre_commit_instructions`.
6.  **Submit Changes:**
    *   Submit branch with the updated pallet grouping implementation.
