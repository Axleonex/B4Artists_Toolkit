"""Verify the frozen subject holdout and materialize every declared cohort window."""
from collections import Counter
from pathlib import Path
import hashlib
import json
import sys
import time

import numpy as np


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results/hierarchy-cohorts-contract-v1"
sys.path.insert(0, str(ROOT))

from build_hierarchy_cohorts_v1 import digest, select_subjects, select_windows
from full_hierarchy_store_v1 import FullHierarchyStore
from motion_conditioning_v1 import MotionConditioning, with_hierarchy_controls


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    OUT.mkdir(exist_ok=False)
    started = time.perf_counter()
    plan_path = ROOT / "hierarchy_cohort_plan_v1.json"
    split_path = ROOT / "results/hierarchy-cohorts-v1/split.json"
    source_report_path = ROOT / "results/hierarchy-cohorts-v1/report.json"
    plan = json.loads(plan_path.read_text())
    split = json.loads(split_path.read_text())
    source_report = json.loads(source_report_path.read_text())
    store = FullHierarchyStore()
    assert source_report["complete"] and source_report["sources"]["split"] == sha256(split_path)
    assert digest({**split, "split_sha256": None}) == split["split_sha256"]
    training = set(split["training_subjects"])
    development = set(split["development_subjects"])
    all_subjects = {row["subject"] for row in store.entries}
    assert not training & development
    assert training | development == all_subjects
    assert len(training) == 68 and len(development) == 17
    expected_development, expected_coverage, _ = select_subjects(store.entries, plan)
    expected_windows = select_windows(store.entries, expected_development, plan)
    assert split["development_subjects"] == expected_development
    assert split["development_subject_coverage"] == expected_coverage
    assert split["task_windows"] == expected_windows
    by_clip = {row["clip"]: (index, row) for index, row in enumerate(store.entries)}
    materialized = 0
    maximum_feature = 0.0
    minimum_windows = None
    for task, by_gap in split["task_windows"].items():
        for gap_text, rows in by_gap.items():
            gap = int(gap_text)
            minimum_windows = len(rows) if minimum_windows is None else min(minimum_windows, len(rows))
            assert len(rows) <= plan["maximum_windows_per_task_gap"]
            assert len({(row["clip"], row["start"], row["end"]) for row in rows}) == len(rows)
            counts = Counter(row["subject"] for row in rows)
            assert max(counts.values()) <= plan["maximum_windows_per_subject_task_gap"]
            for row in rows:
                index, source = by_clip[row["clip"]]
                assert source["subject"] == row["subject"] and row["subject"] in development
                assert row["subject"] not in training
                assert row["gap"] == gap and row["end"] - row["start"] == gap
                assert 1 <= row["start"] < row["end"] + 1 < source["frames"]
                assert row["context"] is True and row["sparse_mask"] in plan["sparse_masks"]
                window = store.clip(index).normalized_window(
                    row["start"], row["end"], context=True, mask_pattern=row["sparse_mask"]
                )
                condition = with_hierarchy_controls(MotionConditioning.empty(gap + 1), window)
                packed, layout = condition.packed()
                assert packed.shape == (gap + 1, 483)
                assert len(layout) == 30 and np.isfinite(packed).all()
                maximum_feature = max(maximum_feature, float(np.max(np.abs(packed))))
                materialized += 1
    assert materialized == source_report["total_development_windows"] == 1125
    assert minimum_windows >= 6
    assert set(split["pending_reviewed_tasks"]) == {
        "static", "landing", "contact_quality", "naturalness_and_intent"
    }
    report = {
        "complete": True,
        "training_subjects": len(training),
        "development_subjects": len(development),
        "subject_overlap": [],
        "deterministic_reproduction": True,
        "materialized_windows": materialized,
        "minimum_windows_per_task_gap": minimum_windows,
        "maximum_absolute_packed_feature": maximum_feature,
        "packed_features": 483,
        "all_windows_finite": True,
        "all_windows_use_development_subjects_only": True,
        "training_subjects_excluded_from_development": True,
        "metadata_stratification_only": True,
        "development_motion_arrays_read_after_split_freeze": True,
        "model_outcomes_read": False,
        "prior_source_exposure_acknowledged": split["prior_models_used_these_sources"],
        "pending_reviewed_tasks": split["pending_reviewed_tasks"],
        "confirmation_read": False,
        "training_run": False,
        "runtime_promoted": False,
        "seconds": time.perf_counter() - started,
        "sources": {
            "script": sha256(Path(__file__)),
            "plan": sha256(plan_path),
            "split": sha256(split_path),
            "cohort_report": sha256(source_report_path),
            "hierarchy_report": sha256(ROOT / "results/full-hierarchy-store-v1/report.json"),
            "conditioning_contract": sha256(ROOT / "results/motion-conditioning-contract-v1/report.json"),
        },
        "full_goal_complete": False,
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
