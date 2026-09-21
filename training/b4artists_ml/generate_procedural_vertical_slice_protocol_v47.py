"""Freeze four-frame landings with exact, unblended contact releases."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v46.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v47.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v47",
        version="47",
        supersedes="procedural_vertical_slice_protocol_v46.json",
        purpose=(
            "Cover each four-frame landing transition with its landing contact while disabling "
            "the extra quarter-frame release blend that exceeded reachable leg range."
        ),
        development_revision={
            "source": "procedural-vertical-slice-v45-smoke-boneforge-run",
            "remaining_failure": "fixed contact was reachable at frame 15 but not at release sample 15.25",
            "v46_result": "shortening the contact violated the contact-impulse coverage invariant",
        },
    )
    run = protocol["tasks"]["run"]
    run["contacts"] = [
        ["leg-L", 1, 3], ["leg-R", 11, 15], ["leg-L", 21, 25],
        ["leg-R", 31, 35], ["leg-L", 40, 40],
    ]
    run["landing_contact_blend_out_frames"] = 0
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
