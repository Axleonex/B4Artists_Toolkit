"""Preserve conditioning/cohort progress while signed goal assessment is unavailable."""
import copy
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parent))
from checkpoint_expanded_goal_v19 import ROOT, read, write, sha, g


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

    paths_by_name = {
        "conditioning": RESULTS + "motion-conditioning-contract-v1/report.json",
        "cohort": RESULTS + "hierarchy-cohorts-v1/report.json",
        "split": RESULTS + "hierarchy-cohorts-v1/split.json",
        "cohort_contract": RESULTS + "hierarchy-cohorts-contract-v1/report.json",
    }
    conditioning, cohort, split, cohort_contract = [read(path) for path in paths_by_name.values()]
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
    assert not any(row["confirmation_read"] for row in (conditioning, cohort, cohort_contract))
    assert not any(row["training_run"] for row in (conditioning, cohort, cohort_contract))

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
    inputs = [
        BASE + "MOTION-CONDITIONING-v1.md",
        BASE + "HIERARCHY-COHORTS-v1.md",
        TR + "motion_conditioning_plan_v1.json",
        TR + "motion_conditioning_v1.py",
        TR + "check_motion_conditioning_v1.py",
        TR + "hierarchy_cohort_plan_v1.json",
        TR + "build_hierarchy_cohorts_v1.py",
        TR + "check_hierarchy_cohorts_v1.py",
        TR + "checkpoint_conditioning_cohorts_pending_v1.py",
    ]
    added = [path for path in inputs if path not in state["contract"]["inputs"]]
    state["contract"]["inputs"] += added
    state["contract_hash"] = g.digest(state["contract"])
    left, right = copy.deepcopy(state["contract"]), copy.deepcopy(old["contract"])
    for value in (left, right):
        value.pop("inputs")
        value.pop("progress_milestones")
    assert left == right
    state["explicit_revisions"].append(
        {
            "reason": (
                "Froze explicit conditioning/provenance and a 68/17 subject split before training. "
                "Formal goalpost79 remains pending because the canonical evaluator requires an existing-host "
                "signed goal-assessment receipt and its owner is unavailable; no receipt is forged."
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

    issue_path = RESULTS + "conditioning-cohorts-goalpost-attempt-v1/receipt.json"
    (ROOT / issue_path).parent.mkdir(exist_ok=False)
    write(
        issue_path,
        {
            "complete": False,
            "attempted_round": 79,
            "canonical_decision": "checkpoint",
            "canonical_reason": "no measurable progress; endpoint may be infeasible",
            "assessment_owner_available": False,
            "proof_result": "unknown",
            "implementation_evidence_validated_locally": True,
            "last_accepted_round_preserved": 78,
            "history_or_floors_changed": False,
            "classification": "DEGRADED_NATIVE_CONTINUE",
            "note": "The proof path requires a host Controller and receipt-signing.key. Neither is created or bypassed here."
        },
    )
    fingerprint = g.fingerprint(ROOT, state["contract"]["inputs"])
    artifact_paths = set(evidence["artifacts"]) | set(inputs) | set(paths_by_name.values()) | {
        checkpoint["state_path"], previous, BASE + "checkpoint-full-hierarchy-store-v1.json", issue_path
    }
    evidence.update(
        contract_hash=state["contract_hash"],
        input_fingerprint=fingerprint,
        artifacts={path: sha(path) for path in sorted(artifact_paths)},
        previous_evidence_recheck={
            "path": previous,
            "sha256": sha(previous),
            "changed_artifacts": [],
            "all_prior_artifacts_unchanged": True,
        },
        preserved_milestones=old["passed_progress_milestones"],
        new_passing_milestones=[milestone["id"]],
        motion_conditioning={
            "packed_features": 483,
            "provenance": conditioning["provenance"],
            "exact_authored_values": True,
            "helper_joints_never_authored": True,
            "unknown_values_zero_required": True,
            "contact_ground_truth_available": False,
            "runtime_promoted": False,
        },
        hierarchy_cohorts={
            "training_subjects": split["training_subjects"],
            "development_subjects": split["development_subjects"],
            "subject_overlap": [],
            "development_subject_coverage": split["development_subject_coverage"],
            "materialized_windows": 1125,
            "pending_reviewed_tasks": split["pending_reviewed_tasks"],
            "prior_source_exposure_acknowledged": True,
            "confirmation_read": False,
            "training_run": False,
            "runtime_promoted": False,
            "full_goal_complete": False,
        },
        goalpost79={
            "pending": True,
            "issue": issue_path,
            "signed_assessment_receipt": False,
            "last_accepted_round": 78,
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
    write(GP + "conditioning-cohorts-observations-v1.json", observations)

    duration = time.perf_counter() - checkpoint["next_controller_monotonic_start"]
    assert 0 <= duration < 40000, duration
    g.record_work(state, "controller-conditioning-cohorts-v1", duration)
    state["pending_evaluation"] = (
        "Formal goalpost79 requires a host-owned signed goal-assessment.v1 receipt; owner unavailable. "
        "Round78 history/floors preserved and attempt79 not counted."
    )
    assert state["history"] == old["history"] and state["floors"] == old["floors"]
    assert state["passed_checks"] == old["passed_checks"]
    assert state["passed_progress_milestones"] == old["passed_progress_milestones"]
    destination = GP + "01a073fe-c240-70c0-b5cd-fe9653aac60e-conditioning-cohorts-pending-v1.json"
    assert not (ROOT / destination).exists()
    write(destination, state)

    checkpoint.update(
        state_path=destination,
        contract_hash=state["contract_hash"],
        input_fingerprint=fingerprint,
        round=78,
        attempted_round=79,
        remaining_evaluations=22,
        evidence=evidence_path,
        decision="DEGRADED_NATIVE_CONTINUE",
        stagnant_rounds=old["stagnant_rounds"],
        next_controller_monotonic_start=time.perf_counter(),
        recorded_at=time.time(),
        current_turn_classification=(
            "Verified local progress: conditioning and 1,125 subject-disjoint cohort windows pass. "
            "Formal goalpost79 is pending because the required signed assessment owner is unavailable."
        ),
        previous_turn_classification=checkpoint["current_turn_classification"],
        active_jobs=[],
        blocked_audit={"consecutive_goal_turns": 0, "condition": None},
        pending_evaluation=True,
        evaluation_infrastructure_issue=issue_path,
        work_accounting="Continuous parent interval from accepted goalpost78 recorded once in pending state; attempt79 not counted.",
        diagnostic_summary=paths_by_name["cohort_contract"],
        motion_conditioning=evidence["motion_conditioning"],
        hierarchy_cohorts=evidence["hierarchy_cohorts"],
    )
    checkpoint["next_safe_actions"] = [
        "Continue authorized local work; do not forge or bypass the missing signed assessment receipt.",
        "Freeze train-only static/contact/landing proposal algorithms and a deterministic representative review queue.",
        "Keep heuristic contact confidence at0.35 or below and distinguish measured scene geometry.",
        "Keep confirmation sealed, runtime unpromoted and17development subjects excluded from future fitting.",
        "Reassess the supported signed evaluator before counting attempted goalpost79."
    ]
    checkpoint["accounting_note"] = "Accepted milestone78/100; attempted79 pending. Same endpoint, deadline and floors; no active processes."
    write(BASE + "checkpoint-conditioning-cohorts-pending-v1.json", checkpoint)
    print(
        {
            "round": 78,
            "attempted_round": 79,
            "pending_evaluation": True,
            "remaining_evaluations": 22,
            "development_windows": 1125,
            "confirmation_read": False,
            "runtime_promoted": False,
            "full_goal_complete": False,
        }
    )


if __name__ == "__main__":
    main()
