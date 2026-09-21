"""ABBA benchmark of archived and exact-constant production smoothing in the full publisher."""
from pathlib import Path
import ast
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
OUT = TRAINING / "results/constant-curve-publication-v2"
ARCHIVE = ROOT / "releases/b4artists_ml_v0.19.2.zip"


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def sha(path):
    return sha_bytes(path.read_bytes())


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def host_main():
    sys.path[:0] = [str(ROOT), str(TRAINING)]
    import bpy
    import numpy as np
    from unittest.mock import patch
    import b4artists_ml
    from b4artists_ml import contacts, curve_smoothing, rig_state, temporal_generation, temporal_preview
    from b4artists_ml import workflow as w

    with zipfile.ZipFile(ARCHIVE) as archive:
        legacy_bytes = archive.read("b4artists_ml/curve_smoothing.py")
    tree = ast.parse(legacy_bytes.decode("utf-8"))
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "smooth_copy")
    namespace = dict(vars(curve_smoothing))
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(ARCHIVE), "exec"), namespace)
    legacy_smooth_copy = namespace["smooth_copy"]
    current_smooth_copy = curve_smoothing.smooth_copy

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

    first, last = anchors[0][0], anchors[-1][0]
    query_frames = np.arange(first, last + 0.125, 0.125)

    def curves(action):
        slot = next(slot for slot in action.slots if slot.identifier == w._slot(obj.animation_data))
        result = {}
        for curve in w.action_curves(action, slot):
            key = (curve.data_path, curve.array_index)
            state = tuple((tuple(point.co), tuple(point.handle_left), tuple(point.handle_right),
                           point.interpolation, point.handle_left_type, point.handle_right_type)
                          for point in curve.keyframe_points)
            coordinates = tuple(row[0] for row in state)
            result[key] = {
                "state": state,
                "coordinates": coordinates,
                "constant": all(row[1] == coordinates[0][1] for row in coordinates),
                "evaluations": np.array([curve.evaluate(float(frame)) for frame in query_frames]),
            }
        return result

    runs = []
    reference_output = None
    for index, variant in enumerate(("legacy", "current", "current", "legacy")):
        smoothing = legacy_smooth_copy if variant == "legacy" else current_smooth_copy
        smoothing_reports = []

        def record_smoothing(*args, **kwargs):
            result, report = smoothing(*args, **kwargs)
            smoothing_reports.append(report)
            return result, report

        scene.frame_set(1)
        obj.b4ml.temporal_smoothing = True
        ticks = []
        with patch.object(curve_smoothing, "smooth_copy", record_smoothing):
            started = time.perf_counter()
            temporal_preview.start(obj, scene)
            setup_seconds = time.perf_counter() - started
            while obj.b4ml.temporal_running:
                started = time.perf_counter()
                done = temporal_preview.step(obj)
                ticks.append(time.perf_counter() - started)
                if not done:
                    assert obj.animation_data.action == source
                    assert contacts._action_signature(obj) == source_signature
        assert len(smoothing_reports) == 1
        candidate = obj.animation_data.action
        output = curves(candidate)
        comparison = {"dense_samples": len(query_frames) * len(output), "max_evaluation_error": 0.0,
                      "metadata_changes_on_constant_curves": 0, "metadata_changes_on_nonconstant_curves": 0}
        if reference_output is None:
            reference_output = output
        else:
            assert output.keys() == reference_output.keys()
            for key, current in output.items():
                legacy = reference_output[key]
                assert current["coordinates"] == legacy["coordinates"]
                error = float(np.max(np.abs(current["evaluations"] - legacy["evaluations"])))
                comparison["max_evaluation_error"] = max(comparison["max_evaluation_error"], error)
                if current["state"] != legacy["state"]:
                    field = ("metadata_changes_on_constant_curves" if current["constant"]
                             else "metadata_changes_on_nonconstant_curves")
                    comparison[field] += 1
            assert comparison["max_evaluation_error"] == 0.0
            assert comparison["metadata_changes_on_nonconstant_curves"] == 0
        w.finish_preview(obj, scene, False)
        assert obj.animation_data.action == source
        assert contacts._action_signature(obj) == source_signature
        assert w.raw_pose(obj) == source_pose
        assert rig_state.mode_values(obj) == source_modes
        assert anchors == [(item.frame, item.payload) for item in obj.b4ml.anchors]
        assert inventory == {name: len(getattr(bpy.data, name)) for name in inventory}
        assert not temporal_preview._JOBS and not temporal_generation._LIVE and not temporal_generation._OWNERS
        row = {
            "index": index,
            "variant": variant,
            "seconds": setup_seconds + sum(ticks),
            "setup_seconds": setup_seconds,
            "ticks": len(ticks),
            "publication_tick_seconds": ticks[-1],
            "max_tick_seconds": max(ticks),
            "p95_tick_seconds": float(np.percentile(ticks, 95)),
            "smoothing_report": smoothing_reports[0],
            "comparison": comparison,
            "exact_curve_evaluation": True,
            "exact_key_coordinates": True,
            "nonconstant_metadata_preserved": True,
            "source_preserved": True,
            "inventory_preserved": True,
        }
        runs.append(row)
        write(OUT / "progress.json", {"runs": runs})
        print(json.dumps(row), flush=True)

    total_medians = {
        name: statistics.median(row["seconds"] for row in runs if row["variant"] == name)
        for name in ("legacy", "current")
    }
    publication_medians = {
        name: statistics.median(row["publication_tick_seconds"] for row in runs if row["variant"] == name)
        for name in ("legacy", "current")
    }
    total_ratio = total_medians["current"] / total_medians["legacy"]
    publication_ratio = publication_medians["current"] / publication_medians["legacy"]
    plan = json.loads((OUT / "plan.json").read_text(encoding="utf-8"))
    report = {
        "schema": 1,
        "complete": True,
        "qualified": publication_ratio <= plan["publication_ratio_max"] and total_ratio <= plan["total_ratio_max"],
        "runs": runs,
        "median_seconds": total_medians,
        "median_publication_tick_seconds": publication_medians,
        "total_ratio": total_ratio,
        "publication_ratio": publication_ratio,
        "performance_gate_passed": publication_ratio <= plan["publication_ratio_max"] and total_ratio <= plan["total_ratio_max"],
        "exact_dense_curve_evaluation": True,
        "exact_key_coordinates": True,
        "nonconstant_metadata_preserved": True,
        "source_preserved": True,
        "inventory_preserved": True,
        "legacy_source_sha256": sha_bytes(legacy_bytes),
        "archive_sha256": sha(ARCHIVE),
        "reference_sha256": sha(reference),
        "production_changed": True,
        "method_promoted": False,
        "full_goal_complete": False,
        "runtime_sha256": {
            path.relative_to(ROOT).as_posix(): sha(path)
            for path in (ROOT / "b4artists_ml").glob("*.py")
        },
        "limitations": (
            "Serial headless default-Rigify reach/hold workflow on one host; this isolates smoothing publication "
            "latency and does not establish UI queue latency, broad hardware performance, or animation quality."
        ),
    }
    write(OUT / "report.json", report)
    print(json.dumps({
        "qualified": report["qualified"],
        "total_medians": total_medians,
        "publication_medians": publication_medians,
        "total_ratio": total_ratio,
        "publication_ratio": publication_ratio,
    }, indent=2), flush=True)


