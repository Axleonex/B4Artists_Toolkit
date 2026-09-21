"""Freeze the reachability correction for v36's faster stance cycle."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v36.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v37.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v37",
        version="37",
        supersedes="procedural_vertical_slice_protocol_v36.json",
        purpose=(
            "End each high-speed stance one frame before the authored toe-off pose so fixed "
            "contacts remain anatomically reachable without stretching or moving the pin."
        ),
        development_revision={
            "source": "procedural-vertical-slice-v36-smoke-boneforge-run",
            "failure": "fixed contact unreachable at frame 6 by 0.0439898 body lengths",
            "repair": "five-frame stance followed by a five-frame aerial transition",
        },
    )
    run = protocol["tasks"]["run"]
    run["contacts"] = [
        ["leg-L", 1, 5], ["leg-R", 11, 15], ["leg-L", 21, 25],
        ["leg-R", 31, 35], ["leg-L", 40, 40],
    ]
    run["flights"] = [[6, 11], [16, 21], [26, 31], [36, 40]]
    for pose in run["poses"]:
        if pose["frame"] in {6, 16, 26, 36}:
            support = "leg-L" if pose["frame"] in {6, 26} else "leg-R"
            contact_position = -0.05 * (pose["frame"] - 1) + 0.23
            pose["limbs"][support] = [0, contact_position, 0.04]
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
