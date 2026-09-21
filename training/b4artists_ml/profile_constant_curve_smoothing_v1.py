"""Profile skipping handle rewrites for exactly constant generated curves."""
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
OUT = TRAINING / "results" / "constant-curve-smoothing-v1"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def host_main():
    sys.path.insert(0, str(ROOT))
    import bpy
    import numpy as np
    import b4artists_ml
    from b4artists_ml import contacts, curve_smoothing, rig_state, temporal_preview
    from b4artists_ml import workflow as w

    def candidate_smooth_copy(obj, action, first, last, *, names=None):
        rows = w.read_anchors(obj)
        owned = set()
        quaternion_paths = []
        selected_names = set(rows[0][1]["pose"]) if names is None else set(names)
        if not selected_names.issubset(rows[0][1]["pose"]):
            raise ValueError("Smooth only captured controls")
        for name, value in rows[0][1]["pose"].items():
            if name not in selected_names:
                continue
            bone = obj.pose.bones[name]
            for prop in ("location", "scale"):
                owned.update((bone.path_from_id(prop), index) for index in value["channels"][prop])
            if value["channels"]["rotation"]:
                if value["mode"] == "AXIS_ANGLE":
                    raise ValueError("Axis-angle continuity needs a separate adapter")
                prop = "rotation_quaternion" if value["mode"] == "QUATERNION" else "rotation_euler"
                count = 4 if prop == "rotation_quaternion" else 3
                owned.update((bone.path_from_id(prop), index) for index in range(count))
                if count == 4:
                    quaternion_paths.append(bone.path_from_id(prop))

        identifier = w._slot(obj.animation_data)
        slot = next(slot for slot in action.slots if slot.identifier == identifier)
        curves = w.action_curves(action, slot)
        plans = {}
        samples = {}
        skipped = {}
        for curve in curves:
            key = (curve.data_path, curve.array_index)
            if key not in owned:
                continue
            if curve.lock or curve.mute or len(curve.modifiers):
                raise ValueError("Curve is not freely editable")
            xy = np.array([list(point.co) for point in curve.keyframe_points])
            x, y = xy.T
            indices = np.flatnonzero((x >= first) & (x <= last))
            if len(indices) < 2 or x[indices[0]] != first or x[indices[-1]] != last:
                raise ValueError("Generated span endpoints must be keyed")
            selected = xy[indices]
            samples[key] = selected
            if np.all(selected[:, 1] == selected[0, 1]):
                skipped[key] = {"keys": len(indices), "value": float(selected[0, 1])}
                continue
            left, right = curve_smoothing.handles(selected[:, 0], selected[:, 1])
            plans[key] = (selected, left, right, indices, xy)

        for path in quaternion_paths:
            if not all((path, index) in samples for index in range(4)):
                raise ValueError("Complete quaternion curves required")
            times = [samples[(path, index)][:, 0] for index in range(4)]
            if not all(np.array_equal(row, times[0]) for row in times):
                raise ValueError("Quaternion sample times disagree")
            quaternions = np.stack([samples[(path, index)][:, 1] for index in range(4)], axis=-1)
            norm = np.linalg.norm(quaternions, axis=-1)
            if np.any(norm < 1e-8) or np.any(np.sum(quaternions[:-1] * quaternions[1:], axis=-1) <= 0):
                raise ValueError("Quaternion signs or turns need explicit continuous representation")

        candidate = action.copy()
        candidate.use_fake_user = False
        candidate.name = action.name + " Shape curves constant-skip"
        try:
            slot = next(slot for slot in candidate.slots if slot.identifier == identifier)
            curves = w.action_curves(candidate, slot)
            for key, (selected, left, right, indices, xy) in plans.items():
                curve = curves.find(key[0], index=key[1])

                def state(point):
                    return (tuple(point.co), tuple(point.handle_left), tuple(point.handle_right),
                            point.handle_left_type, point.handle_right_type, point.interpolation)

                before = [state(point) for point in curve.keyframe_points]
                for local, index in enumerate(indices):
                    point = curve.keyframe_points[int(index)]
                    if local > 0:
                        point.handle_left_type = "FREE"
                        point.handle_left = left[local]
                    if local < len(indices) - 1:
                        point.handle_right_type = "FREE"
                        point.handle_right = right[local]
                        point.interpolation = "BEZIER"
                if not np.array_equal(np.array([list(point.co) for point in curve.keyframe_points]), xy):
                    raise ValueError("Key sample changed")
                after = [state(point) for point in curve.keyframe_points]
                for index in range(len(before)):
                    if index not in indices and before[index] != after[index]:
                        raise ValueError("Unowned key changed")
                start, end = int(indices[0]), int(indices[-1])
                if ((start > 0 and (before[start][1] != after[start][1] or
                                    before[start][3] != after[start][3])) or
                        (end < len(before) - 1 and
                         (before[end][2] != after[end][2] or before[end][4:] != after[end][4:]))):
                    raise ValueError("Unowned boundary handle changed")
            return candidate, {
                "planned_curves": len(plans),
                "skipped_constant_curves": len(skipped),
                "skipped_constant_keys": sum(row["keys"] for row in skipped.values()),
                "owned_curves": len(samples),
                "quaternion_groups": len(quaternion_paths),
                "authored_coordinates_unchanged": True,
            }
        except BaseException:
            if candidate.users == 0:
                bpy.data.actions.remove(candidate)
            raise

    def curve_map(obj, action):
        slot = next(slot for slot in action.slots if slot.identifier == w._slot(obj.animation_data))
        return {(curve.data_path, curve.array_index): curve for curve in w.action_curves(action, slot)}

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
    inventory = {name: len(getattr(bpy.data, name)) for name in ("objects", "armatures", "scenes", "actions")}

    obj.b4ml.temporal_smoothing = False
    generated = temporal_preview.run(obj, scene)
    rows = w.read_anchors(obj)
    first, last = rows[0][0], rows[-1][0]
    generated_signature = contacts._action_signature(obj)
    before_generated = {
        key: tuple((tuple(point.co), tuple(point.handle_left), tuple(point.handle_right),
                    point.handle_left_type, point.handle_right_type, point.interpolation)
                   for point in curve.keyframe_points)
        for key, curve in curve_map(obj, generated).items()
    }

    runs = []
    outputs = []
    metrics = []
    for index, variant in enumerate(("current", "constant_skip", "constant_skip", "current")):
        started = time.perf_counter()
        if variant == "current":
            output, row = curve_smoothing.smooth_copy(obj, generated, first, last)
        else:
            output, row = candidate_smooth_copy(obj, generated, first, last)
        seconds = time.perf_counter() - started
        outputs.append(output)
        metrics.append(row)
        runs.append({"index": index, "variant": variant, "seconds": seconds, "metrics": row})

    queries = np.arange(first, last + 0.125, 0.125)
    baseline_curves = curve_map(obj, outputs[0])
    comparisons = []
    for output_index, output in enumerate(outputs[1:], 1):
        actual_curves = curve_map(obj, output)
        assert actual_curves.keys() == baseline_curves.keys()
        max_error = 0.0
        for key, baseline_curve in baseline_curves.items():
            actual_curve = actual_curves[key]
            for frame in queries:
                max_error = max(max_error, abs(baseline_curve.evaluate(float(frame)) -
                                                   actual_curve.evaluate(float(frame))))
        comparisons.append({
            "output_index": output_index,
            "variant": runs[output_index]["variant"],
            "samples": int(len(queries) * len(baseline_curves)),
            "max_curve_evaluation_error": max_error,
        })
        assert max_error == 0.0

    assert before_generated == {
        key: tuple((tuple(point.co), tuple(point.handle_left), tuple(point.handle_right),
                    point.handle_left_type, point.handle_right_type, point.interpolation)
                   for point in curve.keyframe_points)
        for key, curve in curve_map(obj, generated).items()
    }
    for output in outputs:
        if output.users == 0:
            bpy.data.actions.remove(output)
    w.finish_preview(obj, scene, False)
    assert obj.animation_data.action == source
    assert contacts._action_signature(obj) == source_signature
    assert w.raw_pose(obj) == source_pose
    assert rig_state.mode_values(obj) == source_modes
    assert anchors == [(item.frame, item.payload) for item in obj.b4ml.anchors]
    assert inventory == {name: len(getattr(bpy.data, name)) for name in inventory}
    assert not temporal_preview._JOBS

    medians = {
        variant: statistics.median(row["seconds"] for row in runs if row["variant"] == variant)
        for variant in ("current", "constant_skip")
    }
    report = {
        "schema": 1,
        "complete": True,
        "qualified": False,
        "reference_sha256": sha256(reference),
        "generated_signature": generated_signature,
        "runs": runs,
        "medians": medians,
        "candidate_to_current_ratio": medians["constant_skip"] / medians["current"],
        "comparisons": comparisons,
        "exact_dense_curve_evaluation": True,
        "generated_action_unchanged": True,
        "source_preserved": True,
        "inventory_preserved": True,
        "production_changed": False,
        "confirmation_read": False,
        "method_promoted": False,
        "runtime_sha256": {
            path.relative_to(ROOT).as_posix(): sha256(path)
            for path in (ROOT / "b4artists_ml").glob("*.py")
        },
        "decision": (
            "This is a bounded constant-curve smoothing probe. Promote only after a prospective production plan, "
            "fault/lifecycle coverage, broader rigs, and a full serial workflow comparison."
        ),
        "limitations": (
            "One generated default-Rigify reach/hold action in a headless host; no UI queue latency, memory, visual "
            "quality, learned motion, broader hardware or Cascadeur comparison."
        ),
    }
    write(OUT / "report.json", report)
    print(json.dumps({
        "medians": medians,
        "ratio": report["candidate_to_current_ratio"],
        "candidate_metrics": metrics[1],
        "dense_comparisons": comparisons,
        "production_changed": False,
    }, indent=2), flush=True)


def main():
    OUT.mkdir(exist_ok=False)
    plan = {
        "schema": 1,
        "script_sha256": sha256(HERE),
        "routing_sha256": sha256(ROOT / "docs/b4artists_ml/publication-latency-routing-v1.json"),
        "order": ["current", "constant_skip", "constant_skip", "current"],
        "dense_step_frames": 0.125,
        "candidate_scope": "Skip handle rewriting only when every generated-span scalar key is bit-identical.",
        "acceptance": [
            "Exact FCurve evaluation against current smoothing at every one-eighth frame.",
            "Input generated action, source action, pose, rig modes, anchors and data inventory preserved.",
            "Candidate median faster than current median in serial ABBA order."
        ],
        "max_seconds": 300,
    }
    write(OUT / "plan.json", plan)
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
        "assertions_passed": bool(report and report["exact_dense_curve_evaluation"] and
                                  report["source_preserved"] and report["inventory_preserved"]),
        "host_shutdown_clean": process.returncode == 0,
        "log_sha256": sha256(OUT / "host.log"),
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
