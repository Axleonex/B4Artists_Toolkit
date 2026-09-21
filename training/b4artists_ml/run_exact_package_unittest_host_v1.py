"""Run one unittest module inside Bforartists against an exact ZIP package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from importlib import resources
from pathlib import Path
import sys
import unittest

import bpy


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CLASSES = {
    "test_b4artists_ml_pole_align_v1": "PoleAlignTests",
    "test_b4artists_ml_pole_flip_v1": "PoleFlipTests",
    "test_b4artists_ml_pole_distance_v1": "PoleDistanceTests",
    "test_b4artists_ml_target_reset_v1": "TargetResetTests",
    "test_b4artists_ml_target_mirror_v1": "TargetMirrorTests",
    "test_b4artists_ml_body_controls": "BodyControlTests",
    "test_b4artists_ml_context_preview": "PreviewTests",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--module", required=True)
    parser.add_argument("--class-name")
    parser.add_argument("--report", required=True)
    args = parser.parse_args(values)
    package = Path(os.environ["B4ML_PACKAGE"]).resolve()
    if package.suffix.lower() != ".zip" or not package.is_file():
        raise RuntimeError("B4ML_PACKAGE must name an exact ZIP archive")
    sys.path[:0] = [str(package), str(ROOT / "tests")]
    module = __import__(args.module)
    loaded_package = sys.modules.get("b4artists_ml")
    package_origin = str(getattr(loaded_package, "__file__", "")).replace("\\", "/")
    expected_prefix = str(package).replace("\\", "/") + "/"
    if not package_origin.startswith(expected_prefix):
        raise RuntimeError("Addon was not imported from the exact ZIP: " + package_origin)
    class_name = args.class_name or DEFAULT_CLASSES.get(args.module)
    suite_name = args.module + ("." + class_name if class_name else "")
    suite = (
        unittest.defaultTestLoader.loadTestsFromName(suite_name)
        if class_name
        else unittest.defaultTestLoader.loadTestsFromModule(module)
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    runtime = {
        "b4artists_ml/" + name.rsplit(".", 1)[-1] + ".py": hashlib.sha256(
            resources.files("b4artists_ml")
            .joinpath(name.rsplit(".", 1)[-1] + ".py").read_bytes()
        ).hexdigest()
        for name in sorted(
            item for item in sys.modules
            if item.startswith("b4artists_ml.") and item.count(".") == 1
        )
    }
    report = {
        "schema": "b4ml-exact-package-unittest-v1",
        "suite": args.module,
        "class_name": class_name,
        "tests": result.testsRun,
        "assertions_passed": result.wasSuccessful(),
        "failures": [case.id() for case, _text in result.failures],
        "errors": [case.id() for case, _text in result.errors],
        "skipped": [case.id() for case, _reason in result.skipped],
        "runtime_sha256": runtime,
        "package": str(package),
        "package_sha256": sha256(package),
        "package_import_origin": package_origin,
        "host": "Bforartists " + bpy.app.version_string,
    }
    output = Path(args.report)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("B4ML_EXACT_PACKAGE_UNITTEST: " + json.dumps(report), flush=True)
    bpy.ops.wm.quit_blender()
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
