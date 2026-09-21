"""Freeze the terminal-boundary correction for v41."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v41.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v42.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v42",
        version="42",
        supersedes="procedural_vertical_slice_protocol_v41.json",
        purpose=(
            "Retain one-frame velocity matching on internal landings and disable it only on "
            "the terminal landing where no authored frame exists after frame 40."
        ),
        development_revision={
            "source": "procedural-vertical-slice-v41-smoke-boneforge-run",
            "failure": "terminal landing transition extended beyond authored frame range",
        },
    )
    transitions = protocol["tasks"]["run"]["flight_transitions"]
    transitions[-1]["landing_blend_frames"] = 0
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
