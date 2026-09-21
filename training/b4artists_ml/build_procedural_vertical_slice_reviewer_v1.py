"""Build a blind, offline human review packet from the frozen v12 real-rig scenes.

The packet compares each saved pre-contact candidate with its corrected candidate.
It does not create human ratings and does not turn automated gates into visual evidence.
"""
from pathlib import Path
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import time
import traceback


HERE = Path(__file__).resolve()
TRAIN = HERE.parent
ROOT = HERE.parents[2]
SOURCE = TRAIN / "results/procedural-vertical-slice-v12"
AGGREGATE = SOURCE / "aggregate.json"
PROTOCOL_PATH = TRAIN / "procedural_vertical_slice_protocol_v12.json"
TEMPLATE = TRAIN / "procedural_vertical_slice_review_template_v1.html"
OUT = TRAIN / "results/procedural-vertical-slice-reviewer-v1"
HOST = Path("X:/5.1.0/bforartists.exe")
NAMES = ("Hips", "Spine", "Spine1", "Neck1", "Head", "LeftArm", "LeftForeArm", "LeftHand",
         "RightArm", "RightForeArm", "RightHand", "LeftUpLeg", "LeftLeg", "LeftFoot",
         "RightUpLeg", "RightLeg", "RightFoot")
ROLES = ("pelvis", "spine", "chest", "neck", "head", "upper_arm_L", "elbow_L", "wrist_L",
         "upper_arm_R", "elbow_R", "wrist_R", "hip_L", "knee_L", "ankle_L",
         "hip_R", "knee_R", "ankle_R")
PARENTS = (-1, 0, 1, 2, 3, 2, 5, 6, 2, 8, 9, 0, 11, 12, 0, 14, 15)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write(path, value):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temp, path)


def _case_paths(profile, task):
    directory = SOURCE / profile / task
    return directory, directory / f"{profile}-{task}.blend", directory / "report.json"


