"""Fresh-host validation for the frozen portable comparison characters."""
from pathlib import Path
import hashlib
import json
import math
import os

import addon_utils
import bpy


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
BASE = HERE.parent / "reference-assets-v1"
MANIFEST_PATH = BASE / "manifest.json"
REPORT_PATH = ROOT / "training/b4artists_ml/results/portable-comparison-characters-v1-host.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_sha(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def close(a, b, tolerance=2e-5):
    return math.isclose(float(a), float(b), rel_tol=tolerance, abs_tol=tolerance)


def quantized_vector(vector):
    return tuple(int(round(float(value) * 100000.0)) for value in vector)


def inspect_scene(expected, kind):
    sys_path = str(ROOT)
    if sys_path not in __import__("sys").path:
        __import__("sys").path.insert(0, sys_path)
    from b4artists_ml import rigs

    objects = list(bpy.context.scene.objects)
    armatures = [obj for obj in objects if obj.type == "ARMATURE"]
    meshes = [obj for obj in objects if obj.type == "MESH"]
    if len(objects) != 2 or len(armatures) != 1 or len(meshes) != 1:
        raise ValueError(f"{kind} {expected['id']} must contain exactly one armature and one mesh")
    armature, mesh = armatures[0], meshes[0]
    modifiers = [modifier for modifier in mesh.modifiers if modifier.type == "ARMATURE"]
    modifier_bound = len(modifiers) == 1 and modifiers[0].object == armature
    parent_bound = mesh.parent == armature
    if mesh.find_armature() != armature or not modifier_bound or not parent_bound:
        raise ValueError(f"{kind} {expected['id']} lost its bound mesh")
    names = [bone.name for bone in armature.data.bones]
    if set(names) != set(expected["bones"]) or len(names) != len(expected["bones"]):
        raise ValueError(f"{kind} {expected['id']} skeleton changed")
    for name, parent in expected["bone_parents"].items():
        actual = armature.data.bones[name].parent
        if (actual.name if actual else None) != parent:
            raise ValueError(f"{kind} {expected['id']} parent changed for {name}")
    profile = rigs.detect_rig(names)
    if profile.name != "Unity Humanoid" or profile.missing or profile.family != "humanoid":
        raise ValueError(f"{kind} {expected['id']} is not a complete Unity humanoid")
    if len(mesh.data.vertices) != expected["vertices"] or len(mesh.data.polygons) != expected["faces"]:
        raise ValueError(f"{kind} {expected['id']} mesh topology changed")
    group_names = {group.index: group.name for group in mesh.vertex_groups}
    weighted = 0
    vertex_rows = []
    for vertex in mesh.data.vertices:
        weights = sorted((group_names[item.group], int(round(float(item.weight) * 1000000.0)))
                         for item in vertex.groups)
        if not weights or sum(value for _name, value in weights) != 1000000:
            raise ValueError(f"{kind} {expected['id']} has an unweighted or non-normalized vertex")
        if any(name not in expected["deform_bones"] for name, _value in weights):
            raise ValueError(f"{kind} {expected['id']} has an unexpected vertex group")
        vertex_rows.append((quantized_vector(vertex.co), tuple(weights)))
        weighted += 1
    if weighted != expected["weighted_vertices"]:
        raise ValueError(f"{kind} {expected['id']} weighted-vertex count changed")
    if bpy.data.actions or bpy.data.images or bpy.data.libraries:
        raise ValueError(f"{kind} {expected['id']} contains animation or external data")
    vertex_rows.sort()
    positions = sorted(quantized_vector(vertex.co) for vertex in mesh.data.vertices)
    faces = sorted(tuple(sorted(quantized_vector(mesh.data.vertices[index].co)
                                for index in polygon.vertices))
                   for polygon in mesh.data.polygons)
    geometry_sha256 = json_sha(positions)
    topology_sha256 = json_sha(faces)
    weighting_sha256 = json_sha(vertex_rows)
    transforms = tuple(armature.location) + tuple(armature.rotation_euler) + tuple(armature.scale)
    mesh_transforms = tuple(mesh.location) + tuple(mesh.rotation_euler) + tuple(mesh.scale)
    if not all(close(value, target, 1e-6) for value, target in zip(
            transforms, (0, 0, 0, 0, 0, 0, 1, 1, 1))):
        raise ValueError(f"{kind} {expected['id']} armature transform changed")
    if not all(close(value, target, 1e-6) for value, target in zip(
            mesh_transforms, (0, 0, 0, 0, 0, 0, 1, 1, 1))):
        raise ValueError(f"{kind} {expected['id']} mesh transform changed")
    bones = armature.data.bones
    skeleton_height = float(bones["Head"].tail_local.z)
    shoulder_span = abs(float(bones["LeftUpperArm"].head_local.x - bones["RightUpperArm"].head_local.x))
    hip_span = abs(float(bones["LeftUpperLeg"].head_local.x - bones["RightUpperLeg"].head_local.x))
    left_arm_reach = abs(float(
        bones["LeftHand"].head_local.x - bones["LeftUpperArm"].head_local.x
    ))
    expected_dimensions = expected["dimensions_m"]
    checks = {
        "skeleton_height_m": (skeleton_height, expected["skeleton_height_m"]),
        "shoulder_span_m": (shoulder_span, expected_dimensions["shoulder_half_width"] * 2.0),
        "hip_span_m": (hip_span, expected_dimensions["hip_half_width"] * 2.0),
        "left_arm_horizontal_reach_m": (left_arm_reach, expected_dimensions["arm"]),
    }
    for label, (actual, wanted) in checks.items():
        if not close(actual, wanted):
            raise ValueError(f"{kind} {expected['id']} {label} differs: {actual} != {wanted}")
    pose_bone = armature.pose.bones["LeftUpperArm"]
    pose_bone.rotation_mode = "XYZ"
    before = [tuple(vertex.co) for vertex in
              mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices]
    pose_bone.rotation_euler.z = 0.2
    bpy.context.view_layer.update()
    after = [tuple(vertex.co) for vertex in
             mesh.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices]
    deformation_delta = max(math.dist(a, b) for a, b in zip(before, after))
    pose_bone.rotation_euler.z = 0.0
    bpy.context.view_layer.update()
    if deformation_delta <= 1e-4:
        raise ValueError(f"{kind} {expected['id']} mesh does not deform under its armature")
    return {
        "kind": kind,
        "objects": len(objects),
        "bones": len(names),
        "vertices": len(mesh.data.vertices),
        "faces": len(mesh.data.polygons),
        "weighted_vertices": weighted,
        "all_weights_normalized": True,
        "armature_modifier_count": len(modifiers),
        "armature_modifier_bound": modifier_bound,
        "mesh_parent_bound": parent_bound,
        "deformation_probe_delta": deformation_delta,
        "mesh_deforms_under_pose": True,
        "geometry_sha256": geometry_sha256,
        "topology_sha256": topology_sha256,
        "weighting_sha256": weighting_sha256,
        "detected_profile": profile.name,
        "missing_roles": list(profile.missing),
        "skeleton_height_m": skeleton_height,
        "shoulder_span_m": shoulder_span,
        "hip_span_m": hip_span,
        "left_arm_horizontal_reach_m": left_arm_reach,
        "actions": len(bpy.data.actions),
        "images": len(bpy.data.images),
        "libraries": len(bpy.data.libraries),
    }


