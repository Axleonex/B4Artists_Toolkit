"""Seal experimental 0.20.2 source, vertical-slice, and exact-package evidence."""

from pathlib import Path
import hashlib
import json
import zipfile


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs/b4artists_ml"
RESULTS = ROOT / "training/b4artists_ml/results"
BASE = ROOT / "training/b4artists_ml/cache/procedural-proxy-package-v2"
ARCHIVE = ROOT / "releases/b4artists_ml_v0.20.2.zip"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    meta_path = DOCS / "package-test-v0.20.2.json"
    meta = read(meta_path)
    regression_path = RESULTS / "procedural-proxy-fix-v1-all-regression.json"
    regression = read(regression_path)
    vertical_path = RESULTS / "procedural-vertical-slice-v12/aggregate.json"
    vertical = read(vertical_path)
    offline_path = RESULTS / "procedural-proxy-package-v2.json"
    offline = read(offline_path)
    suggestions_path = RESULTS / "contact-suggestions-procedural-proxy-package-v2.json"
    suggestions = read(suggestions_path)
    ui_path = RESULTS / "procedural-proxy-package-ui-trials-v2.json"
    ui = read(ui_path)

    assert sha(ARCHIVE) == meta["sha256"] == offline["package_sha256"]
    assert len(regression) == 45 and len({row["suite"] for row in regression}) == 45
    assert sum(row["tests"] for row in regression) == 430
    assert all(row["assertions_passed"] and not row.get("failures") and not row.get("errors") and not row.get("skipped") for row in regression)
    tested = regression[0]["runtime_sha256"]
    assert all(row["runtime_sha256"] == tested for row in regression)
    assert vertical["complete"] and vertical["cases"] == vertical["passed"] == 32 and vertical["failed"] == 0
    assert vertical["runtime_sha256"] == tested and vertical["memory_counters_available"]
    assert offline["passed"] and offline["cases"] == 13 and offline["offline_guard_self_test"] and not offline["denied_runtime_calls"]
    assert suggestions["passed"] and suggestions["tests"] == 4 and suggestions["exact_package"]
    assert ui["passed"] and ui["exact_package"] and len(ui["trials"]) == 3 and all(ui["gates"].values())
    assert all(row["backend"] == "geometric_contact_projection_v1_proxy_v1" for row in ui["trials"])
    assert all(Path(row["package"]).resolve().is_relative_to(BASE.resolve()) for row in ui["trials"])

    with zipfile.ZipFile(ARCHIVE) as archive:
        assert len(archive.namelist()) == meta["files"]
        assert all(archive.read(name) == (ROOT / name).read_bytes() for name in archive.namelist())
        archive_runtime = {name: hashlib.sha256(archive.read(name)).hexdigest() for name in archive.namelist() if name.startswith("b4artists_ml/") and name.endswith(".py")}
    assert archive_runtime == meta["runtime_sha256"] == offline["runtime_sha256"]

    meta.update(
        ready_for_local_testing=True,
        exact_package_offline={"evidence": offline_path.relative_to(ROOT).as_posix(), "cases": 13, "passed": True},
        exact_package_contact_suggestions={"evidence": suggestions_path.relative_to(ROOT).as_posix(), "tests": 4, "passed": True},
        exact_package_ui={"evidence": ui_path.relative_to(ROOT).as_posix(), "trials": 3, "passed": True, "summary": ui["summary"], "gates": ui["gates"]},
        source_regression_sha256=sha(regression_path),
        procedural_vertical_slice_sha256=sha(vertical_path),
        host_shutdown_qualified=False,
        package_validation_complete=True,
    )
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "version": meta["version"],
        "archive_sha256": meta["sha256"],
        "regression": "430/430",
        "vertical_slice": "32/32",
        "offline": "13/13",
        "contact_suggestions": "4/4",
        "actual_window": "3/3",
        "ui_summary": ui["summary"],
        "ready_for_local_testing": meta["ready_for_local_testing"],
        "full_goal_complete": meta["full_goal_complete"],
    }, indent=2))


if __name__ == "__main__":
    main()
