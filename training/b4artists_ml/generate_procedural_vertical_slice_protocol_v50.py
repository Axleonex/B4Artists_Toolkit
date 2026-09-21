"""Freeze the minimal remaining run torso acceleration correction."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v49.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v50.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v50",
        version="50",
        supersedes="procedural_vertical_slice_protocol_v49.json",
        purpose=(
            "Reduce the remaining midstance-to-toe-off chest acceleration with the smallest "
            "symmetric value change that preserves 3.5 degrees of displayed chest range."
        ),
        development_revision={
            "source": "procedural-vertical-slice-v49-smoke-boneforge-run",
            "upper_body_angular_acceleration_p95_rad_s2": 18.48198245968339,
            "limit_rad_s2": 18.0,
            "peak_interval": [15.21875, 16.03125],
            "all_other_gates_passed": True,
        },
    )
    torso = protocol["full_body_shaping"]["tasks"]["run"]
    for label in ("left support", "right landing", "left landing"):
        torso[label]["torso"] = {
            "spine_pitch_degrees": 0.35,
            "chest_pitch_degrees": 0.7,
        }
    for side in ("left", "right"):
        torso[f"{side} toe-off"]["torso"] = {
            "spine_pitch_degrees": -1.4,
            "chest_pitch_degrees": -2.8,
        }
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
