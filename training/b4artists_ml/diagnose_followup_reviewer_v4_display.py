"""Prove whether reviewer v4 displayed each scene's native motion layer.

The v4 packet reused a legacy extractor.  This diagnostic reproduces its raw
samples, applies the saved native motion-instance transform, and independently
checks the resulting points against the depsgraph's displayed instance.
"""
from pathlib import Path
import hashlib
import json
import math
import os
import subprocess
import sys
import time
import traceback

HERE = Path(__file__).resolve()
TRAIN = HERE.parent
ROOT = HERE.parents[2]
REVIEW = TRAIN / "results/review-directed-followup-reviewer-v4"
SOURCE = REVIEW / "review-data.json"
OUT = TRAIN / "results/review-directed-followup-reviewer-v4-display-audit"
HOST = Path(r"X:\5.1.0\bforartists.exe")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)


def case_data(variant, profile, task):
    case = next(row for row in read(SOURCE)["cases"] if row["id"] == f"{profile}/{task}")
    label = next(label for label, identity in case["reveal"].items() if identity["variant"] == variant)
    return case, label, case["reveal"][label], case["methods"][label]


def transform_point(matrix, point):
    return [
        sum(matrix[row][column] * point[column] for column in range(3)) + matrix[row][3]
        for row in range(3)
    ]


def metrics(samples):
    pelvis = [sample[0] for sample in samples]
    endpoints = max(pelvis[0][2], pelvis[-1][2])
    return {
        "pelvis_vertical_range_body_fraction": max(row[2] for row in pelvis) - min(row[2] for row in pelvis),
        "pelvis_apex_rise_from_endpoints_body_fraction": max(row[2] for row in pelvis) - endpoints,
        "pelvis_forward_distance_body_fraction": abs(pelvis[-1][1] - pelvis[0][1]),
    }


def marker(value):
    return "B4ML_V4_DISPLAY_AUDIT=" + json.dumps({
        key: value.get(key)
        for key in ("variant", "profile", "task", "complete", "maximum_display_difference", "error", "seconds")
    }, allow_nan=False)


def host(variant, profile, task):
    import bpy
    from mathutils import Vector

    sys.path[:0] = [str(ROOT), str(TRAIN)]
    import b4artists_ml
    from b4artists_ml import body_solver, motion_layer, posing

    destination = OUT / "extracted" / f"{variant}-{profile}-{task}.json"
    result = dict(variant=variant, profile=profile, task=task, complete=False)
    started = time.perf_counter()
    try:
        b4artists_ml.register()
        case, label, identity, prior = case_data(variant, profile, task)
        blend = ROOT / identity["blend_path"]
        report_path = blend.parent / "report.json"
        report = read(report_path)
        if sha(blend) != identity["blend_sha256"] or sha(report_path) != identity["report_sha256"]:
            raise ValueError("Reviewer source identity changed")
        armatures = [obj for obj in bpy.data.objects if obj.type == "ARMATURE" and hasattr(obj, "b4ml")]
        animated = [obj for obj in armatures if (
            (obj.animation_data and obj.animation_data.action is not None)
            or getattr(obj.b4ml, "candidate_action", None) is not None
        )]
        if len(animated) != 1:
            raise ValueError(f"Expected one animated armature, found {len(animated)}")
        obj = animated[0]
        scene = next(scene for scene in bpy.data.scenes if obj.name in scene.objects)
        bpy.context.window.scene = scene
        binding = body_solver.mapping(obj, writable=False)
        names = binding["names"]
        axes = [Vector(row) for row in report["task_basis_world"]]
        height = float(report["reference_height"])
        frames = prior["frames"]
        raw_rows, corrected_rows, layers = [], [], []
        origin = None
        instance_error = 0.0
        has_layer = motion_layer.find(obj) is not None
        if has_layer:
            motion_layer.validate(obj)
        for frame in frames:
            scene.frame_set(math.floor(frame), subframe=frame - math.floor(frame))
            posing._update(obj)
            graph = bpy.context.evaluated_depsgraph_get()
            evaluated = obj.evaluated_get(graph)
            raw = [evaluated.matrix_world @ evaluated.pose.bones[name].head for name in names]
            if origin is None:
                origin = raw[0].copy()
            layer = motion_layer.transform(obj)
            layer_values = [list(row) for row in layer]
            corrected = [Vector(transform_point(layer_values, list(point))) for point in raw]
            instances = [
                instance.matrix_world.copy()
                for instance in graph.object_instances
                if instance.object.original == obj and bool(instance.is_instance) == has_layer
            ]
            if len(instances) != 1:
                raise ValueError(f"Expected one displayed armature instance, found {len(instances)}")
            native = [instances[0] @ evaluated.pose.bones[name].head for name in names]
            instance_error = max(
                instance_error,
                max((a - b).length / height for a, b in zip(corrected, native)),
            )

            def project(points):
                return [[round(float((point - origin).dot(axis) / height), 7) for axis in axes] for point in points]

            raw_rows.append(project(raw))
            corrected_rows.append(project(corrected))
            layers.append(layer_values)
        legacy_error = max(
            abs(a - b)
            for sample_a, sample_b in zip(raw_rows, prior["samples"])
            for point_a, point_b in zip(sample_a, sample_b)
            for a, b in zip(point_a, point_b)
        )
        if legacy_error > 2e-6 or instance_error > 2e-6:
            raise ValueError(f"Native parity failure: legacy={legacy_error}, displayed={instance_error}")
        difference = max(
            abs(a - b)
            for sample_a, sample_b in zip(raw_rows, corrected_rows)
            for point_a, point_b in zip(sample_a, sample_b)
            for a, b in zip(point_a, point_b)
        )
        result.update(
            schema="b4ml-followup-reviewer-v4-display-audit-extract-v1",
            complete=True,
            case_id=case["id"],
            label=label,
            source_data_sha256=sha(SOURCE),
            blend_path=identity["blend_path"],
            blend_sha256=identity["blend_sha256"],
            report_sha256=identity["report_sha256"],
            frames=frames,
            fps=prior["fps"],
            floor_z=prior["floor_z"],
            priority_frames=prior["priority_frames"],
            semantic_bones=list(names),
            has_native_motion_layer=has_layer,
            raw_samples=raw_rows,
            corrected_samples=corrected_rows,
            layer_matrices=layers,
            maximum_legacy_reproduction_error=legacy_error,
            maximum_native_instance_error=instance_error,
            maximum_display_difference=difference,
            raw_metrics=metrics(raw_rows),
            corrected_metrics=metrics(corrected_rows),
            training_authorized=False,
            model_promotion_authorized=False,
        )
    except BaseException:
        result.update(error=traceback.format_exc())
    result["seconds"] = time.perf_counter() - started
    write_new(destination, result)
    print(marker(result), flush=True)


