"""Freeze the post-contact ordering correction after v32."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v32.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v33.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v33",
        version="33",
        supersedes="procedural_vertical_slice_protocol_v32.json",
        purpose=(
            "Apply the unchanged layered candidate arm curves after contact refinement, "
            "because physical refinement correctly rebuilt the earlier candidate-only keys."
        ),
        development_revision=dict(
            source="procedural-vertical-slice-v32-smoke-boneforge-run",
            diagnosis="post-generation arm curves were superseded by flight/contact refinement",
            evidence="final priority arm flexion remained zero",
            correction="apply dense arm layer immediately after contact solve and before assessment",
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
