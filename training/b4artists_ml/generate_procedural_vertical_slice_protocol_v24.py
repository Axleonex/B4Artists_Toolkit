"""Freeze the v6-directed extended, symmetric run repair on top of v23."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v23.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v24.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v24",
        version="24",
        supersedes="procedural_vertical_slice_protocol_v23.json",
        purpose=(
            "Preserve v23 jump/contact behavior and replace the short run hops with "
            "two symmetric six-frame flights, consistent stride spacing, landing "
            "support impulses, and slower visible chest/arm counter-motion."
        ),
    )
    run = protocol["tasks"]["run"]
    layout = {
        "left support": (1, [0, 0, -0.04], {"leg-R": [0, -0.16, 0.06]}),
        "left toe-off": (8, [0, -0.10, -0.02], {"leg-R": [0, -0.2268, 0.08]}),
        "left flight-start": (10, [0, -0.14, 0], {"leg-R": [0, -0.2452, 0.09]}),
        "right pre-land": (14, [0, -0.26, -0.015], {"leg-L": [0, -0.3928, 0.07], "leg-R": [0, -0.3228, 0.02]}),
        "right landing": (16, [0, -0.28, -0.04], {"leg-L": [0, -0.412, 0.07], "leg-R": [0, -0.332, 0]}),
        "right toe-off": (24, [0, -0.40, -0.02], {"leg-L": [0, -0.4988, 0.08]}),
        "right flight-start": (26, [0, -0.44, 0], {"leg-L": [0, -0.5172, 0.09]}),
        "left pre-land": (30, [0, -0.56, -0.015], {"leg-L": [0, -0.6748, 0.02], "leg-R": [0, -0.6148, 0.07]}),
        "left landing": (32, [0, -0.58, -0.04], {"leg-L": [0, -0.684, 0], "leg-R": [0, -0.634, 0.07]}),
        "left recovery": (40, [0, -0.70, -0.025], {"leg-R": [0, -0.68, 0.06]}),
    }
    for pose in run["poses"]:
        frame, pelvis, limbs = layout[pose["label"]]
        pose["frame"] = frame; pose["pelvis"] = pelvis; pose["limbs"] = limbs
    run["contacts"] = [["leg-L", 1, 8], ["leg-R", 16, 24], ["leg-L", 32, 40]]
    run["flights"] = [[10, 16], [26, 32]]
    run["landing_contact_blend_frames"] = 2
    run["flight_transitions"] = [
        dict(takeoff_blend_frames=0, landing_blend_frames=6, match_acceleration=True,
             contact_impulse_strength=1.0, collision_strength=0.0,
             collision_clearance=0.0, non_priority_shape_frames=[14]),
        dict(takeoff_blend_frames=0, landing_blend_frames=6, match_acceleration=True,
             contact_impulse_strength=1.0, collision_strength=0.0,
             collision_clearance=0.0, non_priority_shape_frames=[30]),
    ]
    chest = {
        "left support": 3, "left toe-off": -4, "left flight-start": -2,
        "right pre-land": 3, "right landing": 3, "right toe-off": -4,
        "right flight-start": -2, "left pre-land": 3, "left landing": 3,
        "left recovery": 1,
    }
    arm_offsets = {
        "left support": (-.02, .02), "left toe-off": (-.025, .025),
        "left flight-start": (-.02, .02), "right pre-land": (.02, -.02),
        "right landing": (.04, -.04), "right toe-off": (.025, -.025),
        "right flight-start": (.02, -.02), "left pre-land": (-.02, .02),
        "left landing": (-.04, .04), "left recovery": (-.01, .01),
    }
    shaping = protocol["full_body_shaping"]["tasks"]["run"]
    for label, recipe in shaping.items():
        pelvis_y = layout[label][1][1]
        recipe["torso"] = dict(
            spine_pitch_degrees=chest[label] / 2,
            chest_pitch_degrees=chest[label],
        )
        left, right = arm_offsets[label]
        recipe["limbs"] = {
            "arm-L": [-0.03, pelvis_y + left, 0.01 if left > 0 else -0.01],
            "arm-R": [0.03, pelvis_y + right, 0.01 if right > 0 else -0.01],
        }
    protocol["review_directed_gates"]["run_flight_duration_frames"] = 6
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
