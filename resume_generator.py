
import io
import re
import html

from pypdf import PdfReader

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable
)

from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH


# ==========================================
# TEXT CLEANING
# ==========================================

def clean_text(text):

    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r"\1 (\2)",
        text
    )

    text = text.replace("**", "")
    text = text.replace("__", "")
    text = text.replace("`", "")

    return text.strip()


# ==========================================
# PARSE RESUME
# ==========================================

def parse_resume(text):

    parsed = []

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        if line.startswith("### "):

            parsed.append(
                ("subheading", clean_text(line[4:]))
            )

        elif line.startswith("## "):

            parsed.append(
                ("heading", clean_text(line[3:]))
            )

        elif line.startswith("# "):

            parsed.append(
                ("name", clean_text(line[2:]))
            )

        elif line.startswith(("- ", "* ", "• ")):

            parsed.append(
                ("bullet", clean_text(line[2:]))
            )

        else:

            parsed.append(
                ("body", clean_text(line))
            )

    return parsed


# ==========================================
# PDF SAFE TEXT
# ==========================================

def pdf_safe_text(text):

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "..."
    }

    for old, new in replacements.items():

        text = text.replace(old, new)

    try:

        text.encode("cp1252")

    except UnicodeEncodeError:

        raise ValueError(
            "Unsupported PDF characters detected. "
            "Please edit them before exporting."
        )

    return html.escape(text)


# ==========================================
# BUILD ATS PDF
# ==========================================

def build_pdf(resume_text, font_size, margin):

    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=margin,
        leftMargin=margin,
        topMargin=margin,
        bottomMargin=margin,
        title="Professional Resume"
    )

    styles = {

        "name": ParagraphStyle(
            name="Name",
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=23,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceAfter=5
        ),

        "contact": ParagraphStyle(
            name="Contact",
            fontName="Helvetica",
            fontSize=9,
            leading=11,
            alignment=TA_CENTER,
            textColor=colors.black,
            spaceAfter=2
        ),

        "heading": ParagraphStyle(
            name="Heading",
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=13,
            textColor=colors.black,
            spaceBefore=6,
            spaceAfter=2,
            keepWithNext=True
        ),

        "subheading": ParagraphStyle(
            name="Subheading",
            fontName="Helvetica-Bold",
            fontSize=font_size,
            leading=font_size + 2,
            textColor=colors.black,
            spaceBefore=3,
            spaceAfter=2,
            keepWithNext=True
        ),

        "body": ParagraphStyle(
            name="Body",
            fontName="Helvetica",
            fontSize=font_size,
            leading=font_size + 2,
            textColor=colors.black,
            spaceAfter=2
        ),

        "bullet": ParagraphStyle(
            name="Bullet",
            fontName="Helvetica",
            fontSize=font_size,
            leading=font_size + 2,
            leftIndent=10,
            firstLineIndent=0,
            bulletIndent=0,
            spaceAfter=2,
            textColor=colors.black
        )
    }

    story = []

    before_first_section = True

    for kind, text in parse_resume(resume_text):

        safe_text = pdf_safe_text(text)

        if kind == "name":

            story.append(
                Paragraph(
                    safe_text,
                    styles["name"]
                )
            )

        elif kind == "heading":

            before_first_section = False

            story.append(
                Paragraph(
                    safe_text.upper(),
                    styles["heading"]
                )
            )

            story.append(
    HRFlowable(
        width="100%",
        thickness=0.6,
        color=colors.black,
        spaceBefore=0,
        spaceAfter=3
    )
)

        elif kind == "subheading":

            story.append(
                Paragraph(
                    safe_text,
                    styles["subheading"]
                )
            )

        elif kind == "bullet":

            story.append(
                Paragraph(
                    safe_text,
                    styles["bullet"],
                    bulletText="\u2022"
                )
            )

        else:

            style = (
                styles["contact"]
                if before_first_section
                else styles["body"]
            )

            story.append(
                Paragraph(
                    safe_text,
                    style
                )
            )

    document.build(story)

    buffer.seek(0)

    return buffer.getvalue()


# ==========================================
# AUTOMATIC PAGE FITTING
# ==========================================

def generate_pdf(
    resume_text,
    resume_length="1 Page"
):

    target_pages = (
        1 if resume_length == "1 Page"
        else 2
    )

    # Try readable font sizes and compact margins.
    # Never silently remove candidate information.

    layouts = [
        (11, 36),
        (10.5, 34),
        (10, 32),
        (9.5, 30)
    ]

    for font_size, margin in layouts:

        pdf_data = build_pdf(
            resume_text,
            font_size,
            margin
        )

        reader = PdfReader(
            io.BytesIO(pdf_data)
        )

        page_count = len(reader.pages)

        if page_count <= target_pages:

            return pdf_data

    raise ValueError(
        f"Resume exceeds the selected "
        f"{target_pages}-page limit. "
        "Please shorten the summary or project "
        "descriptions in the resume editor "
        "and try again."
    )


# ==========================================
# GENERATE ATS FRIENDLY DOCX
# ==========================================

def generate_docx(
    resume_text,
    resume_length="1 Page"
):

    document = Document()

    section = document.sections[0]

    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)

    section.top_margin = Inches(0.45)
    section.bottom_margin = Inches(0.45)
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)

    font_size = (
        10 if resume_length == "1 Page"
        else 11
    )

    normal = document.styles["Normal"]

    normal.font.name = "Arial"
    normal.font.size = Pt(font_size)

    normal.font.color.rgb = RGBColor(
        0, 0, 0
    )

    normal.paragraph_format.space_after = Pt(2)
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.line_spacing = 1.0

    # Standard ATS-readable heading styles

    for name in ["Heading 1", "Heading 2"]:

        style = document.styles[name]

        style.font.name = "Arial"

        style.font.size = Pt(
            11 if name == "Heading 1"
            else font_size
        )

        style.font.bold = True

        style.font.color.rgb = RGBColor(
            0, 0, 0
        )

        style.paragraph_format.space_before = Pt(5)
        style.paragraph_format.space_after = Pt(2)
        style.paragraph_format.keep_with_next = True

    bullet_style = document.styles["List Bullet"]

    bullet_style.font.name = "Arial"
    bullet_style.font.size = Pt(font_size)

    bullet_style.paragraph_format.space_after = Pt(2)
    bullet_style.paragraph_format.line_spacing = 1.0

    before_first_section = True

    for kind, text in parse_resume(resume_text):

        if kind == "name":

            paragraph = document.add_paragraph()

            paragraph.alignment = (
                WD_ALIGN_PARAGRAPH.CENTER
            )

            run = paragraph.add_run(text)

            run.font.name = "Arial"
            run.font.size = Pt(20)
            run.bold = True

            paragraph.paragraph_format.space_after = (
                Pt(4)
            )

        elif kind == "heading":

            before_first_section = False

            document.add_heading(
                text.upper(),
                level=1
            )

        elif kind == "subheading":

            document.add_heading(
                text,
                level=2
            )

        elif kind == "bullet":

            document.add_paragraph(
                text,
                style="List Bullet"
            )

        else:

            paragraph = document.add_paragraph(text)

            if before_first_section:

                paragraph.alignment = (
                    WD_ALIGN_PARAGRAPH.CENTER
                )

                for run in paragraph.runs:

                    run.font.size = Pt(9)

    buffer = io.BytesIO()

    document.save(buffer)

    buffer.seek(0)

    return buffer.getvalue()
