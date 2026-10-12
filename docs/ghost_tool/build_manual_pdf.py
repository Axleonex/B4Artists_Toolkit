"""Render the current Ghost Tool Markdown guide as a PDF. Requires reportlab."""
import html
from pathlib import Path
import re
from urllib.parse import urljoin

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate

ROOT = Path(__file__).resolve().parent
BASE = 'https://github.com/Axleonex/B4Artists_Toolkit/blob/main/docs/ghost_tool/'


def inline(text):
    text = html.escape(text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m:
                  f'<a href="{urljoin(BASE, m[2])}" color="#24567a">{m[1]}</a>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    return re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', text)


def main():
    markdown = (ROOT / 'GhostTool_User_Manual.md').read_text(encoding='utf-8')
    title = markdown.splitlines()[0].removeprefix('# ')
    styles = getSampleStyleSheet()
    styles['BodyText'].fontSize = 10
    styles['BodyText'].leading = 14
    styles['BodyText'].spaceAfter = 9
    styles['Heading2'].keepWithNext = True
    story = []
    for block in markdown.strip().split('\n\n'):
        style = 'Title' if block.startswith('# ') else 'Heading2' if block.startswith('## ') else 'BodyText'
        text = block.removeprefix('# ').removeprefix('## ').replace('\n', ' ')
        story.append(Paragraph(inline(text), styles[style]))

    def page_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        canvas.drawString(48, 30, title)
        canvas.drawRightString(letter[0] - 48, 30, str(doc.page))
        canvas.restoreState()

    pdf = ROOT / 'GhostTool_User_Manual.pdf'
    doc = SimpleDocTemplate(str(pdf), pagesize=letter, leftMargin=48,
                            rightMargin=48, topMargin=42, bottomMargin=48,
                            title=title, author='GoingGhost',
                            subject=title, creator='Ghost Tool documentation')
    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    print(f'Wrote {pdf.name}: {pdf.stat().st_size} bytes')


if __name__ == '__main__':
    main()
