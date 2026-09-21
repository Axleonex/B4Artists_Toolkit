"""Compare contact sampling densities with unchanged dense output verification."""
from pathlib import Path
import json
import math
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]

import bpy
from mathutils import Vector
import b4artists_ml
from b4artists_ml import contact_math, contacts, posing, workflow
from test_b4artists_ml_contact_suggestions import ContactSuggestionTests


def sample_at(step):
    def sample_frames(rows, anchors, first, last):
        frames = set(anchors)
        begin = math.ceil(first / step)
        finish = math.floor(last / step)
        frames.update(i * step for i in range(begin, finish + 1))
        for row in rows:
            frames.update((row["start"], row["end"], max(first, row["start"] - row["blend"]), min(last, row["end"] + row["blend"])))
        return sorted(frames)
    return sample_frames


def dense_contact_error(obj, item):
    mapping = {row["id"]: row for row in posing.bindings(obj)[2]}
    row = mapping[item.limb]
    maximum = 0.0
    for index in range(16, 177):
        contacts._frame(bpy.context.scene, index / 16.0)
        reference = max(sum((obj.pose.bones[row["joints"][i + 1]].head - obj.pose.bones[row["joints"][i]].head).length for i in (0, 1)), 1e-8)
        maximum = max(maximum, (contacts._point(obj, row, item.offset) - Vector(item.point)).length / reference)
    return maximum


def run(step):
    obj, scene, _ = ContactSuggestionTests().prepared("rigify_default")
    suggestion = contacts.suggest(obj, scene)
    assert suggestion["suggestions"] >= 2
    item = obj.b4ml.contacts[0]
    item.review_state = "ACCEPTED"
    item.enabled = True
    source = obj.b4ml.candidate_action
    signature = contacts._action_signature(obj)
    started = time.perf_counter()
    report = contacts.solve(obj, scene)
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    workflow.assign_action(obj, source, workflow._slot(obj.animation_data))
    source_preserved = contacts._action_signature(obj) == signature
    workflow.assign_action(obj, obj.b4ml.contact_output, workflow._slot(obj.animation_data))
    return {
        "step_frames": step,
        "elapsed_ms": elapsed_ms,
        "frames": report["frames"],
        "validation_frames": report["validation_frames"],
        "adaptive_refinements": report["adaptive_refinements"],
        "reported_max_after": report["max_after"],
        "dense_1_16_max_after": dense_contact_error(obj, item),
        "source_preserved": source_preserved,
    }


def main():
    b4artists_ml.register()
    original = contact_math.sample_frames
    rows = []
    try:
        for step in (0.125, 0.25, 0.5, 1.0):
            contact_math.sample_frames = sample_at(step)
            rows.append(run(step))
    finally:
        contact_math.sample_frames = original
    baseline = rows[0]["elapsed_ms"]
    for row in rows:
        row["speedup_percent"] = (baseline - row["elapsed_ms"]) / baseline * 100.0
        row["passes_dense_gate"] = row["dense_1_16_max_after"] < 2e-4 and row["reported_max_after"] < 2e-4 and row["source_preserved"]
    result = {
        "schema": 1,
        "passed": all(row["passes_dense_gate"] for row in rows),
        "fixture": "rigify_default",
        "rows": rows,
        "scope": "One accepted full-strength foot hold over frames 1-11; every result is rechecked at 1/16-frame density.",
    }
    output = ROOT / "training/b4artists_ml/results/contact-sampling-ablation-v1.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("CONTACT_SAMPLING_ABLATION: " + json.dumps(result), flush=True)
    bpy.ops.wm.quit_blender()


if __name__ == "__main__":
    main()
