"""Run one Bforartists unittest module and write a compact evidence report."""
from pathlib import Path
import argparse
import hashlib
import importlib
import json
import sys
import unittest

import bpy


ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def distributable_hashes():
    return {
        path.relative_to(ROOT).as_posix(): sha(path)
        for path in sorted((ROOT / "b4artists_ml").rglob("*"))
        if path.is_file()
        and (path.suffix in (".py", ".json", ".md", ".npz") or path.name == "LICENSE")
    }


def main():
    if sys.flags.optimize != 0:
        raise RuntimeError("Release qualification requires Python assertions enabled")
    values = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--module", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--qualification", required=True)
    parser.add_argument("--runner-sha256")
    parser.add_argument("--driver")
    parser.add_argument("--driver-sha256")
    parser.add_argument("--dependency", action="append", default=[])
    parser.add_argument("--dependency-sha256", action="append", default=[])
    args = parser.parse_args(values)
    runner_path = Path(__file__).resolve()
    if args.runner_sha256 and sha(runner_path) != args.runner_sha256:
        raise RuntimeError("Unit-test runner changed before child execution")
    driver_path = Path(args.driver).resolve() if args.driver else None
    if bool(args.driver) != bool(args.driver_sha256):
        raise RuntimeError("Driver binding is incomplete")
    if driver_path and sha(driver_path) != args.driver_sha256:
        raise RuntimeError("Affected driver changed before child execution")
    if len(args.dependency) != len(args.dependency_sha256):
        raise RuntimeError("Dependency binding is incomplete")
    dependency_paths = [Path(value).resolve() for value in args.dependency]
    if len(set(dependency_paths)) != len(dependency_paths):
        raise RuntimeError("Dependency bindings must be unique")
    for path, digest in zip(dependency_paths, args.dependency_sha256):
        try:
            path.relative_to(ROOT)
        except ValueError as exc:
            raise RuntimeError("Dependencies must be inside the project") from exc
        if sha(path) != digest:
            raise RuntimeError("Test dependency changed before child execution: " + str(path))
    sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
    module = importlib.import_module(args.module)
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if args.runner_sha256 and sha(runner_path) != args.runner_sha256:
        raise RuntimeError("Unit-test runner changed during child execution")
    if driver_path and sha(driver_path) != args.driver_sha256:
        raise RuntimeError("Affected driver changed during child execution")
    for path, digest in zip(dependency_paths, args.dependency_sha256):
        if sha(path) != digest:
            raise RuntimeError("Test dependency changed during child execution: " + str(path))
    runtime = {str(path.relative_to(ROOT)).replace("\\", "/"): sha(path)
               for path in sorted((ROOT / "b4artists_ml").glob("*.py"))}
    test_path = ROOT / "tests" / (args.module + ".py")
    report = {
        "schema": 1,
        "qualification": args.qualification,
        "passed": result.wasSuccessful(),
        "tests": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skips": len(result.skipped),
        "host": bpy.app.version_string,
        "python_optimize": sys.flags.optimize,
        "runtime_source_sha256": runtime,
        "distributable_member_sha256": distributable_hashes(),
        "test_sha256": sha(test_path),
        "dependency_source_sha256": {
            str(path.relative_to(ROOT)).replace("\\", "/"): sha(path)
            for path in dependency_paths
        },
        "harness_source_sha256": {
            str(runner_path.relative_to(ROOT)).replace("\\", "/"): sha(runner_path),
            **({str(driver_path.relative_to(ROOT)).replace("\\", "/"): sha(driver_path)}
               if driver_path else {}),
        },
        "shutdown_clean": False,
    }
    output = Path(args.report)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("B4ML_UNITTEST_REPORT: " + json.dumps(report), flush=True)
    if not result.wasSuccessful():
        raise SystemExit(1)


if __name__ == "__main__":
    main()
