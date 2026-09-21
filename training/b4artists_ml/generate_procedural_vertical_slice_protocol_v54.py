"""Freeze cross-rig angular-acceleration margin for dense arm swing."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v53.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v54.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v54",
        version="54",
        supersedes="procedural_vertical_slice_protocol_v53.json",
        purpose=(
            "Give the dense arm layer enough amplitude margin to satisfy the angular-acceleration "
            "gate on both BoneForge and Rigify while preserving its cadence and phase."
        ),
        development_revision={
            "source": "procedural-vertical-slice-v53-smoke-rigify-basic-run",
            "rigify_upper_body_angular_acceleration_p95_rad_s2": 18.258338919758092,
            "limit_rad_s2": 18.0,
            "all_other_rigify_gates_passed": True,
        },
    )
    protocol["dense_gait_shaping"]["amplitude"] = 0.15
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
