from fpdf import FPDF

def save_as_pdf(text, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    # Multi_cell handles line breaks automatically
    pdf.multi_cell(0, 10, txt=text)
    pdf.output(filename)
