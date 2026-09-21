"""Record formal goalpost 79 for conditioning and future-model cohorts."""
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
    checkpoint = read(BASE + "checkpoint-full-hierarchy-store-v1.json")
    old = read(checkpoint["state_path"])
    state = copy.deepcopy(old)
    previous = checkpoint["evidence"]
    evidence = read(previous)
    assert checkpoint["round"] == 78 and checkpoint["remaining_evaluations"] == 22
    assert checkpoint["max_goalposts"] == 100 and checkpoint["deadline_unix"] == 1789053845
    assert not checkpoint["active_jobs"] and not checkpoint["full_goal_complete"]
    assert not [path for path, digest in evidence["artifacts"].items() if sha(path) != digest]

    conditioning_path = RESULTS + "motion-conditioning-contract-v1/report.json"
    cohort_path = RESULTS + "hierarchy-cohorts-v1/report.json"
    split_path = RESULTS + "hierarchy-cohorts-v1/split.json"
    cohort_contract_path = RESULTS + "hierarchy-cohorts-contract-v1/report.json"
    conditioning = read(conditioning_path)
    cohort = read(cohort_path)
    split = read(split_path)
    cohort_contract = read(cohort_contract_path)
    assert conditioning["complete"] and conditioning["packed_features"] == 483
    assert conditioning["exact_authored_values"] and conditioning["helper_joints_never_authored"]
    assert conditioning["unknown_values_zero_required"] and len(conditioning["invalid_cases"]) == 9
    assert cohort["complete"] and cohort["training_subjects"] == 68
    assert cohort["development_subjects"] == 17 and not cohort["subject_overlap"]
    assert cohort["all_declared_metadata_floors_pass"] and cohort["total_development_windows"] == 1125
    assert cohort_contract["complete"] and cohort_contract["deterministic_reproduction"]
    assert cohort_contract["materialized_windows"] == 1125
    assert cohort_contract["all_windows_use_development_subjects_only"]
    assert cohort_contract["training_subjects_excluded_from_development"]
    assert split["confirmation_subjects_or_clips_included"] is False
    assert set(split["pending_reviewed_tasks"]) == {
        "static", "landing", "contact_quality", "naturalness_and_intent"
    }
    assert not conditioning["validation_read"] and not conditioning["confirmation_read"]
    assert not cohort["confirmation_read"] and not cohort_contract["confirmation_read"]
    assert not conditioning["training_run"] and not cohort["training_run"]
    assert not conditioning["runtime_promoted"] and not cohort["runtime_promoted"]

    inputs = [
        BASE + "MOTION-CONDITIONING-v1.md",
        BASE + "HIERARCHY-COHORTS-v1.md",
        TR + "motion_conditioning_plan_v1.json",
        TR + "motion_conditioning_v1.py",
        TR + "check_motion_conditioning_v1.py",
        TR + "hierarchy_cohort_plan_v1.json",
        TR + "build_hierarchy_cohorts_v1.py",
        TR + "check_hierarchy_cohorts_v1.py",
        TR + "checkpoint_conditioning_cohorts_v1.py",
    ]
    milestone = {
        "id": "full_hierarchy_conditioning_ready",
        "description": (
            "The complete train corpus has a verified root/local 23-joint representation, exact 17-control "
            "semantic projection, explicit contact/scene/intent/provenance conditioning, and a frozen "
            "subject-disjoint future-model development split. This is pre-training readiness, not temporal "
            "model qualification, animator usability, physics acceptance or Cascadeur parity."
        ),
    }
    assert milestone["id"] not in {row["id"] for row in old["contract"]["progress_milestones"]}
    state["contract"]["progress_milestones"].append(milestone)
    added = [path for path in inputs if path not in state["contract"]["inputs"]]
    state["contract"]["inputs"] += added
    state["contract_hash"] = g.digest(state["contract"])
    left, right = copy.deepcopy(state["contract"]), copy.deepcopy(old["contract"])
    left.pop("inputs")
    right.pop("inputs")
    left.pop("progress_milestones")
    right.pop("progress_milestones")
    assert left == right
    assert state["contract"]["progress_milestones"] == old["contract"]["progress_milestones"] + [milestone]
    state["explicit_revisions"].append(
        {
            "reason": (
                "Froze an explicit 483-feature contact/scene/intent/provenance/authored-control contract and "
                "a metadata-stratified 68/17 subject split before training. All 1,125 declared future-model "
                "development windows materialize; static, landing, contact-quality and human-intent evidence "
                "remain explicit pending gates rather than inferred successes."
            ),
            "prior_state": checkpoint["state_path"],
            "prior_sha256": sha(checkpoint["state_path"]),
            "prior_contract_hash": old["contract_hash"],
            "new_contract_hash": state["contract_hash"],
            "added_inputs": added,
            "added_progress_milestone": milestone,
            "recorded_at": time.time(),
        }
    )

    paths = set(evidence["artifacts"]) | set(inputs) | {
        checkpoint["state_path"], previous, BASE + "checkpoint-full-hierarchy-store-v1.json",
        conditioning_path, cohort_path, split_path, cohort_contract_path,
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
        motion_conditioning={
            "packed_features": conditioning["packed_features"],
            "effectors": conditioning["effectors"],
            "scene_probes": conditioning["scene_probes"],
            "actions": conditioning["actions"],
            "styles": conditioning["styles"],
            "provenance": conditioning["provenance"],
            "exact_authored_values": conditioning["exact_authored_values"],
            "helper_joints_never_authored": conditioning["helper_joints_never_authored"],
            "unknown_values_zero_required": conditioning["unknown_values_zero_required"],
            "heuristic_confidence_ceiling": conditioning["heuristic_confidence_ceiling"],
            "metadata_confidence_ceiling": conditioning["metadata_confidence_ceiling"],
            "invalid_cases": conditioning["invalid_cases"],
            "contact_ground_truth_available": False,
            "runtime_promoted": False,
        },
        hierarchy_cohorts={
            "training_subjects": split["training_subjects"],
            "development_subjects": split["development_subjects"],
            "subject_overlap": [],
            "development_subject_coverage": split["development_subject_coverage"],
            "materialized_windows": cohort_contract["materialized_windows"],
            "minimum_windows_per_task_gap": cohort_contract["minimum_windows_per_task_gap"],
            "pending_reviewed_tasks": split["pending_reviewed_tasks"],
            "prior_source_exposure_acknowledged": True,
            "confirmation_read": False,
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
    evidence_path = GP + "conditioning-cohorts-evidence-v1.json"
    write(evidence_path, evidence)

    observations = read(GP + "full-hierarchy-store-observations-v1.json")
    for group in observations.values():
        for row in group.values():
            row.update(artifact=evidence_path, sha256=sha(evidence_path), input_fingerprint=fingerprint)
    observations["milestones"][milestone["id"]] = {
        "artifact": evidence_path,
        "sha256": sha(evidence_path),
        "input_fingerprint": fingerprint,
        "method": "deterministic",
        "passed": True,
    }
    observations_path = GP + "conditioning-cohorts-observations-v1.json"
    write(observations_path, observations)

    duration = time.perf_counter() - checkpoint["next_controller_monotonic_start"]
    assert 0 <= duration < 40000, duration
    g.record_work(state, "controller-conditioning-cohorts-v1", duration)
    result = evaluate(state, observations, ROOT)
    print({
        "evaluation_round": result["round"],
        "evaluation_decision": result["decision"],
        "evaluation_reason": result["reason"],
        "implementation_progress": result["implementation_progress"],
        "state_status": state["status"],
        "stagnant_rounds": state["stagnant_rounds"],
    })
    assert result["round"] == 79 and result["decision"] == "iterate"
    assert state["history"][:-1] == old["history"] and state["floors"] == old["floors"]
    result["evidence_transport_note"] = (
        "Verified pre-training controls: conditioning cannot hide unknown labels or expose helper joints, and the "
        "new model must exclude 17 frozen development subjects. Missing reviewed contacts, landing/static labels "
        "and human evidence remain failed/unknown; confirmation and runtime stay untouched."
    )
    state["history"][-1] = result
    destination = GP + "01a073fe-c240-70c0-b5cd-fe9653aac60e-conditioning-cohorts-v1.json"
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
        round=79,
        remaining_evaluations=21,
        evidence=evidence_path,
        decision="iterate",
        stagnant_rounds=state["stagnant_rounds"],
        next_controller_monotonic_start=time.perf_counter(),
        recorded_at=time.time(),
        current_turn_classification=(
            "Verified progress: explicit conditioning/provenance and a frozen subject-held-out future-development "
            "split now prevent hidden-label leakage, helper-joint authorship and subject overlap before training."
        ),
        previous_turn_classification=checkpoint["current_turn_classification"],
        active_jobs=[],
        blocked_audit={"consecutive_goal_turns": 0, "condition": None},
        pending_evaluation=False,
        work_accounting="Continuous parent interval from goalpost78 recorded once; schema/cohort subprocess durations are not added.",
        diagnostic_summary=cohort_contract_path,
        motion_conditioning=evidence["motion_conditioning"],
        hierarchy_cohorts=evidence["hierarchy_cohorts"],
    )
    checkpoint["next_safe_actions"] = [
        "Freeze train-only static/contact/landing proposal algorithms and build a deterministic representative review queue.",
        "Keep all heuristic contact evidence at confidence0.35 or below until reviewed; measured scene geometry remains distinct.",
        "After review evidence exists, freeze full-hierarchy baselines, model ablations and acceptance gates before training.",
        "Keep confirmation sealed, runtime unpromoted and 17 development subjects excluded from all future fitting.",
        "Retain deterministic authored-control and physics projection around every learned proposal."
    ]
    checkpoint["accounting_note"] = "Formal milestone79/100. Same endpoint, deadline and floors; no active processes."
    write(BASE + "checkpoint-conditioning-cohorts-v1.json", checkpoint)
    print(
        {
            "round": 79,
            "remaining_evaluations": 21,
            "packed_features": conditioning["packed_features"],
            "development_windows": cohort_contract["materialized_windows"],
            "pending_reviewed_tasks": list(split["pending_reviewed_tasks"]),
            "confirmation_read": False,
            "runtime_promoted": False,
            "full_goal_complete": False,
        }
    )


if __name__ == "__main__":
    main()