def host(profile, task):
    import bpy
    import numpy as np
    from mathutils import Vector

    sys.path[:0] = [str(ROOT), str(TRAIN)]
    import b4artists_ml
    from b4artists_ml import body_solver, motion_layer, posing, workflow

    destination = OUT / "extracted" / f"{profile}-{task}.json"
    result = dict(schema="b4ml-procedural-review-extract-v1", profile=profile, task=task,
                  complete=False, full_goal_complete=False)
    started = time.perf_counter()
    try:
        b4artists_ml.register()
        _, blend, report_path = _case_paths(profile, task)
        report = read(report_path)
        if sha(blend) != report["blend_sha256"]:
            raise ValueError("Saved scene no longer matches its v12 report")
        objects = [obj for obj in bpy.data.objects if obj.type == "ARMATURE" and
                   hasattr(obj, "b4ml") and obj.b4ml.candidate_action]
        if len(objects) != 1:
            raise ValueError(f"Expected one review armature, found {len(objects)}")
        obj = objects[0]
        scene = next(scene for scene in bpy.data.scenes if obj.name in scene.objects)
        bpy.context.window.scene = scene
        visible = motion_layer.find(obj) or obj
        view_layer = next((layer for layer in scene.view_layers if visible.name in layer.objects), None)
        if view_layer is not None:
            bpy.context.window.view_layer = view_layer
            view_layer.objects.active = visible
            visible.select_set(True)
        binding = body_solver.mapping(obj, writable=False)
        if len(binding["names"]) != 17:
            raise ValueError("Review adapter must expose exactly 17 semantic joints")
        corrected = obj.b4ml.candidate_action
        before = obj.b4ml.contact_input
        if before is None or obj.b4ml.contact_output != corrected:
            raise ValueError("Saved scene does not retain the pre-contact comparison action")
        actions = {"pre_contact": before, "corrected": corrected}
        slot = workflow._slot(obj.animation_data)
        frames = [1.0 + index * 0.5 for index in range(49)]
        axes = [Vector(row) for row in report["task_basis_world"]]
        if any(abs(axis.length - 1.0) > 1e-5 for axis in axes):
            raise ValueError("Task display basis is not orthonormal")
        height = float(report["reference_height"])
        if not math.isfinite(height) or height <= 0:
            raise ValueError("Invalid reference height")

        def world_points(action, frame):
            workflow.assign_action(obj, action, slot)
            scene.frame_set(math.floor(frame), subframe=frame - math.floor(frame))
            posing._update(obj)
            evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
            return [evaluated.matrix_world @ evaluated.pose.bones[name].head for name in binding["names"]]

        origin = world_points(corrected, 1.0)[0]

        def display(action):
            rows = []
            for frame in frames:
                points = world_points(action, frame)
                rows.append([[float((point - origin).dot(axis) / height) for axis in axes] for point in points])
            values = np.asarray(rows, dtype=np.float64)
            if values.shape != (49, 17, 3) or not np.isfinite(values).all():
                raise ValueError("Nonfinite or malformed review skeleton")
            return np.round(values, 7).tolist()

        methods = {name: display(action) for name, action in actions.items()}
        priority_indices = [int(round((float(frame) - 1.0) * 2.0)) for frame in report["priority_frames"]]
        priority_error = float(np.max(np.abs(
            np.asarray(methods["pre_contact"])[priority_indices] -
            np.asarray(methods["corrected"])[priority_indices]
        )))
        if priority_error > 1e-5:
            raise ValueError(f"Review variants changed a priority pose: {priority_error}")
        points = np.concatenate([np.asarray(value).reshape(-1, 3) for value in methods.values()])
        low, high = points.min(axis=0), points.max(axis=0)
        center = (low + high) * 0.5
        radius = float(np.max(np.linalg.norm(points - center, axis=1)))
        floor_point = Vector((0.0, 0.0, float(report["rig_floor_calibration"]["floor_z"])))
        floor_z = float((floor_point - origin).dot(axes[2]) / height)
        workflow.assign_action(obj, corrected, slot)
        scene.frame_set(13)
        posing._update(obj)
        result.update(
            complete=True,
            blend_path=report["blend_path"],
            blend_sha256=report["blend_sha256"],
            report_sha256=sha(report_path),
            semantic_profile=binding["profile"],
            semantic_bones=list(binding["names"]),
            frames=frames,
            fps=float(scene.render.fps / scene.render.fps_base),
            priority_frames=[float(value) for value in report["priority_frames"]],
            priority_variant_error=priority_error,
            methods=methods,
            provenance={name: dict(action=action.name, backend=action.get("b4ml_backend", "unknown"))
                        for name, action in actions.items()},
            center=np.round(center, 7).tolist(),
            radius=radius,
            floor_z=floor_z,
            seconds=time.perf_counter() - started,
        )
    except BaseException:
        result.update(error=traceback.format_exc(), seconds=time.perf_counter() - started)
    write(destination, result)
    print("B4ML_REVIEW_EXTRACT=" + json.dumps({key: result.get(key) for key in
          ("profile", "task", "complete", "error", "seconds")}, allow_nan=False), flush=True)


def _metrics(report):
    metrics = report["automated_metrics"]
    contact = metrics.get("contact_report") or {}
    flight = metrics.get("flight_report") or {}
    return dict(
        priority_matrix_error=metrics["priority_matrix_error"],
        max_pin_residual=metrics["max_pin_residual"],
        max_sampled_limb_stretch=metrics["max_sampled_limb_stretch"],
        max_penetration_body_fraction=metrics["max_penetration_body_fraction"],
        max_rotation_velocity_jump_rad_s=metrics["max_rotation_velocity_jump_rad_s"],
        contact_error_limb_fraction=contact.get("max_after"),
        contact_orientation_error_radians=contact.get("orientation_error_radians"),
        flight_error_body_fraction=flight.get("max_after"),
        scripted_interaction_count=report["interaction_count"],
        scripted_correction_count=report["scripted_correction_count"],
    )


