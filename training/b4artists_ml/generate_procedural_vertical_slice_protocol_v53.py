"""Freeze exact contact starts for cross-rig final-landing reachability."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v52.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v53.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v53",
        version="53",
        supersedes="procedural_vertical_slice_protocol_v52.json",
        purpose=(
            "Disable the cosmetic pre-contact fade that sampled Rigify's final landing before "
            "its declared frame; preserve exact intervals and all force-transition coverage."
        ),
        development_revision={
            "source": "procedural-vertical-slice-v52-smoke-rigify-basic-run",
            "boneforge_v52_complete": True,
            "remaining_failure": "Rigify leg-L final contact unreachable only at fade-in sample 39.5",
            "declared_final_contact": ["leg-L", 40, 40],
        },
    )
    run = protocol["tasks"]["run"]
    run["landing_contact_blend_frames"] = 0
    run["landing_contact_blend_out_frames"] = 0
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
