import os
import re
import html
import shutil
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and stamp total page count (Page X of Y),
    along with running headers and security classification banners.
    """
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
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Top Running Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(40, 815, "PHISHING SHIELD AI — TECHNICAL STACK & CYBERSECURITY ARCHITECTURE")
            self.drawRightString(555, 815, "OFFICIAL SPECIFICATION")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(40, 808, 555, 808)

        # Bottom Running Footer
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(40, 42, 555, 42)

        self.setFont("Helvetica", 8)
        self.drawString(40, 30, "Confidential — Threat Defense & Machine Learning Research")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(555, 30, page_text)
        self.restoreState()


def build_pdf(md_path: str, output_pdf_path: str):
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=48,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    c_primary = colors.HexColor("#0F172A")    # Slate 900
    c_accent = colors.HexColor("#1D4ED8")     # Blue 700
    c_cyan = colors.HexColor("#0284C7")       # Sky 600
    c_text = colors.HexColor("#1E293B")       # Slate 800
    c_muted = colors.HexColor("#475569")      # Slate 600
    c_bg_code = colors.HexColor("#0F172A")    # Dark slate
    c_bg_math = colors.HexColor("#F8FAFC")    # Slate 50
    c_border = colors.HexColor("#E2E8F0")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=c_primary,
        spaceAfter=5
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=c_accent,
        spaceAfter=12
    )

    meta_style = ParagraphStyle(
        'DocMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=c_muted,
        spaceAfter=10
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=c_primary,
        spaceBefore=12,
        spaceAfter=5,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=c_accent,
        spaceBefore=9,
        spaceAfter=4,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'Heading3_Custom',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12.5,
        textColor=c_text,
        spaceBefore=7,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=c_text,
        spaceAfter=4
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=c_text,
        leftIndent=12,
        spaceAfter=3
    )

    math_block_style = ParagraphStyle(
        'MathBlock',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#1E3A8A"),
        backColor=c_bg_math,
        borderColor=colors.HexColor("#93C5FD"),
        borderWidth=0.8,
        borderPadding=5,
        spaceBefore=4,
        spaceAfter=6,
        alignment=1  # Centered
    )

    table_header_style = ParagraphStyle(
        'TH_Style',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TD_Style',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=9.5,
        textColor=c_text
    )

    code_block_style = ParagraphStyle(
        'CodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=7,
        leading=8.5,
        textColor=colors.HexColor("#38BDF8"),
        backColor=c_bg_code,
        borderPadding=5,
        spaceBefore=4,
        spaceAfter=6
    )

    story = []

    # Title & Metadata
    story.append(Paragraph("Phishing Shield AI — Technical Stack, Machine Learning & Cybersecurity Architecture", title_style))
    story.append(Paragraph("Enterprise-Grade Defense-in-Depth Specification | Hybrid Neuro-Symbolic Threat Engine", subtitle_style))
    story.append(Paragraph("<b>Author / System Architect:</b> Ram Narayan (RamNarayan0) &nbsp;|&nbsp; <b>Frameworks:</b> Python FastAPI 3.11, React 18, Scikit-Learn 1.5, MV3 &nbsp;|&nbsp; <b>Date:</b> October 2026", meta_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_accent, spaceBefore=2, spaceAfter=8))

    lines = md_text.splitlines()
    in_code_block = False
    code_lines = []
    in_table = False
    table_rows = []

    def format_inline(text: str) -> str:
        """Converts markdown bold, italic, and inline code to clean ReportLab tags."""
        # 1. Protect code spans
        code_spans = []
        def save_code(match):
            idx = len(code_spans)
            code_spans.append(match.group(1))
            return f"__CODESPAN_{idx}__"
        t = re.sub(r'`([^`]+)`', save_code, text)

        # 2. Protect inline math spans
        math_spans = []
        def save_math(match):
            idx = len(math_spans)
            math_spans.append(match.group(1))
            return f"__MATHSPAN_{idx}__"
        t = re.sub(r'\$([^\$]+)\$', save_math, t)

        # 3. HTML escape remaining literal text
        t = html.escape(t)

        # 4. Convert bold and italics
        t = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', t)
        t = re.sub(r'\*(.*?)\*', r'<i>\1</i>', t)

        # 5. Restore code spans
        for idx, span in enumerate(code_spans):
            escaped_code = html.escape(span)
            replacement = f'<font face="Courier" color="#0369A1"><b>{escaped_code}</b></font>'
            t = t.replace(f"__CODESPAN_{idx}__", replacement)

        # 6. Restore math spans
        for idx, span in enumerate(math_spans):
            clean_math = span.replace(r'\text{', '').replace('}', '').replace(r'\quad', ' ')
            clean_math = clean_math.replace(r'\mathbf{', '').replace(r'\sigma', 'σ')
            escaped_math = html.escape(clean_math)
            replacement = f'<font face="Courier-Bold" color="#1D4ED8"><i>{escaped_math}</i></font>'
            t = t.replace(f"__MATHSPAN_{idx}__", replacement)

        return t

    def flush_table():
        nonlocal in_table, table_rows
        if not table_rows:
            in_table = False
            return
        
        col_count = len(table_rows[0])
        avail_width = 515
        
        data = []
        for r_idx, row in enumerate(table_rows):
            is_header = (r_idx == 0)
            p_row = []
            for cell_text in row:
                st = table_header_style if is_header else table_cell_style
                p_row.append(Paragraph(format_inline(cell_text.strip()), st))
            data.append(p_row)

        if col_count == 4:
            col_widths = [105, 95, 80, 235]
        elif col_count == 3:
            col_widths = [115, 170, 230]
        else:
            col_widths = [avail_width / col_count] * col_count

        t = Table(data, colWidths=col_widths, repeatRows=1)
        t_style = [
            ('BACKGROUND', (0, 0), (-1, 0), c_primary),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, c_border),
        ]
        for r in range(1, len(data)):
            bg = colors.HexColor("#F8FAFC") if r % 2 == 1 else colors.white
            t_style.append(('BACKGROUND', (0, r), (-1, r), bg))
        t.setStyle(TableStyle(t_style))
        story.append(Spacer(1, 3))
        story.append(t)
        story.append(Spacer(1, 5))
        table_rows = []
        in_table = False

    def flush_code():
        nonlocal in_code_block, code_lines
        if code_lines:
            code_text = "\n".join(code_lines)
            story.append(Preformatted(code_text, code_block_style))
            story.append(Spacer(1, 3))
            code_lines = []
        in_code_block = False

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Handle code block start/end
        if stripped.startswith("```"):
            if in_code_block:
                flush_code()
            else:
                if in_table:
                    flush_table()
                in_code_block = True
                code_lines = []
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Handle Math Display Block ($$...$$)
        if stripped.startswith("$$") and stripped.endswith("$$") and len(stripped) > 4:
            raw_math = stripped[2:-2].strip()
            clean_math = raw_math.replace(r'\text{', '').replace('}', '').replace(r'\quad', ' ')
            clean_math = clean_math.replace(r'\mathbf{', '').replace(r'\sigma', 'σ').replace(r'\min', 'min')
            clean_math = clean_math.replace(r'\sum', 'Σ').replace(r'\exp', 'exp').replace(r'\log', 'log')
            clean_math = clean_math.replace(r'\frac', '').replace(r'\left', '').replace(r'\right', '')
            story.append(Paragraph(html.escape(clean_math), math_block_style))
            i += 1
            continue

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

        # Ignore decorative horizontal rules
        if stripped in ("---", "***", "___"):
            story.append(HRFlowable(width="100%", thickness=0.5, color=c_border, spaceBefore=3, spaceAfter=5))
            i += 1
            continue

        if not stripped:
            i += 1
            continue

        if stripped.startswith("# Phishing Shield AI"):
            i += 1
            continue

        if stripped.startswith("## "):
            h_text = stripped[3:].strip()
            story.append(Paragraph(format_inline(h_text), h1_style))
            i += 1
            continue

        if stripped.startswith("### "):
            h_text = stripped[4:].strip()
            story.append(Paragraph(format_inline(h_text), h2_style))
            i += 1
            continue

        if stripped.startswith("#### "):
            h_text = stripped[5:].strip()
            story.append(Paragraph(format_inline(h_text), h3_style))
            i += 1
            continue

        if stripped.startswith("* ") or stripped.startswith("- "):
            b_text = stripped[2:].strip()
            formatted = "&bull;&nbsp;&nbsp;" + format_inline(b_text)
            story.append(Paragraph(formatted, bullet_style))
            i += 1
            continue

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

    if in_code_block:
        flush_code()
    if in_table:
        flush_table()

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully compiled PDF: {output_pdf_path} ({os.path.getsize(output_pdf_path)} bytes)")

if __name__ == "__main__":
    src_md = r"c:\Users\Sai Santhosh Ram\OneDrive\Ram Narayan\OneDrive\Desktop\cyber\phishing-shield-ai\TECHSTACK_AND_CYBER_DOC.md"
    project_pdf = r"c:\Users\Sai Santhosh Ram\OneDrive\Ram Narayan\OneDrive\Desktop\cyber\phishing-shield-ai\TECHSTACK_AND_CYBER_DOC.pdf"
    desktop_pdf = r"C:\Users\Sai Santhosh Ram\OneDrive\Ram Narayan\OneDrive\Desktop\TECHSTACK_AND_CYBER_DOC.pdf"

    build_pdf(src_md, project_pdf)
    shutil.copyfile(project_pdf, desktop_pdf)
    print(f"Successfully placed on Desktop: {desktop_pdf}")
