"""Exercise the exact 0.26.0 archive with outbound Python calls denied."""
from pathlib import Path
import ast
import hashlib
import json
import os
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve()
TAG = "secondary-chain-package-v1"
CACHE = ROOT / f"training/b4artists_ml/cache/{TAG}"
OUT = ROOT / f"training/b4artists_ml/results/{TAG}.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def host():
    import unittest

    denied = []

    def audit(event, args):
        if event in (
            "socket.connect",
            "socket.connect_ex",
            "socket.getaddrinfo",
            "socket.sendto",
            "subprocess.Popen",
            "os.system",
        ):
            denied.append(event)
            raise RuntimeError("Offline package check blocks " + event)

    sys.addaudithook(audit)
    import socket

    try:
        socket.getaddrinfo("offline-self-test.invalid", 443)
    except RuntimeError:
        pass
    else:
        raise AssertionError("Offline guard did not intercept resolution")
    assert denied == ["socket.getaddrinfo"]
    denied.clear()
    sys.path[:0] = [str(CACHE), str(ROOT / "tests")]
    os.environ["B4ML_PACKAGE"] = str(CACHE)
    import b4artists_ml

    assert b4artists_ml.bl_info["version"] == (0, 26, 0)
    assert Path(b4artists_ml.__file__).resolve().parent == CACHE / "b4artists_ml"
    import test_b4artists_ml_angular_math as angular
    import test_b4artists_ml_collision_math as collision
    import test_b4artists_ml_momentum as momentum
    import test_b4artists_ml_secondary_math as secondary_math
    import test_b4artists_ml_secondary_motion as secondary_motion

    suite = unittest.TestSuite(
        [
            unittest.defaultTestLoader.loadTestsFromTestCase(angular.AngularMathTests),
            unittest.defaultTestLoader.loadTestsFromTestCase(momentum.MomentumMathTests),
            unittest.defaultTestLoader.loadTestsFromTestCase(momentum.MomentumHostTests),
            unittest.defaultTestLoader.loadTestsFromTestCase(collision.CollisionMathTests),
            unittest.defaultTestLoader.loadTestsFromTestCase(collision.CollisionHostTests),
            unittest.defaultTestLoader.loadTestsFromTestCase(secondary_math.SecondaryMathTests),
            unittest.defaultTestLoader.loadTestsFromTestCase(secondary_motion.SecondaryMotionTests),
        ]
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    assert result.testsRun == 48
    modules = {
        name: str(Path(value.__file__).resolve())
        for name, value in sys.modules.items()
        if (name == "b4artists_ml" or name.startswith("b4artists_ml."))
        and getattr(value, "__file__", None)
    }
    report = dict(
        passed=result.wasSuccessful() and not denied,
        tests=result.testsRun,
        failures=[item[0].id() for item in result.failures],
        errors=[item[0].id() for item in result.errors],
        offline_guard_self_test=True,
        denied_runtime_calls=denied,
        package_modules=modules,
        runtime_sha256={
            path.relative_to(CACHE).as_posix(): sha(path)
            for path in (CACHE / "b4artists_ml").glob("*.py")
        },
        full_goal_complete=False,
    )
    assert all(Path(path).is_relative_to(CACHE.resolve()) for path in modules.values())
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report), flush=True)


def main():
    if CACHE.exists() or OUT.exists():
        raise RuntimeError("Evidence already exists")
    archive = ROOT / "releases/b4artists_ml_v0.26.0.zip"
    meta_path = ROOT / "docs/b4artists_ml/package-test-v0.26.0.json"
    meta = json.loads(meta_path.read_text())
    assert sha(archive) == meta["sha256"]
    CACHE.mkdir()
    with zipfile.ZipFile(archive) as package:
        assert all(
            not Path(name).is_absolute() and ".." not in Path(name).parts
            for name in package.namelist()
        )
        package.extractall(CACHE)
    for path in (CACHE / "b4artists_ml").rglob("*.py"):
        ast.parse(path.read_bytes())
    log = ROOT / f"training/b4artists_ml/cache/{TAG}.log"
    start = time.perf_counter()
    with log.open("w") as stream:
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
            env=dict(
                os.environ,
                PYTHONDONTWRITEBYTECODE="1",
                OPENBLAS_NUM_THREADS="4",
                B4ML_PACKAGE=str(CACHE),
                B4ML_RUN_LABEL=TAG,
            ),
            timeout=900,
        )
    result = json.loads(OUT.read_text()) if OUT.exists() else dict(passed=False, missing_result=True)
    result.update(
        host_exit=process.returncode,
        elapsed_seconds=time.perf_counter() - start,
        log=log.relative_to(ROOT).as_posix(),
        package_sha256=sha(archive),
        exact_package=True,
        host_shutdown_qualified=process.returncode == 0,
    )
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    meta["exact_package_checks"] = dict(
        passed=result["passed"],
        tests=result.get("tests"),
        evidence=OUT.relative_to(ROOT).as_posix(),
    )
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    if "--host" in sys.argv:
        host()
    else:
        main()
