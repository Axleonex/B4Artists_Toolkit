"""Freeze a cadence-correct run redesign after both v35 runs remained skips."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v35.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v36.json"


def pose(frame, label, pelvis_y, pelvis_z, limbs):
    return {
        "frame": frame,
        "label": label,
        "pelvis": [0, pelvis_y, pelvis_z],
        "limbs": limbs,
        "yaw_degrees": 0,
    }


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v36",
        version="36",
        supersedes="procedural_vertical_slice_protocol_v35.json",
        purpose=(
            "Replace the rejected slow skip-like run with a 180-step-per-minute, "
            "1.5-body-length-per-second stance/flight cycle. Preserve all non-run cases."
        ),
        source_human_review={
            "schema": "b4ml-human-review-summary-v8",
            "candidate_qualified_acceptance": 0,
            "repeated_note": "It looks more like skipping instead of running",
        },
        run_mechanics_gate={
            "minimum_forward_speed_body_per_second": 1.35,
            "maximum_forward_speed_body_per_second": 1.65,
            "minimum_step_cadence_per_minute": 165.0,
            "maximum_step_cadence_per_minute": 190.0,
            "minimum_flight_fraction": 0.25,
            "maximum_flight_fraction": 0.5,
        },
    )
    run = protocol["tasks"]["run"]
    run["poses"] = [
        pose(1, "left support", 0.00, -0.02, {"leg-R": [0, 0.12, 0.08]}),
        pose(3, "left midstance", -0.10, -0.05, {"leg-R": [0, -0.05, 0.12]}),
        pose(6, "left toe-off", -0.25, -0.015, {"leg-R": [0, -0.40, 0.10]}),
        pose(7, "left flight-start", -0.30, 0.02, {"leg-L": [0, -0.02, 0.04], "leg-R": [0, -0.50, 0.08]}),
        pose(9, "right pre-land", -0.40, 0.00, {"leg-L": [0, -0.10, 0.07], "leg-R": [0, -0.55, 0.03]}),
        pose(11, "right landing", -0.50, -0.02, {"leg-L": [0, -0.25, 0.10], "leg-R": [0, -0.55, 0.00]}),
        pose(13, "right midstance", -0.60, -0.05, {"leg-L": [0, -0.45, 0.12]}),
        pose(16, "right toe-off", -0.75, -0.015, {"leg-L": [0, -0.90, 0.10]}),
        pose(17, "right flight-start", -0.80, 0.02, {"leg-L": [0, -1.00, 0.08], "leg-R": [0, -0.52, 0.04]}),
        pose(19, "left pre-land", -0.90, 0.00, {"leg-L": [0, -1.05, 0.03], "leg-R": [0, -0.60, 0.07]}),
        pose(21, "left landing", -1.00, -0.02, {"leg-L": [0, -1.05, 0.00], "leg-R": [0, -0.75, 0.10]}),
        pose(23, "left midstance", -1.10, -0.05, {"leg-R": [0, -0.95, 0.12]}),
        pose(26, "left toe-off", -1.25, -0.015, {"leg-R": [0, -1.40, 0.10]}),
        pose(27, "left flight-start", -1.30, 0.02, {"leg-L": [0, -1.02, 0.04], "leg-R": [0, -1.50, 0.08]}),
        pose(29, "right pre-land", -1.40, 0.00, {"leg-L": [0, -1.10, 0.07], "leg-R": [0, -1.55, 0.03]}),
        pose(31, "right landing", -1.50, -0.02, {"leg-L": [0, -1.25, 0.10], "leg-R": [0, -1.55, 0.00]}),
        pose(33, "right midstance", -1.60, -0.05, {"leg-L": [0, -1.45, 0.12]}),
        pose(36, "right toe-off", -1.75, -0.015, {"leg-L": [0, -1.90, 0.10]}),
        pose(37, "right flight-start", -1.80, 0.02, {"leg-L": [0, -2.00, 0.08], "leg-R": [0, -1.52, 0.04]}),
        pose(39, "left pre-land", -1.90, 0.00, {"leg-L": [0, -2.05, 0.03], "leg-R": [0, -1.60, 0.07]}),
        pose(40, "left landing", -1.95, -0.02, {"leg-L": [0, -2.05, 0.00], "leg-R": [0, -1.70, 0.10]}),
    ]
    run["contacts"] = [
        ["leg-L", 1, 6], ["leg-R", 11, 16], ["leg-L", 21, 26],
        ["leg-R", 31, 36], ["leg-L", 40, 40],
    ]
    transition = {
        "takeoff_blend_frames": 0,
        "landing_blend_frames": 3,
        "match_acceleration": True,
        "contact_impulse_strength": 0.65,
        "collision_strength": 0.0,
        "collision_clearance": 0.0,
        "non_priority_shape_frames": [],
    }
    run["flights"] = [[7, 11], [17, 21], [27, 31], [37, 40]]
    run["flight_transitions"] = [dict(transition) for _ in run["flights"]]
    run["landing_contact_blend_frames"] = 1
    run["landing_contact_blend_out_frames"] = 1

    shaping = protocol["full_body_shaping"]["tasks"]["run"]
    shaping.update({
        "left midstance": {"torso": {"spine_pitch_degrees": -2, "chest_pitch_degrees": -4}, "limbs": {}},
        "right midstance": {"torso": {"spine_pitch_degrees": -2, "chest_pitch_degrees": -4}, "limbs": {}},
    })
    protocol["dense_gait_shaping"].update(
        last_frame=40,
        cycle_frames=20.0,
        amplitude=0.16,
    )
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
