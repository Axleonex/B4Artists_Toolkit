"""Build the BoneForge B4Artists install-from-disk zip.

Packages only the ``boneforge/`` add-on folder (no __pycache__, no tests or
scripts) into ``releases/BoneForge-BFA-<version>.zip``, where <version> is read
from ``bl_info`` so the zip name always tracks the add-on version.

Usage:  python scripts/build_release.py
"""
import ast
import os
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_version():
    src = open(os.path.join(ROOT, "boneforge", "__init__.py"),
               encoding="utf-8").read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if getattr(t, "id", "") == "bl_info":
                    info = ast.literal_eval(node.value)
                    return ".".join(str(x) for x in info["version"])
    raise SystemExit("could not read bl_info version")


def main():
    version = _read_version()
    out = os.path.join(ROOT, "releases", "BoneForge-BFA-%s.zip" % version)
    pkg = os.path.join(ROOT, "boneforge")
    count = 0
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, dirnames, filenames in os.walk(pkg):
            dirnames[:] = [d for d in dirnames if d != "__pycache__"]
            for fn in filenames:
                if fn.endswith((".pyc", ".pyo")):
                    continue
                full = os.path.join(dirpath, fn)
                arc = os.path.relpath(full, ROOT).replace(os.sep, "/")
                z.write(full, arc)
                count += 1
    print("wrote %s (%d files)" % (out, count))


if __name__ == "__main__":
    main()
