"""Materialize the exact locked v11 Codex-browser state as a review export."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json


ROOT = Path(__file__).resolve().parents[2]
TRAIN = ROOT / "training/b4artists_ml"
REVIEW = TRAIN / "results/review-directed-followup-reviewer-v11"
DESTINATION = TRAIN / "results/human-review-exports/b4ml-review-directed-followup-human-review-v11-axlbot.json"

BROWSER_STATE = {
    "rigify_basic/run": {
        "values": {
            "naturalnessA": "4", "naturalnessB": "4",
            "contactA": "3", "contactB": "4",
            "continuityA": "1", "continuityB": "4",
            "intentA": "5", "intentB": "5",
            "acceptableA": "yes", "acceptableB": "yes",
            "correctionsA": "5", "correctionsB": "0",
            "interactionsA": "5", "interactionsB": "0",
            "preference": "B",
            "notes": "Knees on candidate A snap too sharply per step. ",
        },
        "failures": {"A": [], "B": []},
        "locked": True,
        "locked_utc": "2026-09-20T08:19:21.041Z",
        "reveal_seen": True,
        "blind_at_rating": False,
    },
}


def main():
    if DESTINATION.exists():
        raise RuntimeError("Immutable v11 review export already exists: " + str(DESTINATION))
    data = json.loads((REVIEW / "review-data.json").read_text(encoding="utf-8"))
    if set(BROWSER_STATE) != {case["id"] for case in data["cases"]}:
        raise ValueError("Browser capture does not match the v11 case matrix")
    exported = datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
    payload = {
        "schema": "b4ml-review-directed-followup-human-review-v11",
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
