"""Freeze v40 transition-span and final torso-acceleration corrections."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v40.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v41.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v41",
        version="41",
        supersedes="procedural_vertical_slice_protocol_v40.json",
        purpose=(
            "Keep transitions between adjacent anchors with a one-frame post-landing blend, "
            "and redistribute the required torso range to reduce angular acceleration."
        ),
        development_revision={
            "source": "procedural-vertical-slice-v40-smoke-boneforge-run",
            "remaining_failures": [
                "three-frame landing blend crossed frame-13 midstance",
                "upper-body angular acceleration p95 19.8439 above 18",
            ],
            "pelvis_jerk_p95_body_s3": 407.2573,
            "contacts_passed": True,
        },
    )
    run = protocol["tasks"]["run"]
    for transition in run["flight_transitions"]:
        transition["landing_blend_frames"] = 1
    torso = protocol["full_body_shaping"]["tasks"]["run"]
    recipes = {
        "left support": (0.25, 0.5),
        "left midstance": (-0.75, -1.5),
        "left toe-off": (-1.55, -3.1),
        "left flight-start": (-0.5, -1.0),
        "right landing": (0.25, 0.5),
        "right midstance": (-0.75, -1.5),
        "right toe-off": (-1.55, -3.1),
        "right flight-start": (-0.5, -1.0),
        "left landing": (0.25, 0.5),
    }
    for label, (spine, chest) in recipes.items():
        torso[label]["torso"] = {
            "spine_pitch_degrees": spine,
            "chest_pitch_degrees": chest,
        }
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
