"""Display-only product rename for the B4Artists build: BoneForge -> BoneCraft.

Deterministic and reviewable. Changes what users READ, never what Blender or
saved files LOOK UP:

  renamed   "BoneForge" inside Python string literals and docstrings (labels,
            tab names, tooltips, messages, translation keys and values) and in
            the package's Markdown files.
  kept      identifiers and stored names: ``boneforge`` (package, operator ids
            ``boneforge.*``, properties ``boneforge_*``), ``BONEFORGE_*`` class
            ids, ``BoneForge_*`` datablock names (``BoneForge_Rig``,
            ``BoneForge_Widgets`` ... are looked up in saved files),
            ``BoneForgeX`` class names, ``BoneForge/`` paths and user agents,
            release zip names (``BoneForge-8.5.0.zip``, ``BoneForge-BFA-...``),
            and code comments.

Usage:  python scripts/rename_display.py            (dry run: report only)
        python scripts/rename_display.py --apply    (write the changes)
The report lists every change: file, line, before, after.
"""
import io
import os
import re
import sys
import tokenize

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PKG = os.path.join(ROOT, "boneforge")
OLD, NEW = "BoneForge", "BoneCraft"
# a whole-word "BoneForge" that is not part of an identifier, a path or a zip name
# ...and not the name of the Open build ("open Blender BoneForge" stays BoneForge)
# (history notes such as "previously named BoneForge BFA" / "version of
# BoneForge" keep the old name; so do zip-name templates like BoneForge-<version>)
PATTERN = re.compile(r"(?<![A-Za-z0-9_])(?<![Oo]pen Blender\s)(?<!previously named\s)"
                     r"(?<!formerly\s)(?<!version of\s)"
                     r"BoneForge(?![A-Za-z0-9_/])(?!-(?:BFA-)?[\d<])")


def rename_text(text):
    return PATTERN.sub(NEW, text)


def rename_python(src):
    """Rename only inside STRING tokens; returns (new source, [(line, old, new)])."""
    changes = []
    tokens = list(tokenize.generate_tokens(io.StringIO(src).readline))
    lines = src.splitlines(keepends=True)
    # edit from the end so earlier offsets stay valid
    edits = []
    for tok in tokens:
        if tok.type == tokenize.STRING and OLD in tok.string:
            new = rename_text(tok.string)
            if new != tok.string:
                edits.append((tok.start, tok.end, tok.string, new))
    for (sr, sc), (er, ec), old, new in reversed(edits):
        if sr == er:
            line = lines[sr - 1]
            lines[sr - 1] = line[:sc] + new + line[ec:]
        else:
            first, last = lines[sr - 1], lines[er - 1]
            block = first[:sc] + new + last[ec:]
            lines[sr - 1:er] = [block]
        changes.append((sr, old.strip()[:90], new.strip()[:90]))
    return "".join(lines), list(reversed(changes))


def main(apply):
    report = []
    for dirpath, dirs, files in os.walk(PKG):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        for name in sorted(files):
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, ROOT).replace("\\", "/")
            if name.endswith(".py"):
                src = open(path, encoding="utf-8", newline="").read()
                new, changes = rename_python(src)
            elif name.endswith(".md"):
                src = open(path, encoding="utf-8", newline="").read()
                new = rename_text(src)
                changes = [(i + 1, a.strip()[:90], b.strip()[:90])
                           for i, (a, b) in enumerate(zip(src.splitlines(), new.splitlines())) if a != b]
            else:
                continue
            if new != src:
                report.extend("%s:%d\n  - %s\n  + %s" % (rel, ln, a, b) for ln, a, b in changes)
                if apply:
                    # sanity: a renamed Python file must still compile
                    if name.endswith(".py"):
                        compile(new, rel, "exec")
                    open(path, "w", encoding="utf-8", newline="").write(new)
    out = os.path.join(ROOT, "scripts", "rename_display_report.txt")
    open(out, "w", encoding="utf-8").write("\n".join(report) + "\n")
    files = len({r.split(":")[0] for r in report})
    print("%s: %d changes in %d files; report: %s"
          % ("APPLIED" if apply else "DRY RUN", len(report), files, out))


if __name__ == "__main__":
    main("--apply" in sys.argv)
