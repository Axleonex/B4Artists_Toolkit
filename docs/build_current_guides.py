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


ROOT = Path(__file__).resolve().parent
GUIDES = (
    ROOT / "anim_assist/AnimAssist_User_Manual.md",
    ROOT / "ghost_tool/GhostTool_User_Manual.md",
)


def inline(text):
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = escape(text)
    text = re.sub(r"`([^`]+)`", r'<font name="Courier">\1</font>', text)
    return re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)


def build(source):
    text = source.read_text(encoding="utf-8")
    title = text.splitlines()[0].removeprefix("# ")
    styles = getSampleStyleSheet()
    styles["Title"].fontSize = 22
    styles["Title"].leading = 27
    styles["Title"].alignment = TA_LEFT
    styles["Heading2"].textColor = colors.HexColor("#17465B")
    styles["BodyText"].fontSize = 10
    styles["BodyText"].leading = 15
    styles["BodyText"].spaceAfter = 9
    styles["BodyText"].allowWidows = 0
    styles["BodyText"].allowOrphans = 0
    styles.add(ParagraphStyle("BulletText", parent=styles["BodyText"], leftIndent=12))
    story = []
    for block in text.strip().split("\n\n"):
        if block.startswith("# "):
            story += [Paragraph(inline(block[2:]), styles["Title"]), Spacer(1, 8)]
        elif block.startswith("## "):
            story.append(Paragraph(inline(block[3:]), styles["Heading2"]))
        elif block.startswith("- "):
            for line in block.splitlines():
                story.append(Paragraph(inline(line.removeprefix("- ")), styles["BulletText"], bulletText="-"))
        else:
            story.append(Paragraph(inline(block.replace("\n", " ")), styles["BodyText"]))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#53616B"))
        canvas.drawString(42, 28, title)
        canvas.drawRightString(A4[0] - 42, 28, str(doc.page))
        canvas.restoreState()

    output = source.with_suffix(".pdf")
    doc = SimpleDocTemplate(str(output), pagesize=A4, leftMargin=42, rightMargin=42,
                            topMargin=42, bottomMargin=48, title=title,
                            author="B4Artists Tools", subject="Current release guide")
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(output)


if __name__ == "__main__":
    for guide in GUIDES:
        build(guide)
