"""Recompute and validate the immutable current-goal v2 aggregate."""
from pathlib import Path
import hashlib
import json
import sys


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
TRAIN = HERE.parent
RESULTS = TRAIN / "results"
RECEIPT = RESULTS / "current-goal-gate-status-v2.json"
OUTPUT = RESULTS / "current-goal-gate-status-validation-v2.json"
sys.path.insert(0, str(TRAIN))
import build_current_goal_gate_status_v2 as builder


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate():
    stored = json.loads(RECEIPT.read_text(encoding="utf-8"))
    expected = builder.build()
    if stored != expected:
        raise ValueError("Stored v2 aggregate differs from recomputed evidence")
    if stored["full_goal_complete"] is not False:
        raise ValueError("Full goal must remain incomplete")
    boundary = stored["claim_boundary"]
    if any(boundary[key] is not False for key in (
        "learned_temporal_quality_verified",
        "model_training_permitted",
        "model_promotion_permitted",
        "cascadeur_connector_activation_permitted",
        "cascadeur_parity_verified",
        "surpasses_cascadeur",
        "universal_production_compatibility",
        "full_goal_complete",
    )):
        raise ValueError("A fail-closed claim changed state")
    return {
        "schema": "b4ml-current-goal-gate-status-validation-v2",
        "status": "PASS",
        "receipt": RECEIPT.relative_to(ROOT).as_posix(),
        "receipt_sha256": sha(RECEIPT),
        "builder": HERE.relative_to(ROOT).as_posix(),
        "builder_sha256": sha(HERE),
        "evidence_count": len(stored["evidence"]),
        "fail_closed": True,
        "full_goal_complete": False,
    }


def main():
    if OUTPUT.exists():
        raise RuntimeError("Immutable v2 validation already exists: " + str(OUTPUT))
    OUTPUT.write_text(json.dumps(validate(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
