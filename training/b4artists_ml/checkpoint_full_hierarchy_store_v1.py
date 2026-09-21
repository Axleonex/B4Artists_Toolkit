"""Record formal goalpost 78 for the full-hierarchy train store."""
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
    checkpoint = read(BASE + "checkpoint-data-representation-v1.json")
    old = read(checkpoint["state_path"])
    state = copy.deepcopy(old)
    previous = checkpoint["evidence"]
    evidence = read(previous)
    assert checkpoint["round"] == 77 and checkpoint["remaining_evaluations"] == 23
    assert checkpoint["max_goalposts"] == 100 and checkpoint["deadline_unix"] == 1789053845
    assert not checkpoint["active_jobs"] and not checkpoint["full_goal_complete"]
    assert not [path for path, digest in evidence["artifacts"].items() if sha(path) != digest]

    store_report_path = RESULTS + "full-hierarchy-store-v1/report.json"
    store_layout_path = RESULTS + "full-hierarchy-store-v1/layout.json"
    contract_report_path = RESULTS + "full-hierarchy-store-contract-v1/report.json"
    store_report = read(store_report_path)
    contract_report = read(contract_report_path)
    assert store_report["complete"] and store_report["clips"] == 1840
    assert store_report["subjects"] == 85 and store_report["frames"] == 773836
    assert store_report["joints"] == 23 and store_report["full_hierarchy_reconstructs_semantics"]
    assert store_report["sign_continuous_quaternions"]
    assert store_report["store_bytes"] <= 310000000
    assert store_report["plan_sha256"] == sha(TR + "full_hierarchy_store_plan_v1.json")
    assert store_report["script_sha256"] == sha(TR + "build_full_hierarchy_store_v1.py")
    assert store_report["layout_sha256"] == sha(store_layout_path)
    assert contract_report["complete"] and contract_report["representative_subject_windows"] == 85
    assert contract_report["helper_joints_never_authored"] and contract_report["invalid_cases"] == 6
    assert contract_report["sources"]["module"] == sha(TR + "full_hierarchy_store_v1.py")
    assert not store_report["validation_read"] and not store_report["confirmation_read"]
    assert not store_report["downloads"] and not store_report["training_run"]
    assert not store_report["runtime_promoted"]

    inputs = [
        BASE + "FULL-HIERARCHY-STORE-v1.md",
        TR + "full_hierarchy_store_plan_v1.json",
        TR + "build_full_hierarchy_store_v1.py",
        TR + "full_hierarchy_store_v1.py",
        TR + "check_full_hierarchy_store_v1.py",
        TR + "checkpoint_full_hierarchy_store_v1.py",
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
                "Built the versioned train-only full-hierarchy store after its representation decision. "
                "All 773,836 frames preserve semantic poses and true edges through stored float32 root/local "
                "state; representative windows from every training subject verify normalization, velocities, "
                "semantic-only authored masks and invariances."
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
        previous,
        BASE + "checkpoint-data-representation-v1.json",
        store_report_path,
        store_layout_path,
        RESULTS + "full-hierarchy-store-v1/progress.json",
        contract_report_path,
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
        full_hierarchy_store={
            "clips": store_report["clips"],
            "subjects": store_report["subjects"],
            "frames": store_report["frames"],
            "joints": store_report["joints"],
            "source_hours": store_report["source_hours"],
            "store_bytes": store_report["store_bytes"],
            "store_files": store_report["files"],
            "maximum_semantic_position_error": store_report["maximum_stored_semantic_position_error"],
            "maximum_semantic_rotation_error": store_report["maximum_stored_semantic_rotation_matrix_error"],
            "maximum_true_edge_error": store_report["maximum_stored_true_edge_error"],
            "minimum_adjacent_quaternion_dot": store_report["minimum_adjacent_quaternion_dot"],
            "representative_subject_windows": contract_report["representative_subject_windows"],
            "maximum_window_position_error": contract_report["maximum_semantic_position_roundtrip_error"],
            "maximum_window_rotation_error": contract_report["maximum_semantic_rotation_roundtrip_error"],
            "helper_joints_never_authored": contract_report["helper_joints_never_authored"],
            "velocities_derived": contract_report["velocities_derived"],
            "memory_mapped": contract_report["memory_mapped"],
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
    evidence_path = GP + "full-hierarchy-store-evidence-v1.json"
    write(evidence_path, evidence)

    observations = read(GP + "data-representation-observations-v1.json")
    for group in observations.values():
        for row in group.values():
            row.update(artifact=evidence_path, sha256=sha(evidence_path), input_fingerprint=fingerprint)
    observations_path = GP + "full-hierarchy-store-observations-v1.json"
    write(observations_path, observations)

    duration = time.perf_counter() - checkpoint["next_controller_monotonic_start"]
    assert 0 <= duration < 40000, duration
    g.record_work(state, "controller-full-hierarchy-store-v1", duration)
    result = evaluate(state, observations, ROOT)
    assert result["round"] == 78 and result["decision"] == "iterate"
    assert state["history"][:-1] == old["history"] and state["floors"] == old["floors"]
    result["evidence_transport_note"] = (
        "Verified research infrastructure: the complete train corpus now has a memory-mapped local hierarchy "
        "with exact semantic reconstruction and sparse-control contracts. This does not qualify a learned model, "
        "contacts, runtime behavior, animator usability or Cascadeur parity."
    )
    state["history"][-1] = result
    destination = GP + "01a073fe-c240-70c0-b5cd-fe9653aac60e-full-hierarchy-store-v1.json"
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
        round=78,
        remaining_evaluations=22,
        evidence=evidence_path,
        decision="iterate",
        stagnant_rounds=state["stagnant_rounds"],
        next_controller_monotonic_start=time.perf_counter(),
        recorded_at=time.time(),
        current_turn_classification=(
            "Verified progress: a checksum-pinned, memory-mapped 23-joint local hierarchy now covers every "
            "train clip/frame and passes semantic reconstruction, invariant velocity and authored-mask contracts."
        ),
        previous_turn_classification=checkpoint["current_turn_classification"],
        active_jobs=[],
        blocked_audit={"consecutive_goal_turns": 0, "condition": None},
        pending_evaluation=False,
        work_accounting="Continuous parent interval from goalpost77 recorded once; build/check subprocess durations are not added.",
        diagnostic_summary=contract_report_path,
        full_hierarchy_store=evidence["full_hierarchy_store"],
    )
    checkpoint["next_safe_actions"] = [
        "Freeze a contact/support/scene and motion-intent schema with confidence and provenance fields.",
        "Create subject-held-out task cohorts and sparse-control patterns before any new model fit.",
        "Calibrate contact proposals on a reviewed representative subset; do not use threshold pseudo-labels as ground truth.",
        "Keep confirmation sealed, runtime unpromoted and the nearby world-space model hard stop active.",
        "Retain deterministic authored-control and physics projection around all future learned proposals."
    ]
    checkpoint["accounting_note"] = "Formal milestone78/100. Same endpoint, deadline and floors; no active processes."
    write(BASE + "checkpoint-full-hierarchy-store-v1.json", checkpoint)
    print(
        {
            "round": 78,
            "remaining_evaluations": 22,
            "frames": store_report["frames"],
            "subject_windows": contract_report["representative_subject_windows"],
            "confirmation_read": False,
            "runtime_promoted": False,
            "full_goal_complete": False,
        }
    )


if __name__ == "__main__":
    main()
