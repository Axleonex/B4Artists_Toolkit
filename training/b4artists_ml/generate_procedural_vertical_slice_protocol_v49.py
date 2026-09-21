"""Freeze a localized toe-off-to-flight torso correction on the v47 pass."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v47.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v49.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v49",
        version="49",
        supersedes="procedural_vertical_slice_protocol_v48.json",
        purpose=(
            "Preserve the v47 landing and midstance COM that passed flight continuity; change "
            "only the identified toe-off-to-flight torso key to remove its angular snap."
        ),
        development_revision={
            "source": "procedural-vertical-slice-v47-smoke-boneforge-run",
            "v48_rejected": "midstance torso change regressed flight acceleration continuity",
            "v47_upper_body_angular_acceleration_p95_rad_s2": 20.465100389965883,
            "limit_rad_s2": 18.0,
            "peak_interval": [26.59375, 27.40625],
        },
    )
    torso = protocol["full_body_shaping"]["tasks"]["run"]
    for side in ("left", "right"):
        torso[f"{side} flight-start"]["torso"] = {
            "spine_pitch_degrees": -1.25,
            "chest_pitch_degrees": -2.5,
        }
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
