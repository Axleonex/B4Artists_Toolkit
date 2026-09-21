"""Verify the extracted 0.32.0 package with network/process calls denied in-host."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[2]
TAG = "cleanup-package-v1"
CACHE = ROOT / "training/b4artists_ml/cache" / TAG
OUT = ROOT / "training/b4artists_ml/results" / (TAG + ".json")
ARCHIVE = ROOT / "releases/b4artists_ml_v0.32.0.zip"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def host():
    import unittest
    denied = []

    def audit(event, args):
        if event in ("socket.connect", "socket.connect_ex", "socket.getaddrinfo",
                     "socket.sendto", "subprocess.Popen", "os.system"):
            denied.append(event)
            raise RuntimeError("Offline package check blocks " + event)

    sys.addaudithook(audit)
    import socket
    try:
        socket.getaddrinfo("offline-self-test.invalid", 443)
    except RuntimeError:
        pass
    assert denied == ["socket.getaddrinfo"]
    denied.clear()
    os.environ["B4ML_PACKAGE"] = str(CACHE)
    sys.path[:0] = [str(CACHE), str(ROOT / "tests")]
    import b4artists_ml
    import test_b4artists_ml_quadruped_suggestions as paws
    import test_b4artists_ml_contact_suggestions as feet
    import test_b4artists_ml_contact_review_v1 as review
    import test_b4artists_ml_cleanup_v1 as cleanup
    assert b4artists_ml.bl_info["version"] == (0, 32, 0)
    suite = unittest.TestSuite([
        unittest.defaultTestLoader.loadTestsFromTestCase(paws.QuadrupedSuggestionTests),
        unittest.defaultTestLoader.loadTestsFromTestCase(feet.ContactSuggestionTests),
        unittest.defaultTestLoader.loadTestsFromTestCase(review.ContactReviewTests),
        unittest.defaultTestLoader.loadTestsFromTestCase(cleanup.CleanupRuntimeTests),
    ])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    modules = {
        name: str(Path(module.__file__).resolve())
        for name, module in sys.modules.items()
        if (name == "b4artists_ml" or name.startswith("b4artists_ml."))
        and getattr(module, "__file__", None)
    }
    isolated = all(Path(path).is_relative_to(CACHE.resolve()) for path in modules.values())
    report = dict(
        passed=result.wasSuccessful() and result.testsRun == 18 and not denied and isolated,
        tests=result.testsRun,
        failures=[(t.id(), trace) for t, trace in result.failures],
        errors=[(t.id(), trace) for t, trace in result.errors],
        offline_guard_self_test=True,
        denied_runtime_calls=denied,
        all_runtime_imports_from_package=isolated,
        modules=modules,
        runtime_sha256={p.relative_to(CACHE).as_posix(): sha(p) for p in (CACHE / "b4artists_ml").glob("*.py")},
        full_goal_complete=False,
        human_reviews=0,
        cascadeur_comparisons=0,
    )
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def main():
    if CACHE.exists() or OUT.exists():
        raise RuntimeError("Evidence already exists; retain it and use a new run identifier")
    CACHE.mkdir()
    with zipfile.ZipFile(ARCHIVE) as package:
        assert all(not Path(name).is_absolute() and ".." not in Path(name).parts for name in package.namelist())
        package.extractall(CACHE)
    log = CACHE.with_suffix(".log")
    started = time.perf_counter()
    with log.open("w", encoding="utf-8") as stream:
        process = subprocess.run(
            ["X:/5.1.0/bforartists.exe", "--background", "--factory-startup",
             "--disable-autoexec", "--python", str(Path(__file__).resolve()), "--", "--host"],
            stdout=stream, stderr=subprocess.STDOUT, timeout=900,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="4"),
        )
    report = json.loads(OUT.read_text()) if OUT.exists() else dict(passed=False, missing_report=True)
    report.update(
        host_exit=process.returncode,
        host_shutdown_qualified=process.returncode == 0,
        elapsed_seconds=time.perf_counter() - started,
        package_sha256=sha(ARCHIVE),
        log=log.relative_to(ROOT).as_posix(),
        log_sha256=sha(log),
        exact_package=True,
    )
    report["package_members_match_source"] = _members_match_source()
    report["passed"] = bool(report.get("passed") and report["package_members_match_source"])
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report.get(key) for key in ("passed", "tests", "host_exit", "elapsed_seconds", "package_sha256")}))
    if not report["passed"]:
        raise SystemExit(1)


def _members_match_source():
    source = {
        path.relative_to(ROOT).as_posix(): path.read_bytes()
        for path in (ROOT / "b4artists_ml").rglob("*")
        if path.is_file()
        and (path.suffix in (".py", ".json", ".md", ".npz") or path.name == "LICENSE")
    }
    with zipfile.ZipFile(ARCHIVE) as package:
        return set(package.namelist()) == set(source) and all(package.read(name) == payload for name, payload in source.items())


if __name__ == "__main__":
    host() if "--host" in sys.argv else main()
