"""Finalize 0.19.4 evidence and status after exact-archive qualification."""
from pathlib import Path
import hashlib
import json
import re
import time
import zipfile


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "docs/b4artists_ml"
RESULTS = ROOT / "training/b4artists_ml/results"
ARCHIVE = ROOT / "releases/b4artists_ml_v0.19.4.zip"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_hashes():
    return {path.relative_to(ROOT).as_posix(): sha(path) for path in (ROOT / "b4artists_ml").glob("*.py")}


def main():
    meta_path = BASE / "package-test-v0.19.4.json"
    offline_path = RESULTS / "packet-package-v1.json"
    benchmark_path = RESULTS / "anchor-snapshot-publication-v3/report.json"
    regression_path = RESULTS / "packet-production-full-v1-regression.json"
    meta, offline, benchmark, regression = map(read, (meta_path, offline_path, benchmark_path, regression_path))
    runtime = runtime_hashes()
    assert meta["runtime_sha256"] == offline["runtime_sha256"] == runtime
    assert offline["passed"] and offline["cases"] == 13 and offline["offline_guard_self_test"]
    assert not offline["denied_runtime_calls"] and all(row["source_preserved"] for row in offline["records"])
    assert sum(row.get("contact_checks", 0) for row in offline["records"]) == 9813
    assert meta["sha256"] == offline["package_sha256"] == sha(ARCHIVE)
    assert len(regression) == 43 and sum(row["tests"] for row in regression) == 417
    assert all(row["assertions_passed"] and not row["errors"] and not row["failures"] and not row["skipped"] for row in regression)
    assert benchmark["qualified"] and benchmark["exact_dense_curve_evaluation"] and benchmark["exact_keys_and_metadata"]
    assert benchmark["source_preserved"] and benchmark["inventory_preserved"]
    assert benchmark["runtime_sha256"] == meta["regression"]["tested_runtime_sha256"]
    with zipfile.ZipFile(ARCHIVE) as archive:
        assert len(archive.namelist()) == 42
        assert all(archive.read(name) == (ROOT / name).read_bytes() for name in archive.namelist())

    baseline = RESULTS / "packet-documents-baseline-v1"
    baseline.mkdir(exist_ok=False)
    names = ["PROJECT.md", "ROADMAP.md", "REQUIREMENTS.md", "USER_GUIDE.md", "VALIDATION.md", "package-test-v0.19.4.json"]
    revisions = {}
    for name in names:
        source = BASE / name
        destination = baseline / name
        destination.write_bytes(source.read_bytes())
        revisions[source.relative_to(ROOT).as_posix()] = {
            "prior_version": destination.relative_to(ROOT).as_posix(),
            "before_sha256": sha(source),
        }

    old_tick = benchmark["median_publication_seconds"]["legacy"]
    new_tick = benchmark["median_publication_seconds"]["current"]
    reduction = benchmark["reduction_percent"]
    document = BASE / "PUBLICATION-LATENCY-v0.19.4.md"
    assert not document.exists()
    document.write_text(f"""# Publication latency - experimental 0.19.4

Whole-body Motion now validates anchor data once at the synchronous publication boundary and reuses that snapshot while creating and smoothing the candidate. Public workflow and smoothing calls still perform their own anchor validation. The internal path contains no timer or user yield, so the snapshot cannot become stale between its consumers.

Private temporal generation now returns its detached, validated sample buffer through a one-use ownership packet. Publication consumes the packet once and still rescans every frame, control, finite value, rotation representation and authored priority against the live source rig before it creates an action. A deliberately corrupted packet was rejected before action mutation, with exact source and inventory recovery.

In a six-run balanced comparison against the archived 0.19.3 implementation, anchor decoding/validation calls fell from three to one. Median publication time on the preserved default-Rigify reach/hold fixture fell from {old_tick * 1000:.1f} ms to {new_tick * 1000:.1f} ms, a {reduction:.2f}% reduction. All 48,944 dense evaluated curve samples, all keys and all metadata matched exactly. Source action, pose, rig modes, anchors and data inventory recovered in every run.

The exact changed runtime passes 417 native checks across 43 suites. The exact 0.19.4 archive passes 13 offline workflows and 9,813 dense contact checks with outbound networking and process launch denied. Tests complete assertions before the installed host's known `ucrtbase.dll` shutdown access violation; clean host exit remains unqualified. The package was not installed, committed or pushed.

This evidence covers one headless publication workflow on one machine. It does not establish interactive queue latency, broad hardware performance, animation quality, independent animator usability, learned-motion quality, full physics, quadrupeds or Cascadeur parity. The original goal remains active.

Evidence: `anchor-snapshot-publication-v3/report.json`, `packet-production-full-v1-regression.json`, `packet-adversarial-target-v1-regression.json`, `packet-package-v1.json`, and `package-test-v0.19.4.json`.
""", encoding="utf-8")

    summary = (f"Current 0.19.4 update: 417 native checks and 13 exact-package offline workflows pass. "
               f"One-snapshot, one-use publication reduces the default-Rigify reference publication time by {reduction:.2f}% "
               "from archived 0.19.3 with exact evaluated motion and full live-source validation. See "
               "PUBLICATION-LATENCY-v0.19.4.md. Learned motion, broad responsiveness, human usability and Cascadeur parity remain unqualified.")
    for name in names[:-1]:
        path = BASE / name
        original = path.read_text(encoding="utf-8-sig")
        text = original
        if name in ("ROADMAP.md", "REQUIREMENTS.md"):
            text = re.sub(r"^Current 0\.19\.3 update:.*$", summary, text, count=1, flags=re.M)
        elif name == "PROJECT.md":
            text = re.sub(r"^Status:.*$", "Status: experimental 0.19.4 local archive. " + summary.removeprefix("Current 0.19.4 update: "), text, count=1, flags=re.M)
        elif name == "USER_GUIDE.md":
            text = text.replace("releases/b4artists_ml_v0.19.3.zip", "releases/b4artists_ml_v0.19.4.zip", 1)
        elif name == "VALIDATION.md":
            text = re.sub(
                r"^Historical record\. Current status:.*$",
                "Historical record. Current status: REQUIREMENTS.md, package-test-v0.19.4.json and PUBLICATION-LATENCY-v0.19.4.md. The integrated source passes 417 native checks; the exact archive passes 13 offline workflows. The original 0.1 evidence below remains historical.",
                text, count=1, flags=re.M)
        assert text != original, name
        path.write_text(text, encoding="utf-8")

    meta.update(
        ready_for_local_testing=True,
        packaged_host_smoke="passed13offlineworkflows",
        offline_evidence="training/b4artists_ml/results/packet-package-v1.json",
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
        "native_cases": 417,
        "offline_cases": 13,
        "dense_contact_checks": 9813,
        "publication_reduction_percent": reduction,
        "legacy_anchor_reads": benchmark["legacy_anchor_reads"],
        "current_anchor_reads": benchmark["current_anchor_reads"],
        "installed": False,
        "committed": False,
        "pushed": False,
        "full_goal_complete": False,
        "recorded_at": time.time(),
    }
    (RESULTS / "packet-package-finalization-v1.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ready_for_local_testing": True,
        "version": "0.19.4",
        "native_cases": 417,
        "offline_cases": 13,
        "publication_reduction_percent": reduction,
        "sha256": meta["sha256"],
    }, indent=2))


if __name__ == "__main__":
    main()
