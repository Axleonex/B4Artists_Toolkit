"""Build three project-owned neutral FBX characters for matched comparison.

Run only inside Bforartists. The generated assets contain one Unity-style
armature and one rigidly weighted procedural mannequin mesh. No external files,
textures, animation, add-on runtime data, or third-party character assets enter
the files.
"""
from pathlib import Path
import hashlib
import json
import math
import os

import addon_utils
import bpy
from mathutils import Vector


HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
SPEC_PATH = HERE.with_name("portable_comparison_characters_v1.json")
OUTPUT = HERE.parent / "reference-assets-v1"
MANIFEST = OUTPUT / "manifest.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def skeleton(dimensions):
    leg = dimensions["leg"]
    torso = dimensions["torso"]
    head = dimensions["head"]
    shoulder = dimensions["shoulder_half_width"]
    hip = dimensions["hip_half_width"]
    arm = dimensions["arm"]
    foot = dimensions["foot"]
    center = lambda z: (0.0, 0.0, z)
    hips = center(leg)
    spine = center(leg + torso * 0.20)
    chest = center(leg + torso * 0.44)
    upper_chest = center(leg + torso * 0.68)
    neck = center(leg + torso * 0.84)
    head_base = center(leg + torso * 0.94)
    head_top = center(leg + torso + head)
    rows = [
        ("Root", (0.0, 0.0, 0.0), (0.0, 0.0, 0.12), None, False, False),
        ("Hips", hips, spine, "Root", False, True),
        ("Spine", spine, chest, "Hips", True, True),
        ("Chest", chest, upper_chest, "Spine", True, True),
        ("UpperChest", upper_chest, neck, "Chest", True, True),
        ("Neck", neck, head_base, "UpperChest", True, True),
        ("Head", head_base, head_top, "Neck", True, True),
        ("HeadEnd", head_top, (0.0, 0.0, head_top[2] + 0.05), "Head", True, False),
    ]
    for side, sign in (("Left", 1.0), ("Right", -1.0)):
        shoulder_tip = (sign * shoulder, 0.0, upper_chest[2])
        elbow = (sign * (shoulder + arm * 0.52), 0.0, upper_chest[2] - arm * 0.055)
        wrist = (sign * (shoulder + arm), 0.0, upper_chest[2] - arm * 0.09)
        hand_tip = (sign * (shoulder + arm + arm * 0.17), 0.0, wrist[2])
        knee = (sign * hip, 0.0, leg * 0.53)
        ankle = (sign * hip, 0.0, 0.08)
        toe = (sign * hip, -foot, 0.08)
        rows.extend([
            (side + "Shoulder", upper_chest, shoulder_tip, "UpperChest", False, True),
            (side + "UpperArm", shoulder_tip, elbow, side + "Shoulder", True, True),
            (side + "LowerArm", elbow, wrist, side + "UpperArm", True, True),
            (side + "Hand", wrist, hand_tip, side + "LowerArm", True, True),
            (side + "HandEnd", hand_tip,
             (hand_tip[0] + sign * 0.04, hand_tip[1], hand_tip[2]),
             side + "Hand", True, False),
            (side + "UpperLeg", (sign * hip, 0.0, leg), knee, "Hips", False, True),
            (side + "LowerLeg", knee, ankle, side + "UpperLeg", True, True),
            (side + "Foot", ankle, toe, side + "LowerLeg", False, True),
            (side + "ToeEnd", toe, (toe[0], toe[1] - 0.04, toe[2]),
             side + "Foot", True, False),
        ])
    return rows


