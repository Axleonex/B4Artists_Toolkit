"""Build the frozen four-rig procedural task packet through product APIs."""
from pathlib import Path
import ctypes
import hashlib
import json
import math
import os
import subprocess
import sys
import time
import traceback


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve()
PROTOCOL_PATH = Path(__file__).with_name("procedural_vertical_slice_protocol_v13.json")
BASE = ROOT / "training/b4artists_ml/results" / os.environ.get("B4ML_VERTICAL_TAG", "procedural-vertical-slice-v13")
HOST = Path("X:/5.1.0/bforartists.exe")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def memory():
    if os.name != "nt":
        return {}
    class Counters(ctypes.Structure):
        _fields_ = [
            ("cb", ctypes.c_ulong), ("PageFaultCount", ctypes.c_ulong),
            ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t), ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t), ("PeakPagefileUsage", ctypes.c_size_t),
        ]
    counters = Counters()
    counters.cb = ctypes.sizeof(counters)
    kernel = ctypes.windll.kernel32
    psapi = ctypes.windll.psapi
    kernel.GetCurrentProcess.restype = ctypes.c_void_p
    psapi.GetProcessMemoryInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(Counters), ctypes.c_ulong]
    psapi.GetProcessMemoryInfo.restype = ctypes.c_int
    handle = kernel.GetCurrentProcess()
    ok = psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb)
    return dict(working_set_bytes=int(counters.WorkingSetSize), peak_working_set_bytes=int(counters.PeakWorkingSetSize)) if ok else {}


