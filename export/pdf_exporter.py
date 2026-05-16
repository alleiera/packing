from fpdf import FPDF
from settings_manager import SettingsManager

class PDFExporter(FPDF):
    def __init__(self):
        super().__init__()
        # Since I cannot easily bundle a TTF font here, I will try to replace Turkish chars
        # with their ASCII equivalents for the PDF generation if a unicode font is not available.
        # Ideally, in a real environment, you'd use pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        pass

    def tr_fix(self, text):
        if not text: return ""
        mapping = {
            'İ': 'I', 'ı': 'i', 'Ş': 'S', 'ş': 's', 'Ğ': 'G', 'ğ': 'g',
            'Ü': 'U', 'ü': 'u', 'Ö': 'O', 'ö': 'o', 'Ç': 'C', 'ç': 'c'
        }
        for k, v in mapping.items():
            text = text.replace(k, v)
        return text

    def header_info(self, info, lang='tr'):
        settings = SettingsManager.get_all_settings()

        self.set_font('helvetica', 'B', 16)
        self.cell(100, 10, 'PACKING LIST', 0, 0)
        self.set_font('helvetica', 'B', 10)
        self.cell(90, 10, self.tr_fix(settings.get('company_name', '')), 0, 1, 'R')

        self.set_font('helvetica', '', 9)
        self.cell(100, 5, f"Document no: {self.tr_fix(info.get('doc_no', ''))}", 0, 0)
        self.cell(90, 5, self.tr_fix(settings.get('company_address', '')), 0, 1, 'R')

        self.cell(100, 5, f"Date: {info.get('date', '')}", 0, 0)
        self.cell(90, 5, self.tr_fix(settings.get('company_tel', '')), 0, 1, 'R')
        self.ln(10)

        self.set_fill_color(240, 240, 240)
        self.set_font('helvetica', 'B', 10)
        self.cell(0, 7, 'CONSIGNEE', 1, 1, 'L', True)
        self.set_font('helvetica', '', 9)
        self.multi_cell(0, 5, self.tr_fix(info.get('consignee', '')), 1)
        self.ln(5)

    def draw_table(self, headers, data):
        self.set_font('helvetica', 'B', 8)
        self.set_fill_color(220, 220, 220)

        widths = [25, 45, 20, 25, 15, 20, 20, 20]

        for i, h in enumerate(headers):
            self.cell(widths[i], 7, self.tr_fix(h), 1, 0, 'C', True)
        self.ln()

        self.set_font('helvetica', '', 8)
        for row in data:
            for i, val in enumerate(row):
                self.cell(widths[i], 6, self.tr_fix(str(val)), 1, 0, 'C')
            self.ln()

    def draw_footer_totals(self, info):
        self.ln(5)
        self.set_font('helvetica', 'B', 9)
        self.cell(130, 6, '', 0, 0)
        self.cell(30, 6, 'TOTAL BOX:', 1, 0)
        self.cell(30, 6, str(info.get('total_boxes', 0)), 1, 1, 'C')
        self.cell(130, 6, '', 0, 0)
        self.cell(30, 6, 'TOTAL PALLET:', 1, 0)
        self.cell(30, 6, str(info.get('total_pallets', 0)), 1, 1, 'C')

def export_to_pdf(file_path, header_info, items, language='tr'):
    pdf = PDFExporter()
    pdf.add_page()
    pdf.header_info(header_info, language)

    if language == 'tr':
        headers = ["Kod", "Ad", "Olcu", "Metre", "Koli", "Koli Ag.", "Net Agirlik", "Brut Agirlik"]
    else:
        headers = ["Code", "Name", "Size", "Meter", "Box", "Box W.", "Net W.", "Gross W."]

    pdf.draw_table(headers, items)
    pdf.draw_footer_totals(header_info)
    pdf.output(file_path)
