# bonecraft/tests/test_product_name.py
"""Pure test: the add-on is called BoneCraft (spec 2026-10-08-manuals §6): the old two-word name with "BFA"
appears nowhere in its code or tests.

Run: python -W error tests/test_product_name.py [file ...]   (files limit the text scan; bl_info is always checked)
"""
import ast
import os
import sys
from pathlib import Path

ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))       # bonecraft/
OLD = "BoneCraft" + " BFA"                                                       # split so this file passes its own scan


def bl_info():
    tree = ast.parse((ROOT / "boneforge" / "__init__.py").read_text(encoding="utf-8"))
    node = next(n for n in ast.walk(tree) if isinstance(n, ast.Assign)
                and any(getattr(t, "id", "") == "bl_info" for t in n.targets))
    return ast.literal_eval(node.value)


def main(argv):
    info = bl_info()
    problems = []
    if info["name"] != "BoneCraft":
        problems.append("bl_info name is %r, expected 'BoneCraft'" % info["name"])
    if info["location"] != "3D Viewport > Tool Shelf / Sidebar > BoneCraft, Rig Builder, CATS":
        problems.append("bl_info location is %r" % info["location"])
    files = [ROOT / a for a in argv] if argv else sorted(
        list((ROOT / "boneforge").rglob("*.py")) + list((ROOT / "tests").glob("*.py")))
    for path in files:
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if OLD in line:
                problems.append("%s:%d still says %s" % (path.relative_to(ROOT), n, OLD))
    if problems:
        print("\n".join("FAIL " + p for p in problems))
        sys.exit(1)
    print("PASS test_product_name (%d files)" % len(files))


def test_product_name():
    """pytest entry point: the whole package and every test file."""
    main([])


if __name__ == "__main__":
    main(sys.argv[1:])
