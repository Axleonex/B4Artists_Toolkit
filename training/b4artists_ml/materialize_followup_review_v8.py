"""Materialize the exact locked v8 Codex-browser state as a review export."""
from pathlib import Path
import hashlib
import json


ROOT = Path(__file__).resolve().parents[2]
TRAIN = ROOT / "training/b4artists_ml"
REVIEW = TRAIN / "results/review-directed-followup-reviewer-v8"
DESTINATION = TRAIN / "results/human-review-exports/b4ml-review-directed-followup-human-review-v8-axlbot.json"
EXPORTED_UTC = "2026-09-20T05:08:43.404Z"

BROWSER_STATE = {
    "boneforge/run": {
        "values": {
            "naturalnessA": "3", "naturalnessB": "3",
            "contactA": "3", "contactB": "3",
            "continuityA": "2", "continuityB": "3",
            "intentA": "3", "intentB": "3",
            "acceptableA": "no", "acceptableB": "no",
            "correctionsA": "7", "correctionsB": "7",
            "interactionsA": "7", "interactionsB": "7",
            "preference": "neither",
            "notes": "It looks more like skipping instead of running ",
        },
        "failures": {"A": [], "B": []},
        "locked": True,
        "locked_utc": "2026-09-20T05:05:27.584Z",
        "reveal_seen": True,
        "blind_at_rating": False,
    },
    "rigify_basic/run": {
        "values": {
            "naturalnessA": "3", "naturalnessB": "3",
            "contactA": "3", "contactB": "3",
            "continuityA": "3", "continuityB": "3",
            "intentA": "3", "intentB": "3",
            "acceptableA": "no", "acceptableB": "no",
            "correctionsA": "8", "correctionsB": "8",
            "interactionsA": "8", "interactionsB": "8",
            "preference": "neither",
            "notes": "It looks more like skipping instead of running ",
        },
        "failures": {"A": [], "B": []},
        "locked": True,
        "locked_utc": "2026-09-20T05:06:01.266Z",
        "reveal_seen": True,
        "blind_at_rating": False,
    },
}


def main():
    if DESTINATION.exists():
        raise RuntimeError("Immutable v8 review export already exists: " + str(DESTINATION))
    data = json.loads((REVIEW / "review-data.json").read_text(encoding="utf-8"))
    payload = {
        "schema": "b4ml-review-directed-followup-human-review-v8",
        "source_data_sha256": hashlib.sha256(
            (REVIEW / "review-data.json").read_bytes()
        ).hexdigest(),
        "source_qualification_sha256": data["source_qualification_sha256"],
        "source_human_review_sha256": data["source_human_review_sha256"],
        "native_display_validated": True,
        "prior_exposure": True,
        "reviewer": {"id": "Axlbot", "experience": "10+ years"},
        "exported_utc": EXPORTED_UTC,
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
    if set(BROWSER_STATE) != {case["id"] for case in data["cases"]}:
        raise ValueError("Browser capture does not match the v8 case matrix")
    with DESTINATION.open("x", encoding="utf-8") as stream:
        json.dump(payload, stream, indent=2, allow_nan=False)
        stream.write("\n")
    print(DESTINATION)


if __name__ == "__main__":
    main()
