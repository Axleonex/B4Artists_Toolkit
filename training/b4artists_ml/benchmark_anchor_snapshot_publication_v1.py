"""ABBA benchmark of 0.19.3 and one-snapshot temporal publication."""
from pathlib import Path
import ast
import copy
import hashlib
import json
import os
import statistics
import subprocess
import sys
import time
import zipfile


HERE = Path(__file__).resolve()
TRAINING = HERE.parent
ROOT = TRAINING.parents[1]
OUT = TRAINING / "results/anchor-snapshot-publication-v3"
ARCHIVE = ROOT / "releases/b4artists_ml_v0.19.3.zip"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def archived_function(archive, module, name, namespace):
    source = archive.read(f"b4artists_ml/{module}.py")
    tree = ast.parse(source.decode("utf-8"))
    node = next(item for item in tree.body if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == name)
    globals_copy = dict(namespace)
    exec(compile(ast.Module(body=[node], type_ignores=[]), f"{ARCHIVE}!/{module}.py", "exec"), globals_copy)
    return globals_copy[name], hashlib.sha256(source).hexdigest()


def host_main():
    sys.path[:0] = [str(ROOT), str(ROOT / "tests"), str(TRAINING)]
    from unittest.mock import patch
    import bpy
    import numpy as np
    import b4artists_ml
    from b4artists_ml import contacts, curve_smoothing, rig_state, temporal_generation, temporal_math, temporal_preview
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
    inventory = {name: len(getattr(bpy.data, name)) for name in ("objects", "armatures", "scenes", "actions")}

    iterator = temporal_generation.generate_private_steps(
        obj, lambda observed, t: observed.baseline(t), context=False,
        prepare_predictor=temporal_math.prepare)
    try:
        while True:
            try:
                next(iterator)
            except StopIteration as done:
                samples, _ = done.value
                break
    finally:
        iterator.close()

    with zipfile.ZipFile(ARCHIVE) as archive:
        old_preview, workflow_sha = archived_function(archive, "workflow", "preview", vars(w))
        old_smooth, smoothing_sha = archived_function(archive, "curve_smoothing", "smooth_copy", vars(curve_smoothing))
        old_publish, publication_sha = archived_function(archive, "temporal_preview", "_publish", vars(temporal_preview))

    current = (w.preview, curve_smoothing.smooth_copy, temporal_preview._publish)
    legacy = (old_preview, old_smooth, old_publish)
    first, last = anchors[0][0], anchors[-1][0]
    query_frames = np.arange(first, last + 0.125, 0.125)

    def curve_state(action):
        slot = next(slot for slot in action.slots if slot.identifier == w._slot(obj.animation_data))
        result = {}
        for curve in w.action_curves(action, slot):
            key = (curve.data_path, curve.array_index)
            result[key] = {
                "keys": tuple((tuple(point.co), tuple(point.handle_left), tuple(point.handle_right),
                               point.interpolation, point.handle_left_type, point.handle_right_type)
                              for point in curve.keyframe_points),
                "evaluations": np.array([curve.evaluate(float(frame)) for frame in query_frames]),
            }
        return result

    runs = []
    reference_output = None
    order = ("legacy", "current", "current", "legacy", "legacy", "current")
    for index, variant in enumerate(order):
        functions = legacy if variant == "legacy" else current
        obj.b4ml.temporal_smoothing = True
        read_count = 0
        original_read = w.read_anchors

        def counted_read(*args, **kwargs):
            nonlocal read_count
            read_count += 1
            return original_read(*args, **kwargs)

        # The archived preview resolves read_anchors directly from its captured
        # module globals, while the two other consumers resolve it through w.
        if variant == "legacy":
            functions[0].__globals__["read_anchors"] = counted_read
        # Generation creates this detached buffer before publication. Keep that
        # preparation outside the timed boundary for both variants.
        payload = copy.deepcopy(samples)
        if variant == "current":
            payload = w._ValidatedPoseSamples(payload)
        with patch.object(w, "preview", functions[0]), patch.object(curve_smoothing, "smooth_copy", functions[1]), \
             patch.object(temporal_preview, "_publish", functions[2]), patch.object(w, "read_anchors", counted_read):
            started = time.perf_counter()
            temporal_preview._publish({"obj": obj, "scene": scene, "smoothing": True}, payload)
            seconds = time.perf_counter() - started
        if variant == "current":
            assert payload.consumed

        candidate = obj.animation_data.action
        output = curve_state(candidate)
        comparison = {"dense_samples": len(query_frames) * len(output), "max_error": 0.0,
                      "key_or_metadata_mismatches": 0}
        if reference_output is None:
            reference_output = output
        else:
            assert output.keys() == reference_output.keys()
            for key, values in output.items():
                reference_values = reference_output[key]
                comparison["max_error"] = max(
                    comparison["max_error"],
                    float(np.max(np.abs(values["evaluations"] - reference_values["evaluations"]))))
                comparison["key_or_metadata_mismatches"] += values["keys"] != reference_values["keys"]
            assert comparison["max_error"] == 0.0
            assert comparison["key_or_metadata_mismatches"] == 0

        w.finish_preview(obj, scene, False)
        assert obj.animation_data.action == source
        assert contacts._action_signature(obj) == source_signature
        assert w.raw_pose(obj) == source_pose
        assert rig_state.mode_values(obj) == source_modes
        assert anchors == [(item.frame, item.payload) for item in obj.b4ml.anchors]
        assert inventory == {name: len(getattr(bpy.data, name)) for name in inventory}
        row = {"index": index, "variant": variant, "seconds": seconds, "anchor_reads": read_count,
               "comparison": comparison, "source_preserved": True, "inventory_preserved": True}
        runs.append(row)
        write(OUT / "progress.json", {"runs": runs})
        print(json.dumps(row), flush=True)

    medians = {name: statistics.median(row["seconds"] for row in runs if row["variant"] == name)
               for name in ("legacy", "current")}
    ratio = medians["current"] / medians["legacy"]
    report = {
        "schema": 1,
        "complete": True,
        "qualified": ratio <= 0.90,
        "runs": runs,
        "median_publication_seconds": medians,
        "current_to_legacy_ratio": ratio,
        "reduction_percent": (1.0 - ratio) * 100.0,
        "legacy_anchor_reads": [row["anchor_reads"] for row in runs if row["variant"] == "legacy"],
        "current_anchor_reads": [row["anchor_reads"] for row in runs if row["variant"] == "current"],
        "exact_dense_curve_evaluation": True,
        "exact_keys_and_metadata": True,
        "source_preserved": True,
        "inventory_preserved": True,
        "archive_sha256": sha(ARCHIVE),
        "archived_module_sha256": {"workflow.py": workflow_sha, "curve_smoothing.py": smoothing_sha,
                                   "temporal_preview.py": publication_sha},
        "runtime_sha256": {path.relative_to(ROOT).as_posix(): sha(path) for path in (ROOT / "b4artists_ml").glob("*.py")},
        "production_changed": True,
        "method_promoted": False,
        "full_goal_complete": False,
        "limitations": "Serial headless default-Rigify publication on one host; excludes generation and UI queue latency.",
    }
    write(OUT / "report.json", report)
    print(json.dumps({key: report[key] for key in ("qualified", "median_publication_seconds",
                                                   "current_to_legacy_ratio", "reduction_percent",
                                                   "legacy_anchor_reads", "current_anchor_reads")}, indent=2), flush=True)


def main():
    OUT.mkdir(exist_ok=False)
    write(OUT / "plan.json", {
        "schema": 1,
        "script_sha256": sha(HERE),
        "routing_sha256": sha(ROOT / "docs/b4artists_ml/publication-anchor-cache-production-routing-v1.json"),
        "archive_sha256": sha(ARCHIVE),
        "order": ["legacy", "current", "current", "legacy", "legacy", "current"],
        "publication_ratio_max": 0.90,
        "invariants": "One current anchor read versus three legacy reads; exact dense evaluation, keys and metadata; exact source and inventory recovery.",
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
        "assertions_passed": bool(report and report["exact_dense_curve_evaluation"] and
                                  report["exact_keys_and_metadata"] and report["source_preserved"] and
                                  report["inventory_preserved"]),
        "performance_gate_passed": bool(report and report["qualified"]),
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
