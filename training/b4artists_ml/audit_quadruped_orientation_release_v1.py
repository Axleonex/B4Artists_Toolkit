"""Final consistency audit for experimental 0.29.0."""
from pathlib import Path
import ast
import hashlib
import json
import zipfile


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training/b4artists_ml/results"
OUT = RESULTS / "quadruped-orientation-final-audit-v1.json"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists():
        raise RuntimeError("Evidence exists: " + str(OUT))
    archive = ROOT / "releases/b4artists_ml_v0.29.0.zip"
    source = read(RESULTS / "quadruped-orientation-source-v1.json")
    package = read(RESULTS / "quadruped-orientation-package-v1.json")
    metadata = read(ROOT / "docs/b4artists_ml/package-test-v0.29.0.json")
    protocol = read(ROOT / "training/b4artists_ml/quadruped_orientation_protocol_v1.json")
    route = read(RESULTS / "orchestration-route-quadruped-orientation-v24.json")

    assert source["complete"] and source["suites"] == 51 and source["tests"] == 478
    assert source["runtime_hash_sets"] == 1 and not source["full_goal_complete"]
    assert package["passed"] and package["tests"] == 38 and package["exact_package"]
    assert package["offline_guard_self_test"] and package["denied_runtime_calls"] == []
    assert package["quadruped_orientation_profiles"] == ["cat", "horse", "wolf"]
    assert all(row["source_restored"] and row["anchor_saved"]
               and row["metrics"]["max_orientation_error"] <= row["metrics"]["orientation_tolerance"]
               for row in package["quadruped_orientation_records"])
    assert metadata["ready_for_local_testing"] and not metadata["full_goal_complete"]
    assert metadata["sha256"] == package["package_sha256"] == sha(archive)
    assert protocol["release"] == metadata["version"] == "0.29.0"

    assert route["already_active"]["authority_precedence"] == "preserved"
    assert route["already_active"]["execution_routing"] == "T0-T4"
    assert route["already_active"]["evaluation_depths"].startswith("S0-S4")
    assert route["execution"]["classification"] == "DEGRADED_NATIVE_CONTINUE"
    assert not route["execution"]["canonical_entrypoint_completed"]
    assert route["execution"]["canonical_router_recommended_lane"] is None
    assert route["evaluation"]["depth"] == "S3"
    assert route["evaluation"]["classification_only"]
    assert not route["evaluation"]["canonical_evaluator_completed"]
    assert route["evaluation"]["model_calls"] == 0
    assert not route["formal_goal"]["complete"]
    assert not route["compatibility"]["adapter_activated"]
    assert not route["compatibility"]["providers_activated"]
    assert not route["compatibility"]["defaults_changed"]

    python_files = []
    for base in (ROOT / "b4artists_ml", ROOT / "tests", ROOT / "training/b4artists_ml"):
        python_files.extend(base.rglob("*.py"))
    for path in python_files:
        ast.parse(path.read_bytes(), filename=str(path))
    runtime = {path.relative_to(ROOT).as_posix(): sha(path)
               for path in (ROOT / "b4artists_ml").glob("*.py")}
    assert runtime == source["runtime_sha256"] == metadata["runtime_sha256"]

    with zipfile.ZipFile(archive) as zipped:
        names = zipped.namelist()
        assert len(names) == metadata["files"] == 48
        assert len(names) == len(set(names))
        assert all(not Path(name).is_absolute() and ".." not in Path(name).parts for name in names)
        source_files = {path.relative_to(ROOT).as_posix(): path
                        for path in (ROOT / "b4artists_ml").rglob("*")
                        if path.is_file() and
                        (path.suffix in (".py", ".json", ".md", ".npz") or path.name == "LICENSE")}
        assert set(names) == set(source_files)
        assert all(zipped.read(name) == path.read_bytes() for name, path in source_files.items())
        payload = b"\n".join(zipped.read(name).lower() for name in names)
        assert b"jonvilario" not in payload and b"atonlotus" not in payload

    required_docs = [
        ROOT / "docs/b4artists_ml/QUADRUPED-ORIENTATION-v0.29.0.md",
        ROOT / "docs/b4artists_ml/PROJECT.md",
        ROOT / "docs/b4artists_ml/ROADMAP.md",
        ROOT / "docs/b4artists_ml/REQUIREMENTS.md",
        ROOT / "docs/b4artists_ml/VALIDATION.md",
        ROOT / "docs/b4artists_ml/USER_GUIDE.md"
    ]
    assert all("0.29.0" in path.read_text(encoding="utf-8-sig") for path in required_docs)

    report = {
        "passed": True,
        "full_goal_complete": False,
        "release": "0.29.0",
        "python_files_parsed": len(python_files),
        "runtime_files": len(runtime),
        "source_suites": source["suites"],
        "source_tests": source["tests"],
        "exact_package_tests": package["tests"],
        "quadruped_profiles": package["quadruped_orientation_profiles"],
        "package_files": metadata["files"],
        "package_bytes": metadata["bytes"],
        "package_sha256": metadata["sha256"],
        "package_matches_source": True,
        "offline_guard": True,
        "outbound_calls": 0,
        "forbidden_identities_absent": True,
        "host_shutdown_qualified": False,
        "human_reviews": 0,
        "cascadeur_comparisons": 0,
        "routing": {
            "execution": "T0-T4 preserved; DEGRADED_NATIVE_CONTINUE used",
            "evaluation": "S3 shadow/classification-only",
            "canonical_evaluator_completed": False,
            "model_calls": 0
        },
        "remaining": protocol["claim_boundaries"]["not_qualified"]
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
