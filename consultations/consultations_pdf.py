"""
Renders one consultation (diagnosis + prescription) as a PDF, printed on
top of the clinic's letterhead image.

The backend needs ITS OWN copy of the letterhead — this is a different
file from assets/images/... in the frontend repo, which the backend
can't reach. Drop it at static/letterhead.png (relative to your app
root) and this module picks it up automatically.

TOP_MARGIN / BOTTOM_MARGIN below control how much blank space is
reserved at the top/bottom of the page for your letterhead's header and
footer artwork — text is flowed only in between. You'll likely need to
tune these two numbers once you see your real letterhead rendered;
everything else in this file stays the same.
"""

import io
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

NAVY = colors.HexColor("#0B3D78")
LIGHT_GREEN = colors.HexColor("#EEF6EA")
BORDER = colors.HexColor("#DCE6DD")

LETTERHEAD_PATH = os.path.join(os.path.dirname(__file__), "..", "static", "letterhead.png")

# --- Tune these two to match your actual letterhead artwork ---
TOP_MARGIN = 45 * mm
BOTTOM_MARGIN = 30 * mm
SIDE_MARGIN = 18 * mm

_styles = getSampleStyleSheet()
_SECTION = ParagraphStyle(
    "CSection", parent=_styles["Heading2"], textColor=NAVY, fontSize=12, spaceBefore=10, spaceAfter=6
)
_BODY = ParagraphStyle("CBody", parent=_styles["Normal"], fontSize=10, leading=14)
_SMALL = ParagraphStyle("CSmall", parent=_styles["Normal"], fontSize=9, textColor=colors.grey)


def _draw_letterhead(canvas, doc):
    """Page callback: stretches the letterhead to fill the entire page,
    behind whatever text/tables platypus flows on top."""
    canvas.saveState()
    if os.path.exists(LETTERHEAD_PATH):
        page_w, page_h = A4
        canvas.drawImage(
            LETTERHEAD_PATH, 0, 0, width=page_w, height=page_h, preserveAspectRatio=False, mask="auto"
        )
    canvas.restoreState()


def _kv_row(pairs: list[tuple[str, str]]) -> Table:
    row = [Paragraph(f"<b>{label}:</b> {value or '—'}", _BODY) for label, value in pairs]
    t = Table([row], colWidths=[None] * len(row))
    t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    return t


def build_consultation_pdf(data: dict) -> bytes:
    """
    `data` shape (see get_consultation_pdf_data in consultations_services.py):
    {
      "patient_name", "patient_code", "gender", "dob_or_age", "phone",
      "camp_code", "camp_date", "registration_code",
      "doctor_name", "consultation_date",
      "chief_complaint", "clinical_observations", "diagnosis",
      "doctor_notes", "recommendations",
      "prescriptions": [{"medicine_name","dosage","frequency","duration","instructions"}],
    }
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=TOP_MARGIN,
        bottomMargin=BOTTOM_MARGIN,
        leftMargin=SIDE_MARGIN,
        rightMargin=SIDE_MARGIN,
        title=f"Consultation — {data['registration_code']}",
    )

    story = []

    # ---------- Patient / visit strip ----------
    story.append(
        _kv_row(
            [
                ("Patient", f"{data['patient_name']} ({data['patient_code']})"),
                ("Age / Gender", f"{data.get('dob_or_age') or '—'} / {data.get('gender') or '—'}"),
                ("Date", data["consultation_date"]),
            ]
        )
    )
    
    story.append(Spacer(1, 12))

    # ---------- Clinical notes ----------
    for label, key in [
        ("Chief Complaint", "chief_complaint"),
        ("Clinical Observations", "clinical_observations"),
        ("Diagnosis", "diagnosis"),
    ]:
        val = data.get(key)
        if val:
            story.append(Paragraph(f"<b>{label}:</b> {val}", _BODY))
            story.append(Spacer(1, 6))

    # ---------- Prescription table ----------
    story.append(Paragraph("℞ Prescription", _SECTION))
    rx = data.get("prescriptions") or []
    if rx:
        rows = [["Medicine", "Dosage", "Frequency", "Duration", "Instructions"]]
        for p in rx:
            rows.append(
                [
                    p.get("medicine_name", ""),
                    p.get("dosage") or "—",
                    p.get("frequency") or "—",
                    p.get("duration") or "—",
                    p.get("instructions") or "—",
                ]
            )
        table = Table(rows, colWidths=[35 * mm, 25 * mm, 28 * mm, 25 * mm, None])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GREEN]),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(table)
    else:
        story.append(Paragraph("No medicines prescribed.", _BODY))

    # ---------- Recommendations / notes ----------
    for label, key in [("Recommendations", "recommendations"), ("Doctor Notes", "doctor_notes"),("Advised Investigations", "advised_investigations")]:
        val = data.get(key)
        if val:
            story.append(Spacer(1, 10))
            story.append(Paragraph(f"<b>{label}:</b> {val}", _BODY))



    doc.build(story, onFirstPage=_draw_letterhead, onLaterPages=_draw_letterhead)
    return buffer.getvalue()