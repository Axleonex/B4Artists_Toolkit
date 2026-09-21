"""Record formal goalpost 74 for expanded-data constrained sequence research."""
import copy
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from checkpoint_expanded_goal_v19 import ROOT, read, write, sha, g
from evaluate_milestone_goal_v2 import evaluate


BASE = "docs/b4artists_ml/"
GOALPOSTS = BASE + "goalposts/"
TRAINING = "training/b4artists_ml/"
RESULTS = TRAINING + "results/"


def main():
    checkpoint = read(BASE + "checkpoint-vectorized-tangent-v1.json")
    old = read(checkpoint["state_path"])
    state = copy.deepcopy(old)
    previous_evidence = checkpoint["evidence"]
    evidence = read(previous_evidence)
    assert checkpoint["round"] == 73 and checkpoint["remaining_evaluations"] == 27
    assert checkpoint["max_goalposts"] == 100 and checkpoint["deadline_unix"] == 1789053845
    assert not checkpoint["active_jobs"] and not checkpoint["full_goal_complete"]
    changed = [path for path, digest in evidence["artifacts"].items() if sha(path) != digest]
    assert not changed, changed

    training = read(RESULTS + "expanded-constrained-sequence-training-v1/processes.json")
    report = read(RESULTS + "expanded-constrained-sequence-development-v1/report.json")
    plan = read(TRAINING + "expanded_constrained_sequence_evaluation_plan_v1.json")
    assert len(training) == 2 and all(row["exit_code"] == 0 for row in training)
    assert report["complete"] and not report["family_passes"]
    assert report["protected_baselines_match"] and not report["confirmation_read"]
    assert report["plan_sha256"] == sha(TRAINING + "expanded_constrained_sequence_evaluation_plan_v1.json")
    assert len(report["models"]) == 2 and all(
        not report["development_gates"][model["name"]][partition]["passed"]
        for model in report["models"]
        for partition in plan["partitions"]
    )

    inputs = [
        BASE + "ARCHITECTURE-REASSESSMENT-v1.md",
        BASE + "ARCHITECTURE-DECISION-v2.md",
        BASE + "sequence-shape-residual-routing-v1.json",
        TRAINING + "sequence_shape_conditioning_v1.py",
        TRAINING + "sequence_shape_residual_provider_v1.py",
        TRAINING + "train_sequence_shape_residual_v1.py",
        TRAINING + "sequence_shape_residual_fit_plan_v1.json",
        TRAINING + "sequence_shape_ablation_v1.py",
        TRAINING + "evaluate_sequence_shape_residual_v1.py",
        TRAINING + "sequence_shape_residual_evaluation_plan_v1.json",
        TRAINING + "inventory_cmu_corpus_v1.py",
        TRAINING + "acquire_cmu_train_v1.py",
        TRAINING + "cmu_train_acquisition_plan_v1.json",
        TRAINING + "build_cmu_sequence_store_v1.py",
        TRAINING + "cmu_sequence_store_plan_v2.json",
        TRAINING + "build_rotation_matrix_store_v1.py",
        TRAINING + "rotation_matrix_store_plan_v1.json",
        TRAINING + "sequence_store_v1.py",
        TRAINING + "check_sequence_store_v1.py",
        TRAINING + "sequence_constrained_reference_v1.py",
        TRAINING + "check_sequence_constrained_reference_v1.py",
        TRAINING + "train_expanded_constrained_sequence_v1.py",
        TRAINING + "expanded_constrained_sequence_fit_plan_v1.json",
        TRAINING + "sequence_constrained_residual_provider_v1.py",
        TRAINING + "evaluate_expanded_constrained_sequence_v1.py",
        TRAINING + "expanded_constrained_sequence_evaluation_plan_v1.json",
        TRAINING + "checkpoint_expanded_c2_v1.py",
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
                "Expanded the train-only corpus from17.1minutes to7.16hours/1,840clips/85subjects, added a memory-mapped store and exact C2-constrained residual reference, then froze and evaluated two seeds. Both seeds improve new-validation position slightly but regress old/combined position, derivatives and short-gap cohorts, so no runtime promotion or confirmation read occurred. The evidence redirects the primary learned candidate to a data-centered Transformer while preserving the original endpoint and gates."
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
        checkpoint["state_path"],
        previous_evidence,
        BASE + "checkpoint-vectorized-tangent-v1.json",
    }
    result_folders = (
        "sequence-shape-conditioning-v4",
        "sequence-shape-residual-training-v1",
        "sequence-shape-residual-development-v1",
        "cmu-corpus-inventory-v1",
        "cmu-sequence-store-v2",
        "rotation-matrix-store-v1",
        "sequence-store-contract-v3",
        "sequence-constrained-reference-v1",
        "expanded-constrained-sequence-training-v1",
        "expanded-constrained-sequence-development-v1",
    )
    for folder in result_folders:
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
                "shape_reference_position_ratio": report["shape_reference_attribution"][name][partition]["ratios"]["position"],
            }
            for partition in plan["partitions"]
        }
    evidence.update(
        contract_hash=state["contract_hash"],
        input_fingerprint=fingerprint,
        artifacts={path: sha(path) for path in sorted(paths)},
        previous_evidence_recheck={
            "path": previous_evidence,
            "sha256": sha(previous_evidence),
            "changed_artifacts": [],
            "all_prior_artifacts_unchanged": True,
        },
        expanded_learned_research={
            "train_clips": 1840,
            "train_subjects": 85,
            "train_hours": 7.15874219825,
            "training_examples_per_seed": 48000,
            "models": models,
            "development_report": RESULTS + "expanded-constrained-sequence-development-v1/report.json",
            "development_report_sha256": sha(RESULTS + "expanded-constrained-sequence-development-v1/report.json"),
            "confirmation_read": False,
            "runtime_promoted": False,
            "next_model_class": "compact keyframe-conditioned Transformer with velocity inputs",
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
    evidence_path = GOALPOSTS + "expanded-c2-evidence-v1.json"
    write(evidence_path, evidence)

    observations = read(GOALPOSTS + "vectorized-tangent-observations-v1.json")
    for group in observations.values():
        for row in group.values():
            row.update(artifact=evidence_path, sha256=sha(evidence_path), input_fingerprint=fingerprint)
    observations_path = GOALPOSTS + "expanded-c2-observations-v1.json"
    write(observations_path, observations)

    duration = time.perf_counter() - checkpoint["next_controller_monotonic_start"]
    assert 0 <= duration < 40000, duration
    g.record_work(state, "controller-expanded-c2-v1", duration)
    result = evaluate(state, observations, ROOT)
    assert result["round"] == 74 and result["decision"] == "iterate"
    assert state["history"][:-1] == old["history"] and state["floors"] == old["floors"]
    result["evidence_transport_note"] = (
        "The larger subject-disjoint corpus and C2-constrained residual materially narrow the learned gap, but both fixed seeds fail unchanged development gates. Confirmation remains sealed and runtime0.19.5 remains unchanged."
    )
    state["history"][-1] = result
    destination = GOALPOSTS + "01a073fe-c240-70c0-b5cd-fe9653aac60e-expanded-c2-v1.json"
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
        round=74,
        remaining_evaluations=26,
        evidence=evidence_path,
        decision="iterate",
        stagnant_rounds=state["stagnant_rounds"],
        next_controller_monotonic_start=time.perf_counter(),
        recorded_at=time.time(),
        current_turn_classification=(
            "Progress: expanded subject-disjoint training from17.1minutes to7.16hours and added an exact constrained residual path; both seeds narrowed the gap but failed unchanged old/new/combined development gates, so no promotion."
        ),
        previous_turn_classification=checkpoint["current_turn_classification"],
        active_jobs=[],
        blocked_audit={"consecutive_goal_turns": 0, "condition": None},
        pending_evaluation=False,
        work_accounting="Continuous parent interval from goalpost73 recorded once; subprocess durations are not added.",
        diagnostic_summary=RESULTS + "expanded-constrained-sequence-development-v1/report.json",
        expanded_learned_research=evidence["expanded_learned_research"],
    )
    checkpoint["next_safe_actions"] = [
        "Implement one compact keyframe-conditioned Transformer comparison with explicit velocity inputs over the same memory-mapped corpus and unchanged gates.",
        "Add residual confidence or shrinkage so easy short-gap contextual requests can retain the procedural reference.",
        "Do not open confirmation data or promote a learned runtime unless both fixed seeds pass every development partition.",
        "Preserve the separate contact/physics stages, independent animator request, quadruped deferral, optional Cascadeur connector and original full endpoint.",
    ]
    checkpoint["accounting_note"] = "Formal milestone74/100. Same endpoint, deadline and floors; no active processes."
    checkpoint_path = BASE + "checkpoint-expanded-c2-v1.json"
    write(checkpoint_path, checkpoint)
    print(
        {
            "round": 74,
            "remaining_evaluations": 26,
            "train_hours": 7.15874219825,
            "fixed_seeds": 2,
            "family_passes": False,
            "confirmation_read": False,
            "runtime_promoted": False,
            "full_goal_complete": False,
        }
    )


if __name__ == "__main__":
    main()
