"""Create v22 repair 2 after the repair-1 deterministic smoke failures."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v22_repair1.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v22_repair2.json"


def set_arm_offsets(recipe, pelvis_y, left, right):
    recipe["limbs"]["arm-L"] = [-0.03, pelvis_y + left, 0.005 if left < 0 else -0.005]
    recipe["limbs"]["arm-R"] = [0.03, pelvis_y + right, 0.005 if right < 0 else -0.005]


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v22-repair2",
        version="22-repair2",
        supersedes="procedural_vertical_slice_protocol_v22_repair1.json",
        purpose=(
            "Close the repair-1 smoke failures: keep feet clear during the jump velocity "
            "transition, use validated C1 run transitions, and let coupled torso shaping "
            "provide visible whole-body motion while arm counterbalance remains low-amplitude."
        ),
    )
    preimpact = next(
        row for row in protocol["tasks"]["jump"]["poses"]
        if row["label"] == "pre-impact"
    )
    for limb in ("leg-L", "leg-R"):
        preimpact["limbs"][limb][2] = 0.04

    run = protocol["tasks"]["run"]
    for transition in run["flight_transitions"]:
        transition["match_acceleration"] = False

    shaping = protocol["full_body_shaping"]["tasks"]["run"]
    values = {
        "left support": (0, -0.015, 0.015),
        "left toe-off": (-0.0832, -0.0075, 0.0075),
        "left flight-start": (-0.1248, 0, 0),
        "right pre-land": (-0.1872, 0.015, -0.015),
        "right landing": (-0.208, 0.015, -0.015),
        "right toe-off": (-0.2912, 0.0075, -0.0075),
        "right flight-start": (-0.3328, 0, 0),
        "left pre-land": (-0.3952, -0.015, 0.015),
        "left landing": (-0.416, -0.015, 0.015),
        "left recovery": (-0.52, -0.0075, 0.0075),
    }
    for label, (pelvis_y, left, right) in values.items():
        set_arm_offsets(shaping[label], pelvis_y, left, right)
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
