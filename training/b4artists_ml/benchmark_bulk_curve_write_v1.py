"""Research detached bulk FCurve writes using a real generated Rigify action."""
from pathlib import Path
import hashlib
import json
import os
import statistics
import subprocess
import sys
import time


HERE = Path(__file__).resolve()
TRAINING = HERE.parent
ROOT = TRAINING.parents[1]
OUT = TRAINING / "results/bulk-curve-write-v1"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def host_main():
    sys.path[:0] = [str(ROOT), str(ROOT / "tests"), str(TRAINING)]
    import bpy
    import numpy as np
    import b4artists_ml
    from b4artists_ml import contacts, rig_state, temporal_preview
    from b4artists_ml import workflow as w

    b4artists_ml.register()
    reference = TRAINING / "results/broader-shape-runtime-v1/rigify_default/reach_hold-smooth_both.blend"
    bpy.ops.wm.open_mainfile(filepath=str(reference), load_ui=False, use_scripts=False)
    scene = bpy.context.scene
    obj = next(item for item in scene.objects if item.type == "ARMATURE" and item.b4ml.candidate_action)
    w.finish_preview(obj, scene, False)
    source = obj.animation_data.action
    source_signature = contacts._action_signature(obj)
    source_pose = w.raw_pose(obj)
    source_modes = rig_state.mode_values(obj)
    anchors = [(item.frame, item.payload) for item in obj.b4ml.anchors]
    rows = w.read_anchors(obj)
    first, last = rows[0][0], rows[-1][0]
    identifier = w._slot(obj.animation_data)

    obj.b4ml.temporal_smoothing = False
    generated = temporal_preview.run(obj, scene)
    generated_slot = next(slot for slot in generated.slots if slot.identifier == identifier)
    generated_curves = w.action_curves(generated, generated_slot)
    owned = set()
    for name, value in rows[0][1]["pose"].items():
        bone = obj.pose.bones[name]
        for prop in ("location", "scale"):
            owned.update((bone.path_from_id(prop), index) for index in value["channels"][prop])
        if value["channels"]["rotation"]:
            prop = ("rotation_quaternion" if value["mode"] == "QUATERNION" else
                    "rotation_axis_angle" if value["mode"] == "AXIS_ANGLE" else "rotation_euler")
            count = 4 if prop != "rotation_euler" else 3
            owned.update((bone.path_from_id(prop), index) for index in range(count))

    query_frames = np.arange(first, last + 0.125, 0.125)
    desired = {}
    for curve in generated_curves:
        key = (curve.data_path, curve.array_index)
        if key not in owned:
            continue
        points = [point for point in curve.keyframe_points if first <= point.co.x <= last]
        desired[key] = {
            "points": tuple(tuple(point.co) for point in points),
            "state": tuple((tuple(point.co), tuple(point.handle_left), tuple(point.handle_right),
                            point.interpolation, point.handle_left_type, point.handle_right_type)
                           for point in curve.keyframe_points),
            "values": np.array([curve.evaluate(float(frame)) for frame in query_frames]),
        }
    assert len(desired) == 300 and sum(len(row["points"]) for row in desired.values()) == 6300
    w.finish_preview(obj, scene, False)
    assert obj.animation_data.action == source and contacts._action_signature(obj) == source_signature
    inventory = {name: len(getattr(bpy.data, name)) for name in ("objects", "armatures", "scenes", "actions")}

    def build(variant):
        candidate = source.copy()
        candidate.use_fake_user = False
        slot = next(slot for slot in candidate.slots if slot.identifier == identifier)
        curves = w.action_curves(candidate, slot)
        started = time.perf_counter()
        for key, target in desired.items():
            curve = curves.find(key[0], index=key[1]) or curves.new(key[0], index=key[1])
            for index in range(len(curve.keyframe_points) - 1, -1, -1):
                if first <= curve.keyframe_points[index].co.x <= last:
                    curve.keyframe_points.remove(curve.keyframe_points[index], fast=True)
            points = target["points"]
            if variant == "insert":
                for frame, value in points:
                    point = curve.keyframe_points.insert(frame, value, options={"FAST"})
                    point.interpolation = "LINEAR"
            elif variant == "add_direct":
                start = len(curve.keyframe_points)
                curve.keyframe_points.add(len(points))
                for offset, (frame, value) in enumerate(points):
                    point = curve.keyframe_points[start + offset]
                    point.co = (frame, value)
                    point.interpolation = "LINEAR"
            elif variant == "add_foreach":
                existing = [tuple(point.co) for point in curve.keyframe_points]
                start = len(existing)
                curve.keyframe_points.add(len(points))
                coordinates = np.asarray(existing + list(points), dtype=np.float32).reshape(-1)
                curve.keyframe_points.foreach_set("co", coordinates)
                for index in range(start, start + len(points)):
                    curve.keyframe_points[index].interpolation = "LINEAR"
            else:
                raise AssertionError(variant)
            curve.update()
        seconds = time.perf_counter() - started
        max_error = 0.0
        coordinate_mismatches = 0
        metadata_mismatches = 0
        for key, target in desired.items():
            curve = curves.find(key[0], index=key[1])
            state = tuple((tuple(point.co), tuple(point.handle_left), tuple(point.handle_right),
                           point.interpolation, point.handle_left_type, point.handle_right_type)
                          for point in curve.keyframe_points)
            if tuple(row[0] for row in state) != tuple(row[0] for row in target["state"]):
                coordinate_mismatches += 1
            if state != target["state"]:
                metadata_mismatches += 1
            values = np.array([curve.evaluate(float(frame)) for frame in query_frames])
            max_error = max(max_error, float(np.max(np.abs(values - target["values"]))))
        row = {
            "variant": variant,
            "seconds": seconds,
            "curves": len(desired),
            "keys": sum(len(target["points"]) for target in desired.values()),
            "dense_samples": len(desired) * len(query_frames),
            "max_evaluation_error": max_error,
            "coordinate_mismatches": coordinate_mismatches,
            "metadata_mismatches": metadata_mismatches,
        }
        bpy.data.actions.remove(candidate)
        assert inventory == {name: len(getattr(bpy.data, name)) for name in inventory}
        return row

    order = ("insert", "add_direct", "add_foreach", "add_foreach", "add_direct", "insert") * 3
    runs = []
    for index, variant in enumerate(order):
        row = build(variant)
        row["index"] = index
        runs.append(row)
        write(OUT / "progress.json", {"runs": runs})
        print(json.dumps(row), flush=True)
    medians = {variant: statistics.median(row["seconds"] for row in runs if row["variant"] == variant)
               for variant in ("insert", "add_direct", "add_foreach")}
    qualified = [variant for variant in ("add_direct", "add_foreach")
                 if all(row["max_evaluation_error"] == 0.0 and row["coordinate_mismatches"] == 0
                        for row in runs if row["variant"] == variant)]
    selected = min(qualified, key=medians.get) if qualified else None
    report = {
        "schema": 1,
        "complete": True,
        "qualified_candidates": qualified,
        "selected": selected,
        "runs": runs,
        "median_seconds": medians,
        "selected_to_insert_ratio": medians[selected] / medians["insert"] if selected else None,
        "source_preserved": (obj.animation_data.action == source and
                             contacts._action_signature(obj) == source_signature and
                             w.raw_pose(obj) == source_pose and rig_state.mode_values(obj) == source_modes and
                             anchors == [(item.frame, item.payload) for item in obj.b4ml.anchors]),
        "inventory_preserved": inventory == {name: len(getattr(bpy.data, name)) for name in inventory},
        "production_changed": False,
        "method_promoted": False,
        "full_goal_complete": False,
        "runtime_sha256": {path.relative_to(ROOT).as_posix(): sha(path) for path in (ROOT / "b4artists_ml").glob("*.py")},
        "limitations": (
            "Detached transform-curve write kernel on one generated default-Rigify action. This does not include "
            "validation, pose-to-curve sample construction, mode curves, assignment, smoothing, UI scheduling or cancellation."
        ),
    }
    assert report["source_preserved"] and report["inventory_preserved"]
    write(OUT / "report.json", report)
    print(json.dumps({"selected": selected, "medians": medians,
                      "ratio": report["selected_to_insert_ratio"]}, indent=2), flush=True)


