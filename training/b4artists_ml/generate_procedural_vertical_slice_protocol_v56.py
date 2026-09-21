"""Freeze Rigify-only toe-off target damping after release blending proved unreachable."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v55.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v56.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v56",
        version="56",
        supersedes="procedural_vertical_slice_protocol_v55.json",
        purpose=(
            "Keep exact Rigify contacts and damp only the first unconstrained toe-off foot target; "
            "preserve accepted BoneForge v54 byte-for-byte."
        ),
        development_revision={
            "source": "procedural-vertical-slice-v55-smoke-rigify-basic-run-release1",
            "rejected_approach": "0.5-frame release contact was unreachable at frame 15.25",
            "repair_scope": "Rigify toe-off foot targets only",
        },
    )
    rigify = protocol["profile_overrides"]["rigify_basic"]
    rigify.pop("landing_contact_blend_out_frames_by_task", None)
    rigify.pop("zero_terminal_contact_blend_out_by_task", None)
    rigify["pose_overrides_by_task"] = {
        "run": {
            "right toe-off": {"limbs": {"leg-R": [0, -0.54, 0.025]}},
            "left toe-off": {"limbs": {"leg-L": [0, -1.04, 0.025]}},
        }
    }
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