def qualified_exit(code, log, value):
    if value.get("complete") is not True:
        return False
    index = log.find(marker(value))
    if index < 0:
        return False
    if code == 0:
        return "EXCEPTION_ACCESS_VIOLATION" not in log
    crash = log.find("EXCEPTION_ACCESS_VIOLATION")
    return (
        code & 0xFFFFFFFF == 0xC0000005
        and crash > index
        and "ucrtbase.dll" in log[crash:]
    )


def run():
    if OUT.exists():
        raise RuntimeError("Immutable display audit already exists: " + str(OUT))
    (OUT / "extracted").mkdir(parents=True)
    (OUT / "logs").mkdir()
    cases = [(case["profile"], case["task"]) for case in read(SOURCE)["cases"]]
    processes = []
    for variant in ("baseline", "candidate"):
        for profile, task in cases:
            name = f"{variant}-{profile}-{task}"
            log_path = OUT / "logs" / f"{name}.log"
            at = time.perf_counter()
            with log_path.open("x", encoding="utf-8") as stream:
                process = subprocess.run(
                    [str(HOST), "--background", "--factory-startup", "--disable-autoexec",
                     str(ROOT / case_data(variant, profile, task)[2]["blend_path"]),
                     "--python", str(HERE), "--", variant, profile, task],
                    stdout=stream,
                    stderr=subprocess.STDOUT,
                    timeout=180,
                    env=dict(os.environ, OPENBLAS_NUM_THREADS="4", PYTHONDONTWRITEBYTECODE="1"),
                )
            extract_path = OUT / "extracted" / f"{name}.json"
            value = read(extract_path) if extract_path.exists() else {}
            qualified = qualified_exit(
                process.returncode,
                log_path.read_text(encoding="utf-8", errors="replace"),
                value,
            )
            row = {
                "variant": variant,
                "profile": profile,
                "task": task,
                "returncode": process.returncode,
                "qualified": qualified,
                "seconds": time.perf_counter() - at,
                "extract_sha256": sha(extract_path) if extract_path.exists() else None,
                "log_sha256": sha(log_path),
            }
            processes.append(row)
            print(json.dumps(row), flush=True)
            if not qualified:
                write_new(OUT / "processes.json", processes)
                raise RuntimeError("Unqualified extraction: " + name)
    write_new(OUT / "processes.json", processes)
    extracts = [read(path) for path in sorted((OUT / "extracted").glob("*.json"))]
    affected = sorted({row["case_id"] for row in extracts if row["maximum_display_difference"] > 2e-6})
    receipt = {
        "schema": "b4ml-followup-reviewer-v4-display-audit-v1",
        "complete": len(processes) == 16 and all(row["qualified"] for row in processes),
        "source_data_sha256": sha(SOURCE),
        "processes_sha256": sha(OUT / "processes.json"),
        "native_comparisons": len(extracts),
        "affected_cases": affected,
        "maximum_legacy_reproduction_error": max(row["maximum_legacy_reproduction_error"] for row in extracts),
        "maximum_native_instance_error": max(row["maximum_native_instance_error"] for row in extracts),
        "maximum_display_difference": max(row["maximum_display_difference"] for row in extracts),
        "v4_global_motion_representation_qualified": not affected,
        "relative_pose_feedback_qualified": True,
        "training_authorized": False,
        "model_promotion_authorized": False,
        "full_goal_complete": False,
    }
    write_new(OUT / "receipt.json", receipt)
    print(json.dumps(receipt, indent=2), flush=True)


if __name__ == "__main__":
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
        if len(args) != 3:
            raise ValueError("Expected variant/profile/task")
        host(*args)
    else:
        run()
