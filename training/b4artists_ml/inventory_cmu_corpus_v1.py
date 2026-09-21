"""Build a subject-disjoint plan for the pinned CMU BVH corpus.

SPDX-License-Identifier: GPL-2.0-or-later
This inventory reads metadata only. It does not download motion files.
"""
from collections import Counter
from pathlib import Path
import hashlib
import json
import re


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results/cmu-corpus-inventory-v1"
COMMIT = "09a07f54f3bbb58797325f009282d0b2048a2871"
TREE = OUT / "tree.json"
INDEX = OUT / "index.txt"
RIGHTS = OUT / "READMEFIRST.txt"
LEGACY_MANIFEST = ROOT / "temporal_training_manifest_v19.json"
LEGACY_PLAN = ROOT / "temporal_expansion_plan_v19.json"
BYTES_PER_SECOND = 90890.18525111128
STYLE_RULES = {
    "locomotion": ("walk", "run", "jog", "stride", "turn", "veer", "navigate"),
    "jump": ("jump", "leap", "hop"),
    "dance": ("dance", "ballet", "pirouette", "jete"),
    "combat": ("punch", "boxing", "kick", "sword", "fight", "martial"),
    "sport": ("basketball", "soccer", "golf", "baseball", "football", "tennis", "sport"),
    "acrobatics": ("cartwheel", "handstand", "tumble", "acrobat", "flip"),
    "interaction": ("sit", "drink", "lift", "carry", "pick", "throw", "wash", "sweep", "climb", "ladder"),
    "gesture": ("wave", "point", "signal", "laugh", "gesture"),
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def subject(clip):
    return int(clip.split("_", 1)[0])


def hashed_split(subject_id):
    value = hashlib.sha256(f"b4ml-expanded-subject-v1:{subject_id}".encode()).digest()[0]
    if value < 32:
        return "confirmation_new"
    if value < 64:
        return "validation_new"
    return "train"


def main():
    tree = json.loads(TREE.read_text(encoding="utf-8"))
    if tree.get("truncated") or tree["sha"] != COMMIT:
        raise ValueError("Incomplete or unexpected pinned tree")
    rights = RIGHTS.read_text(encoding="utf-8", errors="strict")
    if "CMU places no restrictions" not in rights or "place no additional restrictions" not in rights:
        raise ValueError("Expected CMU/BVH conversion rights text is absent")
    descriptions = {}
    for line in INDEX.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.match(r"^\s*(\d{2,3}_\d{1,3})\s+(.+)$", line)
        if match:
            descriptions[match.group(1)] = match.group(2).strip()
    legacy = json.loads(LEGACY_MANIFEST.read_text())
    legacy_validation_subjects = {
        subject(row["clip"]) for row in legacy["files"] if row["split"] == "validation"
    }
    legacy_confirmation = json.loads(LEGACY_PLAN.read_text())["planned_splits"]["confirmation"]
    legacy_confirmation_subjects = {subject(name) for name in legacy_confirmation}
    entries = []
    for item in tree["tree"]:
        match = re.fullmatch(r"data/(\d{3})/(\d{2,3}_\d{1,3})\.bvh", item["path"])
        if item["type"] != "blob" or not match:
            continue
        clip = match.group(2)
        subject_id = subject(clip)
        if subject_id in legacy_validation_subjects:
            split = "legacy_development_subject"
        elif subject_id in legacy_confirmation_subjects:
            split = "legacy_confirmation_subject"
        else:
            split = hashed_split(subject_id)
        description = descriptions.get(clip, "Unknown")
        lower = description.lower()
        styles = [name for name, words in STYLE_RULES.items() if any(word in lower for word in words)]
        if not styles:
            styles = ["other"]
        entries.append(
            {
                "clip": clip,
                "subject": subject_id,
                "split": split,
                "description": description,
                "style_tags": styles,
                "path": item["path"],
                "url": f"https://raw.githubusercontent.com/una-dinosauria/cmu-mocap/{COMMIT}/{item['path']}",
                "bytes": item["size"],
                "git_blob_sha1": item["sha"],
            }
        )
    if len(entries) != 2548 or len({row["clip"] for row in entries}) != len(entries):
        raise ValueError("Unexpected pinned BVH inventory")
    counts = Counter(row["split"] for row in entries)
    byte_counts = Counter()
    subject_sets = {}
    style_counts = Counter()
    for row in entries:
        byte_counts[row["split"]] += row["bytes"]
        subject_sets.setdefault(row["split"], set()).add(row["subject"])
        if row["split"] == "train":
            style_counts.update(row["style_tags"])
    split_subjects = {name: sorted(values) for name, values in subject_sets.items()}
    names = list(split_subjects)
    for index, left in enumerate(names):
        for right in names[index + 1 :]:
            if set(split_subjects[left]) & set(split_subjects[right]):
                raise AssertionError("Subject leakage between splits")
    report = {
        "complete": True,
        "metadata_only": True,
        "motion_downloaded": False,
        "pinned_commit": COMMIT,
        "tree_truncated": False,
        "bvh_files": len(entries),
        "bvh_bytes": sum(row["bytes"] for row in entries),
        "estimated_full_hours": sum(row["bytes"] for row in entries) / BYTES_PER_SECOND / 3600,
        "split_files": dict(counts),
        "split_bytes": dict(byte_counts),
        "split_estimated_hours": {
            name: value / BYTES_PER_SECOND / 3600 for name, value in byte_counts.items()
        },
        "split_subjects": split_subjects,
        "subject_disjoint": True,
        "legacy_validation_subjects": sorted(legacy_validation_subjects),
        "legacy_confirmation_subjects": sorted(legacy_confirmation_subjects),
        "training_style_tag_counts": dict(style_counts),
        "descriptions_found": sum(row["description"] != "Unknown" for row in entries),
        "rights": {
            "cmu_source": "https://mocap.cs.cmu.edu/",
            "cmu_faq": "https://mocap.cs.cmu.edu/faqs.php",
            "conversion_notice": f"https://raw.githubusercontent.com/una-dinosauria/cmu-mocap/{COMMIT}/READMEFIRST.txt",
            "cmu_summary": "Source permits research/commercial use, copying, modification and redistribution; direct resale of the data is excluded by the current source page.",
            "conversion_summary": "Bruce Hahne's pinned notice places no additional restrictions on the BVH conversion.",
            "acknowledgment_required_by_project_policy": "The data used in this project was obtained from mocap.cs.cmu.edu. The database was created with funding from NSF EIA-0196217.",
            "raw_motion_bundled_with_addon": False,
        },
        "source_sha256": {
            "tree.json": sha256(TREE),
            "index.txt": sha256(INDEX),
            "READMEFIRST.txt": sha256(RIGHTS),
            "temporal_training_manifest_v19.json": sha256(LEGACY_MANIFEST),
            "temporal_expansion_plan_v19.json": sha256(LEGACY_PLAN),
            "inventory_cmu_corpus_v1.py": sha256(Path(__file__)),
        },
        "next_stage": "Download only the prospective train split, verify every git blob identity and record SHA-256. Keep all development and confirmation splits absent.",
        "full_goal_complete": False,
    }
    write(OUT / "selection.json", {"schema": 1, "entries": entries})
    report["selection_sha256"] = sha256(OUT / "selection.json")
    write(OUT / "report.json", report)
    print(json.dumps({key: report[key] for key in ("bvh_files", "bvh_bytes", "estimated_full_hours", "split_files", "split_bytes", "split_estimated_hours", "subject_disjoint")}, indent=2))


if __name__ == "__main__":
    main()
