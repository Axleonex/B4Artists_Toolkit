"""Fail-closed checks for the frozen full-hierarchy model comparison plan."""
from pathlib import Path
import hashlib
import json


ROOT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    plan = json.loads((ROOT / "full_hierarchy_model_comparison_plan_v1.json").read_text())
    paths = {
        "hierarchy_store": ROOT / "full_hierarchy_store_v1.py",
        "conditioning_schema": ROOT / "motion_conditioning_v1.py",
        "conditioning_adapter": ROOT / "hierarchy_conditioning_adapter_v1.py",
        "masked_baseline": ROOT / "masked_hierarchy_baseline_v1.py",
        "proposal_module": ROOT / "motion_label_proposals_v1.py",
        "proposal_plan": ROOT / "motion_label_proposals_plan_v1.json",
        "subject_split": ROOT / "results/hierarchy-cohorts-v1/split.json",
        "hierarchy_layout": ROOT / "results/full-hierarchy-store-v1/layout.json",
        "proposal_report": ROOT / "results/motion-label-proposals-v1/report.json",
        "proposal_contract": ROOT / "results/motion-label-proposals-contract-v1/report.json",
        "tcn_implementation": ROOT / "full_hierarchy_tcn_v1.py",
        "tcn_contract": ROOT / "check_full_hierarchy_tcn_v1.py",
        "torch_kinematics": ROOT / "full_hierarchy_torch_kinematics_v1.py",
        "torch_kinematics_contract": ROOT / "check_full_hierarchy_torch_kinematics_v1.py",
        "loss_scale_diagnostic": ROOT / "diagnose_full_hierarchy_loss_scale_v1.py",
        "microfit_contract": ROOT / "check_full_hierarchy_tcn_microfit_v1.py",
    }
    assert {name: sha(path) for name, path in paths.items()} == plan["sources"]
    split = json.loads(paths["subject_split"].read_text())
    layout = json.loads(paths["hierarchy_layout"].read_text())
    assert len(split["training_subjects"]) == 68
    assert len(split["development_subjects"]) == 17
    assert not set(split["training_subjects"]) & set(split["development_subjects"])
    assert layout["joints"] == plan["representation"]["joints"] == 23
    assert 3 + 6 * layout["joints"] == plan["representation"]["state_per_frame"] == 141
    assert plan["representation"]["conditioning_per_frame"] == 483
    assert plan["representation"]["boundary_context_per_frame"] == 142
    assert plan["representation"]["model_input_per_frame"] == 766
    assert plan["representation"]["world_space_prediction_forbidden"]
    assert plan["data_boundary"]["weak_contact_development"].startswith("Forbidden")
    assert all("Transformer" not in candidate["family"] for candidate in plan["candidates"])
    assert {candidate["id"] for candidate in plan["candidates"]} == {
        "masked_residual_tcn", "masked_conditional_diffusion_unet"
    }
    tcn = next(candidate for candidate in plan["candidates"] if candidate["id"] == "masked_residual_tcn")
    assert tcn["implementation_status"]["implemented"] is True
    assert tcn["implementation_status"]["weights_trained"] is False
    assert tcn["implementation_status"]["runtime_promoted"] is False
    assert plan["shared_training"]["loss_weights"] == {
        "root": 1.0, "position": 1.0, "rotation": 1.0,
        "velocity": 0.05, "acceleration": 0.0005, "contact": 0.1,
    }
    assert plan["local_framework_status"]["bforartists_runtime_dependency"] is False
    assert plan["validation_read"] is False and plan["confirmation_read"] is False
    print(json.dumps({
        "passed": True,
        "candidates": [candidate["id"] for candidate in plan["candidates"]],
        "training_subjects": len(split["training_subjects"]),
        "development_subjects": len(split["development_subjects"]),
        "state_per_frame": plan["representation"]["state_per_frame"],
        "conditioning_per_frame": plan["representation"]["conditioning_per_frame"],
        "development_target_contact_forbidden": True,
        "world_space_prediction_forbidden": True,
        "confirmation_read": False,
    }, indent=2))


if __name__ == "__main__":
    main()