def host(profile, task_name):
    import bpy
    import numpy as np
    from mathutils import Matrix, Quaternion, Vector

    sys.path[:0] = [str(ROOT), str(ROOT / "tests"), str(ROOT / "training/b4artists_ml")]
    import b4artists_ml
    from b4artists_ml import body_solver, contacts, flight, learned, motion_layer, posing, rig_state, support, temporal_preview, workflow
    from b4artists_ml.math_core import two_bone_positions
    from test_b4artists_ml_posing import boneforge_rig, rigify_rig

    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    task = protocol["tasks"][task_name]
    gates = protocol["automated_gates"]
    out = BASE / profile / task_name
    out.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    report = dict(
        schema="procedural-vertical-slice-case-v13",
        profile=profile,
        task=task_name,
        complete=False,
        learned=False,
        visual_quality="unrated",
        animator_corrections="unrated",
        cascadeur_comparison="unverified",
        interactions=[],
        authoring=[],
        failures=[],
        stages={},
        protocol_sha256=sha(PROTOCOL_PATH),
        runtime_sha256={path.relative_to(ROOT).as_posix(): sha(path) for path in (ROOT / "b4artists_ml").glob("*.py")},
    )

    def interaction(kind, count=1, **details):
        report["interactions"].append(dict(kind=kind, count=count, **details))

    def stage(name, at, **details):
        report["stages"][name] = dict(seconds=time.perf_counter() - at, **details)
        write(out / "progress.json", report)

    try:
        b4artists_ml.register()
        temporal_preview.register()
        bpy.context.window.scene = bpy.data.scenes.new(f"B4ML {profile} {task_name}")
        scene = bpy.context.scene
        scene.frame_start = 1
        scene.frame_end = 25
        scene.render.fps = 30
        scene.use_gravity = True
        scene.gravity = (0, 0, -9.81)

        at = time.perf_counter()
        if profile == "boneforge":
            obj = boneforge_rig()
        elif profile == "rigify_basic":
            obj = rigify_rig()
        elif profile == "rigify_default":
            obj = rigify_rig(full=True)
        elif profile == "imported_unity":
            from test_b4artists_ml_imported_humanoids import authored
            obj, _, _ = authored("unity_humanoid", 1)
            scene = bpy.context.scene
            scene.frame_start = 1
            scene.frame_end = 25
            scene.render.fps = 30
            scene.use_gravity = True
            scene.gravity = (0, 0, -9.81)
        else:
            raise ValueError("Unknown profile: " + profile)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        posing._update(obj)
        stage("rig_build", at, bones=len(obj.data.bones), memory=memory())

        profile_map, root_name, limb_rows = posing.bindings(obj)
        root = obj.pose.bones[root_name]
        yaw_root = obj.pose.bones["root"] if "root" in obj.pose.bones and "root" in profile_map.controls else root
        root.rotation_mode = "QUATERNION"
        yaw_root.rotation_mode = "QUATERNION"
        if obj.animation_data:
            obj.animation_data.action = None
        scene.frame_set(1)
        root.location = (0, 0, 0)
        root.rotation_quaternion = Quaternion()
        yaw_root.rotation_quaternion = Quaternion()
        root.keyframe_insert("location", frame=1)
        yaw_root.keyframe_insert("rotation_quaternion", frame=1)
        root.keyframe_insert("location", frame=25)
        yaw_root.keyframe_insert("rotation_quaternion", frame=25)
        source = obj.animation_data.action
        source.name = f"{profile} {task_name} source"
        source.use_fake_user = True
        source_slot = workflow._slot(obj.animation_data)
        source_signature = contacts._action_signature(obj)
        source_modes = rig_state.mode_values(obj)
        scene.frame_set(1)
        posing._update(obj)
        source_pose = workflow.raw_pose(obj)
        binding = body_solver.mapping(obj, writable=False)
        head = obj.pose.bones[profile_map.roles["head"]].tail
        feet = sum((obj.pose.bones[profile_map.roles[f"foot.fk-{side}"]].head for side in ("L", "R")), Vector()) * 0.5
        height = (workflow.display_world(obj).to_3x3() @ (head - feet)).length
        if height <= 1e-6:
            raise ValueError("Degenerate character height")
        report["reference_height"] = height
        anatomical_basis = Matrix(learned.anatomical_basis(*[
            tuple(obj.pose.bones[next(row for row in limb_rows if row["id"] == limb_id)["joints"][0]].head)
            for limb_id in ("leg-L", "leg-R", "arm-L", "arm-R")
        ]).tolist())
        raw_basis_world = workflow.display_world(obj).to_3x3() @ anatomical_basis
        up_world = Vector((0, 0, 1))
        left_world = raw_basis_world.col[0] - up_world * raw_basis_world.col[0].dot(up_world)
        if left_world.length < 1e-7:
            raise ValueError("Anatomical left axis cannot define a grounded task frame")
        left_world.normalize()
        forward_world = up_world.cross(left_world).normalized()
        task_basis_world = Matrix.Identity(3)
        task_basis_world.col[0] = left_world
        task_basis_world.col[1] = forward_world
        task_basis_world.col[2] = up_world
        report["raw_anatomical_basis_world"] = [list(raw_basis_world.col[index]) for index in range(3)]
        report["task_basis_world"] = [list(task_basis_world.col[index]) for index in range(3)]
        initial_foot_points = {}
        for limb_id in ("leg-L", "leg-R"):
            limb = next(row for row in limb_rows if row["id"] == limb_id)
            initial_foot_points[limb_id] = workflow.display_world(obj) @ obj.pose.bones[limb["joints"][2]].head
        benchmark_floor_z = max(point.z for point in initial_foot_points.values())
        foot_floor_offsets = {limb_id: benchmark_floor_z - point.z for limb_id, point in initial_foot_points.items()}
        report["rig_floor_calibration"] = dict(initial_points={key: list(value) for key, value in initial_foot_points.items()}, floor_z=benchmark_floor_z, offsets_body_fraction={key: value / height for key, value in foot_floor_offsets.items()})

        at = time.perf_counter()
        obj.b4ml.anchors.clear()
        max_pin_residual = 0.0
        max_requested_pin_error = 0.0
        max_authoring_stretch = 0.0
        max_preflight_adjustment = 0.0
        preflight_corrections = 0
        floor_normalization_corrections = 0
        clamped = 0
        contact_points = {}
        contact_rows = [dict(index=index, limb=row[0], start=float(row[1]), end=float(row[2])) for index, row in enumerate(task["contacts"])]
        author_limb_map = {row["id"]: row for row in limb_rows}
        for pose_spec in task["poses"]:
            frame = float(pose_spec["frame"])
            scene.frame_set(int(frame), subframe=frame % 1)
            workflow.restore_pose(obj, source_pose)
            yaw = math.radians(float(pose_spec["yaw_degrees"]))
            if abs(yaw) > 1e-9:
                world = workflow.display_world(obj)
                yaw_axis = world.inverted().to_3x3() @ Vector((0, 0, 1))
                yaw_axis.normalize()
                yaw_matrix = Quaternion(yaw_axis, yaw).to_matrix().to_4x4() @ yaw_root.matrix
                yaw_matrix.translation = yaw_root.matrix.translation
                posing._write_rotation(obj, yaw_root.name, yaw_matrix)
                interaction("edit_root_yaw")
            posing._update(obj)
            pelvis = Vector(pose_spec["pelvis"])
            limb_targets = pose_spec["limbs"]
            active_contacts = [row for row in contact_rows if row["start"] <= frame <= row["end"]]
            if len({row["limb"] for row in active_contacts}) != len(active_contacts):
                raise ValueError(f"Protocol has overlapping contacts for one limb at frame {frame:g}")
            requested_limbs = set(limb_targets) | {row["limb"] for row in active_contacts}
            needs_solver = pelvis.length > 0 or bool(requested_limbs)
            target_records = []
            if needs_solver:
                posing.begin(obj, scene)
                interaction("begin_assisted_pose")
                world = workflow.display_world(obj)
                inverse = world.inverted()
                obj.b4ml.pose_offset = task_basis_world @ (pelvis * height)
                local_offset = inverse.to_3x3() @ Vector(obj.b4ml.pose_offset)
                if pelvis.length > 0:
                    interaction("edit_pelvis_offset", components=sum(abs(value) > 0 for value in pelvis))
                posing_payload = json.loads(obj.b4ml.posing_payload)
                pose_limb_map = {row["id"]: row for row in posing_payload["limbs"]}
                for item in obj.b4ml.pose_targets:
                    item.enabled = item.name in requested_limbs
                    if not item.enabled:
                        continue
                    contact = next((row for row in active_contacts if row["limb"] == item.name), None)
                    contact_key = str(contact["index"]) if contact else None
                    fixed_contact = contact_key in contact_points if contact_key is not None else False
                    if fixed_contact:
                        desired_world = Vector(contact_points[contact_key])
                        target_source = "fixed_contact"
                    else:
                        desired_world = item.target.location.copy()
                        if item.name in limb_targets:
                            delta = Vector(limb_targets[item.name]) * height
                            desired_world += task_basis_world @ delta
                            interaction("edit_limb_target", limb=item.name, components=sum(abs(value) > 0 for value in delta))
                        floor_adjustment = foot_floor_offsets.get(item.name, 0.0)
                        if abs(floor_adjustment) > height * 1e-7:
                            desired_world.z += floor_adjustment
                            floor_normalization_corrections += 1
                            interaction("normalize_foot_target_to_floor", limb=item.name)
                        target_source = "contact_start" if contact else "raw_offset"
                    row = pose_limb_map[item.name]
                    root_local = obj.pose.bones[row["joints"][0]].head + local_offset
                    raw_local = inverse @ desired_world
                    pole_local = inverse @ item.pole.location if item.pole else root_local + Vector((0, 0, 1))
                    _, fitted_local = two_bone_positions(tuple(root_local), tuple(raw_local), tuple(pole_local), *row["lengths"], obj.b4ml.max_bend)
                    fitted_local = Vector(fitted_local)
                    fitted_world = world @ fitted_local
                    adjustment = (fitted_world - desired_world).length / height
                    max_preflight_adjustment = max(max_preflight_adjustment, adjustment)
                    if fixed_contact and adjustment > 1e-5:
                        raise ValueError(f"Fixed contact is unreachable at priority frame {frame:g}: {item.name}; normalized adjustment {adjustment:.6g}")
                    if adjustment > 1e-7:
                        preflight_corrections += 1
                        interaction("preflight_target_adjustment", limb=item.name)
                    item.target.location = fitted_world
                    target_records.append(dict(limb=item.name, source=target_source, raw_world=list(desired_world), authored_world=list(fitted_world), adjustment_body_fraction=adjustment, floor_adjustment_body_fraction=foot_floor_offsets.get(item.name, 0.0) / height if not fixed_contact else 0.0))
                rows = posing.solve(obj, scene)
                interaction("solve_assisted_pose")
                max_pin_residual = max(max_pin_residual, max((row["residual"] for row in rows), default=0.0))
                max_requested_pin_error = max(max_requested_pin_error, max((row["normalized_error"] for row in rows), default=0.0))
                max_authoring_stretch = max(max_authoring_stretch, max((row["stretch"] for row in rows), default=0.0))
                clamped += sum(bool(row["clamped"]) for row in rows)
                for contact in active_contacts:
                    contact_key = str(contact["index"])
                    if abs(contact["start"] - frame) < 1e-6 and contact_key not in contact_points:
                        limb = author_limb_map[contact["limb"]]
                        point = world @ obj.pose.bones[limb["joints"][2]].head
                        contact_points[contact_key] = list(point)
                        interaction("establish_contact_target", limb=contact["limb"])
                report["authoring"].append(dict(frame=frame, label=pose_spec["label"], limbs=rows, pelvis=list(pelvis), yaw_degrees=pose_spec["yaw_degrees"], targets=target_records))
                posing.finish(obj, scene, True)
                interaction("keep_priority_pose")
            else:
                workflow.capture_anchor(obj, scene)
                interaction("capture_priority_pose")
                report["authoring"].append(dict(frame=frame, label=pose_spec["label"], limbs=[], pelvis=list(pelvis), yaw_degrees=pose_spec["yaw_degrees"], targets=[]))
        workflow.restore_pose(obj, source_pose)
        posing._update(obj)
        anchors_before = [(anchor.frame, anchor.payload) for anchor in obj.b4ml.anchors]
        report["priority_frames"] = [row[0] for row in anchors_before]
        report["preflight_corrections"] = preflight_corrections
        report["floor_normalization_corrections"] = floor_normalization_corrections
        stage("authoring", at, max_pin_residual=max_pin_residual, max_requested_pin_error_body_fraction=max_requested_pin_error, max_stretch=max_authoring_stretch, clamped=clamped, max_preflight_adjustment_body_fraction=max_preflight_adjustment, fixed_contact_targets=len(contact_points), floor_normalization_corrections=floor_normalization_corrections)

        def matrices(frame):
            scene.frame_set(math.floor(frame), subframe=frame - math.floor(frame))
            evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
            world = evaluated.matrix_world
            return np.asarray([np.asarray(world @ evaluated.pose.bones[name].matrix) for name in binding["names"]])

        at = time.perf_counter()
        obj.b4ml.interpolation_method = "AUTHORED"
        obj.b4ml.temporal_smoothing = True
        temporal_preview.start(obj, scene)
        generation_steps = 0
        generation_step_max = 0.0
        while obj.b4ml.temporal_running:
            tick = time.perf_counter()
            temporal_preview.step(obj)
            generation_step_max = max(generation_step_max, time.perf_counter() - tick)
            generation_steps += 1
            if generation_steps > 10000:
                raise RuntimeError("Temporal preview did not finish")
        interaction("generate_procedural_candidate")
        candidate = obj.b4ml.candidate_action
        candidate.name = f"{profile} {task_name} procedural"
        candidate.use_fake_user = True
        priorities = {frame: matrices(frame) for frame, _ in workflow.read_anchors(obj)}
        stage("generation", at, steps=generation_steps, max_step_seconds=generation_step_max, backend=candidate.get("b4ml_backend", "unknown"))

        limb_map = {row["id"]: row for row in posing.bindings(obj)[2]}
        floor_points = [Vector(contact_points[str(row["index"])]) for row in contact_rows if row["limb"] in ("leg-L", "leg-R")]
        if not floor_points:
            raise ValueError("Protocol must establish at least one foot contact before defining the floor")
        floor_height = sum(point.z for point in floor_points) / len(floor_points)
        contact_plane_spread = max(abs(point.z - floor_height) for point in floor_points) / height
        obj.b4ml.support_plane_point = sum(floor_points, Vector()) / len(floor_points)
        obj.b4ml.support_plane_normal = (0, 0, 1)
        obj.b4ml.contact_suggest_distance = 0.12
        obj.b4ml.contact_suggest_speed = 0.08
        obj.b4ml.contact_suggest_min_frames = 2
        obj.b4ml.contact_suggest_gap_frames = 1

        at = time.perf_counter()
        suggestion_report = contacts.suggest(obj, scene)
        interaction("suggest_foot_contacts")
        proposed = [item for item in obj.b4ml.contacts if item.review_state == "PROPOSED"]
        for item in proposed:
            item.review_state = "REJECTED"
            item.enabled = False
            interaction("reject_contact_suggestion", limb=item.limb)
        manual_contacts = []
        for limb, start, end in task["contacts"]:
            scene.frame_set(int(start), subframe=float(start) % 1)
            obj.b4ml.contact_limb = limb
            item = contacts.capture(obj, scene)
            item.start = float(start)
            item.end = float(end)
            item.blend = 0.0
            item.lock_rotation = False
            manual_contacts.append(item.name)
            interaction("capture_manual_contact", limb=limb)
            interaction("edit_contact_interval", count=2, limb=limb)
        stage("contact_review", at, suggestions=suggestion_report, proposed=len(proposed), rejected=len(proposed), manual_contacts=len(manual_contacts))

        flight_report = None
        flight_error = None
        if task["flights"]:
            at = time.perf_counter()
            support.initialize(obj)
            interaction("initialize_mass_model")
            obj.b4ml.flights.clear()
            for start, end in task["flights"]:
                scene.frame_set(int(start), subframe=float(start) % 1)
                item = flight.add(obj, scene)
                item.start = float(start)
                item.end = float(end)
                interaction("add_flight_interval")
                interaction("edit_flight_interval", count=2)
            obj.b4ml.flight_backend = "NATIVE"
            try:
                flight_report = flight.solve(obj, scene)
                interaction("solve_native_flight")
            except Exception as exc:
                flight_error = str(exc)
                report["failures"].append(dict(stage="flight", error=flight_error))
            stage("flight_refinement", at, passed=flight_error is None, report=flight_report, error=flight_error)

        at = time.perf_counter()
        contact_report = None
        contact_error = None
        try:
            contact_report = contacts.solve(obj, scene)
            interaction("solve_contact_correction")
        except Exception as exc:
            contact_error = str(exc)
            report["failures"].append(dict(stage="contacts", error=contact_error))
        stage("contact_refinement", at, passed=contact_error is None, report=contact_report, error=contact_error)

        at = time.perf_counter()
        priority_error = max(float(np.max(np.abs(matrices(frame) - expected))) for frame, expected in priorities.items())
        max_stretch = 0.0
        worst_stretch = None
        max_penetration = 0.0
        worst_penetration = None
        rotation_jumps = []
        rest_lengths = {
            row["id"]: [obj.data.bones[row["joints"][index]].length for index in (0, 1)]
            for row in limb_map.values()
        }
        for frame in np.linspace(1.0, 25.0, 97):
            scene.frame_set(math.floor(frame), subframe=frame - math.floor(frame))
            posing._update(obj)
            for row in limb_map.values():
                lengths = [
                    (obj.pose.bones[row["joints"][index]].tail - obj.pose.bones[row["joints"][index]].head).length
                    for index in (0, 1)
                ]
                for segment, (value, base) in enumerate(zip(lengths, rest_lengths[row["id"]])):
                    stretch = abs(value / base - 1.0)
                    if stretch > max_stretch:
                        max_stretch = stretch
                        worst_stretch = dict(frame=float(frame), limb=row["id"], segment=segment, length=float(value), baseline=float(base))
            for limb in ("leg-L", "leg-R"):
                row = limb_map[limb]
                point = workflow.display_world(obj) @ obj.pose.bones[row["joints"][2]].head
                penetration = max(0.0, -((point - Vector(obj.b4ml.support_plane_point)).dot(Vector(obj.b4ml.support_plane_normal))) / height)
                if penetration > max_penetration:
                    max_penetration = penetration
                    worst_penetration = dict(frame=float(frame), limb=limb, point=list(point))
        for frame in report["priority_frames"][1:-1]:
            epsilon = 0.0625
            before = matrices(frame - epsilon)
            center = matrices(frame)
            after = matrices(frame + epsilon)
            before_q = [Matrix(matrix[:3, :3].tolist()).to_quaternion() for matrix in before]
            center_q = [Matrix(matrix[:3, :3].tolist()).to_quaternion() for matrix in center]
            after_q = [Matrix(matrix[:3, :3].tolist()).to_quaternion() for matrix in after]
            def omega(a, b):
                values = []
                for first, second in zip(a, b):
                    delta = (second @ first.conjugated()).normalized()
                    if delta.w < 0:
                        delta.negate()
                    vector = Vector((delta.x, delta.y, delta.z))
                    magnitude = vector.length
                    values.append(vector * (2 * math.atan2(magnitude, delta.w) / max(magnitude, 1e-15) / (epsilon / 30.0)))
                return values
            left = omega(before_q, center_q)
            right = omega(center_q, after_q)
            jumps = [(a - b).length for a, b in zip(right, left)]
            rotation_jumps.append(dict(frame=frame, maximum_rad_s=max(jumps), joint=binding["names"][jumps.index(max(jumps))]))
        assessment_memory = memory()
        automated = dict(
            priority_matrix_error=priority_error,
            max_pin_residual=max_pin_residual,
            max_requested_pin_error_body_fraction=max_requested_pin_error,
            max_authoring_stretch=max_authoring_stretch,
            max_preflight_target_adjustment_body_fraction=max_preflight_adjustment,
            preflight_target_corrections=preflight_corrections,
            floor_normalization_corrections=floor_normalization_corrections,
            max_floor_normalization_body_fraction=max(foot_floor_offsets.values()) / height,
            max_sampled_limb_stretch=max_stretch,
            worst_sampled_limb_stretch=worst_stretch,
            sampled_stretch_measurement="evaluated skeletal pose-bone head-tail length / armature rest-bone length",
            contact_plane_spread_body_fraction=contact_plane_spread,
            max_penetration_body_fraction=max_penetration,
            worst_penetration=worst_penetration,
            max_rotation_velocity_jump_rad_s=max((row["maximum_rad_s"] for row in rotation_jumps), default=0.0),
            rotation_jumps=rotation_jumps,
            contact_report=contact_report,
            flight_report=flight_report,
            memory=assessment_memory,
        )
        automated_gates = dict(
            priority=priority_error <= gates["priority_matrix_error"],
            pins=max_pin_residual <= gates["pin_residual"] and max_requested_pin_error <= gates["requested_pin_error_body_fraction"] and clamped == 0,
            authoring_stretch=max_authoring_stretch <= gates["limb_stretch_fraction"],
            target_preflight=max_preflight_adjustment <= gates["preflight_target_adjustment_body_fraction"],
            sampled_stretch=max_stretch <= gates["limb_stretch_fraction"],
            contacts=bool(contact_report and contact_report["max_after"] <= gates["contact_position_error_limb_fraction"] and contact_report["orientation_error_radians"] <= gates["contact_rotation_error_radians"]),
            contact_plane=contact_plane_spread <= gates["contact_plane_spread_body_fraction"],
            penetration=max_penetration <= gates["penetration_body_fraction"],
            flight=not task["flights"] or flight_error is None,
            finite_rotation_velocity=math.isfinite(automated["max_rotation_velocity_jump_rad_s"]),
            memory_counters=bool(assessment_memory.get("working_set_bytes", 0) > 0 and assessment_memory.get("peak_working_set_bytes", 0) >= assessment_memory.get("working_set_bytes", 0)),
        )
        stage("automated_assessment", at, metrics=automated, gates=automated_gates)

        at = time.perf_counter()
        candidate_name = obj.b4ml.candidate_action.name
        source_name = source.name
        obj_name = obj.name
        scene.frame_set(13)
        saved = out / f"{profile}-{task_name}.blend"
        bpy.ops.wm.save_as_mainfile(filepath=str(saved))
        interaction("save_candidate")
        bpy.ops.wm.open_mainfile(filepath=str(saved), use_scripts=False)
        interaction("reload_candidate")
        obj = bpy.data.objects[obj_name]
        scene = next(scene for scene in bpy.data.scenes if obj.name in scene.objects)
        visible = motion_layer.find(obj) or obj
        view_layer = next(layer for layer in scene.view_layers if visible.name in layer.objects)
        bpy.context.window.scene = scene
        bpy.context.window.view_layer = view_layer
        view_layer.objects.active = visible
        visible.select_set(True)
        save_reload = bool(obj.b4ml.candidate_action and obj.b4ml.candidate_action.name == candidate_name and len(obj.b4ml.anchors) == len(task["poses"]))
        workflow.finish_preview(obj, scene, True)
        interaction("keep_candidate")
        workflow.restore_kept_source(obj, scene)
        interaction("restore_source")
        restored = obj.animation_data.action and obj.animation_data.action.name == source_name and contacts._action_signature(obj) == source_signature and rig_state.mode_values(obj) == source_modes
        stage("lifecycle", at, save_reload=save_reload, source_restored=restored, blend_path=saved.relative_to(ROOT).as_posix(), blend_sha256=sha(saved))

        report["interaction_count"] = sum(row["count"] for row in report["interactions"])
        report["scripted_correction_count"] = len(manual_contacts) + sum(row["count"] for row in report["interactions"] if row["kind"] == "edit_contact_interval") + preflight_corrections + floor_normalization_corrections + len(report["failures"])
        report["automated_metrics"] = automated
        report["automated_gates"] = dict(automated_gates, save_reload=save_reload, source_restored=restored)
        report["complete"] = all(report["automated_gates"].values())
        report["source_restored"] = restored
        report["save_reload_passed"] = save_reload
        report["anchor_payloads_unchanged"] = [(anchor.frame, anchor.payload) for anchor in obj.b4ml.anchors] == anchors_before
        report["blend_path"] = saved.relative_to(ROOT).as_posix()
        report["blend_sha256"] = sha(saved)
        report["memory"] = memory()
    except BaseException:
        report["error"] = traceback.format_exc()
        report["failures"].append(dict(stage="unhandled", error=next(line for line in reversed(report["error"].splitlines()) if line.strip())))
    report["seconds"] = time.perf_counter() - started
    write(out / "report.json", report)
    print(json.dumps({key: report.get(key) for key in ("profile", "task", "complete", "interaction_count", "scripted_correction_count", "failures", "error", "seconds")}, allow_nan=False), flush=True)


