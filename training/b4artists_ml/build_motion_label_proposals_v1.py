"""Build weak train-only label proposals and an unreviewed review queue.

SPDX-License-Identifier: GPL-2.0-or-later
"""
from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import sys
import time

import numpy as np


ROOT = Path(__file__).resolve().parent
HERE = Path(__file__).resolve()
PLAN_PATH = ROOT / "motion_label_proposals_plan_v1.json"
SPLIT_PATH = ROOT / "results/hierarchy-cohorts-v1/split.json"
LAYOUT_PATH = ROOT / "results/full-hierarchy-store-v1/layout.json"
STORE_REPORT_PATH = ROOT / "results/full-hierarchy-store-v1/report.json"
OUT = ROOT / "results/motion-label-proposals-v1"
sys.path.insert(0, str(ROOT))

from full_hierarchy_store_v1 import FullHierarchyStore
from motion_label_proposals_v1 import HEURISTIC_CONFIDENCE_CEILING, clip_proposals


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def duration_band(frames, boundaries):
    if frames <= boundaries[0]:
        return "short"
    if frames <= boundaries[1]:
        return "medium"
    return "long"


def candidate_hash(seed, item):
    identity = "|".join(
        str(value)
        for value in (
            seed,
            item["kind"],
            item["duration_band"],
            item["primary_tag"],
            item["clip"],
            item["start"],
            item["end"],
        )
    )
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def build_review_queue(candidates, plan):
    """Select a reproducible, stratum-balanced queue without reading dev poses."""
    seed = plan["review_queue"]["seed"]
    quotas = plan["review_queue"]["quotas"]
    maximum_per_subject = plan["review_queue"]["maximum_per_subject_per_kind"]
    by_kind = defaultdict(list)
    for item in candidates:
        item = dict(item)
        item["selection_hash"] = candidate_hash(seed, item)
        by_kind[item["kind"]].append(item)
    selected = []
    for kind, quota in quotas.items():
        groups = defaultdict(list)
        for item in by_kind[kind]:
            groups[(item["duration_band"], item["primary_tag"])].append(item)
        for values in groups.values():
            values.sort(key=lambda item: item["selection_hash"])
        strata = sorted(
            groups,
            key=lambda key: hashlib.sha256(
                f"{seed}|{kind}|{key[0]}|{key[1]}".encode("utf-8")
            ).hexdigest(),
        )
        subject_counts = Counter()
        while len([item for item in selected if item["kind"] == kind]) < quota:
            changed = False
            for key in strata:
                values = groups[key]
                chosen = None
                for index, item in enumerate(values):
                    if subject_counts[item["subject"]] < maximum_per_subject:
                        chosen = values.pop(index)
                        break
                if chosen is None:
                    continue
                chosen["review_status"] = "unreviewed"
                chosen["reviewed_label"] = None
                selected.append(chosen)
                subject_counts[chosen["subject"]] += 1
                changed = True
                if len([item for item in selected if item["kind"] == kind]) >= quota:
                    break
            if not changed:
                break
    selected.sort(key=lambda item: (list(quotas).index(item["kind"]), item["selection_hash"]))
    for index, item in enumerate(selected, 1):
        item["review_id"] = f"weak-motion-v1-{index:04d}"
    return selected


def proposal_candidates(row, proposals, plan):
    base = {
        "clip": row["clip"],
        "subject": row["subject"],
        "description": row["description"],
        "motion_tags": row["motion_tags"],
        "primary_tag": next((tag for tag in row["motion_tags"] if tag != "other"), "other"),
        "source_path": row["source_path"],
        "source_sha256": row["source_sha256"],
        "dt": proposals["dt"],
        "provenance": "heuristic",
        "ground_truth": False,
    }
    boundaries = plan["review_queue"]["duration_band_frames"]
    result = []
    for item in proposals["contacts"]:
        result.append(
            {
                **base,
                **item,
                "kind": "contact_" + item["side"],
                "duration_band": duration_band(item["frames"], boundaries),
            }
        )
    for item in proposals["events"]:
        result.append(
            {
                **base,
                **item,
                "start": item["flight_start"],
                "end": item["flight_end"],
                "duration_band": duration_band(item["flight_frames"], boundaries),
            }
        )
    for item in proposals["static"]:
        result.append(
            {
                **base,
                **item,
                "duration_band": duration_band(item["frames"], boundaries),
            }
        )
    return result


