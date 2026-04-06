import asyncio
from fpdf import FPDF

def save_as_pdf(text, filename):
    pdf = FPDF()
    pdf.set_margins(5, 5) # 5mm margins
    pdf.add_page()
    # Add Unicode font
    #pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.add_font("ArialUnicode", "", r"C:\Windows\Fonts\Arial.ttf", uni=True)
    pdf.set_font("ArialUnicode", "", 11)
    # Multi_cell handles line breaks automatically
    pdf.multi_cell(0, 7, txt=text)
    pdf.output(filename)

async def save_as_pdf_async(text, filename):
    await asyncio.tothread(save_as_pdf, text, filename)