def main():
    protocol = json.loads(PROTOCOL_PATH.read_text(encoding="utf-8"))
    if BASE.exists():
        raise RuntimeError("Evidence exists: " + str(BASE))
    BASE.mkdir(parents=True)
    requested_profile = os.environ.get("B4ML_VERTICAL_PROFILE")
    requested_task = os.environ.get("B4ML_VERTICAL_TASK")
    profiles = [requested_profile] if requested_profile else protocol["rigs"]
    tasks = [requested_task] if requested_task else list(protocol["tasks"])
    processes = []
    for profile in profiles:
        for task in tasks:
            log = BASE / profile / (task + ".log")
            log.parent.mkdir(parents=True, exist_ok=True)
            at = time.perf_counter()
            with log.open("w") as stream:
                result = subprocess.run(
                    [str(HOST), "--background", "--factory-startup", "--disable-autoexec", "--python", str(HERE), "--", profile, task],
                    cwd=ROOT,
                    stdout=stream,
                    stderr=subprocess.STDOUT,
                    timeout=900,
                    env=dict(os.environ, OPENBLAS_NUM_THREADS="4", PYTHONDONTWRITEBYTECODE="1"),
                )
            report_path = BASE / profile / task / "report.json"
            report = json.loads(report_path.read_text()) if report_path.exists() else dict(complete=False, error="Missing report")
            row = dict(profile=profile, task=task, complete=report.get("complete", False), host_exit=result.returncode, seconds=time.perf_counter() - at, log=log.relative_to(ROOT).as_posix(), log_sha256=sha(log), error=report.get("error"), failures=report.get("failures", []))
            processes.append(row)
            write(BASE / "processes.json", processes)
            print(json.dumps(row), flush=True)
    summary = dict(
        schema="procedural-vertical-slice-summary-v13",
        complete=all(row["complete"] for row in processes),
        cases=len(processes),
        passed=sum(row["complete"] for row in processes),
        failed=sum(not row["complete"] for row in processes),
        profiles=profiles,
        tasks=tasks,
        protocol=PROTOCOL_PATH.relative_to(ROOT).as_posix(),
        protocol_sha256=sha(PROTOCOL_PATH),
        visual_quality="unrated",
        independent_animator_assessment="missing",
        cascadeur_comparison="unverified",
        learned_motion_promoted=False,
        full_goal_complete=False,
    )
    write(BASE / "summary.json", summary)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    if "--" in sys.argv:
        args = sys.argv[sys.argv.index("--") + 1:]
        host(args[0], args[1])
    else:
        main()

