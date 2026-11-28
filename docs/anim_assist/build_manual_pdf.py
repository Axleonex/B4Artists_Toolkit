"""Build the Anim Assist Markdown manual as a linked PDF. Requires ReportLab."""
import html
import os
from pathlib import Path
import re
from urllib.parse import urljoin

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.platypus import Image, KeepTogether, Paragraph, SimpleDocTemplate, Table, TableStyle

ROOT = Path(__file__).resolve().parent
BASE = 'https://github.com/Axleonex/B4Artists_Toolkit/blob/main/docs/anim_assist/'
INK = colors.HexColor('#202830')
LINK = colors.HexColor('#24567a')
FONT = 'AnimAssistManual'


def register_fonts():
    """Embed Noto Sans; allow a portable font folder without changing the recipe."""
    fonts = Path(os.environ.get('ANIM_ASSIST_MANUAL_FONT_DIR', 'C:/Windows/Fonts'))
    for suffix, filename in (('', 'NotoSans-Regular.ttf'), ('-Bold', 'NotoSans-Bold.ttf')):
        path = fonts / filename
        if not path.is_file():
            raise SystemExit(f'Missing font: {path}. Set ANIM_ASSIST_MANUAL_FONT_DIR to a Noto Sans font folder.')
        pdfmetrics.registerFont(TTFont(FONT + suffix, str(path)))
    pdfmetrics.registerFontFamily(FONT, normal=FONT, bold=FONT + '-Bold',
                                 italic=FONT, boldItalic=FONT + '-Bold')


def inline(text):
    text = html.escape(text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m:
                  f'<a href="{urljoin(BASE, m[2])}" color="#24567a">{m[1]}</a>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    return re.sub(r'`([^`]+)`', r'\1', text)


class ManualDocument(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name in {'Heading2', 'Heading3'}:
            key = f'section-{self.seq.nextf("heading")}'
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(flowable.getPlainText(), key,
                                     level=0 if flowable.style.name == 'Heading2' else 1)


def main():
    register_fonts()
    markdown = (ROOT / 'AnimAssist_User_Manual.md').read_text(encoding='utf-8')
    title = markdown.splitlines()[0].removeprefix('# ')
    styles = getSampleStyleSheet()
    for name in ('BodyText', 'Heading2', 'Heading3', 'Title'):
        styles[name].textColor = INK
        styles[name].fontName = FONT if name == 'BodyText' else FONT + '-Bold'
        styles[name].bulletFontName = FONT
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
    styles.add(ParagraphStyle('Caption', parent=styles['BodyText'], fontSize=8,
                              leading=11, textColor=LINK, spaceAfter=10))
    story = []
    for block in markdown.strip().split('\n\n'):
        if not block.strip():
            continue
        picture = re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)', block.strip())
        if picture:
            asset = (ROOT / picture[2]).resolve()
            if not asset.is_relative_to(ROOT.resolve()) or not asset.is_file():
                raise ValueError(f'Missing or out-of-scope manual image: {picture[2]}')
            image = Image(str(asset))
            ratio = min(1.0, (letter[0] - 96) / image.imageWidth, 620 / image.imageHeight)
            image.drawWidth = image.imageWidth * ratio
            image.drawHeight = image.imageHeight * ratio
            story.append(KeepTogether([image, Paragraph(inline(picture[1]), styles['Caption'])]))
            continue
        if block.startswith('|'):
            # A Markdown table: header row, separator row, body rows.
            rows = [[cell.strip() for cell in line.strip().strip('|').split('|')]
                    for line in block.splitlines() if not re.fullmatch(r'\|[\s:|-]+\|', line.strip())]
            data = [[Paragraph(inline(cell) if index else f'<b>{inline(cell)}</b>', styles['Cell']) for cell in row]
                    for index, row in enumerate(rows)]
            table = Table(data, colWidths=[170, letter[0] - 96 - 170], repeatRows=1, spaceAfter=10)
            table.setStyle(TableStyle([('FONTNAME', (0, 0), (-1, -1), FONT),
                                       ('GRID', (0, 0), (-1, -1), .4, colors.HexColor('#c8d0d8')),
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
        canvas.setFont(FONT, 8)
        canvas.drawString(48, 28, title)
        canvas.drawRightString(letter[0] - 48, 28, str(doc.page))
        canvas.restoreState()

    target = ROOT / 'AnimAssist_User_Manual.pdf'
    doc = ManualDocument(str(target), pagesize=letter, leftMargin=48, rightMargin=48,
                         topMargin=42, bottomMargin=48, title=title, author='Axleonex',
                         subject='Bforartists interface and animation workflows',
                         creator='Anim Assist documentation', invariant=1)
    def canvasmaker(filename, **kwargs):
        kwargs['initialFontName'] = FONT
        return pdfcanvas.Canvas(filename, **kwargs)

    doc.build(story, onFirstPage=footer, onLaterPages=footer, canvasmaker=canvasmaker)
    print(f'Wrote {target.name}: {target.stat().st_size} bytes')


if __name__ == '__main__':
    main()