def main():
    OUT.mkdir(exist_ok=False)
    with zipfile.ZipFile(ARCHIVE) as archive:
        legacy_bytes = archive.read("b4artists_ml/curve_smoothing.py")
    plan = {
        "schema": 1,
        "script_sha256": sha(HERE),
        "routing_sha256": sha(ROOT / "docs/b4artists_ml/publication-latency-production-routing-v1.json"),
        "archive_sha256": sha(ARCHIVE),
        "legacy_source_sha256": sha_bytes(legacy_bytes),
        "order": ["legacy", "current", "current", "legacy"],
        "selection": "Archived 0.19.2 smooth_copy versus current production smooth_copy inside the same full publisher.",
        "publication_ratio_max": 0.80,
        "total_ratio_max": 1.02,
        "invariants": "Exact key coordinates and dense curve evaluation; full metadata equality on every nonconstant curve; exact source pose, action, rig modes, anchors and inventory recovery.",
        "max_seconds": 300,
        "concurrent_task_jobs": False,
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
        "assertions_passed": bool(report and report["exact_dense_curve_evaluation"] and report["exact_key_coordinates"] and report["nonconstant_metadata_preserved"] and report["source_preserved"] and report["inventory_preserved"]),
        "performance_gate_passed": bool(report and report["performance_gate_passed"]),
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
