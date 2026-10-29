import os
import re
import html
import shutil
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class SimpleNumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, total_pages):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#475569"))

        # Top Header (pages 2+)
        if self._pageNumber > 1:
            self.drawString(45, 810, "PHISHING SHIELD AI — TECH STACK, ML MODELS & CYBERSECURITY")
            self.drawRightString(550, 810, "OFFICIAL ARCHITECTURE GUIDE")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.8)
            self.line(45, 802, 550, 802)

        # Bottom Footer
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.8)
        self.line(45, 42, 550, 42)

        self.setFont("Helvetica", 8.5)
        self.drawString(45, 28, "Phishing Shield AI — Threat Detection & Machine Learning Documentation")
        self.drawRightString(550, 28, f"Page {self._pageNumber} of {total_pages}")
        self.restoreState()


def generate_simple_pdf(md_path: str, output_path: str):
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=42,
        rightMargin=42,
        topMargin=45,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    c_primary = colors.HexColor("#0F172A")    # Dark slate
    c_blue = colors.HexColor("#2563EB")       # Royal blue
    c_dark_blue = colors.HexColor("#1E3A8A")  # Navy
    c_text = colors.HexColor("#1E293B")       # Dark readable text
    c_sub = colors.HexColor("#475569")        # Slate 600
    c_border = colors.HexColor("#CBD5E1")
    c_step_bg = colors.HexColor("#F8FAFC")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=c_primary,
        spaceAfter=4
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=c_blue,
        spaceAfter=8
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=c_sub,
        spaceAfter=8
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=15.5,
        textColor=c_dark_blue,
        spaceBefore=11,
        spaceAfter=5,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=c_blue,
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_text,
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=c_text,
        leftIndent=12,
        spaceAfter=2.5
    )

    step_box_style = ParagraphStyle(
        'StepBox',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=c_text,
        backColor=c_step_bg,
        borderColor=colors.HexColor("#94A3B8"),
        borderWidth=0.8,
        borderPadding=6,
        spaceBefore=3,
        spaceAfter=4
    )

    th_style = ParagraphStyle(
        'TH',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.white
    )

    td_style = ParagraphStyle(
        'TD',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=c_text
    )

    story = []

    # Title header
    story.append(Paragraph("Phishing Shield AI — Complete Tech Stack, Machine Learning & Cybersecurity Guide", title_style))
    story.append(Paragraph("Clear Technical Documentation: System Architecture, AI Models, and Threat Defenses", subtitle_style))
    story.append(Paragraph("<b>Author / System Architect:</b> Ram Narayan &nbsp;|&nbsp; <b>Framework:</b> Python FastAPI 3.11 + React 18 + Scikit-Learn 1.5 &nbsp;|&nbsp; <b>Date:</b> October 2026", meta_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_blue, spaceBefore=2, spaceAfter=8))

    lines = md_text.splitlines()
    in_table = False
    table_rows = []

    def format_inline(text: str) -> str:
        code_spans = []
        def save_code(m):
            code_spans.append(m.group(1))
            return f"__CODE_{len(code_spans)-1}__"
        t = re.sub(r'`([^`]+)`', save_code, text)

        t = html.escape(t)
        t = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', t)
        t = re.sub(r'\*(.*?)\*', r'<i>\1</i>', t)

        for idx, span in enumerate(code_spans):
            rep = f'<font face="Courier" color="#1D4ED8"><b>{html.escape(span)}</b></font>'
            t = t.replace(f"__CODE_{idx}__", rep)
        return t

    def flush_table():
        nonlocal in_table, table_rows
        if not table_rows:
            in_table = False
            return
        
        data = []
        for r_idx, row in enumerate(table_rows):
            is_header = (r_idx == 0)
            p_row = []
            for cell in row:
                st = th_style if is_header else td_style
                p_row.append(Paragraph(format_inline(cell.strip()), st))
            data.append(p_row)

        col_count = len(table_rows[0])
        avail_width = 511
        if col_count == 4:
            col_widths = [95, 95, 65, 256]
        elif col_count == 3:
            col_widths = [120, 130, 261]
        else:
            col_widths = [avail_width / col_count] * col_count

        t = Table(data, colWidths=col_widths, repeatRows=1)
        t_style = [
            ('BACKGROUND', (0, 0), (-1, 0), c_primary),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ]
        for r in range(1, len(data)):
            bg = colors.HexColor("#F8FAFC") if r % 2 == 1 else colors.white
            t_style.append(('BACKGROUND', (0, r), (-1, r), bg))
        t.setStyle(TableStyle(t_style))
        story.append(Spacer(1, 4))
        story.append(t)
        story.append(Spacer(1, 5))
        table_rows = []
        in_table = False

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Handle Tables
        if "|" in line and (line.startswith("|") or line.endswith("|")):
            parts = [p.strip() for p in line.split("|")]
            if parts and parts[0] == "":
                parts = parts[1:]
            if parts and parts[-1] == "":
                parts = parts[:-1]

            if all(re.match(r'^:?-+:?$', p) for p in parts if p):
                i += 1
                continue

            in_table = True
            table_rows.append(parts)
            i += 1
            continue
        elif in_table:
            flush_table()

        if stripped in ("---", "***", "___"):
            story.append(HRFlowable(width="100%", thickness=0.6, color=c_border, spaceBefore=4, spaceAfter=5))
            i += 1
            continue

        if not stripped:
            i += 1
            continue

        if stripped.startswith("# Phishing Shield AI"):
            i += 1
            continue

        # Step 1, Step 2, Step 3, Step 4 styled into clean visible boxes
        if stripped.startswith("* **Step "):
            step_content = stripped[2:].strip()
            story.append(Paragraph(format_inline(step_content), step_box_style))
            i += 1
            continue

        # Heading 1 (##)
        if stripped.startswith("## "):
            h_text = stripped[3:].strip()
            story.append(Paragraph(format_inline(h_text), h1_style))
            i += 1
            continue

        # Heading 2 (###)
        if stripped.startswith("### "):
            h_text = stripped[4:].strip()
            story.append(Paragraph(format_inline(h_text), h2_style))
            i += 1
            continue

        # Bullets
        if stripped.startswith("* ") or stripped.startswith("- "):
            b_text = stripped[2:].strip()
            formatted = "&bull;&nbsp;&nbsp;" + format_inline(b_text)
            story.append(Paragraph(formatted, bullet_style))
            i += 1
            continue

        # Numbered items
        num_match = re.match(r'^(\d+)\.\s+(.*)$', stripped)
        if num_match:
            num = num_match.group(1)
            b_text = num_match.group(2)
            formatted = f"<b>{num}.</b>&nbsp;&nbsp;" + format_inline(b_text)
            story.append(Paragraph(formatted, bullet_style))
            i += 1
            continue

        story.append(Paragraph(format_inline(stripped), body_style))
        i += 1

    if in_table:
        flush_table()

    doc.build(story, canvasmaker=SimpleNumberedCanvas)
    print(f"Built PDF: {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    src_md = r"c:\Users\Sai Santhosh Ram\OneDrive\Ram Narayan\OneDrive\Desktop\cyber\phishing-shield-ai\TECHSTACK_AND_CYBER_DOC.md"
    project_pdf = r"c:\Users\Sai Santhosh Ram\OneDrive\Ram Narayan\OneDrive\Desktop\cyber\phishing-shield-ai\TECHSTACK_AND_CYBER_DOC.pdf"
    desktop_pdf = r"C:\Users\Sai Santhosh Ram\OneDrive\Ram Narayan\OneDrive\Desktop\TECHSTACK_AND_CYBER_DOC.pdf"

    generate_simple_pdf(src_md, project_pdf)
    shutil.copyfile(project_pdf, desktop_pdf)
    print(f"Successfully updated Desktop PDF: {desktop_pdf}")
