# bonecraft/tests/test_manual.py
"""Pure test: the BoneCraft manual (bonecraft/docs/manual/<lang>/) — structure, names, links, UI labels, sizes.

Run: python -W error tests/test_manual.py [--manual-only] [--partial LANG]
--manual-only  skip the README files (they are updated in their own task)
--partial LANG a language in progress (en included): its files must be a subset of the final set; links to its
               chapters not written yet, and heading/anchor checks against its skeleton chapters (title and
               navigation only, no ## heading), are skipped
"""
import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))       # bonecraft/
sys.path.insert(0, str(ROOT / "scripts"))

import manual_tools as mt  # noqa: E402

# Every language of the manual (all of mt.LANGS). --partial checks one language while it is being written.
EXPECTED_LANGS = ("en", "zh", "fr", "ja", "ko", "pt", "es")
EN_FILES = ("index.md", "01-start.md", "02-guides-a.md", "03-guides-b.md", "04-cats-pipeline.md", "05-rig-tools.md",
            "06-rig-builder.md", "07-mechanisms.md", "08-vrchat.md", "09-cats.md", "10-reference.md", "11-whats-new.md",
            "12-crescent-rose.md")
NOTICE = {
    "zh": "本手册由英文版机器翻译而成。",
    "fr": "Ce manuel a été traduit automatiquement à partir de l'édition anglaise.",
    "ja": "このマニュアルは英語版から機械翻訳されたものです。",
    "ko": "이 설명서는 영어판을 기계 번역한 것입니다.",
    "pt": "Este manual foi traduzido automaticamente a partir da edição em inglês.",
    "es": "Este manual se tradujo automáticamente a partir de la edición en inglés.",
}
OLD_NAME = "BoneCraft" + " BFA"                       # split so this file passes test_product_name
BONEFORGE_SECTION = "BoneCraft and BoneForge"          # the one English `##` section that may name BoneForge
MAX_CHAPTER_BYTES = 50 * 1024
# Bforartists' own UI words a chapter may set in bold (they are not BoneCraft strings).
HOST_LABELS = {
    "Add-ons", "Edit", "Preferences", "Install from Disk...", "Install from Disk…", "Object Mode", "Pose Mode",
    "Edit Mode", "Weight Paint", "Vertex Group", "Vertex Groups", "Shape Keys", "Armature", "Object Data",
    "Properties", "Scene", "Tool Shelf", "Sidebar", "File", "Import", "Export", "Save Preferences",
    "Enter", "Esc", "Tab", "Space", "Delete", "Backspace",          # keys
}
# Bold text that looks like a label but is not one, with the reason.
NOT_LABELS = {
    "You should see": "lead-in", "Note": "lead-in", "Tip": "lead-in", "Important": "lead-in",
}


def manual_files(lang):
    d = mt.MANUAL / lang
    return sorted(p.name for p in d.iterdir() if p.suffix == ".md") if d.is_dir() else []


def scope_docs(manual_only=False):
    """Markdown files the name and link rules cover: the manual, and (unless manual_only) the docs index, the
    README and the Rigging Suite page."""
    files = sorted(mt.MANUAL.rglob("*.md"))
    if not manual_only:
        files += [ROOT / "docs" / "README.md", ROOT / "README.md", ROOT / "docs" / "BoneCraft_Rigging_Suite.md"]
    return files


def indexed(lang):
    """``index.md`` plus every chapter file ``lang``/index.md links to."""
    index = mt.MANUAL / lang / "index.md"
    if not index.exists():
        return []
    names = {t.partition("#")[0] for t in mt.links(index.read_text(encoding="utf-8")) if mt.CHAPTER.match(t.partition("#")[0])}
    return sorted(names | {"index.md"})