def main():
    OUT.mkdir(exist_ok=False)
    write(OUT / "plan.json", {
        "schema": 1,
        "script_sha256": sha(HERE),
        "routing_sha256": sha(ROOT / "docs/b4artists_ml/publication-bulk-routing-v1.json"),
        "order": ["insert", "add_direct", "add_foreach", "add_foreach", "add_direct", "insert"] * 3,
        "selection": "Fastest candidate with exact key coordinates and zero dense evaluation error.",
        "metadata": "Report rather than suppress all FCurve metadata differences.",
        "production_changed": False,
        "max_seconds": 300,
    })
    with (OUT / "host.log").open("w") as log:
        process = subprocess.run(
            ["X:/5.1.0/bforartists.exe", "--background", "--factory-startup", "--disable-autoexec",
             "--python", str(HERE), "--", "host"],
            stdout=log, stderr=subprocess.STDOUT, timeout=300,
            env=dict(os.environ, OPENBLAS_NUM_THREADS="4", PYTHONDONTWRITEBYTECODE="1"))
    report = json.loads((OUT / "report.json").read_text(encoding="utf-8")) if (OUT / "report.json").exists() else None
    process_row = {
        "exit_code": process.returncode,
        "complete": bool(report and report["complete"]),
        "assertions_passed": bool(report and report["source_preserved"] and report["inventory_preserved"]),
        "host_shutdown_clean": process.returncode == 0,
        "log_sha256": sha(OUT / "host.log"),
    }
    write(OUT / "process.json", process_row)
    if report is None:
        print((OUT / "host.log").read_text(encoding="utf-8", errors="replace"))
        raise SystemExit(1)
    print(json.dumps(process_row, indent=2))


if __name__ == "__main__":
    if "host" in sys.argv:
        host_main()
    else:
        main()
