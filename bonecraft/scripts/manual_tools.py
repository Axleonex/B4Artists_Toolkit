"""Pure helpers for the BoneCraft manual (bonecraft/docs/manual/<lang>/).

Used by scripts/build_manual_pdf.py (joins a language's chapters into one HTML page for the PDF) and by
tests/test_manual.py (checks the chapters). No bpy; standard library plus the ``markdown`` package for HTML.
"""
import html as _html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # bonecraft/
MANUAL = ROOT / "docs" / "manual"
LANGS = ("en", "zh", "fr", "ja", "ko", "pt", "es")
CHAPTER = re.compile(r"^\d\d-[a-z0-9-]+\.md$")
_FENCE_RUN = re.compile(r"^ {0,3}(`{3,}|~{3,})")          # up to 3 spaces before a fence (CommonMark)
# [text](target), [text](<target>) and [text](target "title"): group 2 is the target (angle brackets included).
_LINK = re.compile(r'(\[[^\]]*\]\()(<[^>\n]*>|[^)\s]+)((?:\s+"[^"\n]*")?\))')


def chapter_files(lang_dir):
    """``index.md`` first, then the ``NN-name.md`` chapters in order."""
    lang_dir = Path(lang_dir)
    chapters = sorted(p for p in lang_dir.iterdir() if CHAPTER.match(p.name))
    index = lang_dir / "index.md"
    return ([index] if index.exists() else []) + chapters


def code_mask(lines):
    """For each line, True if it belongs to a fenced code block (fence lines included).

    A fence is 3+ backticks or tildes after up to 3 spaces; it closes on a line of the same character, at least as
    long, and nothing else but spaces (CommonMark). An unclosed fence runs to the end. Fences nested in list items
    (indented 4+ spaces) are not recognised: the manual has none."""
    mask, fence = [], None
    for line in lines:
        run = _FENCE_RUN.match(line)
        if fence is None:
            fence = run.group(1) if run else None
            mask.append(run is not None)
            continue
        mask.append(True)
        if run and run.group(1)[0] == fence[0] and len(run.group(1)) >= len(fence) \
                and not line[run.end():].strip(" \t"):
            fence = None
    return mask


def strip_code(text):
    """``text`` with every fenced code line blanked (line numbers stay), so ``#`` lines and links in code are
    ignored."""
    lines = text.split("\n")
    return "\n".join("" if code else line for line, code in zip(lines, code_mask(lines)))


def slug(heading):
    """GitHub-style anchor for a heading: formatting and punctuation dropped, lowercase, spaces to hyphens.

    Letters of every script are kept, so a Japanese heading gets a Japanese anchor."""
    # `*`, backticks and links go; `_` only where it marks emphasis (GitHub keeps mmd_tools' underscore)
    text = re.sub(r"[`*]|(?<!\w)_+|_+(?!\w)|\[([^\]]*)\]\([^)]*\)", lambda m: m.group(1) or "", heading).strip().lower()
    text = re.sub(r"[^\w\- ]", "", text)
    return text.replace(" ", "-")


def headings(text):
    """``[(level, text, slug)]`` for every Markdown heading outside code, with GitHub's ``-1``, ``-2`` suffixes
    for repeated slugs."""
    out, seen = [], {}
    for line in strip_code(text).splitlines():
        m = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if not m:
            continue
        base = slug(m.group(2))
        n = seen.get(base, 0)
        seen[base] = n + 1
        out.append((len(m.group(1)), m.group(2), base if n == 0 else "%s-%d" % (base, n)))
    return out


def _target(raw):
    return raw[1:-1].strip() if raw.startswith("<") else raw


def links(text):
    """Every Markdown link target outside code (angle brackets removed)."""
    return [_target(m.group(2)) for m in _LINK.finditer(strip_code(text))]


def is_external(target):
    return re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I) is not None


def chapter_id(stem):
    return "ch-" + stem


def heading_id(stem, anchor):
    return "%s--%s" % (stem, anchor)