_TEXT = re.compile(r"""\btext\s*=\s*(?:T\(\s*)?(['"])((?:(?!\1).){1,160})\1""")
_T_CALL = re.compile(r"""\bT\(\s*(['"])((?:(?!\1).){1,160})\1\s*\)""")
_NAME = re.compile(r"""\bname\s*=\s*(?:T\(\s*)?(['"])((?:(?!\1).){1,160})\1""")
_ENUM_ITEM = re.compile(r"""\(\s*(['"])[A-Za-z0-9_/]+\1\s*,\s*(['"])(?!boneforge\.)((?:(?!\2).){1,160})\2\s*,""")
_FACTORY = re.compile(r"""(['"])(boneforge\.\w+)\1\s*,\s*(['"])((?:(?!\3).){1,160})\3""")
_CLASS = re.compile(r"^[ \t]*class\s+(\w+)\s*\(([^)]*)\)\s*:", re.M)
_IDNAME = re.compile(r"""\bbl_idname\s*=\s*(['"])([^'"]+)\1""")
_LABEL = re.compile(r"""\bbl_label\s*=\s*(?:T\(\s*)?(['"])((?:(?!\1).){1,160})\1""")
_OP_CALL = re.compile(r"""\.operator\(\s*(?:(['"])(boneforge\.\w+)\1|(\w+)\.bl_idname)""")
_PANEL_FACTORY = re.compile(r"""\(\s*(['"])(?:BF|BONEFORGE)_PT_\w+\1\s*,\s*(['"])((?:(?!\2).){1,160})\2""")
_PROP_CALL = re.compile(r"\b\w*Property\(")
_ITEMS_KW = re.compile(r"\bitems\s*=\s*")
_REPORT_CALL = re.compile(r"\.report\(")
_ASSIGN = re.compile(r"^[ \t]*(\w+)\s*(?::[^=\n]*)?=\s*([\[(])", re.M)
_DEF = re.compile(r"^([ \t]*)def\s+(\w+)\s*\(", re.M)


def call_args(s, start):
    """Source text from ``start`` (just after a call's '(', or a list's '[') to the matching close."""
    depth, i, quote = 1, start, None
    while i < len(s) and depth:
        c = s[i]
        if quote:
            if c == "\\":
                i += 1
            elif c == quote:
                quote = None
        elif c in "'\"":
            quote = c
        elif c in "([{":
            depth += 1
        elif c in ")]}":
            depth -= 1
        i += 1
    return s[start:i - 1]


def items_names(texts):
    """Names passed as ``items=NAME`` anywhere (a constant or a callback defined elsewhere)."""
    names = set()
    for s in texts.values():
        for m in _ITEMS_KW.finditer(s):
            ref = re.match(r"[\w.]+", s[m.end():])
            if ref:
                names.add(ref.group(0).split(".")[-1])
    return names


def enum_regions(s, names):
    """Source that lists enum items: ``items=[...]``, and constants or callbacks named ``*items*`` or passed as
    ``items=``. A tuple of strings elsewhere (bone pairs, table rows) is not an enum item."""
    out = [call_args(s, m.end() + 1) for m in _ITEMS_KW.finditer(s) if s[m.end():m.end() + 1] in ("[", "(")]
    for m in _ASSIGN.finditer(s):
        if "items" in m.group(1).lower() or m.group(1) in names:
            out.append(call_args(s, m.end()))
    for m in _DEF.finditer(s):
        if "items" in m.group(2).lower() or m.group(2) in names:
            body = s.find("\n", m.end()) + 1 or len(s)           # the body starts on the next line
            end = re.search(r"^[ \t]{0,%d}\S" % len(m.group(1)), s[body:], re.M)
            out.append(s[body: body + end.start() if end else len(s)])
    return out


def without_reports(s):
    """``s`` with the arguments of every ``.report(...)`` call blanked: a message is not a label."""
    for m in reversed(list(_REPORT_CALL.finditer(s))):
        args = call_args(s, m.end())
        s = s[:m.end()] + " " * len(args) + s[m.end() + len(args):]
    return s


def addon_strings(texts=None):
    """Text the add-on draws, so a bold label in the manual is what the reader sees: ``text=`` and ``T("...")``
    literals, property names, enum item names, panel/menu/list ``bl_label``s, and an operator's ``bl_label``
    (or factory label) only where some ``layout.operator(...)`` call draws it without its own ``text=``, or as an
    icon-only button (``text=""``, named by its tooltip). Operators no panel draws are not included."""
    found, op_label, cls_id, shown = set(), {}, {}, set()
    if texts is None:
        sources = [p for p in (ROOT / "boneforge").rglob("*.py") if "i18n" not in p.parts]
        texts = {p: p.read_text(encoding="utf-8", errors="replace") for p in sources}
    names = items_names(texts)
    for s in texts.values():
        found.update(m.group(2) for m in _TEXT.finditer(s))
        found.update(m.group(2) for m in _T_CALL.finditer(without_reports(s)))
        found.update(m.group(3) for m in _PANEL_FACTORY.finditer(s))   # _sub("BF_PT_x", "Header", ...)
        for m in _PROP_CALL.finditer(s):                       # name= of a property, not of any call
            n = _NAME.search(call_args(s, m.end()))
            if n:
                found.add(n.group(2))
        for region in enum_regions(s, names):
            found.update(m.group(3) for m in _ENUM_ITEM.finditer(region))
        for m in _FACTORY.finditer(s):
            op_label.setdefault(m.group(2), m.group(4))
        classes = list(_CLASS.finditer(s))
        for i, c in enumerate(classes):
            body = s[c.end(): classes[i + 1].start() if i + 1 < len(classes) else len(s)]
            idm, lab = _IDNAME.search(body), _LABEL.search(body)
            if idm:
                cls_id[c.group(1)] = idm.group(2)
            if lab and idm and idm.group(2).startswith("boneforge."):
                op_label[idm.group(2)] = lab.group(2)          # an operator: shown only where drawn
            elif lab:
                found.add(lab.group(2))                         # a panel, menu or list header
    for s in texts.values():
        for m in _OP_CALL.finditer(s):
            idname = m.group(2) or cls_id.get(m.group(3), "")
            args = call_args(s, m.end())
            if idname and (not re.search(r"\btext\s*=", args) or re.search(r"""\btext\s*=\s*(['"])\1""", args)):
                shown.add(idname)
    found.update(op_label[i] for i in shown if i in op_label)
    return found


