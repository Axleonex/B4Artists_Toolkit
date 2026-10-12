"""Pure test: finding a region's stored width before widening it (owner, 2026-10-10). Run: python tests/test_shelf_width.py

Bforartists has no API to set a shelf's width, so core.shelf_width writes ARegion.sizex directly. It
writes only where the field is found beyond doubt: right after the region's width and height comes
its region type, and sizex sits 6 bytes after that. Anything ambiguous or missing: no write.
"""
import importlib.util
import os
import struct
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("bc_shelf_width", os.path.join(ROOT, "boneforge", "core", "shelf_width.py"))
sw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sw)                       # the file alone: no bpy needed for the pure part


def region_bytes(width, height, rtype, sizex, at=184, gap=8, size=768):
    raw = bytearray(size)
    struct.pack_into("<hh", raw, at, width, height)
    struct.pack_into("<h", raw, at + gap, rtype)
    struct.pack_into("<h", raw, at + gap + 6, sizex)
    return bytes(raw)


TOOLS, UI = sw.REGION_TYPE["TOOLS"], sw.REGION_TYPE["UI"]

# Bforartists 5.2: width/height at 184, region type at 192, sizex at 198
assert sw.locate(region_bytes(132, 751, TOOLS, 132), 132, 751, TOOLS) == 198
assert sw.locate(region_bytes(220, 751, UI, 220), 220, 751, UI) == 198
# another build lays the struct out differently: still found by its neighbours
assert sw.locate(region_bytes(132, 751, TOOLS, 132, at=200, gap=12), 132, 751, TOOLS) == 218

# nothing certain, nothing written
assert sw.locate(region_bytes(132, 751, UI, 132), 132, 751, TOOLS) is None, "wrong region type"
assert sw.locate(region_bytes(132, 700, TOOLS, 132), 132, 751, TOOLS) is None, "height does not match"
twice = bytearray(region_bytes(132, 751, TOOLS, 132))
struct.pack_into("<hhhhhhhh", twice, 400, 132, 751, 0, 0, TOOLS, 0, 0, 132)   # a second full match
assert sw.locate(bytes(twice), 132, 751, TOOLS) is None, "two candidates: ambiguous"
assert sw.locate(region_bytes(132, 751, TOOLS, 999), 132, 751, TOOLS) is None, "stored width must equal the width"
assert sw.locate(region_bytes(264, 1502, TOOLS, 132), 264, 1502, TOOLS, scale=2.0) == 198, "at 2x it is stored unscaled"

# how wide: only ever wider, in the region's unscaled pixels
assert sw.target(132, 240, 1.0) == 240 and sw.target(300, 240, 1.0) is None
assert sw.target(264, 240, 2.0) == 240, "at 2x a 132 px shelf is 264 screen px: stored as 132, widened to 240"
assert sw.target(480, 240, 2.0) is None
assert sw.target(479, 240, 2.0) == 240, "239.5 px is under 240: widened, not rounded away"
assert sw.target(299, 240, 1.25) == 240, "239.2 px at 1.25x is under 240"

# a changed setting applies at once: every shelf is checked again
sw._done.update({(1, "TOOLS"), (2, "UI")})
sw.forget_all()
assert not sw._done

assert "bpy" not in sys.modules, "the pure part imports without Bforartists"
print("PASS shelf width: sizex found by its neighbours only; ambiguous or mismatched means no write; only wider")
