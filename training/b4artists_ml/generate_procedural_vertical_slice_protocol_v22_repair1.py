"""Create the frozen v22 repair-1 protocol from the failed v22 smoke protocol."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v22.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v22_repair1.json"


def set_arm_offsets(recipe, pelvis_y, left, right):
    recipe["limbs"]["arm-L"] = [-0.03, pelvis_y + left, 0.01 if left < 0 else -0.01]
    recipe["limbs"]["arm-R"] = [0.03, pelvis_y + right, 0.01 if right < 0 else -0.01]


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v22-repair1",
        version="22-repair1",
        supersedes="procedural_vertical_slice_protocol_v22.json",
        purpose=(
            "Close the v22 smoke gaps without widening scope: lengthen the jump landing "
            "velocity transition to the next priority pose, use two-frame acceleration-matched "
            "run transitions, and hold bounded counterbalanced arm targets through touchdown."
        ),
    )
    jump_poses = protocol["tasks"]["jump"]["poses"]
    next(row for row in jump_poses if row["label"] == "pre-impact")["frame"] = 41
    protocol["tasks"]["jump"]["flight_transitions"][0]["landing_blend_frames"] = 4

    run = protocol["tasks"]["run"]
    next(row for row in run["poses"] if row["label"] == "right pre-land")["frame"] = 9
    next(row for row in run["poses"] if row["label"] == "left pre-land")["frame"] = 19
    run["flights"] = [[7, 9], [17, 19]]
    for transition in run["flight_transitions"]:
        transition["landing_blend_frames"] = 2
        transition["match_acceleration"] = True

    shaping = protocol["full_body_shaping"]["tasks"]["run"]
    values = {
        "left support": (0, -0.04, 0.04),
        "left toe-off": (-0.0832, -0.02, 0.02),
        "left flight-start": (-0.1248, 0, 0),
        "right pre-land": (-0.1872, 0.04, -0.04),
        "right landing": (-0.208, 0.04, -0.04),
        "right toe-off": (-0.2912, 0.02, -0.02),
        "right flight-start": (-0.3328, 0, 0),
        "left pre-land": (-0.3952, -0.04, 0.04),
        "left landing": (-0.416, -0.04, 0.04),
        "left recovery": (-0.52, -0.02, 0.02),
    }
    for label, (pelvis_y, left, right) in values.items():
        set_arm_offsets(shaping[label], pelvis_y, left, right)
    shaping["right pre-land"]["torso"] = {"spine_pitch_degrees": 1, "chest_pitch_degrees": 2}
    shaping["left pre-land"]["torso"] = {"spine_pitch_degrees": 1, "chest_pitch_degrees": 2}

    gates = protocol["review_directed_gates"]
    gates["flight_transition_velocity_jump_body_per_second"] = 0.02
    gates["run_flight_duration_frames"] = 2
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(
        json.dumps(build(), indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(DESTINATION)


if __name__ == "__main__":
    main()
