"""Freeze a Rigify-run-only contact-release smoothing candidate."""
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "procedural_vertical_slice_protocol_v54.json"
DESTINATION = HERE / "procedural_vertical_slice_protocol_v55.json"


def build():
    protocol = json.loads(SOURCE.read_text(encoding="utf-8"))
    protocol.update(
        schema="procedural-vertical-slice-v55",
        version="55",
        supersedes="procedural_vertical_slice_protocol_v54.json",
        purpose=(
            "Preserve the accepted BoneForge v54 run exactly while smoothing only Rigify run "
            "contact releases implicated by the v9 native-display jitter review."
        ),
        development_revision={
            "source_human_review": "b4ml-human-review-summary-v9",
            "accepted_exact_case": "boneforge/run",
            "repair_case": "rigify_basic/run",
            "review_note": "Candidate A jitters to much, not enough natural flow.",
            "localized_release_frames": [15.625, 26.188, 35.938],
        },
    )
    rigify = protocol.setdefault("profile_overrides", {}).setdefault("rigify_basic", {})
    rigify["landing_contact_blend_out_frames_by_task"] = {"run": 0.5}
    rigify["zero_terminal_contact_blend_out_by_task"] = ["run"]
    protocol["preserved_evidence"] = {
        "exact_case": "boneforge/run",
        "source": "procedural-vertical-slice-v54-run-final",
        "reason": "qualified human acceptance in b4ml-human-review-summary-v9",
    }
    protocol["source_human_review"] = {
        "schema": "b4ml-human-review-summary-v9",
        "candidate_qualified_acceptance": 1,
        "rigify_note": "Candidate A jitters to much, not enough natural flow.",
    }
    return protocol


def main():
    if DESTINATION.exists():
        raise RuntimeError("Frozen protocol already exists: " + str(DESTINATION))
    DESTINATION.write_text(json.dumps(build(), indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(DESTINATION)


if __name__ == "__main__":
    main()
