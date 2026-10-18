"""Build the Anim Assist Markdown manual as a linked PDF. Requires ReportLab."""
import html
from pathlib import Path
import re
from urllib.parse import urljoin

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle

ROOT = Path(__file__).resolve().parent
BASE = 'https://github.com/Axleonex/B4Artists_Toolkit/blob/main/docs/anim_assist/'
INK = colors.HexColor('#202830')
LINK = colors.HexColor('#24567a')


def inline(text):
    text = html.escape(text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m:
                  f'<a href="{urljoin(BASE, m[2])}" color="#24567a">{m[1]}</a>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    return re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', text)


class ManualDocument(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name in {'Heading2', 'Heading3'}:
            key = f'section-{self.seq.nextf("heading")}'
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(flowable.getPlainText(), key,
                                     level=0 if flowable.style.name == 'Heading2' else 1)


def main():
    markdown = (ROOT / 'AnimAssist_User_Manual.md').read_text(encoding='utf-8')
    title = markdown.splitlines()[0].removeprefix('# ')
    styles = getSampleStyleSheet()
    for name in ('BodyText', 'Heading2', 'Heading3', 'Title'):
        styles[name].textColor = INK
    styles['BodyText'].fontSize = 10
    styles['BodyText'].leading = 14
    styles['BodyText'].spaceAfter = 8
    styles['Heading2'].fontSize = 15
    styles['Heading2'].spaceBefore = 15
    styles['Heading2'].keepWithNext = True
    styles['Heading3'].fontSize = 11
    styles['Heading3'].spaceBefore = 10
    styles['Heading3'].keepWithNext = True
    styles.add(ParagraphStyle('List', parent=styles['BodyText'], leftIndent=16,
                              firstLineIndent=0, bulletIndent=2, spaceAfter=5))
    styles.add(ParagraphStyle('List2', parent=styles['List'], leftIndent=32, bulletIndent=18))
    styles.add(ParagraphStyle('Cell', parent=styles['BodyText'], spaceAfter=0))
    story = []
    for block in markdown.strip().split('\n\n'):
        if not block.strip():
            continue
        if block.startswith('|'):
            # A Markdown table: header row, separator row, body rows.
            rows = [[cell.strip() for cell in line.strip().strip('|').split('|')]
                    for line in block.splitlines() if not re.fullmatch(r'\|[\s:|-]+\|', line.strip())]
            data = [[Paragraph(inline(cell) if index else f'<b>{inline(cell)}</b>', styles['Cell']) for cell in row]
                    for index, row in enumerate(rows)]
            table = Table(data, colWidths=[170, letter[0] - 96 - 170], repeatRows=1, spaceAfter=10)
            table.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), .4, colors.HexColor('#c8d0d8')),
                                       ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#eef2f5')),
                                       ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
            story.append(table)
            continue
        if block.startswith(('- ', '1. ')):
            for line in block.splitlines():
                match = re.match(r'( *)(-|\d+\.) (.*)', line)
                if not match:
                    raise ValueError(f'Unsupported wrapped list: {line}')
                indent, prefix, content = match.groups()
                story.append(Paragraph(inline(content), styles['List2' if indent else 'List'],
                                       bulletText='\u2022' if prefix == '-' else prefix))
        else:
            level = re.match(r'^(#{1,3}) ', block)
            style = {1: 'Title', 2: 'Heading2', 3: 'Heading3'}[len(level[1])] if level else 'BodyText'
            content = block[len(level[0]):] if level else block
            story.append(Paragraph(inline(content.replace('\n', ' ')), styles[style]))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(LINK)
        canvas.setFont('Helvetica', 8)
        canvas.drawString(48, 28, title)
        canvas.drawRightString(letter[0] - 48, 28, str(doc.page))
        canvas.restoreState()

    target = ROOT / 'AnimAssist_User_Manual.pdf'
    doc = ManualDocument(str(target), pagesize=letter, leftMargin=48, rightMargin=48,
                         topMargin=42, bottomMargin=48, title=title, author='Axleonex',
                         subject='Bforartists interface and animation workflows',
                         creator='Anim Assist documentation', invariant=1)
    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f'Wrote {target.name}: {target.stat().st_size} bytes')


if __name__ == '__main__':
    main()
