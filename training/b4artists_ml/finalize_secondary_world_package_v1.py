"""Seal exact-package and visible-window evidence for experimental 0.25.0."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[2]


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    archive = ROOT / "releases/b4artists_ml_v0.25.0.zip"
    meta_path = ROOT / "docs/b4artists_ml/package-test-v0.25.0.json"
    meta = read(meta_path)
    package_path = ROOT / "training/b4artists_ml/results/secondary-world-package-v1.json"
    package = read(package_path)
    ui_path = ROOT / "docs/b4artists_ml/secondary-ui-secondary-world-package-v1.json"
    ui = read(ui_path)
    process_path = ROOT / "training/b4artists_ml/results/secondary-ui-process-secondary-world-package-v1.json"
    process = read(process_path)

    assert sha(archive) == meta["sha256"] == package["package_sha256"]
    assert package["passed"] and package["tests"] == 42 and package["exact_package"]
    assert not package["denied_runtime_calls"] and not package["host_shutdown_qualified"]
    assert ui["passed"] and ui["runtime_sha256"] == meta["runtime_sha256"] == package["runtime_sha256"]
    assert Path(ui["module_root"]).resolve().is_relative_to(
        (ROOT / "training/b4artists_ml/cache/secondary-world-package-v1").resolve()
    )
    metrics = ui["metrics"]
    assert metrics["backend"] == "implicit_selected_control_secondary_v2"
    assert metrics["deterministic_physics"] and not metrics["learned"]
    assert metrics["space"] == "WORLD" and metrics["gravity_influence"] > 0
    assert metrics["collision"] and metrics["collision_samples"] > 0
    assert metrics["max_raw_penetration"] > 0 and metrics["max_penetration_after"] <= 1e-8
    assert metrics["max_world_location_error"] <= 2e-4
    assert metrics["max_world_rotation_error_radians"] <= 2e-3
    assert metrics["priority_poses_preserved"] and metrics["editable_linear_keys"]
    assert metrics["max_rotation_correction_radians"] > 0.01
    assert ui["step_p95_ms"] < 50 and ui["step_max_ms"] < 50
    assert process["exit_code"] == 3221225477

    with zipfile.ZipFile(archive) as package_zip:
        source = {
            path.relative_to(ROOT).as_posix(): path
            for path in (ROOT / "b4artists_ml").rglob("*")
            if path.is_file()
            and (path.suffix in (".py", ".json", ".md", ".npz") or path.name == "LICENSE")
        }
        assert set(package_zip.namelist()) == set(source)
        assert all(package_zip.read(name) == path.read_bytes() for name, path in source.items())

    meta["exact_package_checks"] = dict(
        passed=True,
        tests=package["tests"],
        offline_guard=True,
        evidence=package_path.relative_to(ROOT).as_posix(),
    )
    meta["exact_package_ui"] = dict(
        passed=True,
        events=len(ui["events"]),
        step_count=ui["step_count"],
        step_p95_ms=ui["step_p95_ms"],
        step_max_ms=ui["step_max_ms"],
        elapsed_seconds=ui["elapsed_seconds"],
        priority_poses_preserved=metrics["priority_poses_preserved"],
        editable_linear_keys=metrics["editable_linear_keys"],
        evidence=ui_path.relative_to(ROOT).as_posix(),
        process_evidence=process_path.relative_to(ROOT).as_posix(),
    )
    meta["ready_for_local_testing"] = True
    meta["responsiveness_p95_under_50ms_verified"] = ui["step_p95_ms"] < 50
    meta["responsiveness_all_steps_under_50ms_verified"] = ui["step_max_ms"] < 50
    meta["host_shutdown_qualified"] = False
    meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "package_sha256": meta["sha256"],
                "exact_package_tests": package["tests"],
                "ui_passed": ui["passed"],
                "step_p95_ms": ui["step_p95_ms"],
                "step_max_ms": ui["step_max_ms"],
                "host_shutdown_qualified": False,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
