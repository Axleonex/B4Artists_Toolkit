"""Render the current Ghost Tool Markdown guide as a PDF. Requires reportlab."""
import argparse
import html
import os
from pathlib import Path
import re
from urllib.parse import urljoin

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate

ROOT = Path(__file__).resolve().parent
BASE = 'https://github.com/Axleonex/B4Artists_Toolkit/blob/main/docs/ghost_tool/'


def inline(text, base=BASE):
    text = html.escape(text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m:
                  f'<a href="{urljoin(base, m[2])}" color="#24567a">{m[1]}</a>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    return re.sub(r'`([^`]+)`', r'<font name="Courier">\1</font>', text)


LANG_FONTS = {
    'fr': ('arial.ttf', 'arialbd.ttf'),
    'pt': ('arial.ttf', 'arialbd.ttf'),
    'es': ('arial.ttf', 'arialbd.ttf'),
    'zh': ('msyh.ttc', 'msyhbd.ttc'),
    'ja': ('YuGothR.ttc', 'YuGothB.ttc'),
    'ko': ('malgun.ttf', 'malgunbd.ttf'),
}


def build(language='en', font_dir=None):
    home = ROOT if language == 'en' else ROOT / 'manual' / language
    markdown = (home / 'GhostTool_User_Manual.md').read_text(encoding='utf-8')
    base = BASE if language == 'en' else urljoin(BASE, f'manual/{language}/')
    title = markdown.splitlines()[0].removeprefix('# ')
    styles = getSampleStyleSheet()
    font = 'Helvetica'
    if language != 'en':
        directory = Path(font_dir or Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts')
        regular, bold = LANG_FONTS[language]
        font, bold_font = f'Ghost-{language}', f'Ghost-{language}-Bold'
        for name, filename in ((font, regular), (bold_font, bold)):
            path = directory / filename
            if not path.is_file():
                raise FileNotFoundError(f'Required font missing: {path}. Use --font-dir.')
            pdfmetrics.registerFont(TTFont(name, str(path), subfontIndex=0))
        pdfmetrics.registerFontFamily(font, normal=font, bold=bold_font,
                                      italic=font, boldItalic=bold_font)
        for name in ('Title', 'Heading2', 'BodyText'):
            styles[name].fontName = bold_font if name != 'BodyText' else font
            if language in ('zh', 'ja', 'ko'):
                styles[name].wordWrap = 'CJK'
    styles['BodyText'].fontSize = 10
    styles['BodyText'].leading = 14
    styles['BodyText'].spaceAfter = 9 if language == 'en' else 8
    styles['Heading2'].keepWithNext = True
    story = []
    for block in markdown.strip().split('\n\n'):
        style = 'Title' if block.startswith('# ') else 'Heading2' if block.startswith('## ') else 'BodyText'
        text = block.removeprefix('# ').removeprefix('## ').replace('\n', ' ')
        story.append(Paragraph(inline(text, base), styles[style]))

    def page_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont(font, 9)
        canvas.drawString(48, 30, title)
        canvas.drawRightString(letter[0] - 48, 30, str(doc.page))
        canvas.restoreState()

    pdf = home / 'GhostTool_User_Manual.pdf'
    doc = SimpleDocTemplate(str(pdf), pagesize=letter, leftMargin=48,
                            rightMargin=48, topMargin=42, bottomMargin=48,
                            title=title, author='GoingGhost',
                            subject=title, creator='Ghost Tool documentation')
    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    print(f'Wrote {language}/{pdf.name}: {pdf.stat().st_size} bytes')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('languages', nargs='*', choices=['en', *LANG_FONTS],
                        help='Default: en. Translations require their Unicode fonts.')
    parser.add_argument('--font-dir', type=Path,
                        help='Directory containing Arial, Microsoft YaHei, Yu Gothic and Malgun fonts.')
    args = parser.parse_args()
    for language in args.languages or ['en']:
        build(language, args.font_dir)


if __name__ == '__main__':
    main()
