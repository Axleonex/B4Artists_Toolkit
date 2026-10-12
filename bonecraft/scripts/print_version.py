"""Print the boneforge bl_info version (x.y.z) for release tooling.

Used by PUBLISH_BFA.bat so the publish flow always tracks whatever
version the repo currently holds - no per-release script edits.
"""
import ast
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    src = open(os.path.join(ROOT, "boneforge", "__init__.py"),
               encoding="utf-8").read()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if getattr(t, "id", "") == "bl_info":
                    info = ast.literal_eval(node.value)
                    print(".".join(str(x) for x in info["version"]))
                    return
    raise SystemExit("could not read bl_info version")


if __name__ == "__main__":
    main()
