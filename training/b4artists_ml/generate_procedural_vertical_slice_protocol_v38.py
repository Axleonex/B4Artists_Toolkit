"""Freeze the bounded reach and transition corrections for v37."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v37.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v38.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v38",
        version="38",
        supersedes="procedural_vertical_slice_protocol_v37.json",
        purpose=(
            "Keep v37 cadence while bounding the trailing leg to verified reach, ending stance "
            "before frame-5 overextension, and declaring pre-land anchors as flight-shape keys."
        ),
        development_revision={
            "source": "procedural-vertical-slice-v37-smoke-boneforge-run",
            "contact_failure": "leg-L unreachable at frame 5",
            "preflight_peak_body_fraction": 0.05367158031329779,
            "transition_failure": "pre-land priority crossed by landing transition",
        },
    )
    run = protocol["tasks"]["run"]
    run["contacts"] = [
        ["leg-L", 1, 4], ["leg-R", 11, 14], ["leg-L", 21, 24],
        ["leg-R", 31, 34], ["leg-L", 40, 40],
    ]
    for transition, frame in zip(run["flight_transitions"], (9, 19, 29, 39)):
        transition["non_priority_shape_frames"] = [frame]
    for pose in run["poses"]:
        frame = int(pose["frame"])
        if frame in {7, 17, 27, 37}:
            support = "leg-L" if frame in {7, 27} else "leg-R"
            pose["limbs"][support][1] -= 0.10
        if frame in {9, 19, 29, 39}:
            trailing = "leg-L" if frame in {9, 29} else "leg-R"
            pose["limbs"][trailing][1] -= 0.10
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
