# resume template library
# 3 built-in styles + a docx exporter that rebuilds the resume text
# in the chosen layout using python-docx

import io
import re

from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

TEMPLATES = [
    {
        "id": "modern",
        "name": "Modern",
        "description": "Clean, minimal, HR-friendly. Accent color + section rules. Best for tech roles.",
        "accent": "1F4E79",
        "font": "Calibri",
        "layout": "centered header, single page",
    },
    {
        "id": "classic",
        "name": "Classic",
        "description": "Traditional professional look. Serif font, all-caps headings. Best for conservative firms.",
        "accent": "404040",
        "font": "Georgia",
        "layout": "left header, bordered sections",
    },
    {
        "id": "creative",
        "name": "Creative",
        "description": "Bold accent + two-tone headings. Stands out for design/marketing roles.",
        "accent": "7C3AED",
        "font": "Verdana",
        "layout": "two-tone header band",
    },
]


def list_templates():
    """public list (no internal-only fields)"""
    return [
        {k: t[k] for k in ("id", "name", "description", "accent", "font", "layout")}
        for t in TEMPLATES
    ]


def get_template(template_id):
    for t in TEMPLATES:
        if t["id"] == template_id:
            return t
    return None


# ---------------------------------------------------------------- parsing ---

# section headers we recognize in resume text
SECTION_HEADERS = [
    ("summary", r"(professional summary|summary|profile|objective)"),
    ("skills", r"(technical skills|skills|technologies|tech stack)"),
    ("experience", r"(experience|work history|employment)"),
    ("projects", r"(projects|portfolio|academic projects)"),
    ("education", r"(education|university|college|degree)"),
    ("certifications", r"(certifications|courses|achievements|awards)"),
]


def parse_resume(text):
    """roughly split resume text into sections -> list of (section, [lines])"""
    sections = []
    lines = text.splitlines()
    current = None
    current_lines = []

    def flush():
        nonlocal current, current_lines
        if current and current_lines:
            sections.append((current[0], current_lines))
        current_lines = []

    for line in lines:
        stripped = line.strip()
        matched = None
        for name, pattern in SECTION_HEADERS:
            if re.match(pattern, stripped, re.I):
                matched = name
                break
        if matched:
            flush()
            current = (matched, stripped)
        elif current:
            current_lines.append(stripped)
        elif stripped:
            # text before the first section header: treat as header/contact
            current = ("header", [])
            current_lines.append(stripped)
    flush()
    return sections


# ---------------------------------------------------------------- exporter ---

def export_docx(resume_text, template_id):
    """build a .docx resume in the given template style, return bytes"""
    template = get_template(template_id)
    if not template:
        raise ValueError(f"unknown template: {template_id}")

    sections = parse_resume(resume_text)
    accent = template["accent"]
    font_name = template["font"]

    doc = Document()
    # base font
    style = doc.styles["Normal"]
    style.font.name = font_name
    style.font.size = Pt(10.5)

    # margins
    for section in doc.sections:
        section.top_margin = Inches(0.6)
        section.bottom_margin = Inches(0.6)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)

    # separate the header block (name + contact) from the rest
    header_lines = []
    body_sections = []
    for name, lines in sections:
        if name == "header":
            header_lines = lines
        else:
            body_sections.append((name, lines))

    # --- header ---
    if header_lines and header_lines[0].strip():
        p = doc.add_paragraph()
        if template_id == "creative":
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(header_lines[0].upper())
        run.bold = True
        run.font.size = Pt(20)
        run.font.color.rgb = RGBColor.from_string(accent)
        run.font.name = font_name

    for line in header_lines[1:]:
        p = doc.add_paragraph()
        if template_id != "classic":
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(line)
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(0x66, 0x66, 0x66)

    # --- sections ---
    for name, lines in body_sections:
        title = name.upper()
        p = doc.add_paragraph()
        run = p.add_run(title)
        run.bold = True
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor.from_string(accent)
        # underline via border-ish approach: just underline text
        if template_id == "classic":
            run.underline = True

        # thin rule under heading for modern/creative
        if template_id != "classic":
            pPr = p._p.get_or_add_pPr()
            pBdr = pPr.makeelement("w:pBdr", {})
            bottom = pPr.makeelement("w:bottom", {
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val": "single",
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sz": "6",
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}space": "2",
                "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}color": accent,
            })
            pBdr.append(bottom)
            pPr.append(pBdr)

        for line in lines:
            if not line:
                continue
            bullet = line.startswith(("-", "*", "•"))
            clean = line.lstrip("-*• ").strip()
            if not clean:
                continue
            bp = doc.add_paragraph(style="List Bullet" if bullet else None)
            run = bp.add_run(clean)
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf
