"""Freeze two-frame internal velocity transitions after v42 measurement."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v42.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v43.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v43",
        version="43",
        supersedes="procedural_vertical_slice_protocol_v42.json",
        purpose=(
            "Lengthen the three internal post-landing velocity transitions to two frames so "
            "outer acceleration stays below the existing 0.1-body-unit limit."
        ),
        development_revision={
            "source": "procedural-vertical-slice-v42-smoke-boneforge-run",
            "one_frame_outer_acceleration_body_s2": 0.4202561781919919,
            "limit_body_s2": 0.1,
            "terminal_transition_unchanged": 0,
        },
    )
    transitions = protocol["tasks"]["run"]["flight_transitions"]
    for transition in transitions[:-1]:
        transition["landing_blend_frames"] = 2
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
