"""Structural and data-contract checks for the offline motion reviewer."""
from pathlib import Path
import hashlib
import json
import math
import os
import re


ROOT = Path(__file__).resolve().parent
HERE = Path(__file__).resolve()
QUEUE = ROOT / "results/motion-label-proposals-v1/review-queue.json"
BUILD = ROOT / "results/motion-label-reviewer-v1"
OUT = BUILD / "validation.json"


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if OUT.exists(): raise RuntimeError("Reviewer validation exists")
    page = BUILD / "reviewer.html"
    manifest = json.loads((BUILD / "manifest.json").read_text())
    queue = json.loads(QUEUE.read_text())
    source = page.read_text(encoding="utf-8")
    match = re.search(r"const items=(.*),parents=(\[[^;]+\]),qh=([^;]+);let i=", source)
    if not match: raise ValueError("Embedded reviewer payload is missing")
    items = json.loads(match.group(1)); parents = json.loads(match.group(2)); queue_hash = json.loads(match.group(3))
    if sha(page) != manifest["html_sha256"] or sha(QUEUE) != manifest["queue_sha256"] != queue_hash:
        raise ValueError("Reviewer source identity mismatch")
    if len(items) != len(queue["items"]) != 130: raise ValueError("Reviewer item count mismatch")
    if [row["review_id"] for row in items] != [row["review_id"] for row in queue["items"]]:
        raise ValueError("Reviewer queue order changed")
    if len(parents) != 23 or parents[0] != -1: raise ValueError("Reviewer hierarchy mismatch")
    for source_item, item in zip(queue["items"], items):
        if any(item[key] != source_item[key] for key in source_item): raise ValueError("Queue item changed")
        if len(item["positions"]) != len(item["source_frames"]): raise ValueError("Frame count mismatch")
        if not all(len(frame) == 23 and all(len(point) == 3 and all(math.isfinite(v) for v in point) for point in frame)
                   for frame in item["positions"]): raise ValueError("Invalid embedded skeleton")
        if not item["source_frames"][0] <= item["start"] <= item["end"] <= item["source_frames"][-1]:
            raise ValueError("Proposal is outside its preview")
    required = ("id=\"view\"", "data-v=\"accepted\"", "data-v=\"rejected\"", "data-v=\"uncertain\"",
                "corrected_start", "corrected_end", "b4ml-reviewed-motion-labels-v1", "source_queue_sha256",
                "localStorage", "Export reviewed JSON")
    if any(value not in source for value in required): raise ValueError("Reviewer control or export contract missing")
    if re.search(r"<(script|link)[^>]+(src|href)=", source, re.I) or "http://" in source or "https://" in source:
        raise ValueError("Reviewer must not load external dependencies")
    report = {"complete":True,"schema":"motion-label-reviewer-validation-v1","items":len(items),
              "embedded_frames":sum(len(row["positions"]) for row in items),"queue_sha256":queue_hash,
              "html_sha256":sha(page),"builder_sha256":manifest["builder_sha256"],"checker_sha256":sha(HERE),
              "queue_order_exact":True,"finite_23_joint_previews":True,"offline_controls_present":True,
              "external_dependencies":False,"rendered_browser_validation":False,"reviewed_items":0,
              "ground_truth":False,"model_outcomes_read":False,"confirmation_read":False,"full_goal_complete":False}
    temp=OUT.with_suffix(".tmp");temp.write_text(json.dumps(report,indent=2)+"\n");os.replace(temp,OUT)
    print(json.dumps(report,indent=2))


if __name__=="__main__": main()
