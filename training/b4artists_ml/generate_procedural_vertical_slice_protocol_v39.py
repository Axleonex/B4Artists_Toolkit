"""Freeze the v38 flight-anchor and acceleration corrections."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v38.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v39.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v39",
        version="39",
        supersedes="procedural_vertical_slice_protocol_v38.json",
        purpose=(
            "Start flight on its authored flight-start anchor and reduce vertical/torso key "
            "amplitudes to satisfy the existing jerk and angular-acceleration limits."
        ),
        development_revision={
            "source": "procedural-vertical-slice-v38-smoke-boneforge-run",
            "remaining_failures": [
                "flight transition crossed frame-7 priority",
                "upper-body angular acceleration p95 25.5937",
                "pelvis jerk p95 2073.8177",
            ],
        },
    )
    run = protocol["tasks"]["run"]
    run["flights"] = [[7, 11], [17, 21], [27, 31], [37, 40]]
    z_by_phase = {
        "support": -0.01,
        "landing": -0.01,
        "midstance": -0.025,
        "toe-off": 0.0,
        "flight-start": 0.01,
        "pre-land": 0.0,
    }
    for pose in run["poses"]:
        for phase, value in z_by_phase.items():
            if phase in pose["label"]:
                pose["pelvis"][2] = value
                break
    torso = protocol["full_body_shaping"]["tasks"]["run"]
    recipes = {
        "left support": (0.5, 1.0),
        "left midstance": (-1.0, -2.0),
        "left toe-off": (-1.5, -3.0),
        "left flight-start": (-0.5, -1.0),
        "right pre-land": (0.5, 1.0),
        "right landing": (0.5, 1.0),
        "right midstance": (-1.0, -2.0),
        "right toe-off": (-1.5, -3.0),
        "right flight-start": (-0.5, -1.0),
        "left pre-land": (0.5, 1.0),
        "left landing": (0.5, 1.0),
    }
    for label, (spine, chest) in recipes.items():
        torso.setdefault(label, {"limbs": {}})["torso"] = {
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
