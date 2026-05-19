import os
from fpdf import FPDF

class PDFExporter(FPDF):
    def tr_fix(self, text):
        if not text: return ""
        m = {'İ': 'I', 'ı': 'i', 'Ş': 'S', 'ş': 's', 'Ğ': 'G', 'ğ': 'g', 'Ü': 'U', 'ü': 'u', 'Ö': 'O', 'ö': 'o', 'Ç': 'C', 'ç': 'c'}
        for k, v in m.items(): text = text.replace(k, v)
        return text

    def header_section(self, info):
        lp = info.get('logo_path', '')
        if lp and os.path.exists(lp):
            self.image(lp, x=155, y=10, w=45)
        self.set_font('helvetica', 'B', 10)
        self.cell(130, 6, 'PACKING LIST', 1, 1, 'L')
        self.set_font('helvetica', '', 8)
        self.cell(40, 5, 'Document no:', 1, 0)
        self.cell(90, 5, self.tr_fix(info.get('doc_no', '')), 1, 1)
        self.cell(40, 5, 'Date:', 1, 0)
        self.cell(90, 5, info.get('date', ''), 1, 1)
        self.ln(2)

    def sections(self, info):
        self.set_fill_color(240, 240, 240)
        self.set_font('helvetica', 'B', 9)
        self.cell(0, 5, 'CONSIGNE', 1, 1, 'L', True)
        self.set_font('helvetica', '', 8)
        self.cell(30, 4.5, 'Company:', 1, 0); self.cell(160, 4.5, self.tr_fix(info.get('con_company', '')), 1, 1)
        self.cell(30, 4.5, 'Address:', 1, 0); self.cell(160, 4.5, self.tr_fix(info.get('con_address', '')), 1, 1)
        self.cell(30, 4.5, 'Tel:', 1, 0); self.cell(160, 4.5, self.tr_fix(info.get('con_tel', '')), 1, 1)
        self.ln(1)
        self.set_font('helvetica', 'B', 9)
        self.cell(0, 5, 'SHIPPER / EXPORTER', 1, 1, 'L', True)
        self.set_font('helvetica', '', 8)
        self.cell(30, 4.5, 'Company:', 1, 0); self.cell(160, 4.5, self.tr_fix(info.get('ship_company', '')), 1, 1)
        self.cell(30, 4.5, 'Address:', 1, 0); self.cell(160, 4.5, self.tr_fix(info.get('ship_address', '')), 1, 1)
        self.cell(30, 4.5, 'Tel:', 1, 0); self.cell(160, 4.5, self.tr_fix(info.get('ship_tel', '')), 1, 1)
        self.ln(1)
        self.set_font('helvetica', 'B', 9)
        self.cell(0, 5, 'REMARKS', 1, 1, 'L', True)
        self.set_font('helvetica', '', 8)
        fields = [('Incoterms', 'incoterms'), ('Port of Loading', 'pol'), ('Place of Delivery', 'pod'), ('Origin Country', 'origin'), ('Gtip Code', 'gtip')]
        for label, key in fields:
            self.cell(40, 4.5, label + ':', 1, 0)
            self.cell(150, 4.5, self.tr_fix(info.get(key, '')), 1, 1)
        self.ln(3)

    def draw_table(self, headers, data):
        self.set_font('helvetica', 'B', 8)
        self.set_fill_color(220, 220, 220)
        ws = [15, 20, 40, 25, 20, 15, 15, 20, 20]
        for i, h in enumerate(headers): self.cell(ws[i], 6, self.tr_fix(h), 1, 0, 'C', True)
        self.ln()
        self.set_font('helvetica', '', 8)
        for r in data:
            for i, v in enumerate(r): self.cell(ws[i], 5, self.tr_fix(str(v)), 1, 0, 'C')
            self.ln()

    def draw_totals(self, info):
        self.ln(3)
        self.set_font('helvetica', 'B', 9)
        self.set_x(150)
        self.cell(30, 5, 'TOTAL BOX:', 1, 0); self.cell(20, 5, str(info.get('total_boxes', 0)), 1, 1, 'C')
        self.set_x(150)
        self.cell(30, 5, 'TOTAL PALLET:', 1, 0); self.cell(20, 5, str(info.get('total_pallets', 0)), 1, 1, 'C')
        self.set_x(150)
        self.cell(30, 5, 'NET WEIGHT:', 1, 0); self.cell(20, 5, str(info.get('total_net', 0)), 1, 1, 'C')
        self.set_x(150)
        self.cell(30, 5, 'GROSS WEIGHT:', 1, 0); self.cell(20, 5, str(info.get('total_gross', 0)), 1, 1, 'C')

    def draw_page_footer(self, info):
        # Disable auto page break temporarily
        self.set_auto_page_break(False)
        self.set_y(-25)
        self.set_draw_color(255, 0, 0)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(2)
        self.set_text_color(50, 50, 50)
        self.set_font('helvetica', 'B', 8)
        self.cell(0, 4, self.tr_fix(info.get('ship_company', '')), 0, 1, 'C')
        self.set_font('helvetica', '', 7)
        addr = self.tr_fix(info.get('ship_address', ''))
        tel = info.get('ship_tel', '')
        email = "info@hscplastik.com"
        web = "www.hscplastik.com"
        footer_text = f"Adres: {addr} | Tel: {tel} | E-posta: {email} | Web: {web}"
        self.cell(0, 4, footer_text, 0, 1, 'C')
        # Re-enable auto page break
        self.set_auto_page_break(True, margin=15)

def export_to_pdf(fp, info, items, lang='tr'):
    pdf = PDFExporter()
    pdf.add_page()
    pdf.header_section(info)
    pdf.sections(info)
    hs = ["Palet No", "Kod", "Ad", "Olcu", "Metre", "Koli", "Koli Ag.", "Net Ag.", "Brut Ag."] if lang == "tr" else ["Pallet No", "Code", "Name", "Size", "Meter", "Box", "Box W.", "Net W.", "Gross W."]
    pdf.draw_table(hs, items)
    pdf.draw_totals(info)
    pdf.draw_page_footer(info)
    pdf.output(fp)
