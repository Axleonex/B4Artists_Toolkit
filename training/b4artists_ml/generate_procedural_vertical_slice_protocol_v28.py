"""Freeze the second bounded arm-acceleration repair after the v27 host smoke."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v27.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v28.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v28",
        version="28",
        supersedes="procedural_vertical_slice_protocol_v27.json",
        purpose=(
            "Retain v26 constant-speed translation and bent elbows while reducing the "
            "counter-swing to a four-percent body-length range. Pre-land and landing use "
            "the same target so impact cannot introduce a hand-target reversal."
        ),
    )
    swing = {
        "left support": (-0.015, 0.015),
        "left toe-off": (-0.020, 0.020),
        "left flight-start": (-0.020, 0.020),
        "right pre-land": (-0.010, 0.010),
        "right landing": (-0.010, 0.010),
        "right toe-off": (0.020, -0.020),
        "right flight-start": (0.020, -0.020),
        "left pre-land": (0.010, -0.010),
        "left landing": (0.010, -0.010),
        "left recovery": (-0.015, 0.015),
    }
    poses = {row["label"]: row for row in protocol["tasks"]["run"]["poses"]}
    for label, recipe in protocol["full_body_shaping"]["tasks"]["run"].items():
        pelvis_y = poses[label]["pelvis"][1]
        left, right = swing[label]
        recipe["limbs"]["arm-L"][1] = pelvis_y + left
        recipe["limbs"]["arm-R"][1] = pelvis_y + right
    # v26 accidentally added an unused look-alike key. Keep only the existing,
    # enforced review gate used by the v21 assessment engine.
    protocol["review_directed_gates"].pop("run_forward_step_peak_ratio", None)
    protocol["development_revision"] = dict(
        source="procedural-vertical-slice-v27-smoke-boneforge-run",
        failed_gate="review_run_angular_acceleration",
        measured_p95_rad_s2=23.468985509942957,
        required_max_rad_s2=18.0,
        change="smaller landing-continuous arm swing; no gate relaxation",
    )
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
