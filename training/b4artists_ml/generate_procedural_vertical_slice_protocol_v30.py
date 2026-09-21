"""Freeze the binding-shape correction after the v29 fail-closed host smoke."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v29.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v30.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v30",
        version="30",
        supersedes="procedural_vertical_slice_protocol_v29.json",
        purpose=(
            "Retry the unchanged dense candidate-only gait request after deriving semantic "
            "arm lengths from evaluated joints instead of expecting a non-public binding key."
        ),
        development_revision=dict(
            source="procedural-vertical-slice-v29-smoke-boneforge-run",
            failure="KeyError: lengths",
            correction="derive upper/lower lengths from evaluated semantic joint heads",
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
