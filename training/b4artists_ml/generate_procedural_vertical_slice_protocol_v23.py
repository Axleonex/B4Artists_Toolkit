"""Freeze the collision-aware impact timing protocol derived from v22 repair 2."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v22_repair2.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v23.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v23",
        version="23",
        supersedes="procedural_vertical_slice_protocol_v22_repair2.json",
        purpose=(
            "Apply the v6 review literally: retain ballistic motion through first foot "
            "impact, absorb only support-normal momentum at contact, and continue pelvis, "
            "knee, chest, and arm follow-through after impact."
        ),
    )
    jump = protocol["tasks"]["jump"]
    jump["flights"] = [[16, 43]]
    jump["flight_transitions"] = [dict(
        takeoff_blend_frames=0,
        landing_blend_frames=6,
        match_acceleration=True,
        contact_impulse_strength=1.0,
        collision_strength=0.0,
        collision_clearance=0.0,
        non_priority_shape_frames=[37, 41],
    )]
    preimpact = next(row for row in jump["poses"] if row["label"] == "pre-impact")
    for limb in ("leg-L", "leg-R"):
        preimpact["limbs"][limb][2] = 0.0
    crouch = next(row for row in jump["poses"] if row["label"] == "absorb crouch")
    crouch["limbs"] = {
        "leg-L": [0.0, -0.05, 0.0],
        "leg-R": [0.0, -0.05, 0.0],
    }

    shaping = protocol["full_body_shaping"]["tasks"]["jump"]
    shaping["impact"]["torso"] = dict(spine_pitch_degrees=-2.5, chest_pitch_degrees=-5)
    shaping["absorb crouch"]["torso"] = dict(spine_pitch_degrees=-5, chest_pitch_degrees=-10)
    shaping["follow-through"]["torso"] = dict(spine_pitch_degrees=1.5, chest_pitch_degrees=3)
    for label, z in (("impact", -0.015), ("absorb crouch", -0.07), ("follow-through", -0.02)):
        shaping[label]["limbs"]["arm-L"][2] = z
        shaping[label]["limbs"]["arm-R"][2] = z
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
