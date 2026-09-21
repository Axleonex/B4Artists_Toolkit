"""Freeze frame-addressed Rigify toe-off damping."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v56.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v57.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v57",
        version="57",
        supersedes="procedural_vertical_slice_protocol_v56.json",
        purpose=(
            "Address each repeated Rigify toe-off by exact frame so both strides receive the "
            "correct absolute target while accepted BoneForge remains unchanged."
        ),
        development_revision={
            "source": "procedural-vertical-slice-v56",
            "rejected_approach": "pose labels repeat across strides and are ambiguous",
            "repair_scope": "Rigify toe-off foot targets at frames 6, 16, 26 and 36",
        },
    )
    rigify = protocol["profile_overrides"]["rigify_basic"]
    rigify.pop("pose_overrides_by_task", None)
    rigify["pose_frame_overrides_by_task"] = {
        "run": {
            "6": {"limbs": {"leg-L": [0, -0.04, 0.025]}},
            "16": {"limbs": {"leg-R": [0, -0.54, 0.025]}},
            "26": {"limbs": {"leg-L": [0, -1.04, 0.025]}},
            "36": {"limbs": {"leg-R": [0, -1.54, 0.025]}},
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
