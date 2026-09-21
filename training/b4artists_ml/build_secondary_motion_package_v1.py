"""Build experimental 0.24.0 from the same-hash secondary-motion regression."""
from pathlib import Path
import ast
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training/b4artists_ml/results"
DOCS = ROOT / "docs/b4artists_ml"
OUTPUT = ROOT / "releases/b4artists_ml_v0.24.0.zip"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_hashes():
    return {
        path.relative_to(ROOT).as_posix(): sha(path)
        for path in (ROOT / "b4artists_ml").glob("*.py")
    }


def main():
    assert not OUTPUT.exists()
    regression_path = RESULTS / "secondary-motion-full-v1-regression.json"
    regression = read(regression_path)
    assert len(regression) == 49
    assert len({row["suite"] for row in regression}) == 49
    assert sum(row["tests"] for row in regression) == 458
    assert all(
        row["assertions_passed"]
        and not row.get("errors")
        and not row.get("failures")
        and not row.get("skipped")
        for row in regression
    )
    tested = regression[0]["runtime_sha256"]
    assert all(row["runtime_sha256"] == tested for row in regression)
    packaged = runtime_hashes()
    assert len(packaged) == 37 and packaged == tested

    ui_path = DOCS / "secondary-ui-secondary-source-v1.json"
    ui = read(ui_path)
    assert ui["passed"] and ui["runtime_sha256"] == tested
    assert Path(ui["module_root"]).resolve() == (ROOT / "b4artists_ml").resolve()
    metrics = ui["metrics"]
    assert metrics["backend"] == "implicit_selected_control_secondary_v1"
    assert metrics["deterministic_physics"] and not metrics["learned"]
    assert metrics["controls"] and metrics["priority_poses_preserved"]
    assert metrics["editable_linear_keys"]
    assert metrics["max_rotation_correction_radians"] > 0.01
    assert ui["step_p95_ms"] < 50 and ui["step_max_ms"] < 50

    tree = ast.parse((ROOT / "b4artists_ml/__init__.py").read_bytes())
    info = next(
        node.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "bl_info" for target in node.targets)
    )
    index = next(i for i, key in enumerate(info.keys) if key.value == "version")
    assert ast.literal_eval(info.values[index]) == (0, 24, 0)

    paths = {
        path.relative_to(ROOT).as_posix(): path
        for path in (ROOT / "b4artists_ml").rglob("*")
        if path.is_file()
        and (path.suffix in (".py", ".json", ".md", ".npz") or path.name == "LICENSE")
    }
    forbidden = (b"jonvilario", b"atonlotus")
    for path in paths.values():
        payload = path.read_bytes()
        assert not any(name in payload.lower() for name in forbidden)
        if path.suffix == ".py":
            ast.parse(payload)

    with zipfile.ZipFile(
        OUTPUT, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for name, path in sorted(paths.items()):
            item = zipfile.ZipInfo(name, date_time=(2026, 9, 10, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = 0o644 << 16
            archive.writestr(item, path.read_bytes(), compresslevel=9)
    with zipfile.ZipFile(OUTPUT) as archive:
        assert set(archive.namelist()) == set(paths)
        assert all(archive.read(name) == path.read_bytes() for name, path in paths.items())

    report = dict(
        version="0.24.0",
        files=len(paths),
        bytes=OUTPUT.stat().st_size,
        sha256=sha(OUTPUT),
        package_matches_source=True,
        forbidden_identities_absent=True,
        experimental=True,
        full_goal_complete=False,
        ready_for_local_testing=False,
        runtime_sha256=packaged,
        tested_runtime_sha256=tested,
        regression=dict(
            unique_cases=458,
            suites=49,
            evidence=regression_path.relative_to(ROOT).as_posix(),
        ),
        secondary_motion=dict(
            backend=metrics["backend"],
            deterministic_physics=metrics["deterministic_physics"],
            learned=metrics["learned"],
            selected_controls=metrics["controls"],
            priority_poses_preserved=metrics["priority_poses_preserved"],
            editable_linear_keys=metrics["editable_linear_keys"],
            max_rotation_correction_radians=metrics["max_rotation_correction_radians"],
            source_ui_evidence=ui_path.relative_to(ROOT).as_posix(),
        ),
        source_ui_performance=dict(
            step_count=ui["step_count"],
            step_p95_ms=ui["step_p95_ms"],
            step_max_ms=ui["step_max_ms"],
            elapsed_seconds=ui["elapsed_seconds"],
        ),
        exact_package_checks="pending",
        exact_package_ui="pending",
        host_shutdown_qualified=False,
        independent_human_usability="unknown",
        qualification_note=(
            "Selected local-control rotation/location uses deterministic implicit spring dynamics, "
            "preserves captured priority poses and publishes editable candidate keys. It does not "
            "infer secondary controls, apply per-control gravity/global-space dynamics, solve "
            "deformation or arbitrary/self/moving collision, use learned weights, qualify clean host "
            "shutdown, establish independent animator acceptance, or establish Cascadeur parity."
        ),
    )
    (DOCS / "package-test-v0.24.0.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({key: report[key] for key in ("version", "files", "bytes", "sha256")}, indent=2))


if __name__ == "__main__":
    main()
