"""Validate the hash-bound temporal data-boundary revalidation receipt."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RECEIPT = ROOT / "docs" / "b4artists_ml" / "temporal-boundary-revalidation-v2.json"
OUTPUT = ROOT / "training" / "b4artists_ml" / "results" / "temporal-boundary-revalidation-validation-v2.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    report = json.loads(RECEIPT.read_text(encoding="utf-8"))
    if report.get("schema") != "b4ml-temporal-boundary-revalidation-v2":
        raise ValueError("Unexpected temporal boundary revalidation schema")
    if report.get("status") != "PASS_FAIL_CLOSED":
        raise ValueError("Temporal boundary was not proven fail-closed")
    if report.get("suite") != {
        "tests": 12, "passed": 12, "failures": 0, "errors": 0,
        "skipped": 0, "successful": True,
    }:
        raise ValueError("Temporal boundary regression suite is incomplete")
    current = report.get("current_intake", {})
    if current.get("status") != "BLOCKED_INTAKE_MISSING_EVIDENCE":
        raise ValueError("Current temporal intake is not blocked")
    if current.get("missing_required_fields") != [
        "action_id", "skeleton_id", "source_rig_id"
    ]:
        raise ValueError("Current manifest boundary changed")
    if current.get("reviewed_contact_intent_present") is not False:
        raise ValueError("Human review evidence was inferred")
    if current.get("identity_authorization_present") is not False:
        raise ValueError("Reviewer authorization was inferred")
    parent = report.get("parent_boundary", {})
    if parent.get("status") != "BLOCKED_DATA_BOUNDARY_UNQUALIFIED":
        raise ValueError("Parent training boundary is not blocked")
    if parent.get("model_training_permitted") is not False:
        raise ValueError("Model training was incorrectly permitted")
    if parent.get("model_promotion_permitted") is not False:
        raise ValueError("Model promotion was incorrectly permitted")
    for section in (current, parent):
        path = ROOT / section["receipt"]
        if not path.is_file() or _sha256(path) != section["receipt_sha256"]:
            raise ValueError("Temporal boundary child receipt changed")
    sources = report.get("sources", {})
    if len(sources) != 11:
        raise ValueError("Temporal boundary source set changed")
    for relative, expected in sources.items():
        path = ROOT / relative
        if not path.is_file() or _sha256(path) != expected:
            raise ValueError("Temporal boundary source changed: " + relative)
    claims = report.get("claim_boundary", {})
    if any(claims.get(key) is not False for key in (
        "learned_temporal_quality_verified", "independent_animator_usability_verified",
        "cascadeur_parity_verified", "runtime_promoted", "full_goal_complete",
    )):
        raise ValueError("Temporal boundary claim widened")
    validation = {
        "schema": "b4ml-temporal-boundary-revalidation-validation-v2",
        "status": "PASS",
        "receipt": RECEIPT.relative_to(ROOT).as_posix(),
        "receipt_sha256": _sha256(RECEIPT),
        "source_count": len(sources),
        "tests": report["suite"]["tests"],
        "model_training_permitted": False,
        "model_promotion_permitted": False,
        "full_goal_complete": False,
    }
    OUTPUT.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
