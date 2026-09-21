"""Record formal goalpost 70 for jump temporal-envelope research."""
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
SUMMARY_PATH = TRAINING + "results/jump-temporal-envelope-summary-v1.json"


def main():
    checkpoint = read(BASE + "checkpoint-recorded-jump-reference-v1.json")
    old = read(checkpoint["state_path"])
    state = copy.deepcopy(old)
    evidence = read(checkpoint["evidence"])
    assert checkpoint["round"] == 69 and checkpoint["max_goalposts"] == 100
    assert checkpoint["deadline_unix"] == 1789053845 and not checkpoint["active_jobs"]
    assert checkpoint["artifact"]["sha256"] == sha(checkpoint["artifact"]["path"])
    summary = read(SUMMARY_PATH)
    assert summary["complete"] and not summary["full_goal_complete"] and not summary["method_promoted"]
    assert summary["weighted_projection"]["all_variants_spatial_pass"]
    assert summary["weighted_projection"]["selected_to_baseline_ratio"] < 0.75
    assert summary["published_final_spatial_gate_feasible_at_two_boundaries"]
    assert not summary["strict_inner_projection_feasible"] and not summary["confirmation_read"]
    assert all(not (ROOT / TRAINING / "cache" / (name + ".bvh")).exists()
               for name in read(TRAINING + "temporal_expansion_plan_v19.json")["planned_splits"]["confirmation"])

    protected = dict(evidence["artifacts"])
    assert all(sha(path) == digest for path, digest in protected.items())
    inputs = [
        TRAINING + "compare_jump_temporal_envelopes_v1.py",
        TRAINING + "solve_group_weighted_trajectory_v3.py",
        TRAINING + "probe_world_metric_boundary_v1.py",
        TRAINING + "finalize_jump_temporal_envelope_v1.py",
        TRAINING + "checkpoint_jump_temporal_envelope_v1.py",
        BASE + "JUMP-TEMPORAL-ENVELOPE-PLAN-v1.md",
        BASE + "temporal-envelope-routing-v1.json",
    ]
    added = [path for path in inputs if path not in state["contract"]["inputs"]]
    state["contract"]["inputs"] += added
    state["contract_hash"] = g.digest(state["contract"])
    left = copy.deepcopy(state["contract"])
    right = copy.deepcopy(old["contract"])
    left.pop("inputs")
    right.pop("inputs")
    assert left == right
    state["explicit_revisions"].append({
        "reason": "Equal-rate recorded comparison localizes upper-body contact-boundary amplification; balanced weighting improves the diagnostic score by29.5%, and a source-relative world metric restores two boundary speeds inside final spatial gates. No method promoted; endpoint, pins, thresholds, release, limits and sealed split preserved.",
        "prior_state": checkpoint["state_path"],
        "prior_sha256": sha(checkpoint["state_path"]),
        "artifact_revisions": {},
        "added_inputs": added,
        "prior_contract_hash": old["contract_hash"],
        "new_contract_hash": state["contract_hash"],
        "recorded_at": time.time(),
    })

    paths = set(protected) | set(inputs) | {
        checkpoint["state_path"], checkpoint["evidence"],
        BASE + "checkpoint-recorded-jump-reference-v1.json", SUMMARY_PATH,
    }
    for folder in ("jump-temporal-envelope-v1", "group-weighted-trajectory-v3", "world-metric-boundary-v1"):
        paths.update(path.relative_to(ROOT).as_posix()
                     for path in (ROOT / TRAINING / "results" / folder).rglob("*") if path.is_file())
    fingerprint = g.fingerprint(ROOT, state["contract"]["inputs"])
    evidence.update(
        contract_hash=state["contract_hash"],
        input_fingerprint=fingerprint,
        artifacts={path: sha(path) for path in sorted(paths)},
        previous_evidence_recheck={
            "path": checkpoint["evidence"],
            "sha256": sha(checkpoint["evidence"]),
            "all_unrevised_artifacts_unchanged": True,
            "explicit_revisions": {},
        },
        jump_temporal_envelope=summary,
    )
    evidence["qualification"].update(
        temporal_model_qualification=False,
        independent_usability="unknown",
        full_goal_complete=False,
        full_physics_acceptance=False,
    )
    evidence_path = GOALPOSTS + "jump-temporal-envelope-evidence-v1.json"
    write(evidence_path, evidence)

    observations = read(GOALPOSTS + "recorded-jump-reference-observations-v1.json")
    for group in observations.values():
        for row in group.values():
            row.update(artifact=evidence_path, sha256=sha(evidence_path), input_fingerprint=fingerprint)
    observations_path = GOALPOSTS + "jump-temporal-envelope-observations-v1.json"
    write(observations_path, observations)

    wall_duration = time.time() - checkpoint["recorded_at"]
    assert 1800 <= wall_duration < 20000, wall_duration
    g.record_work(state, "controller-jump-temporal-envelope-v1", wall_duration)
    result = evaluate(state, observations, ROOT)
    assert result["round"] == 70 and result["decision"] == "iterate"
    assert state["history"][:-1] == old["history"] and state["floors"] == old["floors"]
    result["evidence_transport_note"] = (
        "The source-relative boundary result is a two-frame solver feasibility observation, not animation-quality "
        "acceptance. It preserves the recorded inner-tolerance miss, the host shutdown fault, and all remaining "
        "learned, physical, usability, rig-family and Cascadeur gaps."
    )
    state["history"][-1] = result
    destination = GOALPOSTS + "01a073fe-c240-70c0-b5cd-fe9653aac60e-jump-temporal-envelope-v1.json"
    assert not (ROOT / destination).exists()
    write(destination, state)
    (ROOT / destination).with_suffix(".md").write_text(
        g.markdown(result) + "\n\n" + result["evidence_transport_note"] + "\n", encoding="utf-8")

    checkpoint.update(
        state_path=destination,
        last_evaluated_state=destination,
        contract_hash=state["contract_hash"],
        input_fingerprint=fingerprint,
        round=70,
        remaining_evaluations=30,
        evidence=evidence_path,
        decision="iterate",
        stagnant_rounds=state["stagnant_rounds"],
        next_controller_monotonic_start=time.perf_counter(),
        recorded_at=time.time(),
        current_turn_classification=(
            "Progress: localized artificial jump spikes to upper-body contact boundaries, improved the full sampled "
            "trajectory metric29.5%, and demonstrated source-relative boundary speed recovery inside final spatial gates."
        ),
        previous_turn_classification=checkpoint["current_turn_classification"],
        active_jobs=[],
        blocked_audit={"consecutive_goal_turns": 0, "condition": None},
        pending_evaluation=False,
        work_accounting="Continuous parent interval from goalpost69 recorded once; host subprocess durations are not added.",
        diagnostic_summary=SUMMARY_PATH,
        jump_temporal_envelope={
            "material_exceedances": len(summary["material_exceedances"]),
            "selected_weighting": summary["weighted_projection"]["selected"],
            "selected_to_baseline_ratio": summary["weighted_projection"]["selected_to_baseline_ratio"],
            "strict_inner_projection_feasible": False,
            "final_spatial_gate_feasible_at_two_boundaries": True,
            "method_promoted": False,
        },
    )
    checkpoint["next_safe_actions"] = [
        "Implement a bounded boundary-window SQP with source-relative upper-body world-orientation residuals, explicit endpoint/pin anchors and unchanged final COM/contact/orientation gates.",
        "Measure speed and acceleration over the full reconstructed trajectory; reject any method that merely moves the boundary spike or exceeds final spatial gates.",
        "Retain the artificial request as a stress case and the recorded clip as calibration. Never silently change authored pins/timing to match the single reference actor.",
        "Full learned posing/motion, physical refinement, animator usability, quadrupeds and the optional connector remain required by the unchanged endpoint.",
        "Preserve goal ID, 100-evaluation ceiling, deadline 1789053845, experimental release 0.19.2 and publication identity/approval rules.",
    ]
    checkpoint["accounting_note"] = "Formal milestone70/100. Same endpoint, deadline and floors; no active processes."
    checkpoint_path = BASE + "checkpoint-jump-temporal-envelope-v1.json"
    write(checkpoint_path, checkpoint)
    print({
        "round": 70,
        "remaining_evaluations": 30,
        "protected_artifacts": len(paths),
        "active_parent_seconds": wall_duration,
        "full_goal_complete": False,
        "method_promoted": False,
    })


if __name__ == "__main__":
    main()