def main():
    started = time.perf_counter()
    plan = json.loads(PLAN_PATH.read_text())
    split = json.loads(SPLIT_PATH.read_text())
    expected = plan["sources"]
    checks = {
        "builder": sha256(HERE),
        "module": sha256(ROOT / "motion_label_proposals_v1.py"),
        "contract": sha256(ROOT / "check_motion_label_proposals_v1.py"),
        "split": sha256(SPLIT_PATH),
        "layout": sha256(LAYOUT_PATH),
        "store_report": sha256(STORE_REPORT_PATH),
    }
    if checks != expected:
        raise ValueError("Frozen motion-label plan source identity mismatch")
    if plan["validation_read"] or plan["confirmation_read"] or plan["training_allowed"]:
        raise ValueError("Proposal plan crosses its train-only evidence boundary")

    training_subjects = set(split["training_subjects"])
    development_subjects = set(split["development_subjects"])
    if training_subjects & development_subjects or len(training_subjects) != 68 or len(development_subjects) != 17:
        raise ValueError("Unexpected frozen subject split")
    store = FullHierarchyStore(ROOT)
    rows = []
    candidates = []
    aggregate = Counter()
    contact_frames = np.zeros(2, dtype=np.int64)
    total_frames = 0
    ineligible = []
    for index, row in enumerate(store.entries):
        if row["subject"] not in training_subjects:
            continue
        if row["frames"] < 2:
            ineligible.append(
                {
                    "clip": row["clip"],
                    "subject": row["subject"],
                    "frames": row["frames"],
                    "reason": "Velocity-based proposals require at least two sampled frames.",
                }
            )
            continue
        proposals = clip_proposals(store.clip(index), plan["thresholds"])
        if proposals["ground_truth"] or proposals["scene_geometry_known"] or proposals["hand_contacts_known"]:
            raise ValueError("Weak proposal was upgraded beyond available evidence")
        for group in (proposals["contacts"], proposals["events"], proposals["static"]):
            if any(item["confidence"] > HEURISTIC_CONFIDENCE_CEILING for item in group):
                raise ValueError("Heuristic confidence ceiling exceeded")
        compact = {
            "clip": row["clip"],
            "subject": row["subject"],
            "description": row["description"],
            "motion_tags": row["motion_tags"],
            "source_sha256": row["source_sha256"],
            **proposals,
        }
        rows.append(compact)
        candidates.extend(proposal_candidates(row, proposals, plan))
        total_frames += proposals["frames"]
        contact_frames += np.rint(np.asarray(proposals["contact_fraction"]) * proposals["frames"]).astype(np.int64)
        aggregate["contacts"] += len(proposals["contacts"])
        aggregate["static"] += len(proposals["static"])
        aggregate["takeoff"] += sum(item["kind"] == "takeoff" for item in proposals["events"])
        aggregate["landing"] += sum(item["kind"] == "landing" for item in proposals["events"])

    if not rows or {row["subject"] for row in rows} != training_subjects:
        raise ValueError("Train-only proposal coverage is incomplete")
    if {row["subject"] for row in rows} & development_subjects:
        raise ValueError("Development pose data entered proposal generation")
    queue = build_review_queue(candidates, plan)
    queue_counts = Counter(item["kind"] for item in queue)
    if any(queue_counts[kind] > quota for kind, quota in plan["review_queue"]["quotas"].items()):
        raise ValueError("Review queue quota exceeded")
    if any(item["review_status"] != "unreviewed" or item["reviewed_label"] is not None for item in queue):
        raise ValueError("Review queue contains fabricated review outcomes")

    proposal_doc = {
        "schema": "weak-motion-label-proposals-v1",
        "goal_id": plan["goal_id"],
        "threshold_plan_sha256": sha256(PLAN_PATH),
        "clips": rows,
        "ineligible_clips": ineligible,
        "provenance": "heuristic",
        "ground_truth": False,
        "development_pose_arrays_read": False,
        "confirmation_read": False,
    }
    queue_doc = {
        "schema": "weak-motion-review-queue-v1",
        "goal_id": plan["goal_id"],
        "selection": plan["review_queue"],
        "items": queue,
        "reviewed_items": 0,
        "all_items_unreviewed": True,
        "ground_truth": False,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(OUT / "proposals.json", proposal_doc)
    write_json(OUT / "review-queue.json", queue_doc)
    report = {
        "complete": True,
        "goal_id": plan["goal_id"],
        "training_clips": len(rows),
        "ineligible_training_clips": len(ineligible),
        "ineligible": ineligible,
        "training_subjects": len(training_subjects),
        "training_frames": total_frames,
        "development_subjects_excluded": len(development_subjects),
        "development_pose_arrays_read": False,
        "proposal_counts": dict(sorted(aggregate.items())),
        "contact_frame_fraction": [float(value / total_frames) for value in contact_frames],
        "review_queue_items": len(queue),
        "review_queue_counts": dict(sorted(queue_counts.items())),
        "review_queue_subjects": len({item["subject"] for item in queue}),
        "review_queue_motion_tags": sorted({tag for item in queue for tag in item["motion_tags"]}),
        "review_queue_duration_bands": sorted({item["duration_band"] for item in queue}),
        "all_items_unreviewed": True,
        "heuristic_confidence_ceiling": HEURISTIC_CONFIDENCE_CEILING,
        "scene_geometry_inferred": False,
        "hand_contacts_inferred": False,
        "ground_truth": False,
        "validation_read": False,
        "confirmation_read": False,
        "model_fit": False,
        "runtime_changed": False,
        "full_goal_complete": False,
        "seconds": time.perf_counter() - started,
        "sources": checks,
        "artifacts": {
            "proposals": {"path": "proposals.json", "sha256": sha256(OUT / "proposals.json")},
            "review_queue": {"path": "review-queue.json", "sha256": sha256(OUT / "review-queue.json")},
        },
        "known_missing_evidence": [
            "No force plates or reviewed foot-contact labels.",
            "No hand-contact labels.",
            "No measured scene geometry, moving supports, or uneven-ground normals.",
            "No animator-reviewed static, takeoff, or landing labels yet.",
            "No naturalness, intent-preservation, or correction-effort ratings.",
        ],
    }
    write_json(OUT / "report.json", report)
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
