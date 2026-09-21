"""Build experimental 0.20.2 from the qualified shape-aware proxy repair."""

from pathlib import Path
import ast
import hashlib
import json
import zipfile


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training/b4artists_ml/results"
DOCS = ROOT / "docs/b4artists_ml"
OUTPUT = ROOT / "releases/b4artists_ml_v0.20.2.zip"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_hashes():
    return {path.relative_to(ROOT).as_posix(): sha(path) for path in (ROOT / "b4artists_ml").glob("*.py")}


def main():
    assert not OUTPUT.exists()
    regression_path = RESULTS / "procedural-proxy-fix-v1-all-regression.json"
    regression = read(regression_path)
    assert len(regression) == 45 and len({row["suite"] for row in regression}) == 45
    assert sum(row["tests"] for row in regression) == 430
    assert all(row["assertions_passed"] and not row.get("errors") and not row.get("failures") and not row.get("skipped") for row in regression)
    tested = regression[0]["runtime_sha256"]
    assert all(row["runtime_sha256"] == tested for row in regression)

    vertical_path = RESULTS / "procedural-vertical-slice-v12/aggregate.json"
    vertical = read(vertical_path)
    assert vertical["complete"] and vertical["cases"] == vertical["passed"] == 32 and vertical["failed"] == 0
    assert vertical["runtime_sha256"] == tested
    assert vertical["memory_counters_available"] and not vertical["full_goal_complete"]

    packaged = runtime_hashes()
    assert set(packaged) == set(tested)
    for name in packaged:
        if name != "b4artists_ml/__init__.py":
            assert packaged[name] == tested[name], name
    current_init = (ROOT / "b4artists_ml/__init__.py").read_text(encoding="utf-8")
    prior_init = current_init.replace('"version": (0, 20, 2)', '"version": (0, 20, 1)')
    assert prior_init != current_init
    assert hashlib.sha256(prior_init.encode("utf-8")).hexdigest() == tested["b4artists_ml/__init__.py"]
    info_tree = ast.parse((ROOT / "b4artists_ml/__init__.py").read_bytes())
    info = next(node.value for node in info_tree.body if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "bl_info" for target in node.targets))
    version_index = next(index for index, key in enumerate(info.keys) if key.value == "version")
    assert ast.literal_eval(info.values[version_index]) == (0, 20, 2)

    paths = {
        path.relative_to(ROOT).as_posix(): path
        for path in (ROOT / "b4artists_ml").rglob("*")
        if path.is_file() and (path.suffix in (".py", ".json", ".md", ".npz") or path.name == "LICENSE")
    }
    for path in paths.values():
        if path.suffix == ".py":
            ast.parse(path.read_bytes())
    with zipfile.ZipFile(OUTPUT, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, path in sorted(paths.items()):
            item = zipfile.ZipInfo(name, date_time=(2026, 9, 10, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = 0o644 << 16
            archive.writestr(item, path.read_bytes(), compresslevel=9)
    with zipfile.ZipFile(OUTPUT) as archive:
        assert set(archive.namelist()) == set(paths)
        assert all(archive.read(name) == path.read_bytes() for name, path in paths.items())

    report = {
        "version": "0.20.2",
        "files": len(paths),
        "bytes": OUTPUT.stat().st_size,
        "sha256": sha(OUTPUT),
        "package_matches_source": True,
        "experimental": True,
        "full_goal_complete": False,
        "ready_for_local_testing": False,
        "runtime_sha256": packaged,
        "tested_runtime_sha256": tested,
        "post_test_version_only_revision": True,
        "regression": {"unique_cases": 430, "suites": 45, "evidence": regression_path.relative_to(ROOT).as_posix()},
        "procedural_vertical_slice": {"cases": 32, "passed": 32, "evidence": vertical_path.relative_to(ROOT).as_posix(), "aggregate_sha256": sha(vertical_path)},
        "exact_package_offline": "pending",
        "exact_package_contact_suggestions": "pending",
        "exact_package_ui": "pending",
        "host_shutdown_qualified": False,
        "independent_human_usability": "unknown",
        "qualification_note": "Shape-aware contact correction now retains the dependency-closed evaluator on the frozen procedural matrix. Learned motion, human review, full physics, quadrupeds and Cascadeur parity remain unqualified."
    }
    (DOCS / "package-test-v0.20.2.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("version", "files", "bytes", "sha256")}, indent=2))


if __name__ == "__main__":
    main()