def cross_section(name, dimensions):
    depth = dimensions["body_depth"]
    shoulder = dimensions["shoulder_half_width"]
    hip = dimensions["hip_half_width"]
    head = dimensions["head"]
    if name == "Hips":
        return hip, depth * 0.56
    if name in {"Spine", "Chest"}:
        return max(hip * 0.82, shoulder * 0.52), depth * 0.50
    if name == "UpperChest":
        return shoulder * 0.72, depth * 0.54
    if name == "Neck":
        return head * 0.18, head * 0.16
    if name == "Head":
        return head * 0.36, head * 0.32
    if name.endswith("Shoulder"):
        return depth * 0.20, depth * 0.18
    if name.endswith(("UpperArm", "UpperLeg")):
        return depth * 0.24, depth * 0.22
    if name.endswith(("LowerArm", "LowerLeg")):
        return depth * 0.19, depth * 0.17
    if name.endswith("Hand"):
        return depth * 0.22, depth * 0.12
    if name.endswith("Foot"):
        return depth * 0.22, depth * 0.16
    raise ValueError("No section for " + name)


def add_box(vertices, faces, head, tail, half_a, half_b):
    start = len(vertices)
    head = Vector(head)
    tail = Vector(tail)
    direction = tail - head
    if direction.length <= 1e-8:
        raise ValueError("Degenerate mannequin segment")
    direction.normalize()
    helper = Vector((0.0, 0.0, 1.0)) if abs(direction.z) < 0.9 else Vector((0.0, 1.0, 0.0))
    axis_a = direction.cross(helper).normalized() * half_a
    axis_b = direction.cross(axis_a).normalized() * half_b
    for point in (head, tail):
        vertices.extend(tuple(point + sa * axis_a + sb * axis_b)
                        for sa, sb in ((-1, -1), (1, -1), (1, 1), (-1, 1)))
    faces.extend((
        (start, start + 1, start + 2, start + 3),
        (start + 4, start + 7, start + 6, start + 5),
        (start, start + 4, start + 5, start + 1),
        (start + 1, start + 5, start + 6, start + 2),
        (start + 2, start + 6, start + 7, start + 3),
        (start + 3, start + 7, start + 4, start),
    ))
    return tuple(range(start, start + 8))