def self_test_addon_strings():
    """Check 5's collector on a small source: drawn text is found, look-alikes are not."""
    src = "\n".join((
        'layout.label(text=T("Shown Label"))',
        'x: bpy.props.StringProperty(name="Prop Name")',
        'y: EnumProperty(items=[("A", "Enum Item", "")])',
        'MODE_ITEMS = [("B", "Const Item", "")]',
        'pairs = [("Index", "Not An Item", 0), ("upperarm", "forearm", 1)]',
        'TOOL = ToolManifest(name="Manifest Name")',
        "self.report({'INFO'}, T(\"Report Only\"))",
        'BF_PT_x = _sub("BF_PT_x", "Panel Header", 1, draw_x)',
        'def _mode_items(self, context):',
        '    return [("C", "Callback Item", "")]',
        'def other():',
        '    return [("D", "After Callback", "")]',
    ))
    got = addon_strings({"sample.py": src})
    want = {"Shown Label", "Prop Name", "Enum Item", "Const Item", "Panel Header", "Callback Item"}
    unwanted = {"Not An Item", "forearm", "Manifest Name", "Report Only", "After Callback"}
    return ["check 5 collector misses %s or accepts %s" % (sorted(want - got), sorted(got & unwanted))
            ] if not want <= got or got & unwanted else []


MAX_IMAGE_BYTES = 300 * 1024
MAX_IMAGE_WIDTH = 1400
_IMAGE = re.compile(r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)|<img\b[^>]*?\ssrc="([^"]+)"[^>]*?(?:\salt="([^"]*)")?[^>]*>')


def image_problems(path):
    """Images of one chapter: the file exists, is a PNG under MAX_IMAGE_BYTES and MAX_IMAGE_WIDTH, alt text given."""
    import struct
    out = []
    for m in _IMAGE.finditer(mt.strip_code(path.read_text(encoding="utf-8"))):
        alt, target = (m.group(1), m.group(2)) if m.group(2) else (m.group(4) or "", m.group(3))
        where = "%s: image %s" % (path.relative_to(ROOT) if path.is_relative_to(ROOT) else path.name, target)
        if not alt.strip():
            out.append(where + " has no alt text")
        dest = path.parent / target
        if not dest.exists():
            out.append(where + " is missing")
            continue
        if dest.stat().st_size > MAX_IMAGE_BYTES:
            out.append(where + " is %d bytes (max %d)" % (dest.stat().st_size, MAX_IMAGE_BYTES))
        with dest.open("rb") as f:
            head = f.read(24)
        if head[:8] != b"\x89PNG\r\n\x1a\n":
            out.append(where + " is not a PNG")
        else:
            width = struct.unpack(">I", head[16:20])[0]
            if width > MAX_IMAGE_WIDTH:
                out.append(where + " is %d px wide (max %d)" % (width, MAX_IMAGE_WIDTH))
    return out


def self_test_image_problems():
    """image_problems on a scratch chapter: a good image passes, the four faults are each named."""
    import struct, tempfile, zlib
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)

        def png(name, width):
            raw = b"".join(b"\x00" + b"\x00" * (width * 3) for _ in range(2))

            def chunk(t, data):
                return struct.pack(">I", len(data)) + t + data + struct.pack(">I", zlib.crc32(t + data))
            (d / name).write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, 2, 8, 2, 0, 0, 0))
                                   + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))
        png("good.png", 1400)
        png("wide.png", 1401)
        (d / "big.png").write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * (MAX_IMAGE_BYTES + 1))
        chapter = d / "99-x.md"
        chapter.write_text("![Step 1](good.png)\n![](good.png)\n![x](gone.png)\n![x](wide.png)\n"
                           "<img src=\"big.png\" alt=\"x\">\n", encoding="utf-8")
        got = image_problems(chapter)
    want = ["has no alt text", "gone.png is missing", "wide.png is 1401 px wide", "big.png is"]
    return [] if len(got) == 4 and all(any(w in g for g in got) for w in want) else ["image check self-test: %s" % got]


