import asyncio
import os
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

def open_pdf(file_url):
    import webbrowser

    if os.name != 'nt':
        print("This function is configured for Windows only.")
        return
    
    opened = False
    try:
        edge_path = "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe %s"
        webbrowser.get(edge_path).open(file_url)
        opened = True
    except Exception as e:
        print(f"Error opening PDF: {e}")

    if not opened:
        webbrowser.open(file_url)
    