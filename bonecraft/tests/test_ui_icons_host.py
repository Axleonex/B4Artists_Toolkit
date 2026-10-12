# bonecraft/tests/test_ui_icons_host.py
"""In-Bforartists test: every icon name the add-on writes in its source is one this host knows.

An unknown icon name raises inside a panel's draw, so the panel stops partway and the VRChat Tools
section shows "Draw error -- see console" (VRChat Performance lost its Calculate button to 'REFRESH').
The scan reads every ``icon=`` keyword through the AST, so names split across lines and both arms
of ``"A" if cond else "B"`` are checked too.
"""
import ast
import os

import bpy

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "boneforge")


def _names(node):
    """The literal names an ``icon=`` value can evaluate to: a string, either arm of a conditional, an
    ``or`` chain. Computed values (a lookup, a variable) are not checkable here and give nothing; the
    condition of a conditional is never an icon."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.IfExp):
        return _names(node.body) + _names(node.orelse)
    if isinstance(node, ast.BoolOp):
        return [n for v in node.values for n in _names(v)]
    return []


def icon_uses(source):
    """[(line, icon name)] for every string an ``icon=`` keyword argument can take in ``source``."""
    out = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Call):
            for kw in node.keywords:
                if kw.arg == "icon":
                    out += [(kw.value.lineno, name) for name in _names(kw.value)]
    return out


def bad_icons(valid, root=ROOT):
    """[(path, line, icon)] for every literal icon name under ``root`` that ``valid`` does not hold."""
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in filenames:
            if fn.endswith(".py"):
                path = os.path.join(dirpath, fn)
                with open(path, encoding="utf-8") as fh:
                    out += [(os.path.relpath(path, root), line, name)
                            for line, name in icon_uses(fh.read()) if name and name not in valid]
    return out


def run():
    # the scanner itself: a name split across lines and both arms of a conditional are found
    sample = ('layout.label(\n    text="x",\n    icon=(\n        "AAA"\n    ),\n)\n'
              'row.operator("o", icon="BBB" if s != "OK" else "CCC")\n'
              'row.label(icon=ICONS.get(kind, "DOT"))\n')
    assert icon_uses(sample) == [(4, "AAA"), (7, "BBB"), (7, "CCC")], icon_uses(sample)

    valid = set(bpy.types.UILayout.bl_rna.functions["label"].parameters["icon"].enum_items.keys())
    assert "FILE_REFRESH" in valid and "NONE" in valid, "this is the host's icon list"
    assert bad_icons(valid) == [], bad_icons(valid)

    # The CATS tab's VRChat section is titled "Avatar Tools" (owner, 2026-10-10)
    import boneforge
    from mech_draw_stubs import Rec
    boneforge.register()
    try:
        log = []
        shim = type("Shim", (), {})()
        shim.layout = Rec(log)
        bpy.types.BF_PT_sb_vrchat.draw_header(shim, bpy.context)
        assert [k.get("text") for n, a, k in log if n == "label"] == ["Avatar Tools"], log
    finally:
        boneforge.unregister()
    print("PASS UI icons: every icon name in the add-on (read through the AST) exists in this host; "
          "the CATS VRChat section is titled Avatar Tools")
