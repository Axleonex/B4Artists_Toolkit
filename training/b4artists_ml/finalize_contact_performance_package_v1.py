"""Finalize exact-package 0.20.1 contact-performance evidence and status docs."""
from pathlib import Path
import hashlib
import json
import re
import zipfile


ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / "docs/b4artists_ml"
RESULTS = ROOT / "training/b4artists_ml/results"
BASE = ROOT / "training/b4artists_ml/cache/contact-performance-package-v1"
ARCHIVE = ROOT / "releases/b4artists_ml_v0.20.1.zip"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_once(text, old, new):
    assert text.count(old) == 1, old
    return text.replace(old, new, 1)


def main():
    meta = read(DOCS / "package-test-v0.20.1.json")
    regression = read(RESULTS / "contact-performance-v3-full-regression.json")
    offline = read(RESULTS / "contact-performance-package-v1.json")
    process = read(RESULTS / "contact-performance-package-v1-process.json")
    suggestions = read(RESULTS / "contact-suggestions-performance-package-v1.json")
    source_ui = read(RESULTS / "contact-ui-trials-v1.json")
    package_ui = read(RESULTS / "contact-performance-package-ui-trials-v1.json")

    assert sha(ARCHIVE) == meta["sha256"] == offline["package_sha256"]
    assert len(regression) == 45 and len({row["suite"] for row in regression}) == 45
    assert sum(row["tests"] for row in regression) == 429
    assert all(
        row["assertions_passed"]
        and not row.get("errors")
        and not row.get("failures")
        and not row.get("skipped")
        and row["runtime_sha256"] == meta["runtime_sha256"]
        for row in regression
    )
    assert offline["passed"] and offline["cases"] == 13
    assert offline["offline_guard_self_test"] and not offline["denied_runtime_calls"]
    assert offline["runtime_sha256"] == meta["runtime_sha256"]
    assert suggestions["passed"] and suggestions["tests"] == 4 and suggestions["exact_package"]
    assert Path(suggestions["package"]).resolve().is_relative_to(BASE.resolve())
    for report in (source_ui, package_ui):
        assert report["passed"] and len(report["trials"]) == 3 and all(report["gates"].values())
        assert report["summary"]["suggestion_callback_max_ms"] < 50
        assert report["summary"]["correction_callback_max_ms"] < 50
        assert report["summary"]["correction_elapsed_max_ms"] < 8000
    assert package_ui["exact_package"]
    assert all(row["exact_package"] and Path(row["package"]).resolve().is_relative_to(BASE.resolve()) for row in package_ui["trials"])

    with zipfile.ZipFile(ARCHIVE) as archive:
        assert len(archive.namelist()) == meta["files"]
        assert all(archive.read(name) == (ROOT / name).read_bytes() for name in archive.namelist())

    current = package_ui["summary"]
    reduction = (17_000.0 - current["correction_elapsed_max_ms"]) / 17_000.0 * 100.0
    meta.update(
        ready_for_local_testing=True,
        exact_package_offline_evidence="training/b4artists_ml/results/contact-performance-package-v1.json",
        exact_package_contact_evidence="training/b4artists_ml/results/contact-suggestions-performance-package-v1.json",
        exact_package_ui_evidence="training/b4artists_ml/results/contact-performance-package-ui-trials-v1.json",
        packaged_host_smoke=dict(
            established_offline_workflows=13,
            contact_suggestion_tests=4,
            actual_window_trials=3,
            established_process_seconds=process["seconds"],
            assertions_passed=True,
            host_exit=process["exit_code"],
            host_shutdown_qualified=False,
        ),
        exact_package_performance=current,
        packaged_ui_qualification=(
            "Three exact-package actual-window event journeys pass the frozen callback, total-time, "
            "accuracy, Keep and Restore Source gates. Independent animator approval remains untested."
        ),
    )
    (DOCS / "package-test-v0.20.1.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    report = f"""# Contact workflow performance - experimental 0.20.1

## Result

The default-Rigify foot-contact workflow now meets its frozen automated responsiveness gate. The exact extracted package completed three actual-window suggestion, review, correction, Keep and Restore Source journeys. Every measured cooperative callback stayed below 50 ms, every correction completed below 8 seconds, and the corrected contact error remained below `2e-4` evaluated limb lengths.

The 0.20.0 baseline correction took approximately 17.0 seconds. The final 0.20.1 package took {current['correction_elapsed_median_ms']/1000:.2f} seconds median and {current['correction_elapsed_max_ms']/1000:.2f} seconds maximum across three runs, a {reduction:.1f}% reduction at the conservative maximum. Suggestions took {min(row['suggestion_elapsed_ms'] for row in package_ui['trials'])/1000:.2f}-{max(row['suggestion_elapsed_ms'] for row in package_ui['trials'])/1000:.2f} seconds. The worst suggestion callback was {current['suggestion_callback_max_ms']:.2f} ms and the worst correction callback was {current['correction_callback_max_ms']:.2f} ms.

## What changed

- Contact fitting samples at quarter-frame intervals and validates cubic output adaptively at quarter and midpoint positions. This retains continuous-curve checks while avoiding an unconditional eighth-frame fit.
- Dependency, driver and constraint discovery yields more often while constructing private evaluators.
- Suggestion sampling uses `scene.frame_set` to restore the untouched action between observations and reserves the full pose and rig-mode restore for finalization.
- Complete-rig verification no longer repeats a view-layer update already performed by `scene.frame_set`.
- Metric assembly, serialization, candidate publication and commit are separate modal callbacks.

## Evidence

- Source regression: 45 unique suites, 429 tests, no failures, errors or skips, all against one runtime hash.
- Source actual-window trials: three of three pass; correction maximum {source_ui['summary']['correction_elapsed_max_ms']/1000:.2f} seconds; suggestion/correction callback maxima {source_ui['summary']['suggestion_callback_max_ms']:.2f}/{source_ui['summary']['correction_callback_max_ms']:.2f} ms.
- Exact archive workflows: 13 established offline cases with 9,813 dense contact checks and blocked outbound network/process calls, plus four contact-suggestion tests.
- Exact archive UI: three of three actual-window journeys pass with maximum contact error {max(row['correction_error'] for row in package_ui['trials']):.8g} limb lengths.
- Archive: `releases/b4artists_ml_v0.20.1.zip`, SHA-256 `{meta['sha256']}`.

Two pre-final timing reports are retained. One exposed a 51.9 ms publication callback and led to finer publication boundaries; the other exposed a 52.7 ms suggestion callback and led to removal of redundant per-sample pose/mode restores. They are failed candidate evidence, not part of the passing release claim.

## Limits

This qualifies one automated default-Rigify contact workflow on this machine. It does not establish zero latency, all hardware responsiveness, manual animator usability, broad action quality or Cascadeur parity. A known `ucrtbase.dll` access violation still occurs after Bforartists writes passing reports, so clean host shutdown remains unqualified. One broader Rigify hand-orientation workflow has previously taken about 10.76 seconds and remains outside this foot-contact performance gate. The next product milestone is the fixed procedural vertical slice across four humanoid rig families and seven action families.
"""
    (DOCS / "CONTACT-PERFORMANCE-v0.20.1.md").write_text(report, encoding="utf-8")

    summary = (
        "Current 0.20.1 update: 429 native checks across 45 suites, 13 exact-package offline workflows, "
        "4 exact-package contact-suggestion tests and 3 exact-package actual-window journeys pass. "
        f"Default-Rigify foot-contact correction is {current['correction_elapsed_median_ms']/1000:.2f}s median, "
        f"{current['correction_elapsed_max_ms']/1000:.2f}s maximum, with suggestion/correction callback maxima "
        f"{current['suggestion_callback_max_ms']:.1f}/{current['correction_callback_max_ms']:.1f}ms. "
        "See CONTACT-PERFORMANCE-v0.20.1.md. Learned temporal motion, full physics, human usability and "
        "Cascadeur parity remain unqualified."
    )
    for name in ("ROADMAP.md", "REQUIREMENTS.md"):
        path = DOCS / name
        text = path.read_text(encoding="utf-8-sig")
        text, count = re.subn(r"^Current 0\.20\.0 update:.*$", summary, text, count=1, flags=re.M)
        assert count == 1
        path.write_text(text, encoding="utf-8")

    path = DOCS / "PROJECT.md"
    text = path.read_text(encoding="utf-8-sig")
    text, count = re.subn(r"^Status: experimental 0\.20\.0 local archive\..*$", "Status: experimental 0.20.1 local archive. " + summary.removeprefix("Current 0.20.1 update: "), text, count=1, flags=re.M)
    assert count == 1
    text += "\n## Contact workflow performance in 0.20.1\n\nCONTACT-PERFORMANCE-v0.20.1.md records the qualified default-Rigify foot-contact latency reduction, exact-package event trials and remaining limits. This closes the contact-performance milestone and advances work to the four-rig, seven-action procedural vertical slice.\n"
    path.write_text(text, encoding="utf-8")

    path = DOCS / "USER_GUIDE.md"
    text = replace_once(path.read_text(encoding="utf-8-sig"), "releases/b4artists_ml_v0.20.0.zip", "releases/b4artists_ml_v0.20.1.zip")
    path.write_text(text, encoding="utf-8")

    path = DOCS / "VALIDATION.md"
    text = path.read_text(encoding="utf-8-sig")
    text, count = re.subn(
        r"^Historical record\. Current status:.*$",
        "Historical record. Current status: REQUIREMENTS.md, package-test-v0.20.1.json and CONTACT-PERFORMANCE-v0.20.1.md. The integrated source passes 429 native checks across 45 suites; the exact archive passes 13 offline workflows, 4 contact-suggestion tests and 3 actual-window journeys. The original 0.1 evidence below remains historical.",
        text,
        count=1,
        flags=re.M,
    )
    assert count == 1
    path.write_text(text, encoding="utf-8")

    path = DOCS / "ARCHITECTURE-REVIEW-v4.md"
    text = replace_once(
        path.read_text(encoding="utf-8-sig"),
        "2. Profile and reduce the default-Rigify contact-correction path. Cooperative UI ticks must stay below 50 ms, and total wait time must be short enough for repeated animator iteration; the measured 17-second 0.20.0 path does not pass that product gate.",
        "2. Default-Rigify contact correction is source- and exact-package-qualified in experimental 0.20.1. Three exact-package actual-window journeys stay below 50 ms per measured callback and below 8 seconds total; preserve this as the automated floor while step 3 measures animator effort and broader actions.",
    )
    path.write_text(text, encoding="utf-8")

    path = DOCS / "REQUIREMENTS.md"
    text = path.read_text(encoding="utf-8-sig")
    old = "| Responsive previews, cancellation and strength | Opt-in Live Solve with newest-request cancellation; private temporal generation preserves eight-profile output and passes a real external-dependency fallback; serial default-Rigify reference work drops 40.9% with exact candidate curves | Partial: 0.17.5 improves default Rigify idle p95 by 44.4% and active work by 14.3%, but worst ticks still exceed 50 ms and larger fits take seconds. Current-package UI interaction remains unverified; earlier automated UI lifecycle evidence is historical |"
    new = f"| Responsive previews, cancellation and strength | Opt-in Live Solve and source-visible cancellation plus 0.20.1 exact-package contact trials | Partial: three default-Rigify foot-contact journeys stay below 50 ms per measured callback and below 8 seconds total ({current['correction_elapsed_median_ms']/1000:.2f}s median); broader actions, hardware and independent animator interaction remain unverified |"
    text = replace_once(text, old, new)
    old = "| Accuracy and performance measurements | Local experimental builds, backend latency/OS memory counters, actual-host comparisons and bounded cache allocation tests | Partial: backend and fixture measurements have different scopes; full application cold startup, complete workflow memory, current UI responsiveness and hardware variants remain unverified |"
    new = "| Accuracy and performance measurements | Versioned source and exact-package benchmarks, actual-window callback timings, backend latency/OS memory counters and bounded cache tests | Partial: the 0.20.1 default-Rigify contact workflow is qualified on this machine; cold startup, full workflow memory, broader actions, other hardware and human-perceived responsiveness remain unverified |"
    text = replace_once(text, old, new)
    path.write_text(text, encoding="utf-8")

    path = DOCS / "ROADMAP.md"
    text = path.read_text(encoding="utf-8-sig")
    text += "\n## 0.20.1 contact-performance checkpoint\n\nThe default-Rigify foot-contact workflow now passes the frozen source and exact-package latency gates. The final archive passes 429 native checks, 13 established offline workflows, 4 packaged contact-suggestion tests and 3 exact-package actual-window journeys. Suggestion sampling avoids redundant state restoration, complete-rig verification avoids a duplicate dependency-graph update, and final publication is split across cooperative callbacks. The next milestone is the fixed procedural vertical slice across BoneForge, generated Rigify basic/default and an imported humanoid convention for reach, crouch, walk, run, jump, land and turn, with correction and interaction counts.\n"
    path.write_text(text, encoding="utf-8")

    route = dict(
        schema=1,
        recorded_date="2026-09-10",
        session_scope="B4Artists Machine Learning contact-performance 0.20.1",
        canonical=dict(
            sdk_version="2.0.1",
            sdk_source_commit="d7eacf8555551e0b658c38600f3a588349638edc",
            orchestration_source_commit="e036d965c659d7249ea9d9beb1bdb7cf544390e4",
            execution_policy_sha256="74041CC3740F3165B7A3280583628C2FBE21B60B626D08045EB0560771492466",
            evaluation_policy_sha256="17029585B11E5E795833F173422EC9A106865B1B4C768A37BD622925B708C8D7",
        ),
        execution=dict(
            router_outcome="REMOTE_EXECUTOR_REQUIRED",
            remote_executor="NucBox",
            remote_repository_visible=False,
            remote_probe="REMOTE_X_MISSING",
            continuation="native",
            continuation_basis="STATIC-NATIVE-EXECUTION-POLICY automatic native continuation after recoverable pre-host-apply infrastructure failure",
            production_state_changed=False,
            providers_activated=False,
            defaults_changed=False,
            services_restarted=False,
        ),
        evaluation=dict(
            depth="S3",
            mode="shadow/classification-only",
            runnable=True,
            model_calls=0,
            policy_fingerprint="caf978d94106bdb7916818c4d4b98e9ffbf17b8299abd674d9da8dbc16f15b0f",
            source_regression="training/b4artists_ml/results/contact-performance-v3-full-regression.json",
            source_tests=429,
            exact_package_ui="training/b4artists_ml/results/contact-performance-package-ui-trials-v1.json",
        ),
        formal_goal=dict(
            last_signed_round=78,
            next_assessment_due=True,
            pending_reason="signed host assessment owner unavailable",
            state_unchanged=True,
        ),
    )
    (RESULTS / "orchestration-route-contact-performance-v1.json").write_text(json.dumps(route, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(dict(version=meta["version"], archive_sha256=meta["sha256"], native_tests=429, exact_package_tests=17, actual_window_trials=3, correction_max_ms=current["correction_elapsed_max_ms"], callback_max_ms=max(current["suggestion_callback_max_ms"], current["correction_callback_max_ms"]), full_goal_complete=False), indent=2))


if __name__ == "__main__":
    main()
