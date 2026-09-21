"""Freeze the declared-layer priority gate after v34."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v34.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v35.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v35",
        version="35",
        supersedes="procedural_vertical_slice_protocol_v34.json",
        purpose=(
            "Qualify the intentional post-contact arm layer with a split priority gate: "
            "all non-arm semantic matrices must remain exact, only four mapped FK controls "
            "may be written, and final evaluated arm flexion must remain bounded."
        ),
        declared_layer_priority_gate=dict(
            schema="b4ml-declared-arm-layer-priority-v1",
            minimum_flexion_degrees=60.0,
            maximum_flexion_degrees=130.0,
            maximum_written_controls=4,
            require_source_action_unchanged=True,
            preserve_legacy_result=True,
        ),
        development_revision=dict(
            source="procedural-vertical-slice-v34-smoke-boneforge-run",
            legacy_priority_result=False,
            reason="the legacy exact matrix gate includes the intentionally changed arms",
            replacement="exact non-arm matrices plus bounded declared arm controls and flexion",
            gate_relaxed=False,
        ),
    )
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
