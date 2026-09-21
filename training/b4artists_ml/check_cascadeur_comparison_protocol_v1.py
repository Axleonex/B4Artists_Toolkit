"""Validate the prospective matched Cascadeur comparison before any result exists."""
from pathlib import Path
import hashlib
import json
from urllib.parse import urlparse


HERE = Path(__file__).resolve()
TRAIN = HERE.parent
ROOT = HERE.parents[2]
PROTOCOL = TRAIN / "cascadeur_comparison_protocol_v1.json"
VERTICAL_PROTOCOL = TRAIN / "procedural_vertical_slice_protocol_v12.json"
AGGREGATE = TRAIN / "results/procedural-vertical-slice-v12/aggregate.json"
OUT = TRAIN / "results/cascadeur-comparison-protocol-validation-v1.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists():
        raise RuntimeError("Cascadeur comparison protocol validation already exists")
    protocol = json.loads(PROTOCOL.read_text(encoding="utf-8-sig"))
    vertical = json.loads(VERTICAL_PROTOCOL.read_text(encoding="utf-8-sig"))
    aggregate = json.loads(AGGREGATE.read_text(encoding="utf-8-sig"))
    if protocol["schema"] != "b4ml-cascadeur-matched-comparison-protocol-v1" or protocol["status"] != "prospective-not-run":
        raise ValueError("Comparison protocol must remain prospective")
    if protocol["results"] is not None or protocol["parity_verified"] or protocol["surpasses_verified"] or protocol["full_goal_complete"]:
        raise ValueError("Unrun comparison cannot contain a result or claim")
    if sha(AGGREGATE) != protocol["b4ml"]["vertical_slice_sha256"]:
        raise ValueError("Vertical-slice source identity mismatch")
    if not sha(VERTICAL_PROTOCOL) == protocol["b4ml"]["protocol_sha256"] == aggregate["protocol_sha256"]:
        raise ValueError("Vertical-slice protocol identity mismatch")
    if protocol["tasks"] != list(vertical["tasks"]):
        raise ValueError("Matched task order changed")
    sources = protocol["cascadeur"]["official_sources"]
    if len(sources) != len(set(sources)) or len(sources) < 5:
        raise ValueError("Official comparison sources are incomplete")
    if any(urlparse(url).scheme != "https" or urlparse(url).netloc != "cascadeur.com" for url in sources):
        raise ValueError("Comparison research must cite official Cascadeur sources")
    characters = protocol["portable_characters"]
    if characters["minimum"] < 3 or len(characters["required_variation"]) != characters["minimum"] or not characters["same_mesh_and_skeleton_per_matched_pair"]:
        raise ValueError("Portable character matrix is not matched")
    scene = protocol["common_scene"]
    if (scene["fps"], scene["frame_start"], scene["frame_end"]) != (30, 1, 25) or scene["input_pose_matrix_tolerance"] > 1e-5:
        raise ValueError("Common scene contract changed")
    metrics = protocol["automated_metrics"] + protocol["human_metrics"]
    required = {"priority_pose_matrix_error", "contact_drift_limb_fraction", "penetration_body_fraction",
                "limb_stretch_fraction", "rotation_velocity_jump_rad_s", "naturalness_1_to_5",
                "intent_preservation_1_to_5", "actual_corrective_edits", "actual_interactions",
                "active_work_seconds", "blind_overall_preference"}
    if not required <= set(metrics) or len(metrics) != len(set(metrics)):
        raise ValueError("Matched metric set is incomplete or duplicated")
    human = protocol["human_protocol"]
    if human["independent_animators_minimum"] < 3 or human["matched_cases_per_animator"] != 24 or not all(
            human[key] for key in ("method_labels_hidden", "pair_order_balanced", "same_camera_mesh_timing_and_playback",
                                   "ratings_locked_before_identity_reveal", "hands_on_sessions_counterbalanced")):
        raise ValueError("Human comparison protocol is too weak")
    gates = protocol["claim_gates"]
    if (gates["parity"]["no_median_human_dimension_deficit_greater_than"] > 0.25 or
            gates["surpasses"]["minimum_named_human_quality_dimensions_with_median_gain_of_0_25"] < 2 or
            gates["surpasses"]["required_efficiency_reduction_percent"] < 20 or
            gates["surpasses"]["minimum_task_families_supporting_each_claim"] < 6):
        raise ValueError("Comparison claim gates were weakened")
    if len(protocol["blocked_comparisons"]) < 4:
        raise ValueError("Known comparison blockers were not retained")
    report = {
        "schema": "b4ml-cascadeur-comparison-protocol-validation-v1",
        "complete": True,
        "prospective": True,
        "tasks": len(protocol["tasks"]),
        "portable_characters_required": characters["minimum"],
        "matched_cases_per_animator": human["matched_cases_per_animator"],
        "independent_animators_required": human["independent_animators_minimum"],
        "automated_metrics": len(protocol["automated_metrics"]),
        "human_metrics": len(protocol["human_metrics"]),
        "official_sources": len(sources),
        "source_vertical_slice_exact": True,
        "claim_gates_frozen_before_results": True,
        "results_present": False,
        "parity_verified": False,
        "surpasses_verified": False,
        "full_goal_complete": False,
        "protocol_sha256": sha(PROTOCOL),
        "checker_sha256": sha(HERE)
    }
    temp = OUT.with_suffix(".tmp")
    temp.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temp.replace(OUT)
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
