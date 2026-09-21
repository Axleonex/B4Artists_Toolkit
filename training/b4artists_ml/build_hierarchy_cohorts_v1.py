"""Freeze metadata-stratified subject holdouts and task windows before training.

SPDX-License-Identifier: GPL-2.0-or-later
This reads only checked train-store metadata, not motion arrays or confirmation data.
"""
from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import time


ROOT = Path(__file__).resolve().parent
HERE = Path(__file__).resolve()
PLAN_PATH = ROOT / "hierarchy_cohort_plan_v1.json"
OUT = ROOT / "results/hierarchy-cohorts-v1"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def tie(seed, *parts):
    return hashlib.sha256(":".join(map(str, (seed, *parts))).encode()).hexdigest()


def select_subjects(entries, plan):
    tags = defaultdict(set)
    for row in entries:
        tags[row["subject"]].update(row["motion_tags"])
    desired = plan["development_subject_coverage"]
    availability = {tag: sum(tag in present for present in tags.values()) for tag in desired}
    if any(availability[tag] < target for tag, target in desired.items()):
        raise ValueError("Requested development coverage exceeds metadata availability")
    selected = []
    covered = Counter()
    while len(selected) < plan["development_subjects"]:
        candidates = []
        for subject, present in tags.items():
            if subject in selected:
                continue
            score = sum(
                max(desired[tag] - covered[tag], 0) / desired[tag] / availability[tag]
                for tag in desired
                if tag in present
            )
            candidates.append((-score, tie(plan["seed"], "subject", subject), subject))
        _, _, chosen = min(candidates)
        selected.append(chosen)
        covered.update(tags[chosen])
    if any(covered[tag] < target for tag, target in desired.items()):
        raise ValueError("Deterministic subject selection missed a coverage floor")
    return sorted(selected), {tag: covered[tag] for tag in desired}, availability


def select_windows(entries, development_subjects, plan):
    dev = set(development_subjects)
    patterns = plan["sparse_masks"]
    windows = {}
    for task, tag in plan["task_tags"].items():
        windows[task] = {}
        for gap in plan["gaps"]:
            candidates = [
                row for row in entries
                if row["subject"] in dev
                and (tag is None or tag in row["motion_tags"])
                and row["frames"] >= gap + 3
            ]
            if not candidates:
                raise ValueError(f"No {task} gap-{gap} development candidates")
            candidates.sort(key=lambda row: tie(plan["seed"], task, gap, row["clip"]))
            per_subject = Counter()
            chosen = []
            for row in candidates:
                if per_subject[row["subject"]] >= plan["maximum_windows_per_subject_task_gap"]:
                    continue
                span = row["frames"] - gap - 2
                start = 1 + int(tie(plan["seed"], task, gap, row["clip"], "start")[:16], 16) % span
                chosen.append(
                    {
                        "clip": row["clip"],
                        "subject": row["subject"],
                        "start": start,
                        "end": start + gap,
                        "gap": gap,
                        "context": True,
                        "sparse_mask": patterns[len(chosen) % len(patterns)],
                        "task_source": "weak_metadata" if tag is not None else "duration_only",
                    }
                )
                per_subject[row["subject"]] += 1
                if len(chosen) == plan["maximum_windows_per_task_gap"]:
                    break
            minimum = min(plan["minimum_windows_per_task_gap"], len(candidates))
            if len(chosen) < minimum:
                raise ValueError(f"Insufficient {task} gap-{gap} development windows")
            windows[task][str(gap)] = chosen
    return windows


def main():
    started = time.perf_counter()
    plan = json.loads(PLAN_PATH.read_text())
    layout_path = ROOT / plan["source_layout"]
    report_path = ROOT / plan["source_report"]
    layout = json.loads(layout_path.read_text())
    report = json.loads(report_path.read_text())
    assert sha256(HERE) == plan["script_sha256"]
    assert sha256(layout_path) == plan["source_layout_sha256"]
    assert sha256(report_path) == plan["source_report_sha256"]
    assert report["complete"] and report["clips"] == 1840 and report["subjects"] == 85
    assert not report["validation_read"] and not report["confirmation_read"]
    assert not plan["training_allowed"] and not plan["confirmation_read"]
    OUT.mkdir(exist_ok=False)
    development, coverage, availability = select_subjects(layout["entries"], plan)
    subjects = sorted({row["subject"] for row in layout["entries"]})
    training = sorted(set(subjects) - set(development))
    assert len(development) == plan["development_subjects"]
    assert len(training) == plan["training_subjects"]
    assert not set(training) & set(development)
    windows = select_windows(layout["entries"], development, plan)
    split = {
        "schema": 1,
        "goal_id": plan["goal_id"],
        "seed": plan["seed"],
        "selection": "Metadata-only deterministic coverage stratification with SHA-256 tie-breaking; no pose/model outcome inspected.",
        "training_subjects": training,
        "development_subjects": development,
        "development_subject_coverage": coverage,
        "subject_tag_availability": availability,
        "task_windows": windows,
        "pending_reviewed_tasks": plan["pending_reviewed_tasks"],
        "task_label_warning": "Current task windows use weak source metadata or duration only; they are future-model development cohorts, not untouched confirmation or reviewed naturalness labels.",
        "prior_models_used_these_sources": True,
        "new_models_may_train_on_development_subjects": False,
        "confirmation_subjects_or_clips_included": False,
        "split_sha256": None,
    }
    split["split_sha256"] = digest({**split, "split_sha256": None})
    write(OUT / "split.json", split)
    task_counts = {
        task: {gap: len(rows) for gap, rows in by_gap.items()}
        for task, by_gap in windows.items()
    }
    report_out = {
        "complete": True,
        "subjects": len(subjects),
        "training_subjects": len(training),
        "development_subjects": len(development),
        "subject_overlap": [],
        "development_subject_coverage": coverage,
        "task_window_counts": task_counts,
        "total_development_windows": sum(count for task in task_counts.values() for count in task.values()),
        "pending_reviewed_tasks": plan["pending_reviewed_tasks"],
        "all_declared_metadata_floors_pass": all(
            coverage[tag] >= target for tag, target in plan["development_subject_coverage"].items()
        ),
        "motion_arrays_read": False,
        "model_outcomes_read": False,
        "prior_source_exposure_acknowledged": True,
        "confirmation_read": False,
        "training_run": False,
        "runtime_promoted": False,
        "seconds": time.perf_counter() - started,
        "sources": {
            "script": sha256(HERE),
            "plan": sha256(PLAN_PATH),
            "source_layout": sha256(layout_path),
            "source_report": sha256(report_path),
            "split": sha256(OUT / "split.json"),
        },
        "full_goal_complete": False,
    }
    write(OUT / "report.json", report_out)
    print(json.dumps(report_out, indent=2))


if __name__ == "__main__":
    main()
