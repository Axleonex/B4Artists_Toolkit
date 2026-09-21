"""Freeze four-frame landings with contacts ending at the proven reachable frame."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v45.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v46.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v46",
        version="46",
        supersedes="procedural_vertical_slice_protocol_v45.json",
        purpose=(
            "Keep the four-frame landing blend but release each fixed foot at the v44-proven "
            "reachable frame immediately before the shifted midstance endpoint."
        ),
        development_revision={
            "source": "procedural-vertical-slice-v45-smoke-boneforge-run",
            "remaining_failure": "leg-R fixed contact unreachable at frame 15.25",
            "v44_reachable_contact_end_frames": [14, 24, 34],
        },
    )
    protocol["tasks"]["run"]["contacts"] = [
        ["leg-L", 1, 3], ["leg-R", 11, 14], ["leg-L", 21, 24],
        ["leg-R", 31, 34], ["leg-L", 40, 40],
    ]
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
