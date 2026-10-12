"""Build the current Anim Assist and Ghost Tool guide PDFs.

[PowerShell] python docs/build_current_guides.py
Requires ReportLab. Markdown files beside the PDFs are the editable sources.
"""

from pathlib import Path
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


ROOT = Path(__file__).resolve().parent
GUIDES = (
    ROOT / "anim_assist/AnimAssist_User_Manual.md",
    ROOT / "ghost_tool/GhostTool_User_Manual.md",
)


def inline(text):
    links = []
    def link(match):
        links.append((match.group(1), match.group(2)))
        return f"LINKTOKEN{len(links) - 1}END"
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
    text = escape(text)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier" size="8">\1</font>', text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
    for index, (label, target) in enumerate(links):
        target = escape(target, {'"': '&quot;'})
        text = text.replace(f"LINKTOKEN{index}END", f'<link href="{target}" color="#17465B">{escape(label)}</link>')
    return text


class ManualDocument(SimpleDocTemplate):
    """Record heading destinations for the contents links and PDF outline."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.heading_keys = {}

    def afterFlowable(self, flowable):
        if not isinstance(flowable, Paragraph) or not flowable.style.name.startswith("Heading"):
            return
        heading = flowable.getPlainText()
        level = int(flowable.style.name[-1]) - 2
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        duplicate = self.heading_keys.get(slug, 0)
        self.heading_keys[slug] = duplicate + 1
        key = slug + (f"-{duplicate}" if duplicate else "")
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(heading, key, level=max(0, level), closed=level > 0)


def build(source):
    text = source.read_text(encoding="utf-8")
    title = text.splitlines()[0].removeprefix("# ")
    styles = getSampleStyleSheet()
    font_root = Path("C:/Windows/Fonts")
    if (font_root / "arial.ttf").exists():
        pdfmetrics.registerFont(TTFont("ManualSans", str(font_root / "arial.ttf")))
        pdfmetrics.registerFont(TTFont("ManualSans-Bold", str(font_root / "arialbd.ttf")))
        pdfmetrics.registerFont(TTFont("ManualSans-Italic", str(font_root / "ariali.ttf")))
        pdfmetrics.registerFont(TTFont("ManualSans-BoldItalic", str(font_root / "arialbi.ttf")))
        pdfmetrics.registerFontFamily("ManualSans", normal="ManualSans", bold="ManualSans-Bold",
                                     italic="ManualSans-Italic", boldItalic="ManualSans-BoldItalic")
        for style in styles.byName.values():
            style.fontName = "ManualSans"
    styles["Title"].fontSize = 25
    styles["Title"].leading = 30
    styles["Title"].alignment = TA_LEFT
    for name, size, leading in (("Heading2", 16, 21), ("Heading3", 12, 17), ("Heading4", 10.5, 15)):
        styles[name].textColor = colors.HexColor("#17465B")
        styles[name].fontSize = size
        styles[name].leading = leading
        styles[name].spaceBefore = 14 if name == "Heading2" else 8
        styles[name].spaceAfter = 6
        styles[name].keepWithNext = True
    styles["BodyText"].fontSize = 9.5
    styles["BodyText"].leading = 14
    styles["BodyText"].spaceAfter = 7
    styles["BodyText"].allowWidows = 0
    styles["BodyText"].allowOrphans = 0
    styles.add(ParagraphStyle("BulletText", parent=styles["BodyText"], leftIndent=12))
    story = []
    for block in text.strip().split("\n\n"):
        if block.startswith("# "):
            story += [Paragraph(inline(block[2:]), styles["Title"]), Spacer(1, 8)]
        elif re.match(r"^#{2,4} ", block):
            heading = re.match(r"^(#{2,4}) (.*)", block, re.S)
            story.append(Paragraph(inline(heading.group(2)), styles[f"Heading{len(heading.group(1))}"]))
        elif block.startswith("- "):
            for line in block.splitlines():
                story.append(Paragraph(inline(line.removeprefix("- ")), styles["BulletText"], bulletText="-"))
        elif re.match(r"^\d+\. ", block):
            for line in block.splitlines():
                if line.strip():
                    story.append(Paragraph(inline(line), styles["BulletText"]))
        else:
            story.append(Paragraph(inline(block.replace("\n", " ")), styles["BodyText"]))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#53616B"))
        canvas.drawString(42, 28, title.split(" - ")[0])
        canvas.drawRightString(A4[0] - 42, 28, str(doc.page))
        canvas.restoreState()

    output = source.with_suffix(".pdf")
    doc = ManualDocument(str(output), pagesize=A4, leftMargin=42, rightMargin=42,
                            topMargin=42, bottomMargin=48, title=title,
                            author="B4Artists Tools", subject="Complete feature and settings manual")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(output)


if __name__ == "__main__":
    for guide in GUIDES:
        build(guide)
