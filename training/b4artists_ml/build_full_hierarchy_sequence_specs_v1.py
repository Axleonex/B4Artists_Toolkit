"""Build frozen metadata-only sequence specs for streaming model input."""
from collections import Counter
from pathlib import Path
import hashlib
import json


ROOT = Path(__file__).resolve().parent
HERE = Path(__file__).resolve()
PLAN_PATH = ROOT / "full_hierarchy_sequence_specs_plan_v1.json"
OUT = ROOT / "results/full-hierarchy-sequence-specs-v1"

from full_hierarchy_sequence_dataset_v1 import MASK_PATTERNS, build_training_specs, flatten_development_specs


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def summarize(specs):
    return {
        "windows": len(specs),
        "subjects": len({item["subject"] for item in specs}),
        "clips": len({item["clip"] for item in specs}),
        "by_gap": dict(sorted(Counter(str(item["gap"]) for item in specs).items())),
        "by_task": dict(sorted(Counter(item["task"] for item in specs).items())),
        "by_mask": dict(sorted(Counter(item["mask_pattern"] for item in specs).items())),
    }


def main():
    plan = json.loads(PLAN_PATH.read_text())
    layout_path = ROOT / "results/full-hierarchy-store-v1/layout.json"
    split_path = ROOT / "results/hierarchy-cohorts-v1/split.json"
    checks = {
        "builder": sha(HERE),
        "module": sha(ROOT / "full_hierarchy_sequence_dataset_v1.py"),
        "layout": sha(layout_path),
        "split": sha(split_path),
        "model_plan": sha(ROOT / "full_hierarchy_model_comparison_plan_v1.json"),
    }
    if checks != plan["sources"]:
        raise ValueError("Frozen sequence-spec source identity mismatch")
    layout = json.loads(layout_path.read_text())
    split = json.loads(split_path.read_text())
    training = build_training_specs(layout, split, plan["selection"])
    development = flatten_development_specs(layout, split)
    training_subjects = {item["subject"] for item in training}
    development_subjects = {item["subject"] for item in development}
    if training_subjects != set(split["training_subjects"]):
        raise ValueError("Training specs do not cover the frozen training subjects")
    if development_subjects != set(split["development_subjects"]):
        raise ValueError("Development specs do not cover the frozen development subjects")
    if training_subjects & development_subjects:
        raise ValueError("Sequence spec subjects overlap")
    if len(development) != 1125:
        raise ValueError("Frozen development window count changed")
    document = {
        "schema": "full-hierarchy-sequence-specs-v1",
        "goal_id": plan["goal_id"],
        "training": training,
        "development": development,
        "motion_arrays_read": False,
        "model_outcomes_read": False,
        "confirmation_read": False,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    write(OUT / "specs.json", document)
    report = {
        "complete": True,
        "training": summarize(training),
        "development": summarize(development),
        "subject_overlap": [],
        "all_masks": list(MASK_PATTERNS),
        "streaming": True,
        "dense_examples_materialized": False,
        "motion_arrays_read": False,
        "model_outcomes_read": False,
        "confirmation_read": False,
        "model_fit": False,
        "runtime_changed": False,
        "full_goal_complete": False,
        "sources": checks,
        "specs_sha256": sha(OUT / "specs.json"),
    }
    write(OUT / "report.json", report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
