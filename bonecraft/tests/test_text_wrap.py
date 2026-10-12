"""Pure test: panel text wraps to the panel width (owner, 2026-10-10). Run: python tests/test_text_wrap.py"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import importlib.util

_spec = importlib.util.spec_from_file_location("bc_helpers", os.path.join(ROOT, "boneforge", "core", "helpers.py"))
_helpers = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_helpers)                  # the file alone: boneforge.core imports bpy
wrap = _helpers.wrap


def px(s):
    """A fixed-width measure: 6 px per narrow character, 12 per wide (CJK) one."""
    import unicodedata
    return sum(12 if unicodedata.east_asian_width(c) in "WF" else 6 for c in s)


text = "Skin needs an armature or a mesh selected."
assert wrap(text, 10_000, px) == [text], "wide enough: one line"
lines = wrap(text, 100, px)
assert lines == ["Skin needs an", "armature or a", "mesh selected."], lines
assert all(px(x) <= 100 for x in lines)
assert " ".join(lines) == text, "nothing lost, nothing added"

# a word longer than the line is split, never dropped or overflowing
lines = wrap("Supercalifragilistic word", 60, px)
assert all(px(x) <= 60 for x in lines), lines
assert lines[0].endswith("-") and "".join(x.rstrip("-") for x in lines).replace(" ", "") == "Supercalifragilisticword",     ("a Latin word split across lines carries a hyphen", lines)

# Japanese / Chinese have no spaces: break between characters, never inside one
ja = "レビューにはアーマチュアの選択が必要です。"
lines = wrap(ja, 96, px)
assert all(px(x) <= 96 for x in lines) and "".join(lines) == ja, lines
# Korean has spaces between words: break there
ko = "리뷰에는 아마추어 선택이 필요합니다."
lines = wrap(ko, 100, px)
assert all(px(x) <= 100 for x in lines) and " ".join(lines) == ko, lines

assert wrap("", 100, px) == [""]
assert wrap("Short", 0, px) == ["Short"], "no width known: one line, unwrapped"
# an icon narrows the first line only; a word that fits a full line is never split
lines = wrap("Go to the bones of the rig", 80, px, first_width=40)
assert px(lines[0]) <= 40 and all(px(x) <= 80 for x in lines[1:]) and " ".join(lines) == "Go to the bones of the rig", lines
lines = wrap("Performance, clothing and naming", 80, px, first_width=40)
assert lines[0] == "", ("the first word cannot sit beside the icon: an empty first line says so", lines)
assert " ".join(x for x in lines if x) == "Performance, clothing and naming", lines

# a header cannot wrap: too long, it is shortened with an ellipsis (Blender would show nothing)
clip = _helpers.clip
assert clip("Visemes", 60, px) == "Visemes"
c = clip("Translate Bone Names", 60, px)
assert px(c) <= 60 and c.endswith("…") and c.startswith("Transl"), c
assert clip("Translate Bone Names", 3, px) == "…"

# the room a line gets: the region minus margins, never so little that wrapping turns off
room = _helpers.line_room
assert room(132, 1.0) == 132 - 56 and room(132, 1.0, icon=True) == 132 - 56 - 24
assert room(132, 1.0, inset=14) == 132 - 56 - 14
assert room(132, 2.0, icon=True) >= 48 * 2.0, "a 132 px region at 2x UI scale still wraps"
assert room(264, 2.0) == 264 - 112

assert "bpy" not in sys.modules, "helpers.wrap stays importable without Bforartists"
print("PASS text wrap: words, long words, CJK, Korean, empty, unknown width")
