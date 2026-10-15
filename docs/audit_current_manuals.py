"""Read-only documentation checks. Run from any directory; requires pypdf.

Prints JSON and returns nonzero on drift. Does not launch Bforartists, execute
manual instructions, access the network or regenerate published artifacts.
"""
import ast
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'bonecraft/scripts'))
import manual_tools as mt


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def addon_version(path):
    tree = ast.parse(read(path))
    assignment = next(n for n in tree.body if isinstance(n, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == 'bl_info' for t in n.targets))
    return '.'.join(map(str, ast.literal_eval(assignment.value)['version']))


def normalize(text):
    return ''.join(c.casefold() for c in text if c.isalnum())


def main():
    checks = []

    def check(name, ok, detail):
        checks.append(dict(name=name, status='VERIFIED' if ok else 'DRIFTED', detail=detail))

    versions = {
        'Anim Assist': addon_version('anim_assist/__init__.py'),
        'Ghost Tool': addon_version('ghost_tool/__init__.py'),
        'BoneCraft': addon_version('bonecraft/boneforge/__init__.py'),
    }
    files = [ROOT / p for p in ('docs/anim_assist/README.md', 'docs/ghost_tool/README.md',
                                'docs/ghost_tool/toolbar/README.md', 'bonecraft/docs/README.md')]
    for tool, directory, prefix in (('Anim Assist', 'anim_assist', 'AnimAssist'),
                                     ('Ghost Tool', 'ghost_tool', 'GhostTool')):
        manual = f'docs/{directory}/{prefix}_User_Manual.md'
        pdf = ROOT / f'docs/{directory}/{prefix}_User_Manual.pdf'
        source = read(manual)
        reader = PdfReader(pdf)
        title = source.splitlines()[0].removeprefix('# ')
        text = '\n'.join(p.extract_text() for p in reader.pages)
        # Footer titles/page numbers must not interrupt paragraphs across pages.
        body = '\n'.join(line for line in text.splitlines()
                         if line.strip() != title and not line.strip().isdigit())
        plain = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', source)
        blocks = [re.sub(r'^#{1,3} ', '', block).strip() for block in plain.split('\n\n')][1:]
        missing = []
        for block in blocks:
            for piece in (block.splitlines() if block.startswith(('- ', '1. ')) else [block]):
                piece = re.sub(r'^(?:- |\d+\. )', '', piece)
                if normalize(piece) not in normalize(body):
                    missing.append(piece[:90])
        check(tool + ' manual/PDF version', versions[tool] in title and
              versions[tool] in str(reader.metadata.title) and normalize(title) in normalize(text), title)
        check(tool + ' PDF content', not missing,
              dict(pages=len(reader.pages), missing_blocks=missing,
                   sha256=hashlib.sha256(pdf.read_bytes()).hexdigest()))
        files.append(ROOT / manual)

    for lang in mt.LANGS:
        home = ROOT / 'bonecraft/docs/manual' / lang
        chapters = mt.chapter_files(home)
        check('BoneCraft ' + lang + ' index/changelog version',
              all(versions['BoneCraft'] in (home / p).read_text(encoding='utf-8')
                  for p in ('index.md', '11-whats-new.md')),
              dict(version=versions['BoneCraft'], chapters=len(chapters)))
        files.extend(chapters)

    broken, total = [], 0
    for path in files:
        for link in mt.links(path.read_text(encoding='utf-8')):
            if mt.is_external(link):
                continue
            total += 1
            target = urlsplit(link)
            dest = (path.parent / unquote(target.path)).resolve() if target.path else path
            valid = dest.exists()
            if valid and target.fragment and dest.suffix.lower() == '.md':
                valid = unquote(target.fragment) in {h[2] for h in mt.headings(dest.read_text(encoding='utf-8'))}
            if not valid:
                broken.append(dict(source=str(path.relative_to(ROOT)), target=link))
    check('Current manual local links and Markdown anchors', not broken,
          dict(files=len(files), links=total, broken=broken))
    result = dict(versions=versions, checks=checks,
                  status='VERIFIED' if all(c['status'] == 'VERIFIED' for c in checks) else 'DRIFTED')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'VERIFIED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
