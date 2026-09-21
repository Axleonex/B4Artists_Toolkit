"""Freeze the layered-action compatibility correction after v30."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v30.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v31.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v31",
        version="31",
        supersedes="procedural_vertical_slice_protocol_v30.json",
        purpose=(
            "Retry the unchanged dense gait request after removing legacy Action.fcurves "
            "access; pose-bone key insertion already targets the active layered action."
        ),
        development_revision=dict(
            source="procedural-vertical-slice-v30-smoke-boneforge-run",
            failure="AttributeError: Action has no fcurves",
            correction="use layered-action-compatible pose-bone key insertion only",
            motion_request_changed=False,
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
