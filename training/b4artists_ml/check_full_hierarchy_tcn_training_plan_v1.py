"""Fail-closed checks for the prospective full-hierarchy TCN training plan."""
from pathlib import Path
import hashlib
import json


ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    plan = json.loads((ROOT / "full_hierarchy_tcn_training_plan_v1.json").read_text())
    paths = {
        "trainer": ROOT / "train_full_hierarchy_tcn_v1.py",
        "model": ROOT / "full_hierarchy_tcn_v1.py",
        "kinematics": ROOT / "full_hierarchy_torch_kinematics_v1.py",
        "dataset": ROOT / "full_hierarchy_sequence_dataset_v1.py",
        "baseline": ROOT / "masked_hierarchy_baseline_v1.py",
        "model_plan": ROOT / "full_hierarchy_model_comparison_plan_v1.json",
        "sequence_plan": ROOT / "full_hierarchy_sequence_specs_plan_v1.json",
        "sequence_specs": ROOT / "results/full-hierarchy-sequence-specs-v1/specs.json",
        "sequence_report": ROOT / "results/full-hierarchy-sequence-specs-v1/report.json",
        "label_plan": ROOT / "motion_label_proposals_plan_v1.json",
        "subject_split": ROOT / "results/hierarchy-cohorts-v1/split.json",
        "loss_diagnostic": ROOT / "diagnose_full_hierarchy_loss_scale_v1.py",
        "microfit": ROOT / "check_full_hierarchy_tcn_microfit_v1.py",
    }
    assert {name: sha(path) for name, path in paths.items()} == plan["sources"]
    assert plan["model_input_width"] == 766
    assert plan["seeds"] == [20260909, 20260910]
    assert plan["contact_modes"] == ["unknown_contact", "weak_contact"]
    assert len(plan["runs"]) == 4 and len(set(plan["runs"])) == 4
    assert plan["data"]["training_subjects"] == 68
    assert plan["data"]["development_subjects"] == 17
    assert plan["data"]["development_contact"].startswith("Always unknown")
    assert plan["optimization"]["loss_weights"] == {
        "root": 1.0, "position": 1.0, "rotation": 1.0,
        "velocity": 0.05, "acceleration": 0.0005, "contact": 0.1,
    }
    assert plan["optimization"]["minimum_epochs"] < plan["optimization"]["maximum_epochs"]
    assert plan["contact_ablation"]["promotion"].startswith("Unknown mode may qualify independently")
    assert plan["environment"]["packages_may_be_modified"] is False
    assert plan["environment"]["bforartists_runtime_dependency"] is False
    assert plan["training_allowed"] and plan["development_read_allowed"]
    assert plan["confirmation_read"] is False
    assert plan["runtime_promotion_allowed"] is False
    print(json.dumps({
        "passed": True,
        "runs": plan["runs"],
        "model_input_width": plan["model_input_width"],
        "loss_weights": plan["optimization"]["loss_weights"],
        "development_contact": "unknown",
        "confirmation_read": False,
        "runtime_promotion_allowed": False
    }, indent=2))


if __name__ == "__main__":
    main()
