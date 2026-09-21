"""Fail-closed check for the one allowed complete-priority TCN repair."""
from pathlib import Path
import hashlib
import json


ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    plan = json.loads((ROOT / "full_hierarchy_tcn_training_plan_v2.json").read_text())
    paths = {
        "trainer": ROOT / "train_full_hierarchy_tcn_v2.py",
        "training_engine": ROOT / "train_full_hierarchy_tcn_v1.py",
        "model": ROOT / "full_hierarchy_tcn_v1.py",
        "kinematics": ROOT / "full_hierarchy_torch_kinematics_v1.py",
        "dataset": ROOT / "full_hierarchy_sequence_dataset_v2.py",
        "priority_plan": ROOT / "priority_cohort_plan_v2.json",
        "priority_split": ROOT / "results/priority-cohorts-v2/split.json",
        "priority_specs": ROOT / "results/priority-sequence-specs-v2/specs.json",
        "priority_report": ROOT / "results/priority-sequence-specs-v2/report.json",
        "label_plan": ROOT / "motion_label_proposals_plan_v1.json",
        "hierarchy_layout": ROOT / "results/full-hierarchy-store-v1/layout.json",
        "v1_rejection": ROOT / "results/full-hierarchy-tcn-v1/priority-helper-diagnosis.json",
    }
    assert {name: sha(path) for name, path in paths.items()} == plan["sources"]
    assert plan["repair_scope"]["v1_checkpoints_qualified"] is False
    assert plan["repair_scope"]["v1_development_may_select_v2"] is False
    assert plan["data"]["training_subjects"] == 54
    assert plan["data"]["development_subjects"] == 14
    assert plan["data"]["excluded_exposed_v1_development_subjects"] == 17
    assert len(plan["runs"]) == 4 and len(set(plan["runs"])) == 4
    assert plan["quality_evaluation"]["exact_complete_priority_error_maximum"] == 1e-6
    assert plan["environment"]["packages_may_be_modified"] is False
    assert plan["training_allowed"] and plan["development_read_allowed"]
    assert plan["confirmation_read"] is False and plan["runtime_promotion_allowed"] is False
    print(json.dumps({
        "passed": True,
        "repair": "complete 23-joint state fixed at full priority frames",
        "runs": plan["runs"],
        "training_subjects": 54,
        "fresh_development_subjects": 14,
        "excluded_exposed_v1_development_subjects": 17,
        "confirmation_read": False,
        "runtime_promotion_allowed": False
    }, indent=2))


if __name__ == "__main__":
    main()
