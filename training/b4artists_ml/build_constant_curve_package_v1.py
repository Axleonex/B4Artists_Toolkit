"""Build experimental 0.19.3 after current-source regression and publication qualification."""
from pathlib import Path
import ast
import hashlib
import json
import zipfile


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training/b4artists_ml/results"
OUTPUT = ROOT / "releases/b4artists_ml_v0.19.3.zip"


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_hashes():
    return {path.relative_to(ROOT).as_posix(): sha(path) for path in (ROOT / "b4artists_ml").glob("*.py")}


def main():
    assert not OUTPUT.exists()
    rows = read("training/b4artists_ml/results/constant-skip-production-full-v1-regression.json")
    benchmark = read("training/b4artists_ml/results/constant-curve-publication-v2/report.json")
    tested_runtime = runtime_hashes()
    assert len(rows) == 43 and sum(row["tests"] for row in rows) == 415
    assert all(row["assertions_passed"] and not row["errors"] and not row["failures"] and not row["skipped"] for row in rows)
    assert all(row["runtime_sha256"] == tested_runtime for row in rows)
    assert benchmark["qualified"] and benchmark["performance_gate_passed"]
    assert benchmark["exact_dense_curve_evaluation"] and benchmark["exact_key_coordinates"]
    assert benchmark["nonconstant_metadata_preserved"] and benchmark["runtime_sha256"] == tested_runtime

    init = ROOT / "b4artists_ml/__init__.py"
    old = init.read_text(encoding="utf-8-sig")
    needle = '"version": (0, 19, 2)'
    assert old.count(needle) == 1
    updated = old.replace(needle, '"version": (0, 19, 3)', 1)
    original_tree = ast.parse(old)
    updated_tree = ast.parse(updated)

    def info(tree):
        return next(node for node in tree.body if isinstance(node, ast.Assign) and
                    any(isinstance(target, ast.Name) and target.id == "bl_info" for target in node.targets)).value

    original_info = info(original_tree)
    updated_info = info(updated_tree)
    version_index = next(index for index, key in enumerate(original_info.keys) if key.value == "version")
    assert ast.literal_eval(updated_info.values[version_index]) == (0, 19, 3)
    updated_info.values[version_index] = original_info.values[version_index]
    assert ast.dump(original_tree) == ast.dump(updated_tree)

    baseline = RESULTS / "constant-curve-package-baseline-v1"
    baseline.mkdir(exist_ok=False)
    (baseline / "__init__.py").write_bytes(init.read_bytes())
    init.write_text(updated, encoding="utf-8", newline="\n")
    packaged_runtime = runtime_hashes()
    assert {name for name in tested_runtime if tested_runtime[name] != packaged_runtime[name]} == {"b4artists_ml/__init__.py"}

    revision = {
        "prior_version": (baseline / "__init__.py").relative_to(ROOT).as_posix(),
        "before_sha256": tested_runtime["b4artists_ml/__init__.py"],
        "after_sha256": packaged_runtime["b4artists_ml/__init__.py"],
        "only_version_literal_changed": True,
        "original": [0, 19, 2],
        "updated": [0, 19, 3],
    }
    paths = {
        path.relative_to(ROOT).as_posix(): path
        for path in (ROOT / "b4artists_ml").rglob("*")
        if path.is_file() and (path.suffix in (".py", ".json", ".md", ".npz") or path.name == "LICENSE")
    }
    assert len(paths) == 42
    for path in paths.values():
        if path.suffix == ".py":
            ast.parse(path.read_bytes())
    with zipfile.ZipFile(OUTPUT, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, path in sorted(paths.items()):
            info = zipfile.ZipInfo(name, date_time=(2026, 9, 9, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes(), compresslevel=9)
    with zipfile.ZipFile(OUTPUT) as archive:
        assert set(archive.namelist()) == set(paths)
        assert all(archive.read(name) == path.read_bytes() for name, path in paths.items())

    report = {
        "version": "0.19.3",
        "files": len(paths),
        "bytes": OUTPUT.stat().st_size,
        "sha256": sha(OUTPUT),
        "package_matches_source": True,
        "experimental": True,
        "full_goal_complete": False,
        "ready_for_local_testing": False,
        "runtime_sha256": packaged_runtime,
        "regression": {
            "unique_cases": 415,
            "suites": 43,
            "tested_runtime_sha256": tested_runtime,
            "post_test_version_only_revision": revision,
            "evidence": "training/b4artists_ml/results/constant-skip-production-full-v1-regression.json",
        },
        "benchmark": "training/b4artists_ml/results/constant-curve-publication-v2/report.json",
        "benchmark_tested_runtime_sha256": tested_runtime,
        "packaged_host_smoke": "pending",
        "packaged_ui_qualification": "unverified",
        "host_shutdown_qualified": False,
        "independent_human_usability": "unknown",
        "qualification_note": (
            "Exact constant-curve publication preserves dense evaluated output and reduces the reference publication "
            "tick. Full learned-motion, physics, human usability, quadruped, and Cascadeur parity remain unqualified."
        ),
    }
    path = ROOT / "docs/b4artists_ml/package-test-v0.19.3.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("version", "files", "bytes", "sha256")}, indent=2))


if __name__ == "__main__":
    main()