def main():
    if REPORT_PATH.exists():
        raise RuntimeError("Fresh-import report already exists")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8-sig"))
    if manifest.get("schema") != "b4ml-portable-comparison-character-manifest-v1":
        raise ValueError("Portable comparison manifest changed")
    results = []
    addon_utils.enable("io_scene_fbx", default_set=False)
    for expected in manifest["assets"]:
        blend_path = ROOT / expected["source_blend"]
        fbx_path = ROOT / expected["fbx"]
        if sha(blend_path) != expected["source_blend_sha256"] or sha(fbx_path) != expected["fbx_sha256"]:
            raise ValueError("Frozen asset hash mismatch: " + expected["id"])
        bpy.ops.wm.open_mainfile(filepath=str(blend_path), load_ui=False)
        source = inspect_scene(expected, "source_blend")
        bpy.ops.wm.read_factory_settings(use_empty=True)
        result = bpy.ops.import_scene.fbx(
            filepath=str(fbx_path), use_anim=False,
            automatic_bone_orientation=False,
        )
        if result != {"FINISHED"}:
            raise RuntimeError("FBX import failed: " + expected["id"])
        imported = inspect_scene(expected, "fresh_fbx_import")
        for field in ("geometry_sha256", "topology_sha256", "weighting_sha256"):
            if source[field] != imported[field]:
                raise ValueError(f"FBX roundtrip changed {field}: {expected['id']}")
        results.append({
            "id": expected["id"],
            "variation": expected["variation"],
            "source_blend_sha256": expected["source_blend_sha256"],
            "fbx_sha256": expected["fbx_sha256"],
            "source": source,
            "imported": imported,
            "roundtrip_geometry_exact_at_1e_5": True,
            "roundtrip_topology_exact_at_1e_5": True,
            "roundtrip_weights_exact_at_1e_6": True,
        })
    report = {
        "schema": "b4ml-portable-comparison-character-host-audit-v1",
        "complete": True,
        "passed": len(results),
        "expected": len(manifest["assets"]),
        "manifest": MANIFEST_PATH.relative_to(ROOT).as_posix(),
        "manifest_sha256_before_audit_binding": sha(MANIFEST_PATH),
        "checker": HERE.relative_to(ROOT).as_posix(),
        "checker_sha256": sha(HERE),
        "host_version": bpy.app.version_string,
        "assets": results,
        "same_asset_required_for_each_matched_pair": True,
        "cascadeur_import_not_yet_run": True,
        "human_review_not_yet_run": True,
        "parity_verified": False,
        "surpasses_verified": False,
        "full_goal_complete": False,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = REPORT_PATH.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, REPORT_PATH)
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
