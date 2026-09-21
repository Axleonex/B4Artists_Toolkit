"""Bind v21 to the qualified v5 native-display review and native evidence."""
from pathlib import Path
import hashlib
import json
import math
import os


ROOT = Path(__file__).resolve().parents[2]
TRAIN = ROOT / "training" / "b4artists_ml"
RESULTS = TRAIN / "results"
CASE_ROOT = RESULTS / "procedural-vertical-slice-v21-final"
OUT = RESULTS / "procedural-vertical-slice-v21-focused.json"
PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v21.json"
BUILDER = TRAIN / "build_procedural_vertical_slice_v21.py"
REVIEW_SUMMARY = RESULTS / "review-directed-followup-reviewer-v5" / "human-review-summary-v5-native-display.json"
REVIEW_EXPORT = RESULTS / "human-review-exports" / "b4ml-review-directed-followup-human-review-v5-axlbot.json"
PRESERVED_BASE = RESULTS / "procedural-vertical-slice-v20-final"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    finite_tree(value)
    return value


def finite_tree(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("Nonfinite evidence")
    if isinstance(value, dict):
        for item in value.values():
            finite_tree(item)
    elif isinstance(value, list):
        for item in value:
            finite_tree(item)


def number(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError("Expected finite numeric measurement")
    return value


def predecessor(profile, task):
    version = "v15" if task in {"reach", "land"} else "v17"
    return RESULTS / f"procedural-vertical-slice-{version}" / profile / task / "report.json"


def validate():
    protocol = read(PROTOCOL)
    if (protocol.get("schema") != "procedural-vertical-slice-v21" or
            protocol.get("frozen_before_results") is not True):
        raise ValueError("Unexpected v21 protocol schema")
    if (protocol.get("source_human_review_schema") != "b4ml-human-review-summary-v5" or
            any(protocol.get("source_feedback_qualification", {}).get(key) is not True
                for key in ("global_motion", "jump_height", "relative_pose", "production_acceptance")) or
            protocol.get("training_authorized") is not False or
            protocol.get("model_promotion_authorized") is not False or
            protocol.get("cascadeur_connector_authorized") is not False):
        raise ValueError("v21 authority boundary changed")
    protocol_sha = sha(PROTOCOL)
    gates = protocol["review_directed_gates"]
    expected = [tuple(row) for row in protocol["case_matrix"]]
    if len(expected) != 16 or len(set(expected)) != len(expected):
        raise ValueError("The frozen follow-up case matrix changed")
    fixed = {(p, t) for p in ("boneforge", "rigify_basic", "rigify_default", "imported_unity")
             for t in ("reach", "land", "jump")}
    fixed.update((p, t) for p in ("boneforge", "rigify_basic") for t in ("walk", "run"))
    if set(expected) != fixed:
        raise ValueError("Unexpected follow-up case identity")
    for value in gates.values():
        number(value)

    review = read(REVIEW_SUMMARY)
    export = read(REVIEW_EXPORT)
    if (review.get("schema") != "b4ml-human-review-summary-v5" or
            review.get("complete") is not True or review.get("candidate_acceptable") != 0 or
            review.get("candidate_qualified_acceptance") != 0 or
            review.get("acceptance_contradictions") != 0 or
            review.get("baseline_acceptable") != 0 or export.get("human_authored") is not True or
            len(export.get("cases", [])) != 8 or review.get("training_authorized") is not False or
            review.get("model_promotion_authorized") is not False or
            export.get("prior_exposure") is not True or
            review.get("display_representation_qualified") is not True or
            review.get("relative_pose_feedback_qualified") is not True or
            review.get("global_motion_feedback_qualified") is not True or
            review.get("jump_height_feedback_qualified") is not True or
            review.get("production_acceptance_qualified") is not True or
            review.get("production_candidates_accepted") != 0):
        raise ValueError("Validated Axlbot follow-up evidence is incomplete or widened")
    if (review.get("export_sha256") != sha(REVIEW_EXPORT) or
            export.get("source_data_sha256") != sha(REVIEW_SUMMARY.parent / "review-data.json") or
            export.get("reviewer") != {"id": "Axlbot", "experience": "10+ years"} or
            {c["id"] for c in export["cases"]} != {c["id"] for c in review["cases"]} or
            any(c.get("rating", {}).get("locked") is not True for c in export["cases"])):
        raise ValueError("Human review binding changed")
    process_rows = read(CASE_ROOT / "processes.json")
    process_map = {(row["profile"], row["task"]): row for row in process_rows}
    if len(process_rows) != len(expected) or set(process_map) != set(expected):
        raise ValueError("Process evidence has missing, duplicate or unexpected cases")
    rows = []
    for profile, task in expected:
        report_path = CASE_ROOT / profile / task / "report.json"
        report = read(report_path)
        if report.get("schema") != "procedural-vertical-slice-case-v21":
            raise ValueError(f"Unexpected report schema: {profile}/{task}")
        if report.get("profile") != profile or report.get("task") != task:
            raise ValueError(f"Report identity mismatch: {profile}/{task}")
        if report.get("protocol_sha256") != protocol_sha:
            raise ValueError(f"Stale protocol binding: {profile}/{task}")
        if report.get("builder_sha256") != sha(BUILDER):
            raise ValueError(f"Stale builder binding: {profile}/{task}")
        current_runtime = {path.relative_to(ROOT).as_posix(): sha(path)
                           for path in (ROOT / "b4artists_ml").glob("*.py")}
        if report.get("runtime_sha256") != current_runtime:
            raise ValueError(f"Runtime changed since case generation: {profile}/{task}")
        if report.get("temporal_learned_motion") is not False:
            raise ValueError("Procedural benchmark cannot authorize temporal learning")
        if report.get("complete") is not True or report.get("failures"):
            raise ValueError(f"Incomplete v21 case: {profile}/{task}")
        required_gates = {
            "priority", "pins", "authoring_stretch", "target_preflight", "sampled_stretch",
            "contacts", "contact_plane", "penetration", "flight", "finite_rotation_velocity",
            "memory_counters", "review_jump_height", "review_native_display_jump_height",
            "review_relative_pose_dynamics", "review_run_pelvis_timing",
            "review_land_angular_acceleration", "review_run_angular_acceleration",
            "review_run_pelvis_jerk", "review_reach_flexion", "review_land_timing",
            "review_jump_impact_absorption", "review_land_upper_body_range",
            "review_imported_bends", "review_imported_balance", "review_rigify_basic_jitter",
            "save_reload", "source_restored",
        }
        observed_gates = report.get("automated_gates", {})
        if (set(observed_gates) != required_gates or
                any(value is not True for value in observed_gates.values())):
            raise ValueError(f"A deterministic v21 gate failed: {profile}/{task}")
        if (report.get("source_restored") is not True or
                report.get("save_reload_passed") is not True or
                report.get("anchor_payloads_unchanged") is not True):
            raise ValueError(f"Lifecycle failed: {profile}/{task}")
        shaping = protocol["full_body_shaping"]
        preserved = f"{profile}/{task}" in set(shaping["preserve_exact_cases"])
        recipes = shaping.get("tasks", {}).get(task, {})
        authored = {row["label"]: row for row in report.get("authoring", [])}
        if len(authored) != len(report.get("authoring", [])):
            raise ValueError(f"Duplicate authored labels: {profile}/{task}")
        if preserved and any("torso_shaping" in row for row in authored.values()):
            raise ValueError(f"Accepted case was reshaped: {profile}/{task}")
        if preserved:
            previous = read(PRESERVED_BASE / profile / task / "report.json")
            if (report.get("authoring") != previous.get("authoring") or
                    report.get("priority_frames") != previous.get("priority_frames") or
                    report.get("profile_override") != previous.get("profile_override")):
                raise ValueError(f"Accepted case authoring changed: {profile}/{task}")
        if not preserved:
            for label, recipe in recipes.items():
                if "torso" not in recipe:
                    continue
                evidence = authored.get(label, {}).get("torso_shaping")
                if not isinstance(evidence, dict):
                    raise ValueError(f"Missing coupled torso evidence: {profile}/{task}/{label}")
                coupling = evidence.get("coupling_metrics", {})
                solve_metrics = evidence.get("solve_metrics", {})
                if (number(coupling.get("orientation_error_radians")) > .001 or
                        number(coupling.get("chest_orientation_error_radians")) > .001 or
                        number(solve_metrics.get("pin_error")) > 2e-4):
                    raise ValueError(f"Invalid coupled torso evidence: {profile}/{task}/{label}")
                repinned = evidence.get("repinned_body_targets", [])
                repin_rows = evidence.get("contact_repin", [])
                if repinned and (not repin_rows or
                        any(number(row.get("normalized_error")) >
                            protocol["automated_gates"]["requested_pin_error_body_fraction"]
                            for row in repin_rows)):
                    raise ValueError(f"Invalid contact re-pin evidence: {profile}/{task}/{label}")
        blend_path = CASE_ROOT / profile / task / f"{profile}-{task}.blend"
        if report["blend_path"] != blend_path.relative_to(ROOT).as_posix():
            raise ValueError("Unexpected blend path")
        if sha(blend_path) != report.get("blend_sha256"):
            raise ValueError(f"Blend evidence changed: {profile}/{task}")

        metrics = report["automated_metrics"]
        directed = metrics["review_directed"]
        finite_tree(metrics)
        for value in directed.values():
            if value is not None and not isinstance(value, (dict, list)):
                number(value)
        bounded = {
            "priority_matrix_error": "priority_matrix_error",
            "max_pin_residual": "pin_residual",
            "max_requested_pin_error_body_fraction": "requested_pin_error_body_fraction",
            "max_authoring_stretch": "limb_stretch_fraction",
            "max_sampled_limb_stretch": "limb_stretch_fraction",
            "max_preflight_target_adjustment_body_fraction": "preflight_target_adjustment_body_fraction",
            "contact_plane_spread_body_fraction": "contact_plane_spread_body_fraction",
            "max_penetration_body_fraction": "penetration_body_fraction",
        }
        for metric, limit in bounded.items():
            if not 0 <= number(metrics[metric]) <= number(protocol["automated_gates"][limit]):
                raise ValueError(f"Numeric gate failed: {profile}/{task}/{metric}")
        comparisons = {}
        if task == "jump":
            if directed["native_display_pelvis_apex_rise_body_fraction"] < gates["jump_apex_rise_body_fraction"]:
                raise ValueError(f"Jump height gate failed: {profile}/{task}")
            interval = metrics["flight_report"]["intervals"][0]
            if interval["start"] != 16.0 or interval["end"] != 37.0:
                raise ValueError(f"Jump flight boundary changed: {profile}/{task}")
            pre = directed["jump_preimpact_mean_knee_flexion_degrees"]
            impact = directed["jump_impact_mean_knee_flexion_degrees"]
            absorb = directed["jump_absorb_mean_knee_flexion_degrees"]
            if (pre < gates["jump_preimpact_knee_flexion_degrees"] or
                    impact < gates["jump_impact_knee_flexion_degrees"] or
                    absorb < impact + gates["jump_postimpact_absorption_degrees"]):
                raise ValueError(f"Jump impact absorption gate failed: {profile}/{task}")
        if task == "reach" and directed["reach_elbow_flexion_degrees"] < gates["reach_elbow_flexion_degrees"]:
            raise ValueError(f"Reach remains too straight: {profile}/{task}")
        if task == "land":
            if directed["land_preimpact_vertical_velocity_body_per_second"] >= 0:
                raise ValueError(f"Landing still floats upward before impact: {profile}/{task}")
            pre = directed["land_preimpact_mean_knee_flexion_degrees"]
            impact = directed["land_impact_mean_knee_flexion_degrees"]
            absorb = directed["land_absorb_mean_knee_flexion_degrees"]
            if pre > impact + gates["land_preimpact_flexion_margin_degrees"]:
                raise ValueError(f"Landing bends knees before impact: {profile}/{task}")
            if absorb < impact + gates["land_postimpact_absorption_degrees"]:
                raise ValueError(f"Landing does not absorb after impact: {profile}/{task}")
            interval = metrics["flight_report"]["intervals"][0]
            if interval["start"] != 1.0 or interval["end"] != 7.0:
                raise ValueError(f"Landing flight boundary changed: {profile}/{task}")
            if not preserved:
                if directed["coupled_chest_pitch_range_degrees"] < gates["land_chest_pitch_range_degrees"]:
                    raise ValueError(f"Landing remains too stiff: {profile}/{task}")
                if (directed["upper_body_angular_acceleration_p95_rad_s2"] >
                        gates["land_upper_body_angular_acceleration_p95_rad_s2"]):
                    raise ValueError(f"Landing upper-body acceleration gate failed: {profile}/{task}")
        if task in {"jump", "land", "run"}:
            if (directed["upper_body_angular_p95_rad_s"] >
                    gates[f"{task}_upper_body_angular_p95_rad_s"]):
                raise ValueError(f"Relative-pose motion gate failed: {profile}/{task}")
        if task == "run":
            if directed["pelvis_forward_step_peak_ratio"] > gates["run_pelvis_forward_step_peak_ratio"]:
                raise ValueError(f"Run pelvis timing gate failed: {profile}/{task}")
            if (directed["upper_body_angular_acceleration_p95_rad_s2"] >
                    gates["run_upper_body_angular_acceleration_p95_rad_s2"]):
                raise ValueError(f"Run acceleration gate failed: {profile}/{task}")
            if directed["pelvis_jerk_p95_body_s3"] > gates["run_pelvis_jerk_p95_body_s3"]:
                raise ValueError(f"Run pelvis jerk gate failed: {profile}/{task}")
        if profile == "imported_unity":
            if directed["explicit_bend_alignment_minimum"] < gates["imported_bend_alignment_minimum"]:
                raise ValueError(f"Imported bend direction gate failed: {profile}/{task}")
            if task == "land" and directed["maximum_priority_lateral_torso_tilt_degrees"] > gates["imported_lateral_torso_tilt_degrees"]:
                raise ValueError("Imported landing remains laterally tilted")
        if profile == "rigify_basic" and task in {"walk", "jump"}:
            old = number(read(predecessor(profile, task))["automated_metrics"]["max_rotation_velocity_jump_rad_s"])
            new = number(metrics["max_rotation_velocity_jump_rad_s"])
            if new > old + 1e-9:
                raise ValueError(f"Rigify Basic {task} jitter regressed: {new} > {old}")
            comparisons["rotation_velocity_jump_before"] = old
            comparisons["rotation_velocity_jump_after"] = new

        process = process_map.get((profile, task))
        if (process is None or process.get("complete") is not True or
                process.get("host_exit_qualified") is not True):
            raise ValueError(f"Missing parent process evidence: {profile}/{task}")
        log_path = CASE_ROOT / profile / f"{task}.log"
        if process["log"] != log_path.relative_to(ROOT).as_posix():
            raise ValueError("Unexpected process log path")
        if sha(log_path) != process.get("log_sha256"):
            raise ValueError(f"Process log changed: {profile}/{task}")
        log_text = log_path.read_text(encoding="utf-8", errors="replace")
        if process["host_exit"] != 0:
            marker = json.dumps({key: report.get(key) for key in (
                "profile", "task", "complete", "interaction_count", "scripted_correction_count",
                "failures", "error", "seconds")}, allow_nan=False)
            marker_index = log_text.find(marker)
            crash_index = log_text.find("EXCEPTION_ACCESS_VIOLATION")
            if (process["host_exit"] & 0xffffffff != 0xc0000005 or
                    marker_index < 0 or crash_index <= marker_index or
                    "ucrtbase.dll" not in log_text[crash_index:]):
                raise ValueError(f"Unqualified host exit: {profile}/{task}")
        rows.append({
            "id": f"{profile}/{task}",
            "report": report_path.relative_to(ROOT).as_posix(),
            "report_sha256": sha(report_path),
            "blend": report["blend_path"],
            "blend_sha256": report["blend_sha256"],
            "review_directed": directed,
            "comparisons": comparisons,
            "host_exit": process["host_exit"],
            "source_restored": True,
            "save_reload_passed": True,
            "anchor_payloads_unchanged": True,
        })

    receipt = {
        "schema": "b4ml-review-directed-procedural-vertical-slice-v21-focused",
        "status": "PASS_FOCUSED_DETERMINISTIC",
        "complete": True,
        "cases": rows,
        "passed": len(rows),
        "expected": len(expected),
        "protocol": PROTOCOL.relative_to(ROOT).as_posix(),
        "protocol_sha256": protocol_sha,
        "builder": BUILDER.relative_to(ROOT).as_posix(),
        "builder_sha256": sha(BUILDER),
        "human_review_summary": REVIEW_SUMMARY.relative_to(ROOT).as_posix(),
        "human_review_summary_sha256": sha(REVIEW_SUMMARY),
        "human_review_export": REVIEW_EXPORT.relative_to(ROOT).as_posix(),
        "human_review_export_sha256": sha(REVIEW_EXPORT),
        "review_priorities": [
            {"id": case["id"], "notes": case["notes"]}
            for case in review["cases"] if case["notes"]
        ],
        "claim_boundary": {
            "deterministic_review_directed_gates_pass": True,
            "v5_relative_pose_feedback_used": True,
            "v5_global_motion_feedback_used": True,
            "v5_jump_height_feedback_used": True,
            "v5_production_acceptance_feedback_used": True,
            "native_display_motion_validated": True,
            "accepted_landings_authoring_preserved": True,
            "human_visual_improvement_verified": False,
            "new_human_review_required": True,
            "temporal_model_trained": False,
            "model_promotion_permitted": False,
            "cascadeur_connector_activated": False,
            "cascadeur_parity_verified": False,
            "full_goal_complete": False,
        },
    }
    return receipt


def main():
    if OUT.exists():
        raise RuntimeError("Focused v21 receipt already exists")
    receipt = validate()
    temporary = OUT.with_suffix(".tmp")
    temporary.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, OUT)
    print(json.dumps(receipt, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
