"""Acquire only the prospective subject-disjoint CMU training split.

SPDX-License-Identifier: GPL-2.0-or-later
The sparse checkout intentionally excludes every development/confirmation subject.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import time


ROOT = Path(__file__).resolve().parent
PLAN_PATH = ROOT / "cmu_train_acquisition_plan_v1.json"
SELECTION_PATH = ROOT / "results/cmu-corpus-inventory-v1/selection.json"
OUT = ROOT / "results/cmu-corpus-inventory-v1"
CACHE_ROOT = (ROOT / "cache-expanded-v1").resolve()
CHECKOUT = (CACHE_ROOT / "cmu-mocap").resolve()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha1(data):
    header = f"blob {len(data)}\0".encode()
    return hashlib.sha1(header + data).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def git_args(*args):
    return ("git", "-c", "safe.directory=" + CHECKOUT.as_posix(), *args)


def run(*args):
    subprocess.run(git_args(*args), cwd=CHECKOUT if CHECKOUT.exists() else CACHE_ROOT, check=True)


def main():
    started = time.perf_counter()
    plan = json.loads(PLAN_PATH.read_text())
    selection = json.loads(SELECTION_PATH.read_text())
    assert sha256(SELECTION_PATH) == plan["selection_sha256"]
    assert sha256(Path(__file__)) == plan["script_sha256"]
    expected = [row for row in selection["entries"] if row["split"] == "train"]
    assert len(expected) == plan["files"]
    assert sum(row["bytes"] for row in expected) == plan["bytes"]
    expected_clips = {row["clip"] for row in expected}
    expected_subjects = {row["subject"] for row in expected}
    assert not expected_subjects & set(plan["excluded_subjects"])
    CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    if not CHECKOUT.exists():
        subprocess.run(
            [
                *git_args(),
                "clone",
                "--filter=blob:none",
                "--no-checkout",
                plan["repository"],
                str(CHECKOUT),
            ],
            cwd=CACHE_ROOT,
            check=True,
        )
    if not (CHECKOUT / ".git").is_dir():
        raise ValueError("Acquisition target exists but is not the expected Git checkout")
    origin = subprocess.check_output(
        git_args("remote", "get-url", "origin"), cwd=CHECKOUT, text=True
    ).strip()
    if origin.rstrip("/") != plan["repository"].rstrip("/"):
        raise ValueError("Unexpected acquisition origin")
    run("sparse-checkout", "init", "--cone")
    subject_paths = [f"data/{value:03d}" for value in sorted(expected_subjects)]
    run("sparse-checkout", "set", *subject_paths)
    run("checkout", "--detach", plan["commit"])
    head = subprocess.check_output(git_args("rev-parse", "HEAD"), cwd=CHECKOUT, text=True).strip()
    if head != plan["commit"]:
        raise ValueError("Pinned acquisition commit was not checked out")
    actual_paths = sorted((CHECKOUT / "data").rglob("*.bvh"))
    actual_clips = {path.stem for path in actual_paths}
    if actual_clips != expected_clips:
        raise ValueError("Sparse checkout includes missing or protected motion clips")
    rows = []
    total = 0
    for index, item in enumerate(sorted(expected, key=lambda row: row["clip"])):
        path = CHECKOUT / item["path"]
        if path.resolve().is_relative_to(CHECKOUT) is False:
            raise ValueError("Motion path escapes the checked cache")
        data = path.read_bytes()
        if len(data) != item["bytes"] or git_blob_sha1(data) != item["git_blob_sha1"]:
            raise ValueError("Motion identity mismatch: " + item["clip"])
        digest = hashlib.sha256(data).hexdigest()
        rows.append(
            {
                "clip": item["clip"],
                "subject": item["subject"],
                "description": item["description"],
                "style_tags": item["style_tags"],
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": len(data),
                "git_blob_sha1": item["git_blob_sha1"],
                "sha256": digest,
            }
        )
        total += len(data)
        if (index + 1) % 100 == 0:
            write(
                OUT / "download-progress.json",
                {
                    "complete": False,
                    "verified_files": index + 1,
                    "files": len(expected),
                    "verified_bytes": total,
                    "seconds": time.perf_counter() - started,
                    "development_motion_downloaded": False,
                    "confirmation_motion_downloaded": False,
                },
            )
    assert total == plan["bytes"]
    manifest = {
        "schema": 1,
        "complete": True,
        "commit": head,
        "files": rows,
        "file_count": len(rows),
        "bytes": total,
        "subjects": sorted(expected_subjects),
        "subject_count": len(expected_subjects),
        "development_motion_downloaded": False,
        "confirmation_motion_downloaded": False,
        "raw_motion_bundled_with_addon": False,
        "plan_sha256": sha256(PLAN_PATH),
        "selection_sha256": sha256(SELECTION_PATH),
        "seconds": time.perf_counter() - started,
        "full_goal_complete": False,
    }
    write(OUT / "train-download-manifest.json", manifest)
    write(
        OUT / "download-progress.json",
        {
            "complete": True,
            "verified_files": len(rows),
            "files": len(rows),
            "verified_bytes": total,
            "seconds": manifest["seconds"],
            "manifest_sha256": sha256(OUT / "train-download-manifest.json"),
            "development_motion_downloaded": False,
            "confirmation_motion_downloaded": False,
        },
    )
    print(json.dumps({key: manifest[key] for key in ("complete", "file_count", "bytes", "subject_count", "development_motion_downloaded", "confirmation_motion_downloaded", "seconds")}, indent=2))


if __name__ == "__main__":
    main()
