"""Freeze the candidate-slot correction after the v31 no-op evidence."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v31.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v32.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v32",
        version="32",
        supersedes="procedural_vertical_slice_protocol_v31.json",
        purpose=(
            "Write the unchanged dense gait rotations through the candidate action's "
            "layered slot/channelbag so they persist into physical refinement while the "
            "source action remains untouched."
        ),
        development_revision=dict(
            source="procedural-vertical-slice-v31-smoke-boneforge-run",
            diagnosis="pose-bone key insertion did not persist in the isolated layered candidate slot",
            evidence="priority arm flexion remained zero despite a shaping receipt",
            correction="write deterministic dense samples via workflow.action_curves",
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
