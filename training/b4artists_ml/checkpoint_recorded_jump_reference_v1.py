"""Record formal goalpost 69 for the recorded human jump reference."""
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
RESULTS = TRAINING + "results/recorded-jump-reference-v1/"


def main():
    checkpoint = read(BASE + "checkpoint-coupled-trajectory-v2.json")
    old = read(checkpoint["state_path"])
    state = copy.deepcopy(old)
    evidence = read(checkpoint["evidence"])
    assert checkpoint["round"] == 68
    assert checkpoint["max_goalposts"] == 100
    assert checkpoint["deadline_unix"] == 1789053845
    assert not checkpoint["active_jobs"] and not checkpoint["full_goal_complete"]
    assert checkpoint["artifact"]["sha256"] == sha(checkpoint["artifact"]["path"])

    summary = read(RESULTS + "summary.json")
    analysis = read(RESULTS + "analysis.json")
    host = read(RESULTS + "scene-host-report.json")
    wrapper = read(RESULTS + "scene-wrapper-report.json")
    assert summary["complete"] and not summary["full_goal_complete"] and not summary["method_promoted"]
    assert summary["recorded_jumps"] == 3 and summary["phase_markers"] == 15
    assert analysis["complete"] and host["complete"] and host["saved"] and wrapper["complete"]
    assert host["blend_sha256"] == sha(RESULTS + "recorded-jump-reference-v1.blend")
    assert wrapper["production_sources_unchanged"] and summary["production_sources_unchanged"]
    assert all(not (ROOT / TRAINING / "cache" / (name + ".bvh")).exists()
               for name in read(TRAINING + "temporal_expansion_plan_v19.json")["planned_splits"]["confirmation"])
    assert not any(item["confirmation_read"] for item in (summary, analysis, host, wrapper))

    protected = dict(evidence["artifacts"])
    assert all(sha(path) == digest for path, digest in protected.items())
    inputs = [
        TRAINING + "analyze_recorded_jump_v1.py",
        TRAINING + "build_recorded_jump_scene_v1.py",
        TRAINING + "finalize_recorded_jump_reference_v1.py",
        TRAINING + "checkpoint_recorded_jump_reference_v1.py",
        BASE + "RECORDED-JUMP-REFERENCE-v1.md",
        BASE + "recorded-jump-routing-v1.json",
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
        "reason": "A licensed exposed validation clip now supplies three recorded jump references, phase markers, group-sensitive motion bounds and a parser-validated Bforartists scene. Production, release, sealed confirmation, floors, limits and full endpoint remain unchanged.",
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
        BASE + "checkpoint-coupled-trajectory-v2.json",
    }
    paths.update(path.relative_to(ROOT).as_posix()
                 for path in (ROOT / RESULTS).rglob("*") if path.is_file())
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
        recorded_jump_reference=summary,
    )
    evidence["qualification"].update(
        temporal_model_qualification=False,
        independent_usability="unknown",
        full_goal_complete=False,
        full_physics_acceptance=False,
    )
    evidence_path = GOALPOSTS + "recorded-jump-reference-evidence-v1.json"
    write(evidence_path, evidence)

    observations = read(GOALPOSTS + "coupled-trajectory-observations-v2.json")
    for group in observations.values():
        for row in group.values():
            row.update(artifact=evidence_path, sha256=sha(evidence_path), input_fingerprint=fingerprint)
    observations_path = GOALPOSTS + "recorded-jump-reference-observations-v1.json"
    write(observations_path, observations)

    wall_duration = time.time() - checkpoint["recorded_at"]
    assert 1800 <= wall_duration < 20000, wall_duration
    g.record_work(state, "controller-recorded-jump-reference-v1", wall_duration)
    result = evaluate(state, observations, ROOT)
    assert result["round"] == 69 and result["decision"] == "iterate"
    assert state["history"][:-1] == old["history"] and state["floors"] == old["floors"]
    result["evidence_transport_note"] = (
        "Recorded actor motion improves calibration evidence but does not replace independent animator assessment, "
        "physical validation, learned-motion qualification or a direct Cascadeur comparison. Absolute foot-channel "
        "maxima are not reused as upper-body solver limits."
    )
    state["history"][-1] = result
    destination = GOALPOSTS + "01a073fe-c240-70c0-b5cd-fe9653aac60e-recorded-jump-reference-v1.json"
    assert not (ROOT / destination).exists()
    write(destination, state)
    (ROOT / destination).with_suffix(".md").write_text(
        g.markdown(result) + "\n\n" + result["evidence_transport_note"] + "\n", encoding="utf-8")

    checkpoint.update(
        state_path=destination,
        last_evaluated_state=destination,
        contract_hash=state["contract_hash"],
        input_fingerprint=fingerprint,
        round=69,
        remaining_evaluations=31,
        evidence=evidence_path,
        decision="iterate",
        stagnant_rounds=state["stagnant_rounds"],
        next_controller_monotonic_start=time.perf_counter(),
        recorded_at=time.time(),
        current_turn_classification=(
            "Progress: established three recorded human jump references, phase markers and joint-group temporal "
            "bounds in a parser-validated Bforartists scene; no production method promoted."
        ),
        previous_turn_classification=checkpoint["current_turn_classification"],
        active_jobs=[],
        blocked_audit={"consecutive_goal_turns": 0, "condition": None},
        pending_evaluation=False,
        work_accounting="Continuous parent interval from goalpost68 recorded once; host subprocess durations are not added.",
        diagnostic_summary=RESULTS + "summary.json",
        recorded_jump_reference={
            "source": summary["source"],
            "jumps": summary["recorded_jumps"],
            "phase_markers": summary["phase_markers"],
            "scene": summary["reference_scene"],
            "scene_sha256": summary["reference_scene_sha256"],
            "host_geometry_validation": summary["host_geometry_validation"],
            "host_shutdown_clean": False,
            "method_promoted": False,
        },
    )
    checkpoint["next_safe_actions"] = [
        "Construct joint-group and phase-normalized temporal penalties from the recorded upper-body distributions; do not use a single global threshold derived from noisy foot channels.",
        "Re-evaluate the retained artificial BoneForge stress trajectory against the recorded reference by semantic joint group while preserving its original pins and timing.",
        "Use additional already licensed exposed validation motion only when it adds a distinct jump or landing regime. Keep the six confirmation clips unopened.",
        "Full learned posing/motion, physical refinement, animator usability, quadrupeds and the optional connector remain required by the unchanged endpoint.",
        "Preserve goal ID, 100-evaluation ceiling, deadline 1789053845, experimental release 0.19.2 and publication identity/approval rules.",
    ]
    checkpoint["accounting_note"] = "Formal milestone69/100. Same endpoint, deadline and floors; no active processes."
    checkpoint_path = BASE + "checkpoint-recorded-jump-reference-v1.json"
    write(checkpoint_path, checkpoint)
    print({
        "round": 69,
        "remaining_evaluations": 31,
        "protected_artifacts": len(paths),
        "active_parent_seconds": wall_duration,
        "full_goal_complete": False,
        "reference_jumps": 3,
        "method_promoted": False,
    })


if __name__ == "__main__":
    main()
