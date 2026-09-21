"""Create the frozen v22 protocol from the accepted v21 repair-2 baseline."""
import copy
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v21_repair2.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v22.json"


def run_pose(frame, label, pelvis_y, pelvis_z, limbs):
    return {
        "frame": frame,
        "label": label,
        "pelvis": [0, pelvis_y, pelvis_z],
        "limbs": limbs,
        "yaw_degrees": 0,
    }


def run_shape(spine, chest, pelvis_y, arm_left, arm_right):
    return {
        "torso": {
            "spine_pitch_degrees": spine,
            "chest_pitch_degrees": chest,
        },
        "limbs": {
            "arm-L": [-0.03, pelvis_y + arm_left, 0.015 if arm_left < 0 else -0.015],
            "arm-R": [0.03, pelvis_y + arm_right, 0.015 if arm_right < 0 else -0.015],
        },
    }


def build():
    protocol = copy.deepcopy(json.loads(SOURCE.read_text(encoding="utf-8")))
    protocol.update(
        schema="procedural-vertical-slice-v22",
        version="22",
        purpose=(
            "Use Axlbot's qualified v6 native-display review for a bounded continuity repair: "
            "match ballistic jump exit velocity into authored landing motion, and replace the "
            "run's hop-like long flights with short transitioned flights, even stride placement, "
            "and visible whole-body counterbalance. Preserve previously accepted landing evidence."
        ),
        source_human_review_schema="b4ml-human-review-summary-v6",
        supersedes="procedural_vertical_slice_protocol_v21_repair2.json",
    )
    protocol["case_matrix"] = [
        ["boneforge", "jump"],
        ["rigify_basic", "jump"],
        ["rigify_default", "jump"],
        ["imported_unity", "jump"],
        ["boneforge", "run"],
        ["rigify_basic", "run"],
    ]
    protocol["preserved_evidence"] = {
        "source": "training/b4artists_ml/results/procedural-vertical-slice-v21-repair2-focused.json",
        "accepted_cases": ["rigify_default/land", "imported_unity/land"],
        "unchanged_cases": [
            "boneforge/reach",
            "boneforge/land",
            "boneforge/walk",
            "rigify_basic/reach",
            "rigify_basic/land",
            "rigify_basic/walk",
            "rigify_default/reach",
            "imported_unity/reach",
        ],
    }
    protocol["tasks"]["jump"]["flight_transitions"] = [
        {
            "takeoff_blend_frames": 0,
            "landing_blend_frames": 3,
            "match_acceleration": False,
        }
    ]

    protocol["tasks"]["run"] = {
        "poses": [
            run_pose(1, "left support", 0, -0.04, {"leg-R": [0, -0.16, 0.06]}),
            run_pose(5, "left toe-off", -0.0832, -0.02, {"leg-R": [0, -0.21, 0.08]}),
            run_pose(7, "left flight-start", -0.1248, 0, {"leg-R": [0, -0.23, 0.09]}),
            run_pose(10, "right pre-land", -0.1872, -0.015, {
                "leg-L": [0, -0.32, 0.07], "leg-R": [0, -0.25, 0.02]
            }),
            run_pose(11, "right landing", -0.208, -0.04, {
                "leg-L": [0, -0.34, 0.07], "leg-R": [0, -0.26, 0]
            }),
            run_pose(15, "right toe-off", -0.2912, -0.02, {"leg-L": [0, -0.39, 0.08]}),
            run_pose(17, "right flight-start", -0.3328, 0, {"leg-L": [0, -0.41, 0.09]}),
            run_pose(20, "left pre-land", -0.3952, -0.015, {
                "leg-L": [0, -0.51, 0.02], "leg-R": [0, -0.45, 0.07]
            }),
            run_pose(21, "left landing", -0.416, -0.04, {
                "leg-L": [0, -0.52, 0], "leg-R": [0, -0.47, 0.07]
            }),
            run_pose(26, "left recovery", -0.52, -0.025, {"leg-R": [0, -0.50, 0.06]}),
        ],
        "contacts": [
            ["leg-L", 1, 5],
            ["leg-R", 11, 15],
            ["leg-L", 21, 26],
        ],
        "flights": [[7, 10], [17, 20]],
        "flight_transitions": [
            {
                "takeoff_blend_frames": 2,
                "landing_blend_frames": 1,
                "match_acceleration": False,
            },
            {
                "takeoff_blend_frames": 2,
                "landing_blend_frames": 1,
                "match_acceleration": False,
            },
        ],
    }

    run = protocol["full_body_shaping"]["tasks"]["run"] = {
        "left support": run_shape(1, 2, 0, -0.06, 0.06),
        "left toe-off": run_shape(-1, -2, -0.0832, -0.03, 0.03),
        "left flight-start": run_shape(-0.5, -1, -0.1248, 0, 0),
        "right pre-land": run_shape(0.5, 1, -0.1872, 0.03, -0.03),
        "right landing": run_shape(1, 2, -0.208, 0.06, -0.06),
        "right toe-off": run_shape(-1, -2, -0.2912, 0.03, -0.03),
        "right flight-start": run_shape(-0.5, -1, -0.3328, 0, 0),
        "left pre-land": run_shape(0.5, 1, -0.3952, -0.03, 0.03),
        "left landing": run_shape(1, 2, -0.416, -0.06, 0.06),
        "left recovery": run_shape(0.5, 1, -0.52, -0.03, 0.03),
    }
    assert len(run) == len(protocol["tasks"]["run"]["poses"])

    protocol["review_directed_gates"].update(
        flight_transition_velocity_jump_body_per_second=1e-4,
        run_chest_pitch_range_degrees=3.5,
        run_flight_duration_frames=3,
        run_stride_contact_delta_spread_body_fraction=0.021,
    )
    protocol["training_authorized"] = False
    protocol["model_promotion_authorized"] = False
    protocol["cascadeur_connector_authorized"] = False
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
