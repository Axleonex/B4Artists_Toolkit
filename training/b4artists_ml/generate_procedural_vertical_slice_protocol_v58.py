"""Freeze Rigify swing-leg toe-off interpolation on top of v57 support damping."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v57.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v58.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v58",
        version="58",
        supersedes="procedural_vertical_slice_protocol_v57.json",
        purpose=(
            "Interpolate the Rigify swing leg through each toe-off while retaining v57's "
            "support-foot damping and leaving accepted BoneForge unchanged."
        ),
        development_revision={
            "source": "procedural-vertical-slice-v57-smoke-rigify-basic-run",
            "measured_result": "lower-limb jerk p95 improved but left-leg peak at frame 35.9375 remained",
            "repair_scope": "Rigify swing-leg targets at toe-off frames 6, 16, 26 and 36",
        },
    )
    protocol["profile_overrides"]["rigify_basic"]["pose_frame_overrides_by_task"] = {
        "run": {
            "6": {
                "limbs": {
                    "leg-L": [0, -0.04, 0.025],
                    "leg-R": [0, -0.3875, 0.09],
                }
            },
            "16": {
                "limbs": {
                    "leg-L": [0, -0.775, 0.1],
                    "leg-R": [0, -0.54, 0.025],
                }
            },
            "26": {
                "limbs": {
                    "leg-L": [0, -1.04, 0.025],
                    "leg-R": [0, -1.275, 0.1],
                }
            },
            "36": {
                "limbs": {
                    "leg-L": [0, -1.775, 0.1],
                    "leg-R": [0, -1.54, 0.025],
                }
            },
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