def ui_like(raw):
    """Bold text that reads like a UI label: up to 6 words, Title Case (or ending in an ellipsis)."""
    if raw.rstrip().endswith(":") or re.search(r"→|>|\bCtrl\b|\bShift\b|\bAlt\b", raw):
        return False
    words = raw.strip().split()
    if not words or len(words) > 6 or (len(words) == 1 and len(raw.strip()) < 4):
        return False
    if raw.strip().endswith(("…", "...")):
        return True
    return all(w[0].isupper() or not w[0].isalpha() for w in words if len(w) > 3)


def bold_labels(text):
    text = re.sub(r"`[^`]*`", "", mt.strip_code(text))
    return [b.strip() for b in re.findall(r"\*\*([^*\n]+?)\*\*", text) if ui_like(b)]


def is_skeleton(path):
    """A chapter written only as its title and navigation lines, to be filled by a later task (no ``##`` heading)."""
    return path.exists() and path.name != "index.md" and not any(
        h[0] == 2 for h in mt.headings(path.read_text(encoding="utf-8")))


def boneforge_allowed_range(lang_text, en_text):
    """Line range of the section that may name BoneForge: the `##` section at the same position as the English
    "BoneCraft and BoneForge" section."""
    en_h2 = [h for h in mt.headings(en_text) if h[0] == 2]
    pos = next((i for i, h in enumerate(en_h2) if h[1] == BONEFORGE_SECTION), None)
    lines = mt.strip_code(lang_text).splitlines()
    starts = [i for i, ln in enumerate(lines) if re.match(r"^##\s", ln)]
    if pos is None or pos >= len(starts):
        return 0, 0, lines                            # no such section yet: BoneForge allowed nowhere
    return starts[pos], (starts[pos + 1] if pos + 1 < len(starts) else len(lines)), lines


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--manual-only", action="store_true")
    ap.add_argument("--partial", default=None)
    args = ap.parse_args(argv)
    problems = []

    # 1. languages and file names: en/ holds index.md and exactly the chapters it links; translations mirror en/
    present = tuple(l for l in mt.LANGS if (mt.MANUAL / l).is_dir())
    if set(present) - {args.partial} != set(EXPECTED_LANGS) - {args.partial}:
        problems.append("languages present %s, expected %s" % (present, EXPECTED_LANGS))
    if not indexed("en") or manual_files("en") != indexed("en"):
        problems.append("en/ files %s, but en/index.md links %s" % (manual_files("en"), indexed("en")))
    final = sorted(EN_FILES)
    if (args.partial == "en" and not set(manual_files("en")) <= set(final)) or (
            args.partial != "en" and manual_files("en") != final):
        problems.append("en/ files %s, expected %s" % (manual_files("en"), final))
    for lang in present:
        if lang == "en":
            continue
        if lang == args.partial:
            extra = sorted(set(manual_files(lang)) - set(manual_files("en")))
            if extra:
                problems.append("%s/ has files en/ lacks: %s" % (lang, extra))
        elif manual_files(lang) != manual_files("en"):
            problems.append("%s/ files differ from en/: %s" % (lang, manual_files(lang)))

    # 2. same headings as English, per chapter: the same sequence of heading levels
    for lang in present:
        for name in manual_files("en"):
            p = mt.MANUAL / lang / name
            if lang == "en" or not p.exists() or (lang == args.partial and is_skeleton(p)):
                continue
            en_levels = [h[0] for h in mt.headings((mt.MANUAL / "en" / name).read_text(encoding="utf-8"))]
            levels = [h[0] for h in mt.headings(p.read_text(encoding="utf-8"))]
            if levels != en_levels:
                problems.append("%s/%s heading levels %s differ from en %s" % (lang, name, levels, en_levels))

    # 3. names: never the old name (OLD_NAME); "BoneForge" only in 01-start's BoneCraft-and-BoneForge section
    en_start = (mt.MANUAL / "en" / "01-start.md")
    for path in scope_docs(args.manual_only):
        if not path.exists():
            problems.append("%s is missing" % path.relative_to(ROOT))
            continue
        text = path.read_text(encoding="utf-8")
        if OLD_NAME in text:
            problems.append("%s says %r" % (path.relative_to(ROOT), OLD_NAME))
        if "BoneForge" not in mt.strip_code(text):
            continue
        if path.name == "01-start.md" and path.parent.parent == mt.MANUAL and en_start.exists():
            lo, hi, lines = boneforge_allowed_range(text, en_start.read_text(encoding="utf-8"))
            bad = [i + 1 for i, ln in enumerate(lines) if "BoneForge" in ln and not lo <= i < hi]
        else:
            bad = [i + 1 for i, ln in enumerate(mt.strip_code(text).splitlines()) if "BoneForge" in ln]
        if bad:
            problems.append("%s names BoneForge outside its section, lines %s" % (path.relative_to(ROOT), bad[:10]))

    # 4. relative links resolve (file, and #anchor to a heading in it)
    for path in scope_docs(args.manual_only):
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for target in mt.links(text):
            if mt.is_external(target):
                continue
            file_part, _, anchor = target.partition("#")
            dest = path if file_part == "" else (path.parent / file_part)
            if (args.partial and path.parent == mt.MANUAL / args.partial and not dest.exists()
                    and file_part in EN_FILES):
                continue                              # a chapter of a translation in progress, not written yet
            if not dest.exists():
                problems.append("%s: link to missing %s" % (path.relative_to(ROOT), target))
            elif anchor and dest.suffix == ".md" and not (args.partial and is_skeleton(dest)):
                if anchor not in {h[2] for h in mt.headings(dest.read_text(encoding="utf-8"))}:
                    problems.append("%s: link to missing anchor %s" % (path.relative_to(ROOT), target))

    # 4b. images exist, are small PNGs, and have alt text
    problems += self_test_image_problems()
    for lang in present:
        for name in manual_files(lang):
            problems += image_problems(mt.MANUAL / lang / name)

    # 5. bold UI labels in the English chapters are text the add-on draws (or host labels / declared non-labels)
    problems += self_test_addon_strings()
    strings = addon_strings()
    for name in manual_files("en"):
        path = mt.MANUAL / "en" / name
        for label in bold_labels(path.read_text(encoding="utf-8")):
            bare = label.rstrip("…").rstrip(".").strip()
            if label in strings or bare in strings or label in HOST_LABELS or label in NOT_LABELS:
                continue
            problems.append("en/%s: bold label '%s' is not text a BoneCraft panel draws (or a Bforartists label)" % (name, label))

    # 6. chapter sizes; 7. translation notices; 8. the English PDF page has no dangling links
    for lang in present:
        for name in manual_files(lang):
            size = (mt.MANUAL / lang / name).stat().st_size
            if size > MAX_CHAPTER_BYTES:
                problems.append("%s/%s is %d bytes (max %d)" % (lang, name, size, MAX_CHAPTER_BYTES))
        if lang != "en":
            index = mt.MANUAL / lang / "index.md"
            if (lang != args.partial or index.exists()) and (
                    not index.exists() or NOTICE[lang] not in index.read_text(encoding="utf-8")):
                problems.append("%s/index.md lacks the machine-translation notice" % lang)
    if (mt.MANUAL / "en").is_dir():
        dangling = mt.html_link_problems(mt.join_html(mt.MANUAL / "en", "BoneCraft Manual"))
        if args.partial == "en":                      # chapters not written yet, or skeletons (as in check 4)
            skeletons = {n[:-3] for n in EN_FILES if is_skeleton(mt.MANUAL / "en" / n)}
            dangling = [d for d in dangling if d.partition("#")[0] not in EN_FILES
                        and not any(d.startswith("#%s--" % s) or d == "#ch-" + s for s in skeletons)]
        if dangling:
            problems.append("en PDF page: links without a target: %s" % sorted(set(dangling)))

    # 9. navigation: every chapter links back to index.md and ends with a link to the next chapter
    order = [f for f in EN_FILES if f != "index.md"]
    for lang in present:
        for name in manual_files(lang):
            if name == "index.md" or name not in order:
                continue
            text = (mt.MANUAL / lang / name).read_text(encoding="utf-8")
            if "index.md" not in [t.partition("#")[0] for t in mt.links(text)]:
                problems.append("%s/%s has no link back to index.md" % (lang, name))
            pos = order.index(name)
            nxt = order[pos + 1] if pos + 1 < len(order) else None
            last = [ln for ln in text.splitlines() if ln.strip()][-1]
            if nxt and nxt not in [t.partition("#")[0] for t in mt.links(last)]:
                problems.append("%s/%s does not end with a link to %s" % (lang, name, nxt))

    if problems:
        print("\n".join("FAIL " + p for p in problems))
        sys.exit(1)
    print("PASS test_manual (%s)" % ", ".join(present))


if __name__ == "__main__":
    main()
