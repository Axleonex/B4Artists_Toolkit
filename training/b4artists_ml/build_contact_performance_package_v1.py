"""Build experimental 0.20.1 after contact-correction performance qualification."""
from pathlib import Path
import ast
import hashlib
import json
import zipfile


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training/b4artists_ml/results"
OUTPUT = ROOT / "releases/b4artists_ml_v0.20.1.zip"


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_hashes():
    return {
        path.relative_to(ROOT).as_posix(): sha(path)
        for path in (ROOT / "b4artists_ml").glob("*.py")
    }


def main():
    assert not OUTPUT.exists()
    rows = read("training/b4artists_ml/results/contact-performance-v3-full-regression.json")
    assert len(rows) == 45 and len({row["suite"] for row in rows}) == 45
    assert sum(row["tests"] for row in rows) == 429
    assert all(
        row["assertions_passed"]
        and not row.get("errors")
        and not row.get("failures")
        and not row.get("skipped")
        for row in rows
    )
    tested = runtime_hashes()
    assert all(row["runtime_sha256"] == tested for row in rows)

    trials = read("training/b4artists_ml/results/contact-ui-trials-v1.json")
    assert trials["passed"] and len(trials["trials"]) == 3
    assert all(trials["gates"].values())
    assert trials["summary"]["suggestion_callback_max_ms"] < 50
    assert trials["summary"]["correction_callback_max_ms"] < 50
    assert trials["summary"]["correction_elapsed_max_ms"] < 8000

    packaged = runtime_hashes()
    assert packaged == tested
    init_tree = ast.parse((ROOT / "b4artists_ml/__init__.py").read_bytes())
    info = next(
        node.value
        for node in init_tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "bl_info" for target in node.targets)
    )
    version_index = next(i for i, key in enumerate(info.keys) if key.value == "version")
    assert ast.literal_eval(info.values[version_index]) == (0, 20, 1)

    paths = {
        path.relative_to(ROOT).as_posix(): path
        for path in (ROOT / "b4artists_ml").rglob("*")
        if path.is_file()
        and (path.suffix in (".py", ".json", ".md", ".npz") or path.name == "LICENSE")
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

    report = dict(
        version="0.20.1",
        files=len(paths),
        bytes=OUTPUT.stat().st_size,
        sha256=sha(OUTPUT),
        package_matches_source=True,
        experimental=True,
        full_goal_complete=False,
        ready_for_local_testing=False,
        runtime_sha256=packaged,
        regression=dict(
            unique_cases=429,
            suites=45,
            evidence=[
                "training/b4artists_ml/results/contact-performance-v3-full-regression.json",
            ],
            tested_runtime_sha256=tested,
            package_runtime_is_tested_runtime=True,
        ),
        source_ui_trials="training/b4artists_ml/results/contact-ui-trials-v1.json",
        source_performance=trials["summary"],
        packaged_host_smoke="pending",
        packaged_ui_trials="pending",
        host_shutdown_qualified=False,
        independent_human_usability="unknown",
        qualification_note=(
            "Default-Rigify contact suggestion and correction pass the frozen source performance gates. "
            "The complete procedural action benchmark, independent usability, learned temporal quality, "
            "quadrupeds and Cascadeur parity remain unqualified."
        ),
    )
    (ROOT / "docs/b4artists_ml/package-test-v0.20.1.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({key: report[key] for key in ("version", "files", "bytes", "sha256")}, indent=2))


if __name__ == "__main__":
    main()
