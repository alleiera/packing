import os
from fpdf import FPDF

class PDFExporter(FPDF):
    def tr_fix(self, text):
        if not text: return ""
        mapping = {
            'İ': 'I', 'ı': 'i', 'Ş': 'S', 'ş': 's', 'Ğ': 'G', 'ğ': 'g',
            'Ü': 'U', 'ü': 'u', 'Ö': 'O', 'ö': 'o', 'Ç': 'C', 'ç': 'c'
        }
        for k, v in mapping.items():
            text = text.replace(k, v)
        return text

    def header_section(self, info):
        # Logo on the right
        logo_path = info.get('logo_path', '')
        if logo_path and os.path.exists(logo_path):
            self.image(logo_path, x=150, y=10, w=50)

        self.set_font('helvetica', 'B', 14)
        self.cell(100, 10, 'PACKING LIST', 'LTB', 0)
        self.set_font('helvetica', '', 10)
        self.cell(90, 10, '', 'RTB', 1)

        self.cell(50, 7, 'Document no:', 1, 0)
        self.cell(140, 7, self.tr_fix(info.get('doc_no', '')), 1, 1)
        self.cell(50, 7, 'Date:', 1, 0)
        self.cell(140, 7, info.get('date', ''), 1, 1)
        self.ln(5)

    def consignee_shipper_sections(self, info):
        self.set_fill_color(240, 240, 240)
        self.set_font('helvetica', 'B', 10)
        self.cell(0, 7, 'CONSIGNEE', 1, 1, 'L', True)
        self.set_font('helvetica', '', 9)
        self.cell(30, 6, 'Company:', 1, 0)
        self.cell(160, 6, self.tr_fix(info.get('con_company', '')), 1, 1)
        self.cell(30, 6, 'Address:', 1, 0)
        self.cell(160, 6, self.tr_fix(info.get('con_address', '')), 1, 1)
        self.cell(30, 6, 'Tel:', 1, 0)
        self.cell(160, 6, self.tr_fix(info.get('con_tel', '')), 1, 1)
        self.ln(2)

        self.set_font('helvetica', 'B', 10)
        self.cell(0, 7, 'SHIPPER / EXPORTER', 1, 1, 'L', True)
        self.set_font('helvetica', '', 9)
        self.cell(30, 6, 'Company:', 1, 0)
        self.cell(160, 6, self.tr_fix(info.get('ship_company', '')), 1, 1)
        self.cell(30, 6, 'Address:', 1, 0)
        self.cell(160, 6, self.tr_fix(info.get('ship_address', '')), 1, 1)
        self.cell(30, 6, 'Tel:', 1, 0)
        self.cell(160, 6, self.tr_fix(info.get('ship_tel', '')), 1, 1)
        self.ln(2)

        self.set_font('helvetica', 'B', 10)
        self.cell(0, 7, 'REMARKS', 1, 1, 'L', True)
        self.set_font('helvetica', '', 9)
        self.multi_cell(0, 5, self.tr_fix(info.get('remarks', '')), 1)
        self.ln(5)

    def draw_table(self, headers, data):
        self.set_font('helvetica', 'B', 8)
        self.set_fill_color(220, 220, 220)
        widths = [20, 50, 25, 20, 15, 20, 20, 20]
        for i, h in enumerate(headers):
            self.cell(widths[i], 7, self.tr_fix(h), 1, 0, 'C', True)
        self.ln()
        self.set_font('helvetica', '', 8)
        for row in data:
            for i, val in enumerate(row):
                self.cell(widths[i], 6, self.tr_fix(str(val)), 1, 0, 'C')
            self.ln()

    def draw_totals(self, info):
        self.ln(5)
        self.set_font('helvetica', 'B', 9)
        # Table of totals
        x_start = 140
        self.set_xy(x_start, self.get_y())
        self.cell(30, 6, 'TOTAL BOX:', 1, 0)
        self.cell(20, 6, str(info.get('total_boxes', 0)), 1, 1, 'C')
        self.set_x(x_start)
        self.cell(30, 6, 'TOTAL PALLET:', 1, 0)
        self.cell(20, 6, str(info.get('total_pallets', 0)), 1, 1, 'C')
        self.set_x(x_start)
        self.cell(30, 6, 'NET WEIGHT:', 1, 0)
        self.cell(20, 6, str(info.get('total_net', 0)), 1, 1, 'C')
        self.set_x(x_start)
        self.cell(30, 6, 'GROSS WEIGHT:', 1, 0)
        self.cell(20, 6, str(info.get('total_gross', 0)), 1, 1, 'C')

def export_to_pdf(file_path, info, items, lang='tr'):
    pdf = PDFExporter()
    pdf.add_page()
    pdf.header_section(info)
    pdf.consignee_shipper_sections(info)

    headers = ["Kod", "Ad", "Olcu", "Metre", "Koli", "Koli Ag.", "Net Ag.", "Brut Ag."] if lang == 'tr' else               ["Code", "Name", "Size", "Meter", "Box", "Box W.", "Net W.", "Gross W."]

    pdf.draw_table(headers, items)
    pdf.draw_totals(info)
    pdf.output(file_path)
