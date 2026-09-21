"""Bind the v18 procedural candidate to the validated Axlbot follow-up priorities."""
from pathlib import Path
import hashlib
import json
import math
import os


ROOT = Path(__file__).resolve().parents[2]
TRAIN = ROOT / "training" / "b4artists_ml"
RESULTS = TRAIN / "results"
CASE_ROOT = RESULTS / "procedural-vertical-slice-v18"
OUT = RESULTS / "procedural-vertical-slice-v18-focused.json"
PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v18.json"
BUILDER = TRAIN / "build_procedural_vertical_slice_v18.py"
REVIEW_SUMMARY = RESULTS / "review-directed-followup-reviewer-v1" / "human-review-summary-v1.json"
REVIEW_EXPORT = RESULTS / "human-review-exports" / "b4ml-review-directed-followup-human-review-v1-axlbot.json"


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
    if (protocol.get("schema") != "procedural-vertical-slice-v18" or
            protocol.get("frozen_before_results") is not True):
        raise ValueError("Unexpected v18 protocol schema")
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
    if (review.get("complete") is not True or review.get("validated") is not True or
            review.get("reviewed_cases") != 16 or export.get("human_authored") is not True or
            len(export.get("cases", [])) != 16 or review.get("training_or_promotion_authorized") is not False):
        raise ValueError("Validated Axlbot follow-up evidence is incomplete or widened")
    if (review.get("human_review_sha256") != sha(REVIEW_EXPORT) or
            review.get("source_data_sha256") != export.get("source_data_sha256") or
            export.get("source_data_sha256") != sha(REVIEW_SUMMARY.parent / "review-data.json") or
            export.get("reviewer") != review.get("reviewer") or
            {c["id"] for c in export["cases"]} != {f"{p}/{t}" for p, t in fixed} or
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
        if report.get("schema") != "procedural-vertical-slice-case-v18":
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
            raise ValueError(f"Incomplete v18 case: {profile}/{task}")
        required_gates = {
            "priority", "pins", "authoring_stretch", "target_preflight", "sampled_stretch",
            "contacts", "contact_plane", "penetration", "flight", "finite_rotation_velocity",
            "memory_counters", "review_jump_height", "review_reach_flexion", "review_land_timing",
            "review_imported_bends", "review_imported_balance", "review_rigify_basic_jitter",
            "save_reload", "source_restored",
        }
        observed_gates = report.get("automated_gates", {})
        if (set(observed_gates) != required_gates or
                any(value is not True for value in observed_gates.values())):
            raise ValueError(f"A deterministic v18 gate failed: {profile}/{task}")
        if (report.get("source_restored") is not True or
                report.get("save_reload_passed") is not True or
                report.get("anchor_payloads_unchanged") is not True):
            raise ValueError(f"Lifecycle failed: {profile}/{task}")
        blend_path = CASE_ROOT / profile / task / f"{profile}-{task}.blend"
        if report["blend_path"] != blend_path.relative_to(ROOT).as_posix():
            raise ValueError("Unexpected blend path")
        if sha(blend_path) != report.get("blend_sha256"):
            raise ValueError(f"Blend evidence changed: {profile}/{task}")

        metrics = report["automated_metrics"]
        directed = metrics["review_directed"]
        finite_tree(metrics)
        for key, value in directed.items():
            if key != "frames" and value is not None:
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
            if directed["jump_apex_rise_body_fraction"] < gates["jump_apex_rise_body_fraction"]:
                raise ValueError(f"Jump height gate failed: {profile}/{task}")
            interval = metrics["flight_report"]["intervals"][0]
            if interval["start"] != 7.0 or interval["end"] != 29.0:
                raise ValueError(f"Jump flight boundary changed: {profile}/{task}")
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
        "schema": "b4ml-review-directed-procedural-vertical-slice-v18-focused",
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
        "review_priorities": review["next_engineering_priorities"],
        "claim_boundary": {
            "deterministic_review_directed_gates_pass": True,
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
        raise RuntimeError("Focused v18 receipt already exists")
    receipt = validate()
    temporary = OUT.with_suffix(".tmp")
    temporary.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, OUT)
    print(json.dumps(receipt, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
