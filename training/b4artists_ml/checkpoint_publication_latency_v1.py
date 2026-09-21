"""Record formal goalpost 71 for exact constant-curve publication latency."""
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
    checkpoint = read(BASE + "checkpoint-jump-temporal-envelope-v1.json")
    old = read(checkpoint["state_path"])
    state = copy.deepcopy(old)
    evidence = read(checkpoint["evidence"])
    assert checkpoint["round"] == 70 and checkpoint["max_goalposts"] == 100
    assert checkpoint["deadline_unix"] == 1789053845 and not checkpoint["active_jobs"]
    assert not checkpoint["full_goal_complete"]
    assert checkpoint["artifact"]["sha256"] == sha(checkpoint["artifact"]["path"])

    benchmark = read(RESULTS + "constant-curve-publication-v2/report.json")
    offline = read(RESULTS + "constant-curve-package-v1.json")
    package = read(BASE + "package-test-v0.19.3.json")
    finalization = read(RESULTS + "constant-curve-package-finalization-v1.json")
    regression = read(RESULTS + "constant-skip-production-full-v1-regression.json")
    assert benchmark["qualified"] and benchmark["publication_ratio"] < 0.8
    assert benchmark["exact_dense_curve_evaluation"] and benchmark["nonconstant_metadata_preserved"]
    assert len(regression) == 43 and sum(row["tests"] for row in regression) == 415
    assert all(row["assertions_passed"] and not row["errors"] and not row["failures"] for row in regression)
    assert offline["passed"] and offline["cases"] == 13 and not offline["denied_runtime_calls"]
    assert package["ready_for_local_testing"] and package["sha256"] == sha("releases/b4artists_ml_v0.19.3.zip")
    assert finalization["complete"] and not finalization["full_goal_complete"]

    protected = dict(evidence["artifacts"])
    expected_revisions = {
        "b4artists_ml/__init__.py",
        "b4artists_ml/curve_smoothing.py",
        "docs/b4artists_ml/PROJECT.md",
        "docs/b4artists_ml/REQUIREMENTS.md",
        "docs/b4artists_ml/ROADMAP.md",
        "docs/b4artists_ml/USER_GUIDE.md",
        "docs/b4artists_ml/VALIDATION.md",
        "tests/test_b4artists_ml_curve_smoothing_native_v1.py",
        "tests/test_b4artists_ml_smoothed_preview_v1.py",
    }
    changed = {path for path, digest in protected.items() if sha(path) != digest}
    assert changed == expected_revisions
    assert all(sha(path) == digest for path, digest in protected.items() if path not in changed)

    prior_versions = {
        "b4artists_ml/__init__.py": RESULTS + "constant-curve-package-baseline-v1/__init__.py",
        "docs/b4artists_ml/PROJECT.md": RESULTS + "constant-curve-documents-baseline-v1/PROJECT.md",
        "docs/b4artists_ml/REQUIREMENTS.md": RESULTS + "constant-curve-documents-baseline-v1/REQUIREMENTS.md",
        "docs/b4artists_ml/ROADMAP.md": RESULTS + "constant-curve-documents-baseline-v1/ROADMAP.md",
        "docs/b4artists_ml/USER_GUIDE.md": RESULTS + "constant-curve-documents-baseline-v1/USER_GUIDE.md",
        "docs/b4artists_ml/VALIDATION.md": RESULTS + "constant-curve-documents-baseline-v1/VALIDATION.md",
    }
    for path, prior in prior_versions.items():
        assert sha(prior) == protected[path]
    revisions = {}
    for path in sorted(changed):
        row = {
            "before_sha256": protected[path],
            "after_sha256": sha(path),
            "reason": ("Exact-constant publication optimization and regression coverage" if path.startswith(("b4artists_ml/", "tests/"))
                       else "0.19.3 evidence/status update after exact package qualification"),
        }
        if path in prior_versions:
            row["prior_version"] = prior_versions[path]
        elif path == "b4artists_ml/curve_smoothing.py":
            row["prior_archive"] = "releases/b4artists_ml_v0.19.2.zip"
            row["prior_archive_member"] = path
        else:
            row["prior_evidence"] = checkpoint["evidence"]
        revisions[path] = row

    inputs = [
        TRAINING + "profile_constant_curve_smoothing_v1.py",
        TRAINING + "benchmark_constant_curve_publication_v1.py",
        TRAINING + "build_constant_curve_package_v1.py",
        TRAINING + "check_constant_curve_package_v1.py",
        TRAINING + "finalize_constant_curve_package_v1.py",
        TRAINING + "checkpoint_publication_latency_v1.py",
        BASE + "publication-latency-routing-v1.json",
        BASE + "publication-latency-production-routing-v1.json",
        BASE + "PUBLICATION-LATENCY-v0.19.3.md",
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
        "reason": "Exact constant-curve handling reduces the integrated blocking publication tick by33.44% with zero dense evaluation error;415native checks and13exact-archive workflows pass. Responsiveness, full learned motion, physics, usability, quadrupeds and Cascadeur parity remain open.",
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
        BASE + "checkpoint-jump-temporal-envelope-v1.json",
        BASE + "package-test-v0.19.3.json",
        "releases/b4artists_ml_v0.19.3.zip",
    }
    for folder in (
        "constant-curve-smoothing-v1", "constant-curve-publication-v1", "constant-curve-publication-v2",
        "constant-curve-package-baseline-v1", "constant-curve-documents-baseline-v1",
    ):
        paths.update(path.relative_to(ROOT).as_posix() for path in (ROOT / RESULTS / folder).rglob("*") if path.is_file())
    paths.update(path.relative_to(ROOT).as_posix() for path in (ROOT / RESULTS).glob("constant-*") if path.is_file())
    paths.update(path.relative_to(ROOT).as_posix() for path in (ROOT / TRAINING / "cache").glob("constant-*.log") if path.is_file())

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
        publication_latency={
            "benchmark": benchmark,
            "native_cases": 415,
            "native_suites": 43,
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
    evidence_path = GOALPOSTS + "publication-latency-evidence-v1.json"
    write(evidence_path, evidence)

    observations = read(GOALPOSTS + "jump-temporal-envelope-observations-v1.json")
    for group in observations.values():
        for row in group.values():
            row.update(artifact=evidence_path, sha256=sha(evidence_path), input_fingerprint=fingerprint)
    observations_path = GOALPOSTS + "publication-latency-observations-v1.json"
    write(observations_path, observations)

    wall_duration = time.time() - checkpoint["recorded_at"]
    assert 1800 <= wall_duration < 20000, wall_duration
    g.record_work(state, "controller-publication-latency-v1", wall_duration)
    result = evaluate(state, observations, ROOT)
    assert result["round"] == 71 and result["decision"] == "iterate"
    assert state["history"][:-1] == old["history"] and state["floors"] == old["floors"]
    result["evidence_transport_note"] = (
        "The publication optimization is exact for the qualified constant-curve case and improves one blocking "
        "update. It does not satisfy the complete responsiveness gate or replace learned-motion, physics, human "
        "usability, quadruped and direct Cascadeur comparison evidence."
    )
    state["history"][-1] = result
    destination = GOALPOSTS + "01a073fe-c240-70c0-b5cd-fe9653aac60e-publication-latency-v1.json"
    assert not (ROOT / destination).exists()
    write(destination, state)
    (ROOT / destination).with_suffix(".md").write_text(
        g.markdown(result) + "\n\n" + result["evidence_transport_note"] + "\n", encoding="utf-8")

    checkpoint.update(
        state_path=destination,
        last_evaluated_state=destination,
        contract_hash=state["contract_hash"],
        input_fingerprint=fingerprint,
        round=71,
        remaining_evaluations=29,
        evidence=evidence_path,
        decision="iterate",
        stagnant_rounds=state["stagnant_rounds"],
        next_controller_monotonic_start=time.perf_counter(),
        recorded_at=time.time(),
        current_turn_classification=(
            "Progress: promoted exact constant-curve publication optimization; median blocking publication tick "
            "fell33.44% with zero dense evaluation error,415native checks and13offline package workflows passing."
        ),
        previous_turn_classification=checkpoint["current_turn_classification"],
        active_jobs=[],
        blocked_audit={"consecutive_goal_turns": 0, "condition": None},
        pending_evaluation=False,
        work_accounting="Continuous parent interval from goalpost70 recorded once; host subprocess durations are not added.",
        diagnostic_summary=RESULTS + "constant-curve-publication-v2/report.json",
        publication_latency={
            "legacy_publication_tick_seconds": benchmark["median_publication_tick_seconds"]["legacy"],
            "current_publication_tick_seconds": benchmark["median_publication_tick_seconds"]["current"],
            "ratio": benchmark["publication_ratio"],
            "exact_dense_curve_evaluation": True,
            "native_cases": 415,
            "offline_cases": 13,
            "method_promoted": True,
        },
        artifact={
            "path": "releases/b4artists_ml_v0.19.3.zip",
            "sha256": package["sha256"],
            "files": package["files"],
            "bytes": package["bytes"],
            "matches_current_source": True,
            "experimental": True,
            "ready_for_local_testing": True,
            "note": "415 native checks before version-only bump;13 exact-archive offline workflows; full goal incomplete.",
        },
    )
    checkpoint["next_safe_actions"] = [
        "Profile and cooperatively split the remaining final publication work; the current median blocking update is275ms and full responsiveness remains unqualified.",
        "Resume the deferred boundary-window nonlinear constrained solver only with cached Jacobians and explicit temporal/spatial gates; do not retune the single artificial jump indefinitely.",
        "Prioritize learned-motion and independent animator task evidence over adding more deterministic feature surface.",
        "Full physical refinement, quadrupeds, broader rigs/hardware and the optional Cascadeur connector remain required by the unchanged endpoint.",
        "Preserve goal ID,100evaluation ceiling,deadline1789053845,experimental release0.19.3,sealed confirmation clips and publication identity/approval rules.",
    ]
    checkpoint["accounting_note"] = "Formal milestone71/100. Same endpoint, deadline and floors; no active processes."
    checkpoint_path = BASE + "checkpoint-publication-latency-v1.json"
    write(checkpoint_path, checkpoint)
    print({
        "round": 71,
        "remaining_evaluations": 29,
        "protected_artifacts": len(paths),
        "active_parent_seconds": wall_duration,
        "full_goal_complete": False,
        "method_promoted": True,
        "publication_ratio": benchmark["publication_ratio"],
    })


if __name__ == "__main__":
    main()