def build(profile):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = "B4ML Comparison " + profile["label"]
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.length_unit = "METERS"
    scene.unit_settings.scale_length = 1.0
    scene.render.fps = 30
    dimensions = profile["dimensions_m"]
    rows = skeleton(dimensions)

    armature_data = bpy.data.armatures.new("B4ML_Unity_Humanoid")
    armature = bpy.data.objects.new("B4ML_Unity_Humanoid", armature_data)
    scene.collection.objects.link(armature)
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    for name, head, tail, _parent, _connected, deform in rows:
        bone = armature_data.edit_bones.new(name)
        bone.head = head
        bone.tail = tail
        bone.use_deform = deform
    for name, _head, _tail, parent, connected, _deform in rows:
        if parent:
            bone = armature_data.edit_bones[name]
            bone.parent = armature_data.edit_bones[parent]
            bone.use_connect = connected
    bpy.ops.object.mode_set(mode="OBJECT")

    vertices, faces, groups = [], [], []
    for name, head, tail, _parent, _connected, deform in rows:
        if not deform:
            continue
        half_a, half_b = cross_section(name, dimensions)
        groups.append((name, add_box(vertices, faces, head, tail, half_a, half_b)))
    mesh_data = bpy.data.meshes.new("B4ML_Comparison_Mannequin")
    mesh_data.from_pydata(vertices, (), faces)
    mesh_data.validate(verbose=True)
    mesh_data.update()
    mesh = bpy.data.objects.new("B4ML_Comparison_Mannequin", mesh_data)
    scene.collection.objects.link(mesh)
    for name, indices in groups:
        mesh.vertex_groups.new(name=name).add(indices, 1.0, "REPLACE")
    modifier = mesh.modifiers.new("B4ML Armature", "ARMATURE")
    modifier.object = armature
    mesh.parent = armature
    material = bpy.data.materials.new("B4ML Neutral Gray")
    material.diffuse_color = (0.42, 0.48, 0.55, 1.0)
    mesh.data.materials.append(material)

    armature["b4ml_comparison_profile"] = profile["id"]
    armature["b4ml_asset_license"] = "GPL-2.0-or-later"
    armature["b4ml_rest_pose"] = "neutral T pose"
    mesh["b4ml_project_owned_geometry"] = True
    for obj in (armature, mesh):
        obj.location = (0.0, 0.0, 0.0)
        obj.rotation_euler = (0.0, 0.0, 0.0)
        obj.scale = (1.0, 1.0, 1.0)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    blend_path = OUTPUT / (profile["id"] + ".blend")
    fbx_path = OUTPUT / (profile["id"] + ".fbx")
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path), check_existing=False, compress=False)
    bpy.ops.object.select_all(action="DESELECT")
    armature.select_set(True)
    mesh.select_set(True)
    bpy.context.view_layer.objects.active = armature
    addon_utils.enable("io_scene_fbx", default_set=False)
    if not hasattr(bpy.ops, "export_scene") or not hasattr(bpy.ops.export_scene, "fbx"):
        raise RuntimeError("Installed host has no FBX exporter")
    result = bpy.ops.export_scene.fbx(
        filepath=str(fbx_path), use_selection=True,
        object_types={"ARMATURE", "MESH"}, add_leaf_bones=False,
        bake_anim=False, use_mesh_modifiers=False,
        apply_unit_scale=True, apply_scale_options="FBX_SCALE_NONE",
        axis_forward="-Y", axis_up="Z", mesh_smooth_type="OFF",
        use_tspace=False, path_mode="AUTO",
    )
    if result != {"FINISHED"} or not fbx_path.is_file():
        raise RuntimeError("FBX export failed for " + profile["id"])
    expected_names = [row[0] for row in rows]
    parents = {row[0]: row[3] for row in rows}
    deform_names = [row[0] for row in rows if row[5]]
    overall_height = dimensions["leg"] + dimensions["torso"] + dimensions["head"]
    return {
        "id": profile["id"],
        "label": profile["label"],
        "variation": profile["variation"],
        "dimensions_m": dimensions,
        "skeleton_height_m": overall_height,
        "source_blend": blend_path.relative_to(ROOT).as_posix(),
        "source_blend_sha256": sha(blend_path),
        "fbx": fbx_path.relative_to(ROOT).as_posix(),
        "fbx_sha256": sha(fbx_path),
        "bones": expected_names,
        "bone_parents": parents,
        "deform_bones": deform_names,
        "vertices": len(vertices),
        "faces": len(faces),
        "weighted_vertices": len(vertices),
        "object_count": 2,
        "actions": 0,
        "external_images": 0,
        "external_libraries": 0,
    }


def main():
    if MANIFEST.exists():
        raise RuntimeError("Portable comparison manifest already exists; remove it only for an intentional rebuild")
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8-sig"))
    if spec.get("schema") != "b4ml-portable-comparison-character-spec-v1":
        raise ValueError("Portable comparison specification changed")
    assets = [build(profile) for profile in spec["profiles"]]
    manifest = {
        "schema": "b4ml-portable-comparison-character-manifest-v1",
        "complete": True,
        "assets_frozen": True,
        "asset_count": len(assets),
        "same_asset_required_for_each_matched_pair": True,
        "source_spec": SPEC_PATH.relative_to(ROOT).as_posix(),
        "source_spec_sha256": sha(SPEC_PATH),
        "builder": HERE.relative_to(ROOT).as_posix(),
        "builder_sha256": sha(HERE),
        "host_version": bpy.app.version_string,
        "host_binary": str(Path(bpy.app.binary_path).resolve()),
        "license": spec["license"],
        "third_party_assets": [],
        "assets": assets,
        "fresh_import_audit": None,
        "cascadeur_results": None,
        "parity_verified": False,
        "surpasses_verified": False,
        "full_goal_complete": False,
    }
    write_json(MANIFEST, manifest)
    print(json.dumps(manifest, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
