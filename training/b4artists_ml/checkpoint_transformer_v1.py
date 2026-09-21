"""Record formal goalpost 75 for the compact Transformer comparison."""
import copy
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from checkpoint_expanded_goal_v19 import ROOT, read, write, sha, g
from evaluate_milestone_goal_v2 import evaluate

BASE = "docs/b4artists_ml/"
GP = BASE + "goalposts/"
TR = "training/b4artists_ml/"
RESULTS = TR + "results/"


def main():
    checkpoint = read(BASE + "checkpoint-expanded-c2-v1.json")
    old = read(checkpoint["state_path"])
    state = copy.deepcopy(old)
    previous = checkpoint["evidence"]
    evidence = read(previous)
    assert checkpoint["round"] == 74 and checkpoint["remaining_evaluations"] == 26
    assert checkpoint["max_goalposts"] == 100 and checkpoint["deadline_unix"] == 1789053845
    assert not checkpoint["active_jobs"] and not checkpoint["full_goal_complete"]
    assert not [path for path, digest in evidence["artifacts"].items() if sha(path) != digest]

    plan = read(TR + "transformer_sequence_evaluation_plan_v1.json")
    report = read(RESULTS + "transformer-sequence-development-v1/report.json")
    processes = read(RESULTS + "transformer-sequence-training-v1/processes.json")
    assert len(processes) == 2 and all(row["exit_code"] == 0 for row in processes)
    assert report["complete"] and not report["family_passes"]
    assert report["protected_baselines_match"] and not report["confirmation_read"]
    assert report["plan_sha256"] == sha(TR + "transformer_sequence_evaluation_plan_v1.json")
    assert len(report["models"]) == 2 and all(
        not report["development_gates"][model["name"]][partition]["passed"]
        for model in report["models"]
        for partition in plan["partitions"]
    )

    inputs = [
        BASE + "transformer-comparison-routing-v1.json",
        TR + "sequence_velocity_conditioning_v1.py",
        TR + "sequence_transformer_model_v1.py",
        TR + "sequence_transformer_numpy_v1.py",
        TR + "check_sequence_transformer_v1.py",
        TR + "sequence_transformer_provider_v1.py",
        TR + "train_transformer_sequence_v1.py",
        TR + "transformer_sequence_fit_plan_v1.json",
        TR + "evaluate_transformer_sequence_v1.py",
        TR + "transformer_sequence_evaluation_plan_v1.json",
        TR + "checkpoint_transformer_v1.py",
    ]
    added = [path for path in inputs if path not in state["contract"]["inputs"]]
    state["contract"]["inputs"] += added
    state["contract_hash"] = g.digest(state["contract"])
    left, right = copy.deepcopy(state["contract"]), copy.deepcopy(old["contract"])
    left.pop("inputs")
    right.pop("inputs")
    assert left == right
    state["explicit_revisions"].append(
        {
            "reason": (
                "Compared a compact four-layer keyframe Transformer with observed-reference velocity inputs and learned residual confidence against the paired expanded-data convolution and unchanged procedural controls. Both seeds substantially reduce convolutional position/velocity/acceleration error and nearly match the shape reference, but fail the required3% position and short-gap cohort gates. NumPy inference is65ms for a cold65-frame train-only request; no promotion or confirmation read occurred."
            ),
            "prior_state": checkpoint["state_path"],
            "prior_sha256": sha(checkpoint["state_path"]),
            "prior_contract_hash": old["contract_hash"],
            "new_contract_hash": state["contract_hash"],
            "added_inputs": added,
            "recorded_at": time.time(),
        }
    )

    paths = set(evidence["artifacts"]) | set(inputs) | {
        checkpoint["state_path"], previous, BASE + "checkpoint-expanded-c2-v1.json"
    }
    for folder in (
        "sequence-transformer-contract-v1",
        "transformer-sequence-training-v1",
        "transformer-sequence-development-v1",
    ):
        root = ROOT / RESULTS / folder
        assert root.exists(), folder
        paths.update(path.relative_to(ROOT).as_posix() for path in root.rglob("*") if path.is_file())

    fingerprint = g.fingerprint(ROOT, state["contract"]["inputs"])
    models = {}
    for model in report["models"]:
        name = model["name"]
        models[name] = {
            partition: {
                "passed": report["development_gates"][name][partition]["passed"],
                "ratios": report["development_gates"][name][partition]["ratios"],
                "max_cohort_position_ratio": report["development_gates"][name][partition]["max_cohort_position_ratio"],
                "shape_position_ratio": report["shape_reference_attribution"][name][partition]["ratios"]["position"],
                "paired_tcn_ratios": report["tcn_comparison_ratios"][name][partition],
            }
            for partition in plan["partitions"]
        }
    evidence.update(
        contract_hash=state["contract_hash"],
        input_fingerprint=fingerprint,
        artifacts={path: sha(path) for path in sorted(paths)},
        previous_evidence_recheck={
            "path": previous,
            "sha256": sha(previous),
            "changed_artifacts": [],
            "all_prior_artifacts_unchanged": True,
        },
        transformer_research={
            "parameters": 620186,
            "parameter_bytes": 2480744,
            "cold_train_only_65_frame_seconds": 0.06548070000280859,
            "models": models,
            "development_report": RESULTS + "transformer-sequence-development-v1/report.json",
            "development_report_sha256": sha(RESULTS + "transformer-sequence-development-v1/report.json"),
            "confirmation_read": False,
            "runtime_promoted": False,
            "decision": "Retain the Transformer architecture; improve residual allocation/objective and curated data before another model-class expansion.",
            "full_goal_complete": False,
        },
    )
    evidence["qualification"].update(
        responsiveness=False,
        independent_usability="unknown",
        temporal_model_qualification=False,
        full_goal_complete=False,
        full_physics_acceptance=False,
    )
    evidence_path = GP + "transformer-evidence-v1.json"
    write(evidence_path, evidence)

    observations = read(GP + "expanded-c2-observations-v1.json")
    for group in observations.values():
        for row in group.values():
            row.update(artifact=evidence_path, sha256=sha(evidence_path), input_fingerprint=fingerprint)
    observations_path = GP + "transformer-observations-v1.json"
    write(observations_path, observations)

    duration = time.perf_counter() - checkpoint["next_controller_monotonic_start"]
    assert 0 <= duration < 40000, duration
    g.record_work(state, "controller-transformer-v1", duration)
    result = evaluate(state, observations, ROOT)
    assert result["round"] == 75 and result["decision"] == "iterate"
    assert state["history"][:-1] == old["history"] and state["floors"] == old["floors"]
    result["evidence_transport_note"] = (
        "The Transformer is a materially stronger learned baseline and meets standalone inference feasibility, but both seeds still fail unchanged development gates. Confirmation remains sealed and runtime0.19.5 remains unchanged."
    )
    state["history"][-1] = result
    destination = GP + "01a073fe-c240-70c0-b5cd-fe9653aac60e-transformer-v1.json"
    assert not (ROOT / destination).exists()
    write(destination, state)
    (ROOT / destination).with_suffix(".md").write_text(
        g.markdown(result) + "\n\n" + result["evidence_transport_note"] + "\n", encoding="utf-8"
    )

    checkpoint.update(
        state_path=destination,
        last_evaluated_state=destination,
        contract_hash=state["contract_hash"],
        input_fingerprint=fingerprint,
        round=75,
        remaining_evaluations=25,
        evidence=evidence_path,
        decision="iterate",
        stagnant_rounds=state["stagnant_rounds"],
        next_controller_monotonic_start=time.perf_counter(),
        recorded_at=time.time(),
        current_turn_classification=(
            "Progress: a620k-parameter Transformer with velocity inputs and confidence cuts paired convolutional combined position by1.9-2.2% and derivatives by3.6-5.2%, with65ms cold NumPy inference; both seeds still fail unchanged position/cohort gates."
        ),
        previous_turn_classification=checkpoint["current_turn_classification"],
        active_jobs=[],
        blocked_audit={"consecutive_goal_turns": 0, "condition": None},
        pending_evaluation=False,
        work_accounting="Continuous parent interval from goalpost74 recorded once; subprocess durations are not added.",
        diagnostic_summary=RESULTS + "transformer-sequence-development-v1/report.json",
        transformer_research=evidence["transformer_research"],
    )
    checkpoint["next_safe_actions"] = [
        "Retain the compact Transformer and exact constrained reference; do not spend the next evaluation on another model class.",
        "Prospectively test gap-aware residual allocation and cohort-balanced loss so eight-frame contextual cases can retain the procedural reference while longer gaps learn useful motion.",
        "Expand legally usable curated animation coverage before diffusion or a parity claim; keep source rights and subject separation explicit.",
        "Keep confirmation sealed, runtime unpromoted, contact/physics separate, and the pending independent animator request unchanged.",
    ]
    checkpoint["accounting_note"] = "Formal milestone75/100. Same endpoint, deadline and floors; no active processes."
    write(BASE + "checkpoint-transformer-v1.json", checkpoint)
    print(
        {
            "round": 75,
            "remaining_evaluations": 25,
            "family_passes": False,
            "confirmation_read": False,
            "runtime_promoted": False,
            "full_goal_complete": False,
        }
    )


if __name__ == "__main__":
    main()
