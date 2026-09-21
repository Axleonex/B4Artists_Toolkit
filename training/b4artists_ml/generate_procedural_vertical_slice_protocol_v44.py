"""Freeze three-frame landing transitions ending on shifted midstance anchors."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v43.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v44.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v44",
        version="44",
        supersedes="procedural_vertical_slice_protocol_v43.json",
        purpose=(
            "Use three-frame internal landing transitions ending exactly on midstance; extend "
            "each accepted landing contact to the same endpoint."
        ),
        development_revision={
            "source": "procedural-vertical-slice-v43-smoke-boneforge-run",
            "two_frame_outer_acceleration_body_s2": 0.10448967014961984,
            "limit_body_s2": 0.1,
        },
    )
    run = protocol["tasks"]["run"]
    shifted = {13: 14, 23: 24, 33: 34}
    for pose in run["poses"]:
        old = int(pose["frame"])
        if old in shifted:
            pose["frame"] = shifted[old]
            pose["pelvis"][1] -= 0.05
            for target in pose["limbs"].values():
                target[1] -= 0.05
    run["contacts"] = [
        ["leg-L", 1, 3], ["leg-R", 11, 14], ["leg-L", 21, 24],
        ["leg-R", 31, 34], ["leg-L", 40, 40],
    ]
    transitions = run["flight_transitions"]
    for transition in transitions[:-1]:
        transition["landing_blend_frames"] = 3
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
