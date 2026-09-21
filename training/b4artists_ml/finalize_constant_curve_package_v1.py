"""Finalize 0.19.3 evidence and status only after exact-archive qualification."""
from pathlib import Path
import hashlib
import json
import re
import time
import zipfile


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "docs/b4artists_ml"
RESULTS = ROOT / "training/b4artists_ml/results"
ARCHIVE = ROOT / "releases/b4artists_ml_v0.19.3.zip"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_hashes():
    return {path.relative_to(ROOT).as_posix(): sha(path) for path in (ROOT / "b4artists_ml").glob("*.py")}


def main():
    meta_path = BASE / "package-test-v0.19.3.json"
    offline_path = RESULTS / "constant-curve-package-v1.json"
    benchmark_path = RESULTS / "constant-curve-publication-v2/report.json"
    regression_path = RESULTS / "constant-skip-production-full-v1-regression.json"
    meta = read(meta_path)
    offline = read(offline_path)
    benchmark = read(benchmark_path)
    regression = read(regression_path)
    runtime = runtime_hashes()
    assert meta["runtime_sha256"] == offline["runtime_sha256"] == runtime
    assert offline["passed"] and offline["cases"] == 13 and offline["offline_guard_self_test"]
    assert not offline["denied_runtime_calls"] and all(row["source_preserved"] for row in offline["records"])
    assert sum(row.get("contact_checks", 0) for row in offline["records"]) == 9813
    assert meta["sha256"] == offline["package_sha256"] == sha(ARCHIVE)
    assert len(regression) == 43 and sum(row["tests"] for row in regression) == 415
    assert all(row["assertions_passed"] for row in regression)
    assert benchmark["qualified"] and benchmark["runtime_sha256"] == meta["regression"]["tested_runtime_sha256"]
    with zipfile.ZipFile(ARCHIVE) as archive:
        assert len(archive.namelist()) == 42
        assert all(archive.read(name) == (ROOT / name).read_bytes() for name in archive.namelist())

    baseline = RESULTS / "constant-curve-documents-baseline-v1"
    baseline.mkdir(exist_ok=False)
    names = ["PROJECT.md", "ROADMAP.md", "REQUIREMENTS.md", "USER_GUIDE.md", "VALIDATION.md", "package-test-v0.19.3.json"]
    revisions = {}
    for name in names:
        source = BASE / name
        destination = baseline / name
        destination.write_bytes(source.read_bytes())
        revisions[source.relative_to(ROOT).as_posix()] = {
            "prior_version": destination.relative_to(ROOT).as_posix(),
            "before_sha256": sha(source),
        }

    old_tick = benchmark["median_publication_tick_seconds"]["legacy"]
    new_tick = benchmark["median_publication_tick_seconds"]["current"]
    reduction = 100.0 * (1.0 - benchmark["publication_ratio"])
    total_change = 100.0 * (benchmark["total_ratio"] - 1.0)
    document = BASE / "PUBLICATION-LATENCY-v0.19.3.md"
    assert not document.exists()
    document.write_text(f"""# Publication latency - experimental 0.19.3

Whole-body Motion now leaves an owned scalar FCurve unchanged when every generated-span key has exactly the same value. A constant linear segment and the previously generated harmonic Bezier segment evaluate to the same constant function, so calculating and publishing those handles adds work without changing the motion. Complete quaternion-component, sample-time, sign, finite-value, editability and source-recovery checks still run before the action is published.

On the preserved default-Rigify reach/hold fixture, 224 of 300 owned curves and 4,704 of 6,300 owned keys were exactly constant. A serial ABBA comparison against the archived 0.19.2 function reduced the median blocking publication update from {old_tick * 1000:.1f} ms to {new_tick * 1000:.1f} ms, a {reduction:.2f}% reduction. Median full generation changed by {total_change:+.2f}%, which is neutral at this measurement scale.

All 48,944 dense curve samples per comparison matched exactly, all key coordinates matched, and full metadata matched on every nonconstant curve. The 224 constant curves retain their original linear metadata instead of receiving redundant Bezier handles. Source actions, pose, rig modes, anchors and data inventory recovered exactly in every run.

The current source passes 415 native checks across 43 suites. The exact 0.19.3 archive passes 13 offline workflows and 9,813 dense contact checks with outbound networking and process launch denied. Tests complete their assertions before the installed host's known `ucrtbase.dll` shutdown access violation; clean host exit remains unqualified. The package was not installed, committed or pushed.

This evidence covers one headless publication workflow on one machine. It does not establish interactive queue latency, broad hardware performance, animation quality, independent animator usability, learned-motion quality, full physics, quadrupeds or Cascadeur parity. The original goal remains active.

Evidence: `constant-curve-publication-v2/report.json`, `constant-skip-production-full-v1-regression.json`, `constant-curve-package-v1.json`, and `package-test-v0.19.3.json`.
""", encoding="utf-8")

    summary = (f"Current 0.19.3 update: 415 native checks and 13 exact-package offline workflows pass. "
               f"Exact constant-curve handling reduces the default-Rigify reference publication tick by {reduction:.2f}% "
               "with zero dense evaluation error. See PUBLICATION-LATENCY-v0.19.3.md. Learned motion, full responsiveness, "
               "human usability and Cascadeur parity remain unqualified.")
    for name in names[:-1]:
        path = BASE / name
        original = path.read_text(encoding="utf-8-sig")
        text = original
        if name in ("ROADMAP.md", "REQUIREMENTS.md"):
            text = re.sub(r"^Current 0\.19\.2 update:.*$", summary, text, count=1, flags=re.M)
        elif name == "PROJECT.md":
            text = re.sub(r"^Status:.*$", "Status: experimental 0.19.3 local archive. " + summary.removeprefix("Current 0.19.3 update: "), text, count=1, flags=re.M)
        elif name == "USER_GUIDE.md":
            text = text.replace("releases/b4artists_ml_v0.19.2.zip", "releases/b4artists_ml_v0.19.3.zip", 1)
        elif name == "VALIDATION.md":
            text = re.sub(
                r"^Historical record\. Current status:.*$",
                "Historical record. Current status: REQUIREMENTS.md, package-test-v0.19.3.json and PUBLICATION-LATENCY-v0.19.3.md. The integrated source passes 415 native checks; the exact archive passes 13 offline workflows. The original 0.1 evidence below remains historical.",
                text, count=1, flags=re.M)
        assert text != original, name
        path.write_text(text, encoding="utf-8")

    meta.update(
        ready_for_local_testing=True,
        packaged_host_smoke="passed13offlineworkflows",
        offline_evidence="training/b4artists_ml/results/constant-curve-package-v1.json",
        package_standalone_verified=True,
    )
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    for name, row in revisions.items():
        row["after_sha256"] = sha(ROOT / name)
    result = {
        "complete": True,
        "document_revisions": revisions,
        "runtime_sha256": runtime,
        "package_sha256": meta["sha256"],
        "native_cases": 415,
        "offline_cases": 13,
        "dense_contact_checks": 9813,
        "publication_tick_reduction_percent": reduction,
        "installed": False,
        "committed": False,
        "pushed": False,
        "full_goal_complete": False,
        "recorded_at": time.time(),
    }
    (RESULTS / "constant-curve-package-finalization-v1.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ready_for_local_testing": True,
        "version": "0.19.3",
        "native_cases": 415,
        "offline_cases": 13,
        "publication_tick_reduction_percent": reduction,
        "sha256": meta["sha256"],
    }, indent=2))


if __name__ == "__main__":
    main()
