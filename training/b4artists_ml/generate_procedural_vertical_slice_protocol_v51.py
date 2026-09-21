"""Freeze projection-safe margins for the final run torso gates."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v50.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v51.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v51",
        version="51",
        supersedes="procedural_vertical_slice_protocol_v50.json",
        purpose=(
            "Add sub-tenth-degree projection-safe margins to both final run torso gates "
            "without changing timing, contacts, speed or cadence."
        ),
        development_revision={
            "source": "procedural-vertical-slice-v50-smoke-boneforge-run",
            "upper_body_angular_acceleration_p95_rad_s2": 18.153054851752056,
            "angular_limit_rad_s2": 18.0,
            "displayed_chest_range_degrees": 3.499556704282753,
            "range_minimum_degrees": 3.5,
        },
    )
    torso = protocol["full_body_shaping"]["tasks"]["run"]
    for label in ("left support", "right landing", "left landing"):
        torso[label]["torso"] = {
            "spine_pitch_degrees": 0.375,
            "chest_pitch_degrees": 0.75,
        }
    for side in ("left", "right"):
        torso[f"{side} toe-off"]["torso"] = {
            "spine_pitch_degrees": -1.38,
            "chest_pitch_degrees": -2.76,
        }
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
