"""Fail-closed validation for the distinct diffusion training plan."""
from pathlib import Path
import hashlib
import json


ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    plan = json.loads((ROOT / "full_hierarchy_diffusion_training_plan_v1.json").read_text())
    paths = {
        "trainer": ROOT / "train_full_hierarchy_diffusion_v1.py",
        "data_engine": ROOT / "train_full_hierarchy_tcn_v2.py",
        "batch_engine": ROOT / "train_full_hierarchy_tcn_v1.py",
        "model": ROOT / "full_hierarchy_diffusion_v1.py",
        "model_contract": ROOT / "check_full_hierarchy_diffusion_v1.py",
        "microfit": ROOT / "check_full_hierarchy_diffusion_microfit_v1.py",
        "kinematics": ROOT / "full_hierarchy_torch_kinematics_v1.py",
        "dataset": ROOT / "full_hierarchy_sequence_dataset_v2.py",
        "priority_split": ROOT / "results/priority-cohorts-v2/split.json",
        "priority_specs": ROOT / "results/priority-sequence-specs-v2/specs.json",
        "tcn_evaluation": ROOT / "results/full-hierarchy-tcn-v2/evaluation.json",
    }
    assert {name: sha(path) for name, path in paths.items()} == plan["sources"]
    assert plan["family_change"]["nearby_tcn_tuning_performed"] is False
    assert plan["parameters"] < 8_000_000 and plan["diffusion_steps"] == 100
    assert plan["seeds"] == [20260914, 20260915]
    assert len(plan["runs"]) == 4 and len(set(plan["runs"])) == 4
    assert plan["optimization"]["selection_ddim_steps"] == 4
    assert plan["quality_evaluation"]["ddim_steps"] == [4, 8, 12]
    assert plan["quality_evaluation"]["reviewed_contact_required_for_physical_promotion"]
    assert plan["quality_evaluation"]["bforartists_latency_required_for_runtime_promotion"]
    assert plan["environment"]["cuda_required"] is True
    assert plan["environment"]["packages_may_be_modified"] is False
    assert plan["environment"]["bforartists_runtime_dependency"] is False
    assert plan["training_allowed"] and plan["development_read_allowed"]
    assert plan["confirmation_read"] is False and plan["runtime_promotion_allowed"] is False
    print(json.dumps({
        "passed": True,
        "family": plan["family_change"]["to"],
        "parameters": plan["parameters"],
        "runs": plan["runs"],
        "selection_ddim_steps": 4,
        "final_ddim_steps": [4, 8, 12],
        "confirmation_read": False,
        "runtime_promotion_allowed": False
    }, indent=2))


if __name__ == "__main__":
    main()
