from fpdf import FPDF

def save_as_pdf(text, filename):
    pdf = FPDF()
    pdf.add_page()
    # Add Unicode font
    #pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.add_font("ArialUnicode", "", r"C:\Windows\Fonts\Arial.ttf", uni=True)
    pdf.set_font("ArialUnicode", "", 12)
    # Multi_cell handles line breaks automatically
    pdf.multi_cell(0, 10, txt=text)
    pdf.output(filename)
