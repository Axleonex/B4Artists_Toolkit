"""Build and independently validate a review scene for exposed CMU jump clip 141_04."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve()
TRAINING = HERE.parent
RESULTS = TRAINING / "results" / "recorded-jump-reference-v1"
ANALYSIS = RESULTS / "analysis.json"
SOURCE = TRAINING / "cache" / "141_04.bvh"
BLEND = RESULTS / "recorded-jump-reference-v1.blend"
HOST_REPORT = RESULTS / "scene-host-report.json"
WRAPPER_REPORT = RESULTS / "scene-wrapper-report.json"
HOST_LOG = RESULTS / "scene-host.log"
BFA = Path("X:/5.1.0/bforartists.exe")
JOINTS = (
    "Hips", "Spine", "Spine1", "Neck1", "Head",
    "LeftArm", "LeftForeArm", "LeftHand",
    "RightArm", "RightForeArm", "RightHand",
    "LeftUpLeg", "LeftLeg", "LeftFoot", "LeftToeBase",
    "RightUpLeg", "RightLeg", "RightFoot", "RightToeBase",
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def kabsch(expected, actual):
    expected_center = expected.mean(axis=0)
    actual_center = actual.mean(axis=0)
    covariance = (expected - expected_center).T @ (actual - actual_center)
    u, _, vt = np.linalg.svd(covariance)
    rotation = vt.T @ u.T
    if np.linalg.det(rotation) < 0:
        vt[-1] *= -1
        rotation = vt.T @ u.T
    translation = actual_center - expected_center @ rotation.T
    return rotation, translation


def pairwise_distances(points):
    delta = points[:, None, :] - points[None, :, :]
    return np.linalg.norm(delta, axis=2)


def host_main():
    import bpy

    started = time.perf_counter()
    analysis = json.loads(ANALYSIS.read_text(encoding="utf-8"))
    assert analysis["complete"] and not analysis["qualified"]
    assert analysis["source_sha256"] == sha256(SOURCE)
    assert analysis["confirmation_read"] is False
    leg_length = float(analysis["leg_length_source_units"])

    properties = set(bpy.ops.import_anim.bvh.get_rna_type().properties.keys())
    requested = {
        "filepath": str(SOURCE),
        "target": "ARMATURE",
        "global_scale": 1.0 / leg_length,
        "frame_start": 1,
        "use_fps_scale": False,
        "update_scene_fps": True,
        "update_scene_duration": True,
        "rotate_mode": "QUATERNION",
        "axis_forward": "-Z",
        "axis_up": "Y",
    }
    arguments = {key: value for key, value in requested.items() if key in properties}
    required = {"filepath", "target", "global_scale", "frame_start"}
    assert required <= set(arguments), sorted(properties)
    result = bpy.ops.import_anim.bvh(**arguments)
    assert "FINISHED" in result
    armatures = [obj for obj in bpy.context.scene.objects if obj.type == "ARMATURE"]
    assert len(armatures) == 1
    armature = armatures[0]
    armature.name = "CMU_141_04_Jump_Distances"
    armature.data.name = "CMU_141_04_Skeleton"
    armature.show_in_front = True
    armature.data.display_type = "STICK"
    armature.data.show_names = True
    action = armature.animation_data.action
    assert action is not None
    if hasattr(action, "fcurves"):
        curves = list(action.fcurves)
        action_api = "legacy_fcurves"
    else:
        slot = armature.animation_data.action_slot
        assert slot is not None
        curves = []
        for layer in action.layers:
            for strip in layer.strips:
                bag = strip.channelbag(slot)
                if bag is not None:
                    curves.extend(bag.fcurves)
        action_api = "layered_channelbag"
    assert curves
    keyframes = sorted({round(point.co.x, 6) for curve in curves for point in curve.keyframe_points})
    assert keyframes[0] == 1.0 and keyframes[-1] == float(analysis["frames"])

    scene = bpy.context.scene
    scene.name = "Recorded Jump Reference"
    scene.frame_start = 1
    scene.frame_end = analysis["frames"]
    scene.render.fps = 120
    scene.render.fps_base = 1.0
    scene["b4ml_reference_only"] = True
    scene["b4ml_qualified"] = False
    scene["source_clip"] = "CMU 141_04 Jump Distances"
    scene["source_sha256"] = analysis["source_sha256"]
    scene["normalization"] = "Mean hip-knee-ankle chain length = 1 Blender unit"

    sys.path.insert(0, str(TRAINING))
    from bvh_data import parse_bvh
    motion = parse_bvh(SOURCE.read_text(encoding="utf-8"))
    source_positions, _ = motion.transforms()
    source_index = {name: index for index, name in enumerate(motion.names)}
    assert set(JOINTS) <= set(source_index)
    assert set(JOINTS) <= set(armature.pose.bones.keys())

    def imported_positions(review_frame):
        scene.frame_set(review_frame)
        bpy.context.view_layer.update()
        return np.asarray([
            tuple(armature.matrix_world @ armature.pose.bones[name].head)
            for name in JOINTS
        ])

    expected_zero = source_positions[0, [source_index[name] for name in JOINTS]] / leg_length
    actual_zero = imported_positions(1)
    rotation, translation = kabsch(expected_zero, actual_zero)
    phase_frames = sorted({1, analysis["frames"]} | {row["review_frame"] for row in analysis["phases"]})
    residuals = []
    distance_errors = []
    frame_rows = []
    for review_frame in phase_frames:
        source_frame = review_frame - 1
        expected = source_positions[source_frame, [source_index[name] for name in JOINTS]] / leg_length
        actual = imported_positions(review_frame)
        transformed = expected @ rotation.T + translation
        residual = np.linalg.norm(actual - transformed, axis=1)
        distance_error = np.abs(pairwise_distances(actual) - pairwise_distances(expected))
        residuals.extend(residual.tolist())
        distance_errors.extend(distance_error.ravel().tolist())
        frame_rows.append({
            "review_frame": review_frame,
            "max_rigid_mapping_error": float(residual.max()),
            "max_pairwise_distance_error": float(distance_error.max()),
        })
    max_residual = max(residuals)
    max_distance_error = max(distance_errors)
    assert max_residual < 5e-4, max_residual
    assert max_distance_error < 5e-4, max_distance_error

    marker_rows = []
    for row in analysis["phases"]:
        label = row["phase"].replace("_", " ").title()
        name = f"J{row['jump']} {label}"
        marker = scene.timeline_markers.new(name, frame=row["review_frame"])
        marker_rows.append({"name": marker.name, "frame": marker.frame})
    assert len(marker_rows) == 15 and len(scene.timeline_markers) == 15

    all_site_positions = []
    for source_frame in range(analysis["frames"]):
        expected = source_positions[source_frame, [source_index[name] for name in analysis["site_names"]]] / leg_length
        all_site_positions.append(expected @ rotation.T + translation)
    all_site_positions = np.concatenate(all_site_positions, axis=0)
    floor_z = float(np.percentile(all_site_positions[:, 2], 2))
    low = all_site_positions.min(axis=0)
    high = all_site_positions.max(axis=0)
    center_x = float((low[0] + high[0]) * 0.5)
    center_y = float((low[1] + high[1]) * 0.5)
    size = float(max(high[0] - low[0], high[1] - low[1], 2.0) + 2.0)
    bpy.ops.mesh.primitive_plane_add(size=size, location=(center_x, center_y, floor_z))
    floor = bpy.context.object
    floor.name = "Kinematic_Floor_Guide"
    floor.display_type = "WIRE"
    floor.show_in_front = False
    floor["meaning"] = "2nd-percentile ankle/toe height; visual guide, not measured force contact"

    notes = bpy.data.texts.new("READ_ME_Recorded_Jump_Reference")
    notes.write(
        "B4Artists Machine Learning - recorded jump reference v1\n\n"
        "Source: CMU 141_04, Jump Distances (exposed validation clip)\n"
        f"SHA-256: {analysis['source_sha256']}\n"
        "Normalization: mean hip-knee-ankle chain length = 1 Blender unit.\n"
        "Markers: preparation, clear takeoff, apex, clear landing, and landing for three jumps.\n"
        "The floor and phase markers are kinematic estimates. They are not force-plate contact events.\n"
        "This is a research reference scene. It does not qualify interpolation, retargeting, physics, or learned prediction.\n"
        "The sealed confirmation set was not read.\n"
    )
    armature["reference_notes"] = notes.name
    scene.frame_set(analysis["jumps"][1]["apex"] + 1)
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    floor.select_set(False)

    report = {
        "schema": 1,
        "complete": True,
        "qualified": False,
        "host": "Bforartists",
        "host_version": bpy.app.version_string,
        "host_binary": bpy.app.binary_path,
        "source_sha256": analysis["source_sha256"],
        "analysis_sha256": sha256(ANALYSIS),
        "builder_sha256": sha256(HERE),
        "import_arguments": arguments,
        "armature": armature.name,
        "action": action.name,
        "action_api": action_api,
        "fcurves": len(curves),
        "unique_keyframes": len(keyframes),
        "action_frame_range": [keyframes[0], keyframes[-1]],
        "scene_fps": scene.render.fps / scene.render.fps_base,
        "scene_frame_range": [scene.frame_start, scene.frame_end],
        "timeline_markers": marker_rows,
        "validation_frames": frame_rows,
        "max_rigid_mapping_error": max_residual,
        "max_pairwise_distance_error": max_distance_error,
        "rigid_mapping_rotation": rotation.tolist(),
        "rigid_mapping_translation": translation.tolist(),
        "floor_guide_z": floor_z,
        "confirmation_read": False,
        "runtime_seconds": time.perf_counter() - started,
    }
    write_json(HOST_REPORT, report)
    bpy.ops.wm.save_as_mainfile(filepath=str(BLEND), check_existing=False)
    assert BLEND.exists() and BLEND.stat().st_size < 64_000_000
    report["blend_bytes"] = BLEND.stat().st_size
    report["blend_sha256"] = sha256(BLEND)
    report["saved"] = True
    write_json(HOST_REPORT, report)
    print("RECORDED_JUMP_SCENE_COMPLETE " + json.dumps({
        "blend": str(BLEND),
        "max_rigid_mapping_error": max_residual,
        "max_pairwise_distance_error": max_distance_error,
        "markers": len(marker_rows),
    }))


def wrapper_main():
    assert BFA.exists() and ANALYSIS.exists() and SOURCE.exists()
    before = {path.name: sha256(path) for path in ROOT.joinpath("b4artists_ml").glob("*.py")}
    command = [str(BFA), "--background", "--factory-startup", "--disable-autoexec",
               "--python", str(HERE), "--", "--host"]
    started = time.perf_counter()
    with HOST_LOG.open("w", encoding="utf-8") as stream:
        process = subprocess.run(
            command,
            cwd=ROOT,
            stdout=stream,
            stderr=subprocess.STDOUT,
            timeout=1000,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1", OPENBLAS_NUM_THREADS="4"),
        )
    after = {path.name: sha256(path) for path in ROOT.joinpath("b4artists_ml").glob("*.py")}
    report = json.loads(HOST_REPORT.read_text(encoding="utf-8")) if HOST_REPORT.exists() else None
    complete = bool(report and report.get("complete") and report.get("saved") and BLEND.exists())
    wrapper = {
        "schema": 1,
        "complete": complete,
        "host_returncode": process.returncode,
        "known_shutdown_crash_tolerated": bool(complete and process.returncode == 3221225477),
        "host_report_sha256": sha256(HOST_REPORT) if HOST_REPORT.exists() else None,
        "host_log_sha256": sha256(HOST_LOG),
        "prior_corrective_attempt_error_sha256": sha256(RESULTS / "scene-host-error.json") if (RESULTS / "scene-host-error.json").exists() else None,
        "production_sources_unchanged": before == after,
        "confirmation_read": False,
        "runtime_seconds": time.perf_counter() - started,
    }
    write_json(WRAPPER_REPORT, wrapper)
    assert complete, HOST_LOG.read_text(encoding="utf-8", errors="replace")[-5000:]
    assert before == after
    assert process.returncode in (0, 3221225477), process.returncode
    print(json.dumps(wrapper, indent=2))


if __name__ == "__main__":
    if "--host" in sys.argv:
        try:
            host_main()
        except Exception:
            write_json(RESULTS / "scene-host-error.json", {
                "complete": False,
                "error": traceback.format_exc(),
                "confirmation_read": False,
            })
            raise
    else:
        wrapper_main()
