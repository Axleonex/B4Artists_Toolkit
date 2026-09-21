"""Freeze dense local gait shaping after sparse hand-target failures."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v28.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v29.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v29",
        version="29",
        supersedes="procedural_vertical_slice_protocol_v28.json",
        purpose=(
            "Keep constant-speed v26 root translation, remove sparse world-space hand "
            "targets, and apply a bounded dense FK arm swing directly to the isolated "
            "candidate before contact and flight refinement."
        ),
    )
    for recipe in protocol["full_body_shaping"]["tasks"]["run"].values():
        recipe["limbs"] = {}
    protocol["dense_gait_shaping"] = dict(
        schema="b4ml-dense-arm-swing-request-v1",
        task="run",
        first_frame=1,
        last_frame=40,
        cycle_frames=31.0,
        amplitude=0.10,
        drop=0.52,
        outward=0.12,
        source_action_unchanged=True,
        candidate_only=True,
    )
    protocol["development_revision"] = dict(
        sources=[
            "procedural-vertical-slice-v26-smoke-boneforge-run",
            "procedural-vertical-slice-v27-smoke-boneforge-run",
            "procedural-vertical-slice-v28-smoke-boneforge-run",
        ],
        failed_gate="review_run_angular_acceleration",
        diagnosis="sparse world-space hand IK reverses at landing",
        change="dense FK shoulder/elbow shaping before physical refinement",
        gate_relaxed=False,
    )
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
