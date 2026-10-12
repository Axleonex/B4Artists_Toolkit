"""Regression test for the name-hygiene scanner (no bpy).

Guards the bug an external review found: the allow-list used to be stripped
from the text before blocklist matching, so a blocked product name that merely
*contained* an allowed generic term (the longer name shares a substring with a
generic term) was silently masked and the scan reported clean. The blocked
phrase used below is assembled at runtime so the literal name never appears in
this file.
"""
import importlib.util
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load():
    path = os.path.join(ROOT, "scripts", "name_scan.py")
    spec = importlib.util.spec_from_file_location("bf_name_scan", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write(dirpath, name, text):
    with open(os.path.join(dirpath, name), "w", encoding="utf-8") as fh:
        fh.write(text)


def main():
    ns = _load()

    # The blocked phrase is ASSEMBLED so the literal product name never appears
    # in this file (the no-product-names rule applies to tests too).
    allow = "auto-rig"
    blocked = allow + " pro"            # the masked-product-name pattern

    # 1. THE BUG: a blocked phrase that contains an allowed substring must flag.
    assert ns._blocked_hit(("see " + blocked.title() + " here").lower(),
                           blocked, [allow]), "blocked phrase masked by allow-list"

    # 2. A blocked term occurring ONLY inside an allowed phrase is suppressed.
    assert not ns._blocked_hit("auto-rigging tools", "rig", ["auto-rigging"])

    # 3. A standalone occurrence is flagged even if an allow term exists.
    assert ns._blocked_hit("the rig moved", "rig", [allow])

    # 4. End-to-end scan_root: planted product name in a file -> hit.
    with tempfile.TemporaryDirectory() as d:
        _write(d, "doc.md", "Reference: the " + blocked.title() + " suite.")
        hits = ns.scan_root(d, [blocked], [], [allow])
        assert hits, "scan_root missed the blocked product name"

    # 5. End-to-end: only generic allowed usage -> clean.
    with tempfile.TemporaryDirectory() as d:
        _write(d, "doc.md", "BoneForge auto-rigging and auto-rig controls.")
        hits = ns.scan_root(d, [blocked], [], [allow, "auto-rigging"])
        assert not hits, "scan_root false-positived on generic terms"

    print("test_name_scan PASS  (allow-list can't mask a blocked product name)")


if __name__ == "__main__":
    main()
