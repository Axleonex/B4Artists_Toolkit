"""Freeze the v7-directed run de-skipping repair on top of v25."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v25.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v26.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v26",
        version="26",
        supersedes="procedural_vertical_slice_protocol_v25.json",
        source_human_review_schema="b4ml-human-review-summary-v7",
        purpose=(
            "Preserve the accepted v25 Rigify Basic jump and repair the rejected run "
            "slice: constant forward pelvis spacing removes the visible speed pulse, "
            "while smoothly phased bent-arm targets restore gait counter-swing without "
            "the abrupt v24 world-space reversal."
        ),
    )
    run = protocol["tasks"]["run"]
    layout = {
        "left support": (1, [0, 0, -0.04], {"leg-R": [0, -0.16, 0.06]}),
        "left toe-off": (8, [0, -0.126, -0.02], {"leg-R": [0, -0.226, 0.08]}),
        "left flight-start": (10, [0, -0.162, 0], {"leg-R": [0, -0.262, 0.09]}),
        "right pre-land": (14, [0, -0.234, -0.015], {"leg-L": [0, -0.366, 0.07], "leg-R": [0, -0.304, 0.02]}),
        "right landing": (16, [0, -0.27, -0.04], {"leg-L": [0, -0.402, 0.07], "leg-R": [0, -0.322, 0]}),
        "right toe-off": (24, [0, -0.414, -0.02], {"leg-L": [0, -0.514, 0.08]}),
        "right flight-start": (26, [0, -0.45, 0], {"leg-L": [0, -0.55, 0.09]}),
        "left pre-land": (30, [0, -0.522, -0.015], {"leg-L": [0, -0.592, 0.02], "leg-R": [0, -0.654, 0.07]}),
        "left landing": (32, [0, -0.558, -0.04], {"leg-L": [0, -0.61, 0], "leg-R": [0, -0.69, 0.07]}),
        "left recovery": (40, [0, -0.702, -0.02], {"leg-R": [0, -0.802, 0.06]}),
    }
    for pose in run["poses"]:
        frame, pelvis, limbs = layout[pose["label"]]
        pose["frame"] = frame
        pose["pelvis"] = pelvis
        pose["limbs"] = limbs
    run["contacts"] = [["leg-L", 1, 8], ["leg-R", 16, 24], ["leg-L", 32, 40]]

    # The hand target includes root progression.  Its relative swing changes sign
    # over a full support phase instead of during the two-frame landing interval.
    swing = {
        "left support": (-0.030, 0.030),
        "left toe-off": (-0.050, 0.050),
        "left flight-start": (-0.050, 0.050),
        "right pre-land": (-0.025, 0.025),
        "right landing": (0.000, 0.000),
        "right toe-off": (0.050, -0.050),
        "right flight-start": (0.050, -0.050),
        "left pre-land": (0.025, -0.025),
        "left landing": (0.000, 0.000),
        "left recovery": (-0.030, 0.030),
    }
    shaping = protocol["full_body_shaping"]["tasks"]["run"]
    for label, recipe in shaping.items():
        pelvis_y = layout[label][1][1]
        left, right = swing[label]
        recipe["limbs"] = {
            "arm-L": [-0.03, pelvis_y + left, -0.02],
            "arm-R": [0.03, pelvis_y + right, -0.02],
        }
    protocol["review_directed_gates"]["run_forward_step_peak_ratio"] = 1.25
    protocol["preserved_evidence"] = dict(
        exact_case="rigify_basic/jump",
        source="procedural-vertical-slice-v25-final",
        reason="qualified human acceptance in b4ml-human-review-summary-v7",
    )
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
