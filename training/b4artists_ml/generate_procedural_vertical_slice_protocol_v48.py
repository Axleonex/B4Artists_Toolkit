"""Freeze a smooth run torso cycle while retaining visible chest range."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v47.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v48.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v48",
        version="48",
        supersedes="procedural_vertical_slice_protocol_v47.json",
        purpose=(
            "Remove the one-frame toe-off-to-flight torso snap while retaining at least "
            "3.5 degrees of visible coupled chest range."
        ),
        development_revision={
            "source": "procedural-vertical-slice-v47-smoke-boneforge-run",
            "passed": ["contacts", "flight continuity", "run speed", "cadence", "pelvis jerk"],
            "upper_body_angular_acceleration_p95_rad_s2": 20.465100389965883,
            "limit_rad_s2": 18.0,
            "peak_segment": "chest -> neck",
            "peak_interval": [26.59375, 27.40625],
        },
    )
    torso = protocol["full_body_shaping"]["tasks"]["run"]
    recipes = {
        "left support": (0.25, 0.5),
        "left midstance": (-1.25, -2.5),
        "left toe-off": (-1.55, -3.1),
        "left flight-start": (-1.25, -2.5),
        "right landing": (0.25, 0.5),
        "right midstance": (-1.25, -2.5),
        "right toe-off": (-1.55, -3.1),
        "right flight-start": (-1.25, -2.5),
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
