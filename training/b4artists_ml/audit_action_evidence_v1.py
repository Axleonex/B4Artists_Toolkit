"""Audit action coverage without reading motion arrays or model outcomes."""
from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import os


ROOT = Path(__file__).resolve().parent
HERE = Path(__file__).resolve()
RESULTS = ROOT / "results"
SPECS = RESULTS / "priority-sequence-specs-v2/specs.json"
LAYOUT = RESULTS / "full-hierarchy-store-v1/layout.json"
OUT = RESULTS / "action-evidence-audit-v1.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def summarize(rows):
    by_task = defaultdict(list)
    for row in rows:
        by_task[row["task"]].append(row)
    return {
        task: {
            "windows": len(items),
            "clips": len({item["clip"] for item in items}),
            "subjects": len({int(item["subject"]) for item in items}),
            "gaps": dict(sorted(Counter(int(item["gap"]) for item in items).items())),
            "mask_patterns": dict(sorted(Counter(item["mask_pattern"] for item in items).items())),
        }
        for task, items in sorted(by_task.items())
    }


def main():
    if OUT.exists():
        raise RuntimeError("Evidence exists: " + str(OUT))
    specs = json.loads(SPECS.read_text())
    layout = json.loads(LAYOUT.read_text())
    training = specs["training"]
    development = specs["development"]
    training_subjects = {int(row["subject"]) for row in training}
    development_subjects = {int(row["subject"]) for row in development}
    if training_subjects & development_subjects:
        raise ValueError("Subject-disjoint contract changed")
    known_tasks = {row["task"] for row in training}
    novel = [row for row in development if row["task"] not in known_tasks]
    seen = [row for row in development if row["task"] in known_tasks]
    entry_by_clip = {row["clip"]: row for row in layout["entries"]}
    if any(row["clip"] not in entry_by_clip for row in training + development):
        raise ValueError("Sequence spec references an unknown source clip")
    tag_sources = Counter(entry_by_clip[row["clip"]]["motion_tag_source"] for row in training + development)
    required = {
        "reaching": ["reach_or_object"],
        "crouching": ["crouch"],
        "walking": ["walk"],
        "running": ["run"],
        "jumping": ["jump", "aerial"],
        "landing": ["recovery"],
        "turning": ["turn"],
        "difficult_pose_transitions": ["other", "interaction", "combat", "dance", "gesture"],
    }
    report = {
        "complete": True,
        "schema": "action-evidence-audit-v1",
        "method": "Metadata only. No motion arrays, model checkpoints, development metrics or confirmation data were read.",
        "subject_disjoint": True,
        "training_windows": len(training),
        "development_windows": len(development),
        "training": summarize(training),
        "development": summarize(development),
        "development_partition": {
            "seen_action_windows": len(seen),
            "novel_action_windows": len(novel),
            "novel_action_fraction": len(novel) / len(development),
            "novel_tasks": sorted({row["task"] for row in novel}),
            "novel_task_counts": dict(sorted(Counter(row["task"] for row in novel).items())),
        },
        "required_workflow_mapping": required,
        "tag_sources": dict(sorted(tag_sources.items())),
        "review_status": "Task and motion tags are description-keyword heuristics, not reviewed animator intent or contact truth.",
        "action_disjoint_qualification_ready": False,
        "reasons_not_ready": [
            "The split is subject-disjoint but was not prospectively designed as an action-disjoint benchmark.",
            "Aerial and recovery are absent from training yet present in development and must be reported separately.",
            "Landing is represented only indirectly by the unreviewed recovery heuristic.",
            "Difficult transitions do not have a reviewed, task-specific label.",
        ],
        "next_evidence": [
            "Review task and intent labels for the reference-scene subset.",
            "Review takeoff, airborne and landing boundaries independently of target motion.",
            "Freeze separate seen-action and deliberately held-out-action evaluation cohorts before another fit.",
            "Report real-rig transfer separately from motion-corpus subject and action generalization.",
        ],
        "sources": {"script": sha(HERE), "specs": sha(SPECS), "layout": sha(LAYOUT)},
        "motion_arrays_read": False,
        "model_outcomes_read": False,
        "confirmation_read": False,
        "full_goal_complete": False,
    }
    temporary = OUT.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, OUT)
    print(json.dumps({
        "complete": True,
        "training_windows": len(training),
        "development_windows": len(development),
        "seen_action_windows": len(seen),
        "novel_action_windows": len(novel),
        "novel_tasks": report["development_partition"]["novel_tasks"],
        "action_disjoint_qualification_ready": False,
        "motion_arrays_read": False,
        "model_outcomes_read": False,
    }, indent=2))


if __name__ == "__main__":
    main()
