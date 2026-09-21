"""Independent integrity checks for weak motion-label proposal artifacts.

SPDX-License-Identifier: GPL-2.0-or-later
"""
from collections import Counter
from pathlib import Path
import hashlib
import json
import sys


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results/motion-label-proposals-v1"
REPORT_OUT = ROOT / "results/motion-label-proposals-contract-v1/report.json"
sys.path.insert(0, str(ROOT))

from build_motion_label_proposals_v1 import build_review_queue, proposal_candidates


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    plan = read(ROOT / "motion_label_proposals_plan_v1.json")
    split = read(ROOT / "results/hierarchy-cohorts-v1/split.json")
    layout = read(ROOT / "results/full-hierarchy-store-v1/layout.json")
    report = read(OUT / "report.json")
    proposals = read(OUT / "proposals.json")
    queue = read(OUT / "review-queue.json")
    training = set(split["training_subjects"])
    development = set(split["development_subjects"])
    rows = proposals["clips"]
    items = queue["items"]

    assert sha256(OUT / report["artifacts"]["proposals"]["path"]) == report["artifacts"]["proposals"]["sha256"]
    assert sha256(OUT / report["artifacts"]["review_queue"]["path"]) == report["artifacts"]["review_queue"]["sha256"]
    assert {row["subject"] for row in rows} == training
    assert not ({row["subject"] for row in rows} & development)
    assert not ({item["subject"] for item in items} & development)
    assert len(rows) == report["training_clips"] == 1392
    assert report["ineligible_training_clips"] == 2
    assert {item["kind"] for item in items} == set(plan["review_queue"]["quotas"])
    assert Counter(item["kind"] for item in items) == Counter(report["review_queue_counts"])
    assert all(item["review_status"] == "unreviewed" for item in items)
    assert all(item["reviewed_label"] is None for item in items)
    assert all(item["ground_truth"] is False and item["provenance"] == "heuristic" for item in items)
    assert max(item["confidence"] for item in items) <= plan["heuristic_confidence_ceiling"]
    assert proposals["development_pose_arrays_read"] is False
    assert proposals["confirmation_read"] is False
    assert report["scene_geometry_inferred"] is False
    assert report["hand_contacts_inferred"] is False

    source_rows = {row["clip"]: row for row in layout["entries"]}
    candidates = []
    proposal_identities = set()
    dense_forbidden = {"probability", "contact", "height", "speed", "positions", "rotations"}
    for row in rows:
        assert not dense_forbidden.intersection(row)
        candidates.extend(proposal_candidates(source_rows[row["clip"]], row, plan))
        for item in row["contacts"]:
            proposal_identities.add(("contact_" + item["side"], row["clip"], item["start"], item["end"]))
        for item in row["events"]:
            proposal_identities.add((item["kind"], row["clip"], item["flight_start"], item["flight_end"]))
        for item in row["static"]:
            proposal_identities.add(("static", row["clip"], item["start"], item["end"]))
        for group in (row["contacts"], row["events"], row["static"]):
            assert all(item["ground_truth"] is False for item in group)
            assert all(item["provenance"] == "heuristic" for item in group)
            assert all(item["confidence"] <= plan["heuristic_confidence_ceiling"] for item in group)
    assert all((item["kind"], item["clip"], item["start"], item["end"]) in proposal_identities for item in items)

    rebuilt = build_review_queue(candidates, plan)
    assert rebuilt == items
    assert len({item["selection_hash"] for item in items}) == len(items)
    assert [item["review_id"] for item in items] == [f"weak-motion-v1-{index:04d}" for index in range(1, len(items) + 1)]
    expected_ineligible = {
        row["clip"] for row in layout["entries"]
        if row["subject"] in training and row["frames"] < 2
    }
    assert {row["clip"] for row in proposals["ineligible_clips"]} == expected_ineligible

    result = {
        "passed": True,
        "eligible_training_clips": len(rows),
        "training_subjects": len(training),
        "development_subjects_excluded": len(development),
        "queue_items": len(items),
        "queue_reproduced_exactly": True,
        "queue_identities_present_in_proposals": True,
        "dense_frame_arrays_not_serialized": True,
        "all_confidence_within_heuristic_ceiling": True,
        "all_items_unreviewed": True,
        "scene_and_hand_contact_claims_absent": True,
        "validation_read": False,
        "confirmation_read": False,
        "model_fit": False,
        "runtime_changed": False,
        "full_goal_complete": False,
        "sources": {
            "checker": sha256(Path(__file__)),
            "plan": sha256(ROOT / "motion_label_proposals_plan_v1.json"),
            "report": sha256(OUT / "report.json"),
            "proposals": sha256(OUT / "proposals.json"),
            "review_queue": sha256(OUT / "review-queue.json"),
        },
    }
    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
