import pandas as pd
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.drawing.image import Image
import os

class ExcelExporter:
    @staticmethod
    def export(fp, info, items, lang='tr'):
        hs = ["Kod", "Ad", "Olcu", "Metre", "Koli", "Koli Ag.", "Net Ag.", "Brut Ag."] if lang == 'tr' else              ["Code", "Name", "Size", "Meter", "Box", "Box W.", "Net W.", "Gross W."]
        df = pd.DataFrame(items, columns=hs)
        with pd.ExcelWriter(fp, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, startrow=25)
            ws = writer.sheets['Sheet1']

            # Header
            ws['A1'] = "PACKING LIST"; ws['A1'].font = Font(bold=True, size=14)
            ws['A2'] = f"Document no: {info.get('doc_no', '')}"
            ws['A3'] = f"Date: {info.get('date', '')}"

            lp = info.get('logo_path', '')
            if lp and os.path.exists(lp):
                try:
                    img = Image(lp); img.width, img.height = 180, 70
                    ws.add_image(img, 'F1')
                except: pass

            # Sections
            ws['A5'] = "CONSIGNE"; ws['A5'].font = Font(bold=True)
            ws['A6'] = f"Company: {info.get('con_company', '')}"
            ws['A7'] = f"Address: {info.get('con_address', '')}"
            ws['A8'] = f"Tel: {info.get('con_tel', '')}"

            ws['A10'] = "SHIPPER / EXPORTER"; ws['A10'].font = Font(bold=True)
            ws['A11'] = f"Company: {info.get('ship_company', '')}"
            ws['A12'] = f"Address: {info.get('ship_address', '')}"
            ws['A13'] = f"Tel: {info.get('ship_tel', '')}"

            ws['A15'] = "REMARKS"; ws['A15'].font = Font(bold=True)
            ws['A16'] = f"Incoterms: {info.get('incoterms', '')}"
            ws['A17'] = f"Port of Loading: {info.get('pol', '')}"
            ws['A18'] = f"Place of Delivery: {info.get('pod', '')}"
            ws['A19'] = f"Origin Country: {info.get('origin', '')}"
            ws['A20'] = f"Gtip Code: {info.get('gtip', '')}"

            # Totals
            tr = 25 + len(items) + 2
            ws.cell(row=tr, column=7, value="TOTAL BOX:")
            ws.cell(row=tr, column=8, value=info.get('total_boxes'))
            ws.cell(row=tr+1, column=7, value="TOTAL PALLET:")
            ws.cell(row=tr+1, column=8, value=info.get('total_pallets'))
            ws.cell(row=tr+2, column=7, value="NET WEIGHT:")
            ws.cell(row=tr+2, column=8, value=info.get('total_net'))
            ws.cell(row=tr+3, column=7, value="GROSS WEIGHT:")
            ws.cell(row=tr+3, column=8, value=info.get('total_gross'))

        return True
