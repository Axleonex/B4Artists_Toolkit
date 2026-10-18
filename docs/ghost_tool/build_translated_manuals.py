"""Build all six Ghost Tool 4.3.1 translated manuals with embedded Unicode fonts.

[PowerShell] python docs/ghost_tool/build_translated_manuals.py
Requires reportlab and suitable TrueType fonts. GHOST_MANUAL_FONT_DIR overrides
the font directory; Windows fonts are used by default. English stays unchanged.
"""
import hashlib
import html
import json
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
DEST = ROOT / 'translations'
BASE = 'https://github.com/Axleonex/B4Artists_Toolkit/blob/main/docs/ghost_tool/translations/'
LANGUAGES = {
    'zh': ('简体中文', 'msyh.ttc', 'msyhbd.ttc', True),
    'fr': ('Français', 'NotoSans-Regular.ttf', 'NotoSans-Bold.ttf', False),
    'ja': ('日本語', 'YuGothM.ttc', 'YuGothB.ttc', True),
    'ko': ('한국어', 'malgun.ttf', 'malgunbd.ttf', False),
    'pt': ('Português', 'NotoSans-Regular.ttf', 'NotoSans-Bold.ttf', False),
    'es': ('Español', 'NotoSans-Regular.ttf', 'NotoSans-Bold.ttf', False),
}


def inline(text):
    text = html.escape(text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m:
                  f'<a href="{html.escape(urljoin(BASE, html.unescape(m[2])), quote=True)}" color="#24567a">{m[1]}</a>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    return re.sub(r'`([^`]+)`', r'\1', text)


def build(code, source_blocks, fonts):
    name, regular_file, bold_file, cjk = LANGUAGES[code]
    regular, bold = 'GhostManual-' + code, 'GhostManual-' + code + '-Bold'
    for family, filename in ((regular, regular_file), (bold, bold_file)):
        font = fonts / filename
        if not font.is_file():
            raise SystemExit(f'Missing font: {font}. Set GHOST_MANUAL_FONT_DIR to a folder containing the required fonts.')
        pdfmetrics.registerFont(TTFont(family, str(font), subfontIndex=0))
    pdfmetrics.registerFontFamily(regular, normal=regular, bold=bold, italic=regular, boldItalic=bold)
    markdown = DEST / f'GhostTool_User_Manual_{code}.md'
    text = markdown.read_text(encoding='utf-8')
    blocks = text.strip().split('\n\n')
    if len(blocks) != len(source_blocks) + 1:
        raise SystemExit(f'{code}: expected all {len(source_blocks)} source blocks and one translation note, got {len(blocks)}')
    comparable = [blocks[0], *blocks[2:]]
    if [b.startswith('## ') for b in comparable] != [b.startswith('## ') for b in source_blocks]:
        raise SystemExit(f'{code}: section order differs from the English source')
    title = blocks[0].removeprefix('# ')
    if '4.3.1' not in title:
        raise SystemExit(f'{code}: missing version in title')
    styles = getSampleStyleSheet()
    for style in styles.byName.values():
        style.fontName = regular
    styles['Title'].fontName = bold
    styles['Title'].fontSize = 19
    styles['Title'].leading = 26
    styles['Heading2'].fontName = bold
    styles['Heading2'].fontSize = 13
    styles['Heading2'].leading = 19
    styles['Heading2'].keepWithNext = True
    styles['BodyText'].fontSize = 10
    styles['BodyText'].leading = 15 if cjk or code == 'ko' else 14
    styles['BodyText'].spaceAfter = 9
    styles['BodyText'].allowWidows = 0
    styles['BodyText'].allowOrphans = 0
    if cjk:
        for key in ('Title', 'Heading2', 'BodyText'):
            styles[key].wordWrap = 'CJK'
    story = []
    for block in blocks:
        style = 'Title' if block.startswith('# ') else 'Heading2' if block.startswith('## ') else 'BodyText'
        body = block.removeprefix('# ').removeprefix('## ').replace('\n', ' ')
        story.append(Paragraph(inline(body), styles[style]))

    def footer(canvas, document):
        canvas.saveState()
        canvas.setFont(regular, 8)
        canvas.drawString(48, 30, title)
        canvas.drawRightString(letter[0] - 48, 30, str(document.page))
        canvas.restoreState()

    pdf = markdown.with_suffix('.pdf')
    document = SimpleDocTemplate(str(pdf), pagesize=letter, leftMargin=48,
                                 rightMargin=48, topMargin=42, bottomMargin=48,
                                 title=title, author='GoingGhost', subject=title,
                                 creator='Ghost Tool documentation')
    document.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f'{code}: {pdf.name}, {pdf.stat().st_size} bytes', flush=True)
    return {'language': name, 'markdown': markdown.name,
            'markdown_sha256_lf': hashlib.sha256(text.encode('utf-8')).hexdigest(),
            'pdf': pdf.name, 'pdf_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(),
            'pdf_bytes': pdf.stat().st_size, 'source_blocks_covered': len(source_blocks)}


def main():
    source = (ROOT / 'GhostTool_User_Manual.md').read_text(encoding='utf-8')
    source_blocks = source.strip().split('\n\n')
    fonts = Path(os.environ.get('GHOST_MANUAL_FONT_DIR', str(Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts')))
    manifest = {'version': '4.3.1', 'source': '../GhostTool_User_Manual.md',
                'source_sha256_lf': hashlib.sha256(source.encode('utf-8')).hexdigest(),
                'source_block_count': len(source_blocks),
                'translation_note': 'Translated from the English guide; English UI labels retained. No professional linguistic review claimed.',
                'languages': {code: build(code, source_blocks, fonts) for code in LANGUAGES}}
    (DEST / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
