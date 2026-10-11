
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas


OUTPUT_DIR = Path(__file__).resolve().parent.parent / "generated_certificates"


def generate_certificate(
    certificate_id: int,
    recipient_name: str,
    course_name: str,
    completion_date: str
) -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    file_path = OUTPUT_DIR / f"certificate_{certificate_id}.pdf"

    page_width, page_height = landscape(A4)
    pdf = canvas.Canvas(str(file_path), pagesize=(page_width, page_height))

    # Background and decorative borders
    pdf.setFillColor(colors.HexColor("#FDFBF5"))
    pdf.rect(0, 0, page_width, page_height, fill=1, stroke=0)

    pdf.setStrokeColor(colors.HexColor("#B08D57"))
    pdf.setLineWidth(4)
    pdf.rect(20, 20, page_width - 40, page_height - 40)

    pdf.setLineWidth(1)
    pdf.rect(28, 28, page_width - 56, page_height - 56)

    # Certificate content
    pdf.setFillColor(colors.HexColor("#19324D"))
    pdf.setFont("Helvetica-Bold", 30)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 110,
        "CERTIFICATE OF COMPLETION"
    )

    pdf.setFillColor(colors.HexColor("#555555"))
    pdf.setFont("Helvetica", 15)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 155,
        "This certificate is proudly presented to"
    )

    pdf.setFillColor(colors.HexColor("#9A7135"))
    pdf.setFont("Helvetica-Bold", 27)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 205,
        recipient_name
    )

    pdf.setFillColor(colors.HexColor("#555555"))
    pdf.setFont("Helvetica", 15)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 250,
        "for successfully completing"
    )

    pdf.setFillColor(colors.HexColor("#19324D"))
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawCentredString(
        page_width / 2,
        page_height - 290,
        course_name
    )

    pdf.setFillColor(colors.HexColor("#555555"))
    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(
        page_width / 2,
        85,
        f"Completion Date: {completion_date}"
    )

    pdf.drawCentredString(
        page_width / 2,
        62,
        f"Certificate ID: {certificate_id}"
    )

    pdf.save()

    return str(file_path)
