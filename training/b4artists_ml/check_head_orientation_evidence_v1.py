"""Fail-closed evidence check for the existing procedural humanoid Head path."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "training" / "b4artists_ml" / "results"
OUT = RESULTS / "head-orientation-evidence-v1.json"
RECEIPT = RESULTS / "body-controls-v1.json"
SOLVER = ROOT / "b4artists_ml" / "body_solver.py"
PREVIEW = ROOT / "b4artists_ml" / "body_preview.py"
TEST = ROOT / "tests" / "test_b4artists_ml_body_controls.py"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> dict:
    errors: list[str] = []
    required = {
        "solver_orientation_joints": (SOLVER, "ORIENTATION_JOINTS=(0,4,7,10,13,16)"),
        "solver_head_effector_mapping": (
            SOLVER,
            "binding['effectors'][ORIENTATION_JOINTS.index(index)-1]",
        ),
        "preview_head_target": (PREVIEW, "(4,'Head')"),
        "preview_rotation_toggle": (PREVIEW, "item.use_orientation"),
        "test_iterates_orientation_joints": (TEST, "if index in solver.ORIENTATION_JOINTS"),
        "test_checks_six_orientations": (TEST, "requested_orientations'],6"),
    }
    source_hashes = {}
    for key, (path, token) in required.items():
        if not path.is_file():
            errors.append(f"missing:{path.as_posix()}")
            continue
        source_hashes[path.relative_to(ROOT).as_posix()] = sha256(path)
        if token not in path.read_text(encoding="utf-8"):
            errors.append(f"missing_token:{key}")

    receipt = None
    if not RECEIPT.is_file():
        errors.append(f"missing:{RECEIPT.as_posix()}")
    else:
        try:
            receipt = json.loads(RECEIPT.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid_receipt:{exc}")
        else:
            if receipt.get("passed") is not True:
                errors.append("body_controls_not_passed")
            if receipt.get("tests") != 10 or receipt.get("failures") != 0 or receipt.get("errors") != 0:
                errors.append("body_controls_suite_shape_changed")
            records = receipt.get("records")
            orientation_records = (
                [row for row in records if isinstance(row, dict)
                 and "requested_orientations" in row]
                if isinstance(records, list) else []
            )
            if len(orientation_records) != 5:
                errors.append("body_controls_fixture_count_changed")
            elif any(row.get("requested_orientations") != 6
                     for row in orientation_records):
                errors.append("six_orientation_contract_missing")
        orientation_records = (
            [row for row in receipt.get("records", []) if isinstance(row, dict)
             and "requested_orientations" in row]
            if isinstance(receipt, dict) and isinstance(receipt.get("records"), list)
            else []
        )

    report = {
        "schema": "b4ml-head-orientation-evidence-v1",
        "status": "PASS" if not errors else "FAIL",
        "scope": "Machine-checked evidence for the existing procedural humanoid Head orientation path; not learned-motion or human-usability evidence.",
        "semantic_target": {
            "label": "Head",
            "joint_index": 4,
            "direct_orientation": True,
            "target_row_present": "preview_head_target" not in errors,
        },
        "coverage": {
            "focused_receipt": RECEIPT.relative_to(ROOT).as_posix(),
            "focused_receipt_sha256": sha256(RECEIPT) if RECEIPT.is_file() else None,
            "tests": receipt.get("tests") if isinstance(receipt, dict) else None,
            "fixtures": [row.get("fixture") for row in orientation_records],
            "requested_orientations_per_fixture": 6,
            "head_in_direct_orientation_set": "solver_orientation_joints" not in errors,
        },
        "source_hashes": source_hashes,
        "claim_boundary": {
            "procedural_evaluated_rig_constraint": True,
            "learned_temporal_quality_verified": False,
            "independent_animator_usability_verified": False,
            "cascadeur_conversion_verified": False,
            "cascadeur_parity_verified": False,
            "full_goal_complete": False,
        },
        "errors": errors,
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("HEAD_ORIENTATION_EVIDENCE: " + json.dumps(report), flush=True)
    if errors:
        raise SystemExit(1)
    return report


if __name__ == "__main__":
    main()
