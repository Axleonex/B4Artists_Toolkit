"""Freeze adjacent-anchor flight intervals after v39 validation."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v39.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v40.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v40",
        version="40",
        supersedes="procedural_vertical_slice_protocol_v39.json",
        purpose=(
            "Make each flight span adjacent authored anchors and end stance on its reachable "
            "midstance priority. Landing preparation remains continuous interpolation."
        ),
        development_revision={
            "source": "procedural-vertical-slice-v39-smoke-boneforge-run",
            "flight_failure": "transition still crossed interior pre-land priority",
            "contact_failure": "stance became unreachable at frame 4 after reachable frame-3 midstance",
        },
    )
    run = protocol["tasks"]["run"]
    run["poses"] = [pose for pose in run["poses"] if pose["frame"] not in {9, 19, 29, 39}]
    run["contacts"] = [
        ["leg-L", 1, 3], ["leg-R", 11, 13], ["leg-L", 21, 23],
        ["leg-R", 31, 33], ["leg-L", 40, 40],
    ]
    for transition in run["flight_transitions"]:
        transition["non_priority_shape_frames"] = []
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
