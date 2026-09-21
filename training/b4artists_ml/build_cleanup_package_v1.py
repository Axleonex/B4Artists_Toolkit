"""Build experimental 0.32.0 from the frozen cleanup/contact-review regression."""
from pathlib import Path
import ast
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training/b4artists_ml/results"
DOCS = ROOT / "docs/b4artists_ml"
OUTPUT = ROOT / "releases/b4artists_ml_v0.32.0.zip"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def runtime_hashes(root=ROOT):
    return {
        path.relative_to(root).as_posix(): sha(path)
        for path in (root / "b4artists_ml").glob("*.py")
    }


def main():
    assert not OUTPUT.exists()
    regression_path = RESULTS / "full-regression-032-v1-regression.json"
    regression = read(regression_path)
    assert len(regression) == 55
    assert len({row["suite"] for row in regression}) == 55
    assert sum(row["tests"] for row in regression) == 495
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
    assert packaged == tested

    cleanup = read(RESULTS / "cleanup-v1.json")
    assert cleanup["passed"] and cleanup["tests"] == 5
    human, quadruped = cleanup["records"]
    assert not human["learned"] and not quadruped["learned"]
    assert human["priority_poses_preserved"] and human["contacts_preserved"]
    assert quadruped["priority_poses_preserved"] and quadruped["contacts_preserved"]
    assert human["contact_frame_evaluations"] == 6
    assert quadruped["contact_samples"] == 12
    assert quadruped["contact_sample_frames"] == 3
    assert quadruped["contact_frame_evaluations"] == 6

    cleanup_ui_path = DOCS / "cleanup-ui-v4.json"
    cleanup_ui = read(cleanup_ui_path)
    assert cleanup_ui["passed"]
    assert cleanup_ui["metrics"]["keys_removed"] > 0
    assert cleanup_ui["metrics"]["priority_poses_preserved"]
    assert cleanup_ui["metrics"]["source_action_unchanged"]
    assert cleanup_ui["step_max_ms"] < 50

    review_ui_path = DOCS / "contact-review-ui-v4.json"
    review_ui = read(review_ui_path)
    assert review_ui["passed"]
    assert {row["scenario"] for row in review_ui["scenarios"]} == {"humanoid", "quadruped"}
    assert all(
        row["passed"]
        and row["operator_undo_flag"]
        and any("Undo restored" in event for event in row["events"])
        and any("Redo restored" in event for event in row["events"])
        for row in review_ui["scenarios"]
    )

    tree = ast.parse((ROOT / "b4artists_ml/__init__.py").read_bytes())
    info = next(
        node.value
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "bl_info" for target in node.targets)
    )
    index = next(i for i, key in enumerate(info.keys) if key.value == "version")
    assert ast.literal_eval(info.values[index]) == (0, 32, 0)

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

    with zipfile.ZipFile(OUTPUT, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, path in sorted(paths.items()):
            item = zipfile.ZipInfo(name, date_time=(2026, 9, 11, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = 0o644 << 16
            archive.writestr(item, path.read_bytes(), compresslevel=9)
    with zipfile.ZipFile(OUTPUT) as archive:
        assert set(archive.namelist()) == set(paths)
        assert all(archive.read(name) == path.read_bytes() for name, path in paths.items())

    report = dict(
        version="0.32.0",
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
        regression=dict(unique_cases=495, suites=55, evidence=regression_path.relative_to(ROOT).as_posix()),
        cleanup=dict(
            backend=human["backend"], learned=False,
            humanoid_keys_removed=human["keys_removed"],
            quadruped_keys_removed=quadruped["keys_removed"],
            accepted_contacts=human["accepted_contacts"] + quadruped["accepted_contacts"],
            priority_poses_preserved=True, contacts_preserved=True,
            source_evidence="training/b4artists_ml/results/cleanup-v1.json",
            real_window_evidence=cleanup_ui_path.relative_to(ROOT).as_posix(),
        ),
        contact_review=dict(
            real_window_evidence=review_ui_path.relative_to(ROOT).as_posix(),
            families=[row["scenario"] for row in review_ui["scenarios"]],
            undo_redo_verified=True,
        ),
        exact_package_checks="pending",
        host_shutdown_qualified=False,
        independent_human_usability="unknown",
        qualification_note=(
            "Deterministic contact review and contact-aware curve cleanup preserve priority poses and "
            "source animation and publish editable candidates. Cleanup is not learned motion. This "
            "package does not qualify clean host shutdown, independent animator acceptance, learned "
            "inbetweening, or Cascadeur parity."
        ),
    )
    (DOCS / "package-test-v0.32.0.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("version", "files", "bytes", "sha256")}, indent=2))


if __name__ == "__main__":
    main()
