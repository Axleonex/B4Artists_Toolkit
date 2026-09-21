"""Freeze a fresh repaired-model holdout from the former training pool.

Selection reads metadata identities only.  The previously exposed v1
development subjects remain excluded from both repaired training and selection.
"""
from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import os


ROOT = Path(__file__).resolve().parent
PLAN_PATH = ROOT / "priority_cohort_plan_v2.json"
OUT_SPLIT = ROOT / "results/priority-cohorts-v2"
OUT_SPECS = ROOT / "results/priority-sequence-specs-v2"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(*parts):
    return hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def main():
    plan = json.loads(PLAN_PATH.read_text())
    old_split_path = ROOT / "results/hierarchy-cohorts-v1/split.json"
    old_specs_path = ROOT / "results/full-hierarchy-sequence-specs-v1/specs.json"
    sources = {
        "builder": sha(Path(__file__).resolve()),
        "old_split": sha(old_split_path),
        "old_specs": sha(old_specs_path),
    }
    if sources != plan["sources"]:
        raise ValueError("Priority cohort source mismatch")
    old_split = json.loads(old_split_path.read_text())
    old_specs = json.loads(old_specs_path.read_text())
    candidates = set(int(value) for value in old_split["training_subjects"])
    old_development = set(int(value) for value in old_split["development_subjects"])
    by_subject = defaultdict(set)
    for item in old_specs["training"]:
        if int(item["subject"]) not in candidates:
            raise ValueError("Old training spec escaped its subject partition")
        by_subject[int(item["subject"])].add(item["task"])
    availability = Counter()
    for tasks in by_subject.values():
        availability.update(tasks)
    desired = {task: min(int(plan["coverage_subjects_per_task"]), count)
               for task, count in availability.items()}
    selected = []
    covered = Counter()
    while len(selected) < int(plan["development_subjects"]):
        choices = []
        for subject in sorted(candidates - set(selected)):
            gain = sum(
                1.0 / availability[task]
                for task in by_subject[subject]
                if covered[task] < desired[task]
            )
            choices.append((-gain, digest(plan["seed"], subject), subject))
        if not choices:
            raise ValueError("Insufficient candidate subjects")
        _, _, chosen = min(choices)
        selected.append(chosen)
        covered.update(by_subject[chosen])
    development = set(selected)
    training = candidates - development
    training_specs = [item for item in old_specs["training"] if int(item["subject"]) in training]
    development_specs = [item for item in old_specs["training"] if int(item["subject"]) in development]
    if training & development or development & old_development or training & old_development:
        raise ValueError("Repaired partitions overlap excluded subjects")
    if len(training) != plan["training_subjects"] or len(development) != plan["development_subjects"]:
        raise ValueError("Unexpected repaired split size")
    split = {
        "schema": "priority-cohort-split-v2",
        "seed": plan["seed"],
        "training_subjects": sorted(training),
        "development_subjects": sorted(development),
        "excluded_exposed_v1_development_subjects": sorted(old_development),
        "coverage_by_task": dict(sorted((task, sum(task in by_subject[subject] for subject in development))
                                         for task in availability)),
        "selection": plan["selection"],
        "motion_arrays_read": False,
        "model_outcomes_read": False,
        "confirmation_read": False,
    }
    specs = {
        "schema": "priority-sequence-specs-v2",
        "training": training_specs,
        "development": development_specs,
        "source_specs_sha256": sources["old_specs"],
        "identities_changed": False,
        "only_partition_changed": True,
        "motion_arrays_read": False,
        "model_outcomes_read": False,
        "confirmation_read": False,
    }
    write(OUT_SPLIT / "split.json", split)
    write(OUT_SPECS / "specs.json", specs)
    report = {
        "complete": True,
        "sources": sources,
        "training_subjects": len(training),
        "development_subjects": len(development),
        "excluded_exposed_v1_development_subjects": len(old_development),
        "training_windows": len(training_specs),
        "development_windows": len(development_specs),
        "training_by_gap": dict(sorted(Counter(str(item["gap"]) for item in training_specs).items())),
        "development_by_gap": dict(sorted(Counter(str(item["gap"]) for item in development_specs).items())),
        "development_by_task": dict(sorted(Counter(item["task"] for item in development_specs).items())),
        "development_by_mask": dict(sorted(Counter(item["mask_pattern"] for item in development_specs).items())),
        "subject_overlap": sorted(training & development),
        "old_development_overlap": sorted((training | development) & old_development),
        "motion_arrays_read": False,
        "model_outcomes_read": False,
        "confirmation_read": False,
        "runtime_changed": False,
        "full_goal_complete": False,
    }
    write(OUT_SPLIT / "report.json", report)
    write(OUT_SPECS / "report.json", report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