def rewrite_links(text, stem, stems):
    """Point links between chapters (and to anchors) at ids inside the joined document.

    ``stem`` is this chapter's file stem; ``stems`` all chapter stems of the language (``index`` included).
    ``07-mechanisms.md`` -> ``#ch-07-mechanisms``; ``07-mechanisms.md#parts`` -> ``#07-mechanisms--parts``;
    ``#parts`` -> ``#<stem>--parts``. Anything else is left as it is."""
    def fix(m):
        target = _target(m.group(2))
        if is_external(target):
            return m.group(0)
        path, _, anchor = target.partition("#")
        if path == "":
            new = "#" + heading_id(stem, anchor)
        elif path.endswith(".md") and path[:-3] in stems and "/" not in path:
            new = "#" + (heading_id(path[:-3], anchor) if anchor else chapter_id(path[:-3]))
        else:
            return m.group(0)
        if m.group(2).startswith("<"):
            new = "<%s>" % new                        # keep the author's angle brackets
        return m.group(1) + new + m.group(3)

    lines = text.split("\n")
    return "\n".join(line if code else _LINK.sub(fix, line) for line, code in zip(lines, code_mask(lines)))


def add_heading_ids(text, stem):
    """Append ``{#<stem>--<anchor>}`` (Markdown attr_list) to every heading, and put an empty ``<a id="ch-<stem>">``
    before the chapter's first ``#`` heading, so links to the chapter and to its title heading both resolve."""
    first, used, out = True, {}, []
    lines = text.splitlines()
    for line, in_code in zip(lines, code_mask(lines)):
        m = None if in_code else re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if m:
            level, title = len(m.group(1)), m.group(2)
            base = slug(title)
            n = used.get(base, 0)
            used[base] = n + 1
            anchor = base if n == 0 else "%s-%d" % (base, n)
            line = "%s %s {#%s}" % (m.group(1), title, heading_id(stem, anchor))
            if first and level == 1:
                line = '<a id="%s"></a>\n\n%s' % (chapter_id(stem), line)
                first = False
        out.append(line)
    return "\n".join(out) + "\n"


CSS = """
@page { size: A4; margin: 18mm 16mm; }
body { font-family: "Segoe UI", "Yu Gothic UI", "Meiryo", "Malgun Gothic", "Microsoft YaHei", sans-serif;
       font-size: 10.5pt; line-height: 1.45; color: #111; }
h1 { font-size: 20pt; border-bottom: 2px solid #333; padding-bottom: 4px; }
h2 { font-size: 14pt; margin-top: 1.4em; }
h3 { font-size: 12pt; }
code, pre { font-family: Consolas, "Courier New", monospace; font-size: 9pt; }
pre { background: #f3f3f3; padding: 6px 8px; white-space: pre-wrap; }
table { border-collapse: collapse; } td, th { border: 1px solid #999; padding: 3px 6px; }
section.chapter { break-before: page; }
section.chapter:first-of-type { break-before: auto; }
a { color: #0645ad; text-decoration: none; }
"""


def join_html(lang_dir, title):
    """One HTML page holding every chapter of ``lang_dir``, links pointed inside the page."""
    import markdown
    files = chapter_files(lang_dir)
    stems = {p.stem for p in files}
    body = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        text = add_heading_ids(rewrite_links(text, path.stem, stems), path.stem)
        html = markdown.markdown(text, extensions=["attr_list", "tables", "fenced_code", "sane_lists"])
        html = re.sub(r'(<img[^>]*?\ssrc=")([^"]+)(")',                # the page is written elsewhere:
                      lambda m: m.group(0) if is_external(m.group(2)) or m.group(2).startswith("/") else
                      m.group(1) + (path.parent / _html.unescape(m.group(2))).resolve().as_uri() + m.group(3), html)
        body.append('<section class="chapter">\n%s\n</section>' % html)
    return ('<!doctype html>\n<html><head><meta charset="utf-8"><title>%s</title><style>%s</style></head>\n'
            '<body>\n%s\n</body></html>\n') % (_html.escape(title), CSS, "\n".join(body))


def html_link_problems(html):
    """``href`` values in ``html`` that still point at a ``.md`` file or at an id the page does not have."""
    ids = set(re.findall(r'\sid="([^"]+)"', html))
    problems = []
    for href in re.findall(r'href="([^"]+)"', html):
        target = _html.unescape(href)
        if re.search(r"\.md(#|$)", target) and not is_external(target):
            problems.append(target)
        elif target.startswith("#") and target[1:] not in ids:
            problems.append(target)
    return problems
