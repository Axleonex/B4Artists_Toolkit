"""Freeze the writable-control correction after v33."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v33.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v34.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v34",
        version="34",
        supersedes="procedural_vertical_slice_protocol_v33.json",
        purpose=(
            "Apply the unchanged dense gait geometry to mapped writable FK controls, "
            "while measuring the evaluated semantic joints used by final assessment."
        ),
        development_revision=dict(
            source="procedural-vertical-slice-v33-smoke-boneforge-run",
            diagnosis="dense curves targeted evaluated deform joints instead of writable FK controls",
            evidence="post-contact priority arm flexion remained zero",
            correction="write row.fk controls and verify row.joints flexion immediately",
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
