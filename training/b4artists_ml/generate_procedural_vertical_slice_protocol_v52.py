"""Freeze a bounded dense-arm amplitude correction for angular acceleration."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v51.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v52.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v52",
        version="52",
        supersedes="procedural_vertical_slice_protocol_v51.json",
        purpose=(
            "Reduce only dense arm positional amplitude after the remaining angular-acceleration "
            "peak localized to a forearm-hand segment; preserve cycle timing and torso range."
        ),
        development_revision={
            "source": "procedural-vertical-slice-v51-smoke-boneforge-run",
            "upper_body_angular_acceleration_p95_rad_s2": 18.275838809958568,
            "limit_rad_s2": 18.0,
            "peak_segment": "forearm.def-R -> hand.def-R",
            "displayed_chest_range_degrees": 3.509559516322237,
        },
    )
    protocol["dense_gait_shaping"]["amplitude"] = 0.155
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
