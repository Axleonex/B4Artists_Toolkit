"""Test human-evidence rejection and the correction-trial validation contract."""
from pathlib import Path
import hashlib
import json

import validate_correction_trial_v1 as validator


HERE = Path(__file__).resolve()
TRAIN = HERE.parent
SOURCE = TRAIN / "results/correction-trial-smoke-v2/boneforge-reach-B-347275e8601c.json"
OUT = TRAIN / "results/correction-trial-validator-v1.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists():
        raise RuntimeError("Correction-trial validator evidence already exists")
    synthetic = json.loads(SOURCE.read_text(encoding="utf-8"))
    rejected = False
    try:
        validator.validate_report(synthetic)
    except ValueError as exc:
        rejected = "human evidence" in str(exc)
    if not rejected:
        raise ValueError("Synthetic smoke was not rejected as human evidence")
    fixture = dict(synthetic)
    fixture.update(
        human_authored=True, synthetic_smoke=False, production_acceptable="NO",
        active_work_seconds=max(0.001, fixture["active_work_seconds"]),
    )
    normalized = validator.validate_report(fixture)
    if not normalized["valid"] or normalized["case_id"] != "boneforge/reach":
        raise ValueError("Structurally valid human fixture did not normalize")
    result = dict(
        schema="b4ml-correction-trial-validator-check-v1", complete=True,
        synthetic_export_sha256=sha(SOURCE), synthetic_rejected_as_human=True,
        valid_contract_fixture_accepted=True, fixture_persisted=False,
        human_reviewed_cases=0, validator_sha256=sha(TRAIN / "validate_correction_trial_v1.py"),
        checker_sha256=sha(HERE), full_goal_complete=False,
    )
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
