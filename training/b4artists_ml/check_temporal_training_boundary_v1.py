"""Fail-closed gate for learned temporal training evidence."""
from __future__ import annotations

import json
import os
from pathlib import Path


ROOT = Path(os.environ.get(
    "B4ML_REPO",
    r"X:\Scripting Attempts\B4Artists_Tools\B4Artists_Anim_Tools_github"))
RESULTS = ROOT / "training" / "b4artists_ml" / "results"
AUDIT = RESULTS / "action-rig-disjoint-audit-v1.json"
PROTOCOL = RESULTS / "action-disjoint-protocol-v1.json"
SKELETON_AUDIT = RESULTS / "cached-skeleton-provenance-v1.json"
JOINT_PROTOCOL = RESULTS / "joint-action-skeleton-protocol-v1.json"
INTAKE = RESULTS / "temporal-corpus-intake-v1.json"
OUT = RESULTS / "temporal-training-boundary-v1.json"


def build_gate(
    audit: dict,
    protocol: dict,
    skeleton: dict | None = None,
    joint: dict | None = None,
    intake: dict | None = None,
) -> dict:
    failures = []
    if audit.get("action_disjoint") is not True:
        failures.append("action-disjointness is not qualified")
    if protocol.get("action_partition_has_no_group_leakage") is not True:
        failures.append("the action partition proposal does not prove group safety")
    if protocol.get("rig_disjoint") is not True:
        if joint and joint.get("status") == "REDUCED_JOINT_PARTITION_PROPOSAL_READY":
            excluded = joint.get("proposal", {}).get("excluded_actions", [])
            failures.append(
                "full action/skeleton corpus is connected; the reduced joint "
                "proposal excludes action groups " + str(excluded) + " and is "
                "not a qualified holdout")
        elif skeleton and skeleton.get("joint_action_skeleton_partition_feasible") is False:
            failures.append(
                "derived skeleton topology exists, but the current corpus has no "
                "joint action/skeleton-disjoint partition")
        else:
            failures.append("rig/skeleton identity and rig-disjointness are missing")
    if protocol.get("reviewed_contact_intent_available") is not True:
        failures.append("reviewed contact/intent provenance is missing")
    if intake is None:
        failures.append("temporal corpus intake preflight is missing")
    elif intake.get("qualified_for_parent_boundary") is not True:
        failures.append("temporal corpus intake preflight is not qualified")
    return {
        "schema": "b4ml-temporal-training-boundary-v1",
        "status": "QUALIFIED" if not failures else "BLOCKED_DATA_BOUNDARY_UNQUALIFIED",
        "failures": failures,
        "model_training_permitted": not failures,
        "model_promotion_permitted": False,
        "source_audit": "training/b4artists_ml/results/action-rig-disjoint-audit-v1.json",
        "source_protocol": "training/b4artists_ml/results/action-disjoint-protocol-v1.json",
        "source_skeleton_audit": (
            "training/b4artists_ml/results/cached-skeleton-provenance-v1.json"
            if skeleton else None
        ),
        "source_joint_protocol": (
            "training/b4artists_ml/results/joint-action-skeleton-protocol-v1.json"
            if joint else None
        ),
        "source_intake": (
            "training/b4artists_ml/results/temporal-corpus-intake-v1.json"
            if intake else None
        ),
        "claim_boundary": {
            "learned_temporal_quality_verified": False,
            "reduced_joint_partition_temporal_evaluation_qualified": False,
            "runtime_promoted": False,
            "full_goal_complete": False,
        },
    }


def main() -> dict:
    report = build_gate(
        json.loads(AUDIT.read_text(encoding="utf-8")),
        json.loads(PROTOCOL.read_text(encoding="utf-8")),
        json.loads(SKELETON_AUDIT.read_text(encoding="utf-8"))
        if SKELETON_AUDIT.is_file() else None,
        json.loads(JOINT_PROTOCOL.read_text(encoding="utf-8"))
        if JOINT_PROTOCOL.is_file() else None,
        json.loads(INTAKE.read_text(encoding="utf-8"))
        if INTAKE.is_file() else None,
    )
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return report


if __name__ == "__main__":
    result = main()
    if result["status"] != "QUALIFIED":
        raise SystemExit(2)