def _qualified_exit(returncode, log_text, extracted):
    if returncode == 0:
        return True, "clean"
    known = {1, 11, -1073741819, 3221225477}
    if returncode in known and extracted.get("complete") and "ucrtbase.dll" in log_text:
        return True, "known post-result ucrtbase.dll host crash"
    return False, "unqualified host exit"


def build():
    if (OUT / "manifest.json").exists():
        raise RuntimeError("Completed review evidence already exists: " + str(OUT))
    aggregate = read(AGGREGATE)
    protocol = read(PROTOCOL_PATH)
    if not aggregate.get("complete") or aggregate.get("passed") != 32 or aggregate.get("failed") != 0:
        raise ValueError("The frozen v12 procedural slice is not complete")
    if sha(PROTOCOL_PATH) != aggregate["protocol_sha256"]:
        raise ValueError("The v12 protocol changed after aggregation")
    expected = [(profile, task) for profile in protocol["rigs"] for task in protocol["tasks"]]
    if len(expected) != 32:
        raise ValueError("Expected the frozen 4-rig by 8-task matrix")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "extracted").mkdir(exist_ok=True)
    (OUT / "logs").mkdir(exist_ok=True)
    process_path = OUT / "processes.json"
    processes = read(process_path) if process_path.exists() else []
    for profile, task in expected:
        _, blend, _ = _case_paths(profile, task)
        extract_path = OUT / "extracted" / f"{profile}-{task}.json"
        existing = read(extract_path) if extract_path.exists() else None
        if existing and existing.get("complete") and existing.get("blend_sha256") == sha(blend):
            print(json.dumps(dict(profile=profile, task=task, resumed=True, extract_sha256=sha(extract_path))), flush=True)
            continue
        previous_attempts = sum(row.get("profile") == profile and row.get("task") == task for row in processes)
        if extract_path.exists():
            preserved = OUT / "extracted" / f"{profile}-{task}.failed-attempt-{previous_attempts}.json"
            if not preserved.exists():
                shutil.copy2(extract_path, preserved)
        log_name = f"{profile}-{task}.log" if previous_attempts == 0 else f"{profile}-{task}.attempt-{previous_attempts + 1}.log"
        log = OUT / "logs" / log_name
        started = time.perf_counter()
        environment = dict(os.environ, OPENBLAS_NUM_THREADS="4", PYTHONDONTWRITEBYTECODE="1")
        with log.open("w", encoding="utf-8") as stream:
            process = subprocess.run(
                [str(HOST), "--background", "--factory-startup", "--disable-autoexec", str(blend),
                 "--python", str(HERE), "--", profile, task],
                stdout=stream, stderr=subprocess.STDOUT, timeout=180, env=environment,
            )
        extracted = read(extract_path) if extract_path.exists() else {"complete": False, "error": "missing extract"}
        log_text = log.read_text(encoding="utf-8", errors="replace")
        qualified, qualification = _qualified_exit(process.returncode, log_text, extracted)
        row = dict(profile=profile, task=task, returncode=process.returncode,
                   result_written=bool(extracted.get("complete")), qualified=qualified,
                   qualification=qualification, seconds=time.perf_counter() - started,
                   log_sha256=sha(log), extract_sha256=sha(extract_path) if extract_path.exists() else None)
        processes.append(row)
        write(process_path, processes)
        print(json.dumps(row, allow_nan=False), flush=True)
        if not qualified or not extracted.get("complete"):
            raise RuntimeError(f"Review extraction failed: {profile}/{task}")

    aggregate_hash = sha(AGGREGATE)
    ids = [f"{profile}/{task}" for profile, task in expected]
    ranked = sorted(ids, key=lambda case_id: hashlib.sha256((aggregate_hash + ":" + case_id).encode()).digest())
    corrected_as_a = set(ranked[:len(ranked) // 2])
    cases = []
    for profile, task in expected:
        case_id = f"{profile}/{task}"
        extract = read(OUT / "extracted" / f"{profile}-{task}.json")
        _, blend, report_path = _case_paths(profile, task)
        report = read(report_path)
        if sha(blend) != extract["blend_sha256"] or extract["blend_sha256"] != report["blend_sha256"]:
            raise ValueError("Review source identity mismatch: " + case_id)
        mapping = {"A": "corrected", "B": "pre_contact"} if case_id in corrected_as_a else {"A": "pre_contact", "B": "corrected"}
        methods = {label: extract["methods"][kind] for label, kind in mapping.items()}
        reveal = {label: dict(kind=kind, **extract["provenance"][kind]) for label, kind in mapping.items()}
        contacts = [dict(limb=row[0], start=float(row[1]), end=float(row[2]))
                    for row in protocol["tasks"][task]["contacts"]]
        cases.append(dict(
            id=case_id, profile=profile, task=task, semantic_profile=extract["semantic_profile"],
            frames=extract["frames"], fps=extract["fps"], priority_frames=extract["priority_frames"],
            contacts=contacts, methods=methods, reveal=reveal, center=extract["center"],
            radius=extract["radius"], floor_z=extract["floor_z"],
            source_blend=report["blend_path"], source_blend_sha256=report["blend_sha256"],
            source_report_sha256=sha(report_path), priority_variant_error=extract["priority_variant_error"],
            automated_metrics=_metrics(report),
        ))
    payload = dict(
        schema="b4ml-procedural-vertical-slice-review-data-v1",
        title="B4Artists Machine Learning procedural vertical slice review",
        aggregate_sha256=aggregate_hash,
        protocol_sha256=sha(PROTOCOL_PATH),
        names=list(NAMES), roles=list(ROLES), parents=list(PARENTS),
        frame_sampling="1 through 25 at 0.5-frame intervals",
        blind_assignment="balanced deterministic SHA-256 rank; identity hidden until each case is locked",
        cases=cases,
        human_review_status="unreviewed",
        full_goal_complete=False,
    )
    encoded = json.dumps(payload, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    data_hash = hashlib.sha256(encoded.encode("utf-8")).hexdigest()
    data_path = OUT / "review-data.json"
    data_path.write_text(encoded, encoding="utf-8")
    template = TEMPLATE.read_text(encoding="utf-8")
    if template.count("__REVIEW_DATA__") != 1 or template.count("__DATA_SHA256__") != 1:
        raise ValueError("Review template placeholders changed")
    page = template.replace("__REVIEW_DATA__", encoded.replace("<", "\\u003c"))
    page = page.replace("__DATA_SHA256__", data_hash)
    page_path = OUT / "reviewer.html"
    page_path.write_text(page, encoding="utf-8")
    manifest = dict(
        schema="b4ml-procedural-vertical-slice-reviewer-manifest-v1",
        complete=True,
        cases=len(cases),
        variants=2,
        balanced_blinding={"corrected_as_A": len(corrected_as_a), "corrected_as_B": len(ids) - len(corrected_as_a)},
        embedded_frames=sum(len(case["frames"]) for case in cases) * 2,
        aggregate_sha256=aggregate_hash,
        protocol_sha256=sha(PROTOCOL_PATH),
        data_sha256=data_hash,
        html_sha256=sha(page_path),
        builder_sha256=sha(HERE),
        template_sha256=sha(TEMPLATE),
        external_dependencies=False,
        reviewed_cases=0,
        human_assessment="awaiting independent animator",
        automated_metrics_hidden_until_case_lock=True,
        method_identity_hidden_until_case_lock=True,
        full_goal_complete=False,
    )
    write(OUT / "manifest.json", manifest)
    print(json.dumps(manifest, indent=2, allow_nan=False), flush=True)


if __name__ == "__main__":
    if "--" in sys.argv:
        index = sys.argv.index("--")
        host(sys.argv[index + 1], sys.argv[index + 2])
    else:
        build()
