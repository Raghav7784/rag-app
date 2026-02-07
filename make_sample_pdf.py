from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

file_name = "sample.pdf"

c = canvas.Canvas(file_name, pagesize=A4)
width, height = A4

c.setFont("Helvetica", 14)
c.drawString(100, height - 100, "Sample PDF Generated Successfully!")

c.setFont("Helvetica", 10)
c.drawString(100, height - 140, "This PDF was created using Python and ReportLab.")

c.showPage()
c.save()

print(f"PDF created: {file_name}")
