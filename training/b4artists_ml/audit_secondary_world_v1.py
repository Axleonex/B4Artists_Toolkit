"""Final consistency audit for the experimental 0.25.0 release candidate."""
from pathlib import Path
import ast
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "training/b4artists_ml/results/secondary-world-final-audit-v1.json"


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
    assert not OUT.exists()
    archive = ROOT / "releases/b4artists_ml_v0.25.0.zip"
    regression = read(ROOT / "training/b4artists_ml/results/secondary-world-full-v1-regression.json")
    package = read(ROOT / "training/b4artists_ml/results/secondary-world-package-v1.json")
    source_ui = read(ROOT / "docs/b4artists_ml/secondary-ui-secondary-world-source-v1.json")
    package_ui = read(ROOT / "docs/b4artists_ml/secondary-ui-secondary-world-package-v1.json")
    metadata = read(ROOT / "docs/b4artists_ml/package-test-v0.25.0.json")
    route = read(ROOT / "training/b4artists_ml/results/orchestration-route-secondary-world-v20.json")

    python_files = sorted((ROOT / "b4artists_ml").rglob("*.py"))
    python_files += sorted((ROOT / "training/b4artists_ml").rglob("*.py"))
    for path in python_files:
        ast.parse(path.read_bytes(), filename=str(path))

    assert len(regression) == 49 and sum(row["tests"] for row in regression) == 465
    assert all(
        row["assertions_passed"]
        and not row.get("failures")
        and not row.get("errors")
        and not row.get("skipped")
        for row in regression
    )
    assert len({json.dumps(row["runtime_sha256"], sort_keys=True) for row in regression}) == 1
    current = runtime_hashes()
    tested = regression[0]["runtime_sha256"]
    assert len(current) == 37 and current == tested
    assert current == source_ui["runtime_sha256"] == package["runtime_sha256"]
    assert current == package_ui["runtime_sha256"] == metadata["runtime_sha256"]
    assert package["passed"] and package["tests"] == 42 and package["exact_package"]
    assert package["offline_guard_self_test"] and not package["denied_runtime_calls"]
    package_root = (ROOT / "training/b4artists_ml/cache/secondary-world-package-v1").resolve()
    assert package["package_modules"]
    assert all(Path(path).resolve().is_relative_to(package_root) for path in package["package_modules"].values())
    assert source_ui["passed"] and package_ui["passed"]
    assert Path(source_ui["module_root"]).resolve() == (ROOT / "b4artists_ml").resolve()
    assert Path(package_ui["module_root"]).resolve().is_relative_to(package_root)
    assert source_ui["step_p95_ms"] < 50 and source_ui["step_max_ms"] < 50
    assert package_ui["step_p95_ms"] < 50 and package_ui["step_max_ms"] < 50
    assert metadata["ready_for_local_testing"] and not metadata["full_goal_complete"]
    assert metadata["package_matches_source"] and metadata["forbidden_identities_absent"]
    assert not package["full_goal_complete"] and not route["formal_goal"]["complete"]
    assert route["evaluation"]["mode"] == "shadow/classification-only"
    assert route["evaluation"]["model_calls"] == 0
    assert route["execution"]["continuation"] == "native"
    assert not route["session_adoption"]["production_state_changed"]
    assert sha(archive) == metadata["sha256"] == package["package_sha256"]
    assert sha(archive) == route["evaluation"]["archive_sha256"]

    source = {
        path.relative_to(ROOT).as_posix(): path
        for path in (ROOT / "b4artists_ml").rglob("*")
        if path.is_file()
        and (path.suffix in (".py", ".json", ".md", ".npz") or path.name == "LICENSE")
    }
    forbidden = (b"jonvilario", b"atonlotus")
    with zipfile.ZipFile(archive) as package_zip:
        assert set(package_zip.namelist()) == set(source)
        for name, path in source.items():
            payload = package_zip.read(name)
            assert payload == path.read_bytes()
            assert not any(identity in payload.lower() for identity in forbidden)

    metrics = package_ui["metrics"]
    assert metrics["backend"] == "implicit_selected_control_secondary_v2"
    assert metrics["space"] == "WORLD" and metrics["gravity_influence"] > 0
    assert metrics["collision_samples"] > 0
    assert metrics["max_raw_penetration"] > 0 and metrics["max_penetration_after"] == 0
    assert metrics["max_world_location_error"] < 2e-4
    assert metrics["max_world_rotation_error_radians"] < 2e-3
    assert metrics["priority_poses_preserved"] and metrics["editable_linear_keys"]

    result = dict(
        passed=True,
        release="0.25.0",
        parsed_python_files=len(python_files),
        runtime_files=len(current),
        regression_suites=len(regression),
        regression_tests=sum(row["tests"] for row in regression),
        runtime_hash_sets=1,
        exact_package_tests=package["tests"],
        exact_package_modules=len(package["package_modules"]),
        outbound_runtime_calls=len(package["denied_runtime_calls"]),
        source_ui_passed=source_ui["passed"],
        package_ui_passed=package_ui["passed"],
        package_matches_source=True,
        forbidden_identities_absent=True,
        archive_sha256=sha(archive),
        route=route["execution"]["continuation"],
        evaluation=route["evaluation"]["mode"],
        model_calls=route["evaluation"]["model_calls"],
        ready_for_local_testing=True,
        full_goal_complete=False,
        host_shutdown_qualified=False,
    )
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
