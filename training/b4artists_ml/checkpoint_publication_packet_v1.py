"""Record formal goalpost 72 for one-snapshot, one-use publication."""
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
    checkpoint = read(BASE + "checkpoint-publication-latency-v1.json")
    old = read(checkpoint["state_path"])
    state = copy.deepcopy(old)
    evidence = read(checkpoint["evidence"])
    assert checkpoint["round"] == 71 and checkpoint["max_goalposts"] == 100
    assert checkpoint["remaining_evaluations"] == 29
    assert checkpoint["deadline_unix"] == 1789053845 and not checkpoint["active_jobs"]
    assert not checkpoint["full_goal_complete"]
    assert checkpoint["artifact"]["sha256"] == sha(checkpoint["artifact"]["path"])

    benchmark = read(RESULTS + "anchor-snapshot-publication-v3/report.json")
    offline = read(RESULTS + "packet-package-v1.json")
    package = read(BASE + "package-test-v0.19.4.json")
    finalization = read(RESULTS + "packet-package-finalization-v1.json")
    regression = read(RESULTS + "packet-production-full-v1-regression.json")
    adversarial = read(RESULTS + "packet-adversarial-target-v1-regression.json")
    assert benchmark["qualified"] and benchmark["current_to_legacy_ratio"] < .90
    assert benchmark["exact_dense_curve_evaluation"] and benchmark["exact_keys_and_metadata"]
    assert benchmark["legacy_anchor_reads"] == [3, 3, 3] and benchmark["current_anchor_reads"] == [1, 1, 1]
    assert len(regression) == 43 and sum(row["tests"] for row in regression) == 417
    assert all(row["assertions_passed"] and not row["errors"] and not row["failures"] and not row["skipped"] for row in regression)
    assert len(adversarial) == 1 and adversarial[0]["assertions_passed"] and adversarial[0]["tests"] == 10
    assert offline["passed"] and offline["cases"] == 13 and not offline["denied_runtime_calls"]
    assert package["ready_for_local_testing"] and package["sha256"] == sha("releases/b4artists_ml_v0.19.4.zip")
    assert finalization["complete"] and not finalization["full_goal_complete"]

    protected = dict(evidence["artifacts"])
    expected_revisions = {
        "b4artists_ml/__init__.py",
        "b4artists_ml/curve_smoothing.py",
        "b4artists_ml/temporal_generation.py",
        "b4artists_ml/temporal_preview.py",
        "b4artists_ml/workflow.py",
        "docs/b4artists_ml/PROJECT.md",
        "docs/b4artists_ml/REQUIREMENTS.md",
        "docs/b4artists_ml/ROADMAP.md",
        "docs/b4artists_ml/USER_GUIDE.md",
        "docs/b4artists_ml/VALIDATION.md",
        "tests/test_b4artists_ml_smoothed_preview_v2.py",
    }
    changed = {path for path, digest in protected.items() if sha(path) != digest}
    assert changed == expected_revisions
    assert all(sha(path) == digest for path, digest in protected.items() if path not in changed)

    prior_versions = {
        "b4artists_ml/__init__.py": RESULTS + "packet-package-baseline-v1/__init__.py",
        "docs/b4artists_ml/PROJECT.md": RESULTS + "packet-documents-baseline-v1/PROJECT.md",
        "docs/b4artists_ml/REQUIREMENTS.md": RESULTS + "packet-documents-baseline-v1/REQUIREMENTS.md",
        "docs/b4artists_ml/ROADMAP.md": RESULTS + "packet-documents-baseline-v1/ROADMAP.md",
        "docs/b4artists_ml/USER_GUIDE.md": RESULTS + "packet-documents-baseline-v1/USER_GUIDE.md",
        "docs/b4artists_ml/VALIDATION.md": RESULTS + "packet-documents-baseline-v1/VALIDATION.md",
    }
    for path, prior in prior_versions.items():
        assert sha(prior) == protected[path]
    revisions = {}
    for path in sorted(changed):
        row = {
            "before_sha256": protected[path],
            "after_sha256": sha(path),
            "reason": ("One-snapshot and one-use publication optimization with adversarial validation" if path.startswith(("b4artists_ml/", "tests/"))
                       else "0.19.4 evidence/status update after exact package qualification"),
        }
        if path in prior_versions:
            row["prior_version"] = prior_versions[path]
        elif path.startswith("b4artists_ml/"):
            row["prior_archive"] = "releases/b4artists_ml_v0.19.3.zip"
            row["prior_archive_member"] = path
        else:
            row["prior_evidence"] = checkpoint["evidence"]
        revisions[path] = row

    inputs = [
        TRAINING + "benchmark_bulk_curve_write_v1.py",
        TRAINING + "profile_publication_tick_v2.py",
        TRAINING + "benchmark_anchor_snapshot_publication_v1.py",
        TRAINING + "build_publication_packet_package_v1.py",
        TRAINING + "check_publication_packet_package_v1.py",
        TRAINING + "finalize_publication_packet_package_v1.py",
        TRAINING + "checkpoint_publication_packet_v1.py",
        BASE + "publication-bulk-routing-v1.json",
        BASE + "publication-anchor-cache-production-routing-v1.json",
        BASE + "publication-packet-production-routing-v1.json",
        BASE + "PUBLICATION-LATENCY-v0.19.4.md",
    ]
    added = [path for path in inputs if path not in state["contract"]["inputs"]]
    state["contract"]["inputs"] += added
    state["contract_hash"] = g.digest(state["contract"])
    left, right = copy.deepcopy(state["contract"]), copy.deepcopy(old["contract"])
    left.pop("inputs"); right.pop("inputs")
    assert left == right
    state["explicit_revisions"].append({
        "reason": "One validated anchor snapshot and one-use sample ownership reduce archived0.19.3 publication time by26.17% with exact motion;417native checks and13exact-archive workflows pass. The complete endpoint remains open.",
        "prior_state": checkpoint["state_path"],
        "prior_sha256": sha(checkpoint["state_path"]),
        "artifact_revisions": revisions,
        "added_inputs": added,
        "prior_contract_hash": old["contract_hash"],
        "new_contract_hash": state["contract_hash"],
        "recorded_at": time.time(),
    })

    paths = set(protected) | set(inputs) | set(changed) | {
        checkpoint["state_path"], checkpoint["evidence"],
        BASE + "checkpoint-publication-latency-v1.json",
        BASE + "package-test-v0.19.4.json",
        "releases/b4artists_ml_v0.19.4.zip",
    }
    folders = (
        "bulk-curve-write-v1", "publication-tick-profile-v2", "publication-tick-profile-v3",
        "anchor-snapshot-publication-v1", "anchor-snapshot-publication-v2", "anchor-snapshot-publication-v3",
        "packet-package-baseline-v1", "packet-documents-baseline-v1", "packet-package-v1",
    )
    for folder in folders:
        root = ROOT / RESULTS / folder
        if root.exists():
            paths.update(path.relative_to(ROOT).as_posix() for path in root.rglob("*") if path.is_file())
    paths.update(path.relative_to(ROOT).as_posix() for path in (ROOT / RESULTS).glob("packet-*.json") if path.is_file())
    paths.update(path.relative_to(ROOT).as_posix() for path in (ROOT / TRAINING / "cache").glob("packet-*.log") if path.is_file())

    fingerprint = g.fingerprint(ROOT, state["contract"]["inputs"])
    evidence.update(
        contract_hash=state["contract_hash"],
        input_fingerprint=fingerprint,
        artifacts={path: sha(path) for path in sorted(paths)},
        previous_evidence_recheck={
            "path": checkpoint["evidence"],
            "sha256": sha(checkpoint["evidence"]),
            "all_unrevised_artifacts_unchanged": True,
            "explicit_revisions": revisions,
        },
        publication_packet={
            "benchmark": benchmark,
            "native_cases": 417,
            "native_suites": 43,
            "adversarial_cases": 10,
            "offline_cases": 13,
            "dense_contact_checks": 9813,
            "package": package,
            "host_shutdown_clean": False,
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
    evidence_path = GOALPOSTS + "publication-packet-evidence-v1.json"
    write(evidence_path, evidence)

    observations = read(GOALPOSTS + "publication-latency-observations-v1.json")
    for group in observations.values():
        for row in group.values():
            row.update(artifact=evidence_path, sha256=sha(evidence_path), input_fingerprint=fingerprint)
    observations_path = GOALPOSTS + "publication-packet-observations-v1.json"
    write(observations_path, observations)

    wall_duration = time.time() - checkpoint["recorded_at"]
    assert 1800 <= wall_duration < 20000, wall_duration
    g.record_work(state, "controller-publication-packet-v1", wall_duration)
    result = evaluate(state, observations, ROOT)
    assert result["round"] == 72 and result["decision"] == "iterate"
    assert state["history"][:-1] == old["history"] and state["floors"] == old["floors"]
    result["evidence_transport_note"] = (
        "The qualified publication transaction is faster and retains complete validation and exact output. It does "
        "not satisfy the full responsiveness, learned-motion, physics, human-usability, quadruped or direct "
        "Cascadeur-comparison gates."
    )
    state["history"][-1] = result
    destination = GOALPOSTS + "01a073fe-c240-70c0-b5cd-fe9653aac60e-publication-packet-v1.json"
    assert not (ROOT / destination).exists()
    write(destination, state)
    (ROOT / destination).with_suffix(".md").write_text(
        g.markdown(result) + "\n\n" + result["evidence_transport_note"] + "\n", encoding="utf-8")

    checkpoint.update(
        state_path=destination,
        last_evaluated_state=destination,
        contract_hash=state["contract_hash"],
        input_fingerprint=fingerprint,
        round=72,
        remaining_evaluations=28,
        evidence=evidence_path,
        decision="iterate",
        stagnant_rounds=state["stagnant_rounds"],
        next_controller_monotonic_start=time.perf_counter(),
        recorded_at=time.time(),
        current_turn_classification=(
            "Progress: promoted one-snapshot, one-use publication; archived0.19.3 median publication fell26.17% "
            "with exact motion,417native checks and13offline package workflows passing."
        ),
        previous_turn_classification=checkpoint["current_turn_classification"],
        active_jobs=[],
        blocked_audit={"consecutive_goal_turns": 0, "condition": None},
        pending_evaluation=False,
        work_accounting="Continuous parent interval from goalpost71 recorded once; subprocess durations are not added.",
        diagnostic_summary=RESULTS + "anchor-snapshot-publication-v3/report.json",
        publication_packet={
            "legacy_publication_seconds": benchmark["median_publication_seconds"]["legacy"],
            "current_publication_seconds": benchmark["median_publication_seconds"]["current"],
            "ratio": benchmark["current_to_legacy_ratio"],
            "legacy_anchor_reads": benchmark["legacy_anchor_reads"],
            "current_anchor_reads": benchmark["current_anchor_reads"],
            "exact_dense_curve_evaluation": True,
            "native_cases": 417,
            "offline_cases": 13,
            "method_promoted": True,
        },
        artifact={
            "path": "releases/b4artists_ml_v0.19.4.zip",
            "sha256": package["sha256"],
            "files": package["files"],
            "bytes": package["bytes"],
            "matches_current_source": True,
            "experimental": True,
            "ready_for_local_testing": True,
            "note": "417 native checks before version-only bump;13 exact-archive offline workflows; full goal incomplete.",
        },
    )
    checkpoint["next_safe_actions"] = [
        "Profile the remaining roughly153ms final publication span and split only work that can retain atomic rollback and source-visible cancellation.",
        "Prioritize learned temporal generalization and independent animator task evidence over further deterministic surface expansion.",
        "Resume the deferred nonlinear boundary-window solver only with cached Jacobians and frozen temporal/spatial gates; do not retune one artificial jump indefinitely.",
        "Full physical refinement, quadrupeds, broader rigs/hardware and the optional Cascadeur connector remain required by the unchanged endpoint.",
        "Preserve goal ID,100evaluation ceiling,deadline1789053845,experimental release0.19.4,sealed confirmation clips and publication identity/approval rules.",
    ]
    checkpoint["accounting_note"] = "Formal milestone72/100. Same endpoint, deadline and floors; no active processes."
    checkpoint_path = BASE + "checkpoint-publication-packet-v1.json"
    write(checkpoint_path, checkpoint)
    print({
        "round": 72,
        "remaining_evaluations": 28,
        "protected_artifacts": len(paths),
        "active_parent_seconds": wall_duration,
        "full_goal_complete": False,
        "method_promoted": True,
        "publication_ratio": benchmark["current_to_legacy_ratio"],
    })


if __name__ == "__main__":
    main()
