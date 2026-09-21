"""Bind paired torso shaping and its preserved first-attempt failure evidence."""
from pathlib import Path
import hashlib
import json
import os


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training" / "b4artists_ml" / "results"
SOURCE = ROOT / "b4artists_ml" / "body_solver.py"
TEST = ROOT / "tests" / "test_b4artists_ml_coupled_torso_orientation_v1.py"
FIRST = RESULTS / "coupled-torso-orientation-v1.json"
PASS = RESULTS / "coupled-torso-orientation-v1-second-attempt.json"
CHEST_ORIENTATION = RESULTS / "chest-orientation-v1-coupled-regression.json"
CHEST_POSITION = RESULTS / "chest-target-v1-coupled-regression.json"
OUT = RESULTS / "coupled-torso-orientation-v1-focused.json"
EXPECTED = {
    "boneforge",
    "rigify_basic",
    "rigify_default",
    "metarig_basic",
    "metarig_default",
    "unity_humanoid_fbx",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    if OUT.exists():
        raise RuntimeError("Coupled torso focused receipt already exists")
    first = read(FIRST)
    passed = read(PASS)
    chest_orientation = read(CHEST_ORIENTATION)
    chest_position = read(CHEST_POSITION)
    if first.get("schema") != "b4ml-coupled-torso-orientation-v1":
        raise ValueError("First-attempt schema changed")
    if first.get("passed") is not False or first.get("failures") != 2:
        raise ValueError("First-attempt rejection evidence changed")
    if passed.get("schema") != "b4ml-coupled-torso-orientation-v1":
        raise ValueError("Passing schema changed")
    if passed.get("passed") is not True or passed.get("failures") or passed.get("errors"):
        raise ValueError("Paired torso host result is not passing")
    records = passed.get("records", [])
    if {row.get("fixture") for row in records} != EXPECTED:
        raise ValueError("Paired torso adapter set changed")
    if any(row.get("pin_error_body_scales", 1) >= 2e-4 for row in records):
        raise ValueError("Paired torso pin gate failed")
    if any(row.get("spine_orientation_error_radians", 1) >= 0.001 for row in records):
        raise ValueError("Paired Spine orientation gate failed")
    if any(row.get("chest_orientation_error_radians", 1) >= 0.001 for row in records):
        raise ValueError("Paired Chest orientation gate failed")
    for label, report in (
        ("Chest-only orientation", chest_orientation),
        ("Chest position", chest_position),
    ):
        if report.get("passed") is not True or report.get("failures") or report.get("errors"):
            raise ValueError(f"{label} regression failed")
        if len(report.get("records", [])) != 6:
            raise ValueError(f"{label} adapter coverage changed")

    receipt = {
        "schema": "b4ml-coupled-torso-orientation-v1-focused",
        "status": "PASS_FOCUSED_DETERMINISTIC",
        "complete": True,
        "source": SOURCE.relative_to(ROOT).as_posix(),
        "source_sha256": sha(SOURCE),
        "test": TEST.relative_to(ROOT).as_posix(),
        "test_sha256": sha(TEST),
        "preserved_first_attempt": {
            "report": FIRST.relative_to(ROOT).as_posix(),
            "sha256": sha(FIRST),
            "passed": False,
            "rejected_adapters": ["rigify_basic", "rigify_default"],
            "reason": "A one-control target generator could not exercise paired shaping on generated Rigify.",
        },
        "passing_host_result": {
            "report": PASS.relative_to(ROOT).as_posix(),
            "sha256": sha(PASS),
            "tests": passed["tests"],
            "adapters": sorted(EXPECTED),
            "maximum_pin_error_body_scales": max(row["pin_error_body_scales"] for row in records),
            "maximum_spine_orientation_error_radians": max(
                row["spine_orientation_error_radians"] for row in records
            ),
            "maximum_chest_orientation_error_radians": max(
                row["chest_orientation_error_radians"] for row in records
            ),
        },
        "regressions": [
            {
                "name": "Chest-only orientation",
                "report": CHEST_ORIENTATION.relative_to(ROOT).as_posix(),
                "sha256": sha(CHEST_ORIENTATION),
                "tests": chest_orientation["tests"],
                "adapters": len(chest_orientation["records"]),
                "passed": True,
            },
            {
                "name": "Chest position",
                "report": CHEST_POSITION.relative_to(ROOT).as_posix(),
                "sha256": sha(CHEST_POSITION),
                "tests": chest_position["tests"],
                "adapters": len(chest_position["records"]),
                "passed": True,
            },
            {
                "name": "Spine-only production-character orientation",
                "tests": 3,
                "passed_marker_observed": True,
                "durable_output_added_by_legacy_test": False,
            },
        ],
        "host_process_exit_capture": False,
        "known_host_shutdown_fault_not_qualified": True,
        "claim_boundary": {
            "procedural_only": True,
            "independent_lower_spine_translation": False,
            "joint_limit_aware_torso_shaping": False,
            "production_character_qualification": False,
            "human_usability_verified": False,
            "learned_motion": False,
            "cascadeur_parity": False,
            "full_goal_complete": False,
        },
    }
    temporary = OUT.with_suffix(".tmp")
    temporary.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, OUT)
    print(json.dumps(receipt, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
