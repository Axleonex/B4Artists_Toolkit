"""Reproducible direct-ZIP imported-humanoid regression for the current package."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
import traceback
from importlib import resources
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve()
ARCHIVE = Path(os.environ.get(
    "B4ML_ARCHIVE",
    str(ROOT / "releases" / "b4artists_ml_v0.37.29-dev.zip"),
))
TAG = os.environ.get("B4ML_DIRECT_ZIP_TAG", "current-package-direct-zip-import-v1")
RESULT = ROOT / "training" / "b4artists_ml" / "results" / f"{TAG}.json"
LOG = ROOT / "training" / "b4artists_ml" / "cache" / f"{TAG}.log"
SUITE = "test_b4artists_ml_imported_humanoids.ImportedHumanoidTests"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _runtime_source_sha256(module) -> str:
    package_name, _, module_name = module.__name__.rpartition(".")
    package_name = package_name or module.__package__ or module.__name__
    return _sha256_bytes(resources.files(package_name).joinpath(module_name + ".py").read_bytes())


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def host() -> None:
    import unittest

    import bpy

    package = os.environ["B4ML_PACKAGE"]
    sys.path[:0] = [package, str(ROOT / "tests")]
    suite_module = __import__("test_b4artists_ml_imported_humanoids", fromlist=["ImportedHumanoidTests"])
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(suite_module.ImportedHumanoidTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    modules = (
        suite_module.p,
        suite_module.w,
        suite_module.solver,
    )
    record = {
        "schema": "b4ml-current-package-direct-zip-import-v1",
        "suite": SUITE,
        "tests": result.testsRun,
        "assertions_passed": result.wasSuccessful(),
        "failures": [test.id() for test, _ in result.failures],
        "errors": [test.id() for test, _ in result.errors],
        "skipped": [test.id() for test, _ in result.skipped],
        "runtime_sha256": {
            f"b4artists_ml/{module.__name__.rsplit('.', 1)[-1]}.py": _runtime_source_sha256(module)
            for module in modules
        },
        "package": package,
    }
    RESULT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record), flush=True)
    bpy.ops.wm.quit_blender()


def main() -> int:
    if not ARCHIVE.is_file():
        raise FileNotFoundError(ARCHIVE)
    if RESULT.exists():
        raise RuntimeError(f"Evidence already exists: {RESULT}")
    started = time.perf_counter()
    environment = dict(
        os.environ,
        B4ML_PACKAGE=str(ARCHIVE),
        B4ML_DIRECT_ZIP_TAG=TAG,
        PYTHONDONTWRITEBYTECODE="1",
        OPENBLAS_NUM_THREADS="4",
    )
    with LOG.open("w", encoding="utf-8") as stream:
        process = subprocess.run(
            [
                "X:/5.1.0/bforartists.exe",
                "--background",
                "--factory-startup",
                "--disable-autoexec",
                "--python",
                str(HERE),
                "--",
                "--host",
            ],
            stdout=stream,
            stderr=subprocess.STDOUT,
            env=environment,
            timeout=900,
        )
    record = json.loads(RESULT.read_text(encoding="utf-8")) if RESULT.is_file() else {
        "schema": "b4ml-current-package-direct-zip-import-v1",
        "suite": SUITE,
        "tests": 0,
        "assertions_passed": False,
        "failures": [],
        "errors": ["Missing host receipt"],
        "skipped": [],
    }
    record.update(
        archive=str(ARCHIVE),
        archive_sha256=_sha256(ARCHIVE),
        host_exit=process.returncode,
        elapsed_seconds=time.perf_counter() - started,
        log=str(LOG.relative_to(ROOT)),
        known_shutdown_only=(
            record.get("assertions_passed") is True
            and process.returncode in (0, 1, -1073741819, 3221225477)
        ),
    )
    RESULT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record), flush=True)
    return 0 if record.get("assertions_passed") is True else 1


if __name__ == "__main__":
    try:
        if "--host" in sys.argv:
            host()
        else:
            raise SystemExit(main())
    except BaseException:
        print(traceback.format_exc(), file=sys.stderr, flush=True)
        raise
