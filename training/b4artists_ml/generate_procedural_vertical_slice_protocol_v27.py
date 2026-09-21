"""Freeze the bounded arm-acceleration repair after the v26 host smoke."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v26.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v27.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v27",
        version="27",
        supersedes="procedural_vertical_slice_protocol_v26.json",
        purpose=(
            "Preserve v26 constant-speed run translation and reduce its otherwise useful "
            "bent-arm swing to a gradual six-percent body-length range. Landing keys retain "
            "the incoming swing sign, removing the measured forearm reversal spike."
        ),
    )
    swing = {
        "left support": (-0.020, 0.020),
        "left toe-off": (-0.030, 0.030),
        "left flight-start": (-0.030, 0.030),
        "right pre-land": (-0.015, 0.015),
        "right landing": (-0.010, 0.010),
        "right toe-off": (0.030, -0.030),
        "right flight-start": (0.030, -0.030),
        "left pre-land": (0.015, -0.015),
        "left landing": (0.010, -0.010),
        "left recovery": (-0.020, 0.020),
    }
    poses = {row["label"]: row for row in protocol["tasks"]["run"]["poses"]}
    for label, recipe in protocol["full_body_shaping"]["tasks"]["run"].items():
        pelvis_y = poses[label]["pelvis"][1]
        left, right = swing[label]
        recipe["limbs"]["arm-L"][1] = pelvis_y + left
        recipe["limbs"]["arm-R"][1] = pelvis_y + right
    protocol["development_revision"] = dict(
        source="procedural-vertical-slice-v26-smoke-boneforge-run",
        failed_gate="review_run_angular_acceleration",
        measured_p95_rad_s2=26.706891652394926,
        required_max_rad_s2=18.0,
        change="smaller phase-continuous arm swing; no gate relaxation",
    )
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
