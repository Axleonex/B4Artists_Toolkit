"""Materialize the exact locked v9 Codex-browser state as a review export."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json


ROOT = Path(__file__).resolve().parents[2]
TRAIN = ROOT / "training/b4artists_ml"
REVIEW = TRAIN / "results/review-directed-followup-reviewer-v9"
DESTINATION = TRAIN / "results/human-review-exports/b4ml-review-directed-followup-human-review-v9-axlbot.json"

BROWSER_STATE = {
    "boneforge/run": {
        "values": {
            "naturalnessA": "1", "naturalnessB": "4",
            "contactA": "1", "contactB": "5",
            "continuityA": "1", "continuityB": "5",
            "intentA": "1", "intentB": "5",
            "acceptableA": "no", "acceptableB": "yes",
            "correctionsA": "8", "correctionsB": "0",
            "interactionsA": "7", "interactionsB": "0",
            "preference": "B",
            "notes": "Candidate A is skipping not running",
        },
        "failures": {"A": [], "B": []},
        "locked": True,
        "locked_utc": "2026-09-20T07:39:43.022Z",
        "reveal_seen": True,
        "blind_at_rating": False,
    },
    "rigify_basic/run": {
        "values": {
            "naturalnessA": "3", "naturalnessB": "1",
            "contactA": "3", "contactB": "1",
            "continuityA": "2", "continuityB": "2",
            "intentA": "3", "intentB": "2",
            "acceptableA": "no", "acceptableB": "no",
            "correctionsA": "6", "correctionsB": "10",
            "interactionsA": "5", "interactionsB": "10",
            "preference": "neither",
            "notes": "Candidate A jitters to much, not enough natural flow. Candidate B is just giving hoping movements. ",
        },
        "failures": {"A": [], "B": []},
        "locked": True,
        "locked_utc": "2026-09-20T07:45:10.663Z",
        "reveal_seen": True,
        "blind_at_rating": False,
    },
}


def main():
    if DESTINATION.exists():
        raise RuntimeError("Immutable v9 review export already exists: " + str(DESTINATION))
    data = json.loads((REVIEW / "review-data.json").read_text(encoding="utf-8"))
    if set(BROWSER_STATE) != {case["id"] for case in data["cases"]}:
        raise ValueError("Browser capture does not match the v9 case matrix")
    exported = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    payload = {
        "schema": "b4ml-review-directed-followup-human-review-v9",
        "source_data_sha256": hashlib.sha256((REVIEW / "review-data.json").read_bytes()).hexdigest(),
        "source_qualification_sha256": data["source_qualification_sha256"],
        "source_human_review_sha256": data["source_human_review_sha256"],
        "native_display_validated": True,
        "prior_exposure": True,
        "reviewer": {"id": "Axlbot", "experience": "10+ years"},
        "exported_utc": exported,
        "complete": True,
        "human_authored": True,
        "training_authorized": False,
        "model_promotion_authorized": False,
        "cases": [
            {
                "id": case["id"],
                "rating": BROWSER_STATE[case["id"]],
                "revealed_identity": case["reveal"],
            }
            for case in data["cases"]
        ],
    }
    with DESTINATION.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(DESTINATION)


if __name__ == "__main__":
    main()
