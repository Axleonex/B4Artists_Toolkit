"""Record formal goalpost 77 for the train-only data/representation decision."""
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
    checkpoint = read(BASE + "checkpoint-mixture-transformer-v1.json")
    old = read(checkpoint["state_path"])
    state = copy.deepcopy(old)
    previous = checkpoint["evidence"]
    evidence = read(previous)
    assert checkpoint["round"] == 76 and checkpoint["remaining_evaluations"] == 24
    assert checkpoint["max_goalposts"] == 100 and checkpoint["deadline_unix"] == 1789053845
    assert not checkpoint["active_jobs"] and not checkpoint["full_goal_complete"]
    assert not [path for path, digest in evidence["artifacts"].items() if sha(path) != digest]

    plan_path = TR + "data_representation_audit_plan_v1.json"
    script_path = TR + "audit_data_representation_v2.py"
    report_path = RESULTS + "data-representation-audit-v1/report.json"
    decision_path = BASE + "DATA-REPRESENTATION-DECISION-v1.md"
    report = read(report_path)
    assert report["complete"] and report["clips"] == 1840 and report["subjects"] == 85
    assert report["source_hours"] == 7.15874219825
    assert report["sources"]["script"] == sha(script_path)
    assert report["sources"]["plan"] == sha(plan_path)
    assert report["full_hierarchy"]["full_hierarchy_reconstructs_semantics"]
    assert report["full_hierarchy"]["subjects_checked"] == 85
    assert not report["full_hierarchy"]["failures"]
    assert not report["contact_pseudo_label"]["ground_truth"]
    assert not report["contact_pseudo_label"]["suitable_as_unreviewed_hard_constraint"]
    assert not report["validation_read"] and not report["confirmation_read"]
    assert not report["downloads"] and not report["training_run"] and not report["runtime_promoted"]

    inputs = [decision_path, plan_path, script_path, TR + "checkpoint_data_representation_v1.py"]
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
                "Replaced nearby model retuning with a frozen train-only data and representation audit. "
                "The complete 23-joint local hierarchy reconstructs the 17 semantic controls and true edges "
                "to numerical precision across all 85 train subjects, while corpus metadata and threshold "
                "sensitivity show that explicit landing, contact, scene and intent/style evidence remains weak."
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
        checkpoint["state_path"], previous, BASE + "checkpoint-mixture-transformer-v1.json", report_path
    }
    fingerprint = g.fingerprint(ROOT, state["contract"]["inputs"])
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
        data_representation_decision={
            "source_hours": report["source_hours"],
            "clips": report["clips"],
            "subjects": report["subjects"],
            "unclassified_or_other_only_clips": report["other_only_or_unclassified_clips"],
            "explicit_landing_label_clips": report["metadata_coverage"]["explicit_landing_label"]["clips"],
            "contact_fraction_primary": report["contact_pseudo_label"]["contact_fraction"],
            "contact_fraction_sensitivity": [
                row["contact_fraction"] for row in report["contact_pseudo_label"]["sensitivity"]
            ],
            "contact_ground_truth": False,
            "hierarchy_subjects_checked": report["full_hierarchy"]["subjects_checked"],
            "hierarchy_unique_topologies": report["full_hierarchy"]["unique_topologies"],
            "max_semantic_position_reconstruction_error": report["full_hierarchy"]["maximum_semantic_position_reconstruction_error"],
            "max_semantic_rotation6_reconstruction_error": report["full_hierarchy"]["maximum_semantic_rotation6_reconstruction_error"],
            "max_true_edge_length_error": report["full_hierarchy"]["maximum_true_edge_length_error"],
            "decision": (
                "Use the full ancestor-local hierarchy as the next generative state and retain the 17 semantic "
                "joints as animator constraints/evaluation. Add explicit contact, support/scene and intent/style "
                "evidence before another learned fit; deterministic projection owns hard constraints."
            ),
            "validation_read": False,
            "confirmation_read": False,
            "downloads": [],
            "training_run": False,
            "runtime_promoted": False,
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
    evidence_path = GP + "data-representation-evidence-v1.json"
    write(evidence_path, evidence)

    observations = read(GP + "mixture-transformer-observations-v1.json")
    for group in observations.values():
        for row in group.values():
            row.update(artifact=evidence_path, sha256=sha(evidence_path), input_fingerprint=fingerprint)
    observations_path = GP + "data-representation-observations-v1.json"
    write(observations_path, observations)

    duration = time.perf_counter() - checkpoint["next_controller_monotonic_start"]
    assert 0 <= duration < 40000, duration
    g.record_work(state, "controller-data-representation-v1", duration)
    result = evaluate(state, observations, ROOT)
    assert result["round"] == 77 and result["decision"] == "iterate"
    assert state["history"][:-1] == old["history"] and state["floors"] == old["floors"]
    result["evidence_transport_note"] = (
        "Verified architectural progress, not learned-quality qualification: train-only evidence supports the "
        "full local hierarchy and rejects weak contact heuristics as ground truth. Runtime0.19.5 remains unchanged, "
        "confirmation remains sealed, and parity remains unverified."
    )
    state["history"][-1] = result
    destination = GP + "01a073fe-c240-70c0-b5cd-fe9653aac60e-data-representation-v1.json"
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
        round=77,
        remaining_evaluations=23,
        evidence=evidence_path,
        decision="iterate",
        stagnant_rounds=state["stagnant_rounds"],
        next_controller_monotonic_start=time.perf_counter(),
        recorded_at=time.time(),
        current_turn_classification=(
            "Verified progress: the frozen train-only audit proves exact full-hierarchy reconstruction across "
            "85 subjects and exposes contact/intent/style data gaps, establishing a defensible next representation."
        ),
        previous_turn_classification=checkpoint["current_turn_classification"],
        active_jobs=[],
        blocked_audit={"consecutive_goal_turns": 0, "condition": None},
        pending_evaluation=False,
        work_accounting="Continuous parent interval from goalpost76 recorded once; audit subprocess duration is not added.",
        diagnostic_summary=report_path,
        data_representation_decision=evidence["data_representation_decision"],
    )
    checkpoint["next_safe_actions"] = [
        "Build a versioned full-hierarchy train store with root/local state, velocities, offsets, proportions, masks and exact semantic reconstruction contracts.",
        "Define calibrated contact, scene/support, intent and style schemas before fitting another learned model.",
        "Freeze task/cohort gates and model ablations before training; keep confirmation sealed and runtime unpromoted.",
        "Retain deterministic authored-control, contact, collision, balance, gravity and momentum projection around every learned proposal.",
        "Collect representative original-rig and independent animator/Cascadeur evidence before any parity claim."
    ]
    checkpoint["accounting_note"] = "Formal milestone77/100. Same endpoint, deadline and floors; no active processes."
    write(BASE + "checkpoint-data-representation-v1.json", checkpoint)
    print(
        {
            "round": 77,
            "remaining_evaluations": 23,
            "hierarchy_subjects": report["full_hierarchy"]["subjects_checked"],
            "contact_ground_truth": False,
            "confirmation_read": False,
            "runtime_promoted": False,
            "full_goal_complete": False,
        }
    )


if __name__ == "__main__":
    main()
