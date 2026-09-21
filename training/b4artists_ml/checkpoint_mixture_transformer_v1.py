"""Record formal goalpost 76 for the bounded reference-mixture experiment."""
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
    checkpoint = read(BASE + "checkpoint-transformer-v1.json")
    old = read(checkpoint["state_path"])
    state = copy.deepcopy(old)
    previous = checkpoint["evidence"]
    evidence = read(previous)
    assert checkpoint["round"] == 75 and checkpoint["remaining_evaluations"] == 25
    assert checkpoint["max_goalposts"] == 100 and checkpoint["deadline_unix"] == 1789053845
    assert not checkpoint["active_jobs"] and not checkpoint["full_goal_complete"]
    assert not [path for path, digest in evidence["artifacts"].items() if sha(path) != digest]

    plan = read(TR + "mixture_transformer_sequence_evaluation_plan_v1.json")
    report = read(RESULTS + "mixture-transformer-sequence-development-v1/report.json")
    processes = read(RESULTS + "mixture-transformer-sequence-training-v1/processes.json")
    assert len(processes) == 2 and all(row["exit_code"] == 0 for row in processes)
    assert report["complete"] and not report["family_passes"] and report["hard_stop_triggered"]
    assert report["protected_baselines_match"] and not report["confirmation_read"]
    assert report["plan_sha256"] == sha(TR + "mixture_transformer_sequence_evaluation_plan_v1.json")
    assert len(report["models"]) == 2 and all(
        not report["development_gates"][model["name"]][partition]["passed"]
        for model in report["models"]
        for partition in plan["partitions"]
    )

    inputs = [
        BASE + "ARCHITECTURE-DECISION-v3.md",
        BASE + "ARCHITECTURE-EXECUTION-PLAN-v4.md",
        TR + "sequence_reference_bank_v1.py",
        TR + "sequence_mixture_transformer_model_v1.py",
        TR + "sequence_mixture_transformer_numpy_v1.py",
        TR + "check_sequence_mixture_transformer_v1.py",
        TR + "sequence_mixture_transformer_provider_v1.py",
        TR + "train_mixture_transformer_sequence_v1.py",
        TR + "mixture_transformer_sequence_fit_plan_v1.json",
        TR + "evaluate_mixture_transformer_sequence_v1.py",
        TR + "mixture_transformer_sequence_evaluation_plan_v1.json",
        TR + "checkpoint_mixture_transformer_v1.py",
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
                "Audited the architecture, enforced exact authored-value restoration, and ran the prospectively frozen two-seed reference-mixture Transformer. Both seeds improve the pure Transformer on combined development metrics but fail the unchanged position and cohort gates; the stronger prior selector remains better in aggregate. The declared hard stop ends nearby Transformer/selector fitting and redirects work to data, representation, contact/intent conditioning and end-to-end human evidence."
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
        checkpoint["state_path"], previous, BASE + "checkpoint-transformer-v1.json"
    }
    for folder in (
        "sequence-mixture-transformer-contract-v1",
        "mixture-transformer-sequence-training-v1",
        "mixture-transformer-sequence-development-v1",
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
                "pure_transformer_ratios": report["prior_comparison_ratios"][name]["pure_transformer_ratios"][partition],
                "tail_risk_selector_v28_ratios": report["prior_comparison_ratios"][name]["tail_risk_selector_v28_ratios"][partition],
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
        mixture_transformer_research={
            "parameters": 659741,
            "source_hours": 7.15874219825,
            "training_examples_total": 96000,
            "models": models,
            "development_report": RESULTS + "mixture-transformer-sequence-development-v1/report.json",
            "development_report_sha256": sha(RESULTS + "mixture-transformer-sequence-development-v1/report.json"),
            "confirmation_read": False,
            "runtime_promoted": False,
            "hard_stop_triggered": True,
            "decision": "Stop nearby Transformer/selector fitting. Redesign the data and representation comparison prospectively, with explicit contact and intent/style coverage, before another trained candidate.",
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
    evidence_path = GP + "mixture-transformer-evidence-v1.json"
    write(evidence_path, evidence)

    observations = read(GP + "transformer-observations-v1.json")
    for group in observations.values():
        for row in group.values():
            row.update(artifact=evidence_path, sha256=sha(evidence_path), input_fingerprint=fingerprint)
    observations_path = GP + "mixture-transformer-observations-v1.json"
    write(observations_path, observations)

    duration = time.perf_counter() - checkpoint["next_controller_monotonic_start"]
    assert 0 <= duration < 40000, duration
    g.record_work(state, "controller-mixture-transformer-v1", duration)
    result = evaluate(state, observations, ROOT)
    assert result["round"] == 76 and result["decision"] == "iterate"
    assert state["history"][:-1] == old["history"] and state["floors"] == old["floors"]
    result["evidence_transport_note"] = (
        "The reference-mixture experiment is valid negative evidence: exact contracts and both seeds complete, controls reproduce, but every partition fails position/cohort acceptance. The family hard stop is now active; confirmation remains sealed and runtime0.19.5 remains unchanged."
    )
    state["history"][-1] = result
    destination = GP + "01a073fe-c240-70c0-b5cd-fe9653aac60e-mixture-transformer-v1.json"
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
        round=76,
        remaining_evaluations=24,
        evidence=evidence_path,
        decision="iterate",
        stagnant_rounds=state["stagnant_rounds"],
        next_controller_monotonic_start=time.perf_counter(),
        recorded_at=time.time(),
        current_turn_classification=(
            "Verified progress: exact mixture contracts and two fixed 48k-window fits complete; both models improve the pure Transformer on combined metrics but fail unchanged position/cohort gates, activating the prospective family hard stop."
        ),
        previous_turn_classification=checkpoint["current_turn_classification"],
        active_jobs=[],
        blocked_audit={"consecutive_goal_turns": 0, "condition": None},
        pending_evaluation=False,
        work_accounting="Continuous parent interval from goalpost75 recorded once; subprocess durations are not added.",
        diagnostic_summary=RESULTS + "mixture-transformer-sequence-development-v1/report.json",
        mixture_transformer_research=evidence["mixture_transformer_research"],
    )
    checkpoint["next_safe_actions"] = [
        "Honor the hard stop: do not train another nearby Transformer, selector or loss-weight variant.",
        "Freeze a data/representation decision study covering root plus local rotations, explicit contact phases, proportions and intent/style, with legal provenance and broader motion tasks.",
        "Build missing representative benchmark journeys and collect independent animator correction-time evidence before a parity claim.",
        "Keep confirmation sealed, runtime unpromoted, physics explicit, quadrupeds second and the optional connector deferred."
    ]
    checkpoint["accounting_note"] = "Formal milestone76/100. Same endpoint, deadline and floors; no active processes."
    write(BASE + "checkpoint-mixture-transformer-v1.json", checkpoint)
    print(
        {
            "round": 76,
            "remaining_evaluations": 24,
            "family_passes": False,
            "hard_stop_triggered": True,
            "confirmation_read": False,
            "runtime_promoted": False,
            "full_goal_complete": False,
        }
    )


if __name__ == "__main__":
    main()
