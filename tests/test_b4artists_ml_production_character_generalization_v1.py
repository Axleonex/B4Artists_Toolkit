"""Real frozen-character, generated-rig, and authored-import compatibility coverage.

This is a bounded engineering probe, not a production-quality or animator-review
claim. The FBX files are the three project-owned portable comparison characters;
the generated cases use project-owned BoneForge/Rigify fixtures; and the authored
import cases use the existing project-authored FBX roundtrips for the supported
Mocap, Unity, and Unreal adapter families. Temporary actions and weighted probe
meshes are created only to exercise source-action preservation and evaluated
deformation.
"""
from pathlib import Path
import hashlib
import json
import os
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [os.environ.get("B4ML_PACKAGE", str(ROOT)), str(ROOT / "tests")]

import addon_utils
import bpy
import numpy as np
from mathutils import Quaternion

import b4artists_ml
from b4artists_ml import body_preview as body
from b4artists_ml import body_solver as solver
from b4artists_ml import posing as posing
from b4artists_ml import rigs
from b4artists_ml import workflow as workflow


TRAIN = ROOT / "training/b4artists_ml"
MANIFEST_PATH = TRAIN / "reference-assets-v1/manifest.json"
REPORT_PATH = TRAIN / "results" / os.environ.get(
    "B4ML_PRODUCTION_GENERALIZATION_RESULT",
    "production-character-generalization-v1.json",
)
PROFILE_IDS = ("standard", "tall_long_limbed", "short_broad")
NATIVE_PROFILE_IDS = (
    "boneforge_generated",
    "rigify_basic_generated",
    "rigify_default_generated",
)
AUTHORED_PROFILE_IDS = (
    "mocap_humanoid_authored",
    "unity_humanoid_authored",
    "unreal_mannequin_authored",
)
ALL_PROFILE_IDS = PROFILE_IDS + NATIVE_PROFILE_IDS + AUTHORED_PROFILE_IDS
NATIVE_ENABLED_TARGETS = {
    "Pelvis",
    "Head",
    "Hand L",
    "Hand R",
    "Foot L",
    "Foot R",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def action_signature(obj, action):
    return [
        (
            curve.data_path,
            curve.array_index,
            [
                (
                    tuple(key.co),
                    tuple(key.handle_left),
                    tuple(key.handle_right),
                    key.interpolation,
                )
                for key in curve.keyframe_points
            ],
        )
        for curve in workflow.action_curves(
            action, getattr(obj.animation_data, "action_slot", None)
        )
    ]


def assign_disposable_action(obj):
    """Give the imported asset a tiny real action without changing its asset data."""
    action = bpy.data.actions.new(obj.name + " - production probe source")
    workflow.assign_action(obj, action)
    curves = workflow.action_curves(action, ensure=True, obj=obj)
    if hasattr(action, "slots") and len(action.slots) == 1:
        obj.animation_data.action_slot = action.slots[0]
    root_path = obj.pose.bones["Root"].path_from_id("location")
    hips_path = obj.pose.bones["Hips"].path_from_id("rotation_quaternion")
    root_curves = [curves.new(data_path=root_path, index=index) for index in range(3)]
    hips_curves = [curves.new(data_path=hips_path, index=index) for index in range(4)]
    for frame in (1, 9, 17):
        root_values = (0.012 * frame, -0.004 * frame, 0.0)
        hips_values = tuple(Quaternion((0, 0, 1), 0.004 * frame))
        for curve, value in zip(root_curves, root_values):
            curve.keyframe_points.insert(frame, value)
        for curve, value in zip(hips_curves, hips_values):
            curve.keyframe_points.insert(frame, value)
    bpy.context.scene.frame_set(1)
    posing._update(obj)
    return action


def imported_asset(manifest_row):
    addon_utils.enable("io_scene_fbx", default_set=False)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    result = bpy.ops.import_scene.fbx(
        filepath=str(ROOT / manifest_row["fbx"]),
        use_anim=False,
        automatic_bone_orientation=False,
    )
    if result != {"FINISHED"}:
        raise RuntimeError("FBX import failed: " + manifest_row["id"])
    armatures = [obj for obj in scene.objects if obj.type == "ARMATURE"]
    meshes = [obj for obj in scene.objects if obj.type == "MESH"]
    if len(armatures) != 1 or len(meshes) != 1:
        raise ValueError("Expected one imported armature and one mesh")
    armature, mesh = armatures[0], meshes[0]
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)
    if mesh.find_armature() != armature:
        raise ValueError("Imported mesh is not bound to its armature")
    if sha(ROOT / manifest_row["fbx"]) != manifest_row["fbx_sha256"]:
        raise ValueError("Frozen FBX hash mismatch: " + manifest_row["id"])
    profile = rigs.detect_rig(armature.data.bones.keys())
    if profile.name != "Unity Humanoid" or profile.family != "humanoid" or profile.missing:
        raise ValueError("Imported asset is not a complete Unity Humanoid: " + manifest_row["id"])
    return scene, armature, mesh


def evaluated_vertices(mesh):
    evaluated = mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
    return np.asarray([tuple(evaluated.matrix_world @ vertex.co) for vertex in evaluated.data.vertices], dtype=float)


def target_pose(obj):
    """Create targets that require pelvis, chest/spine and limb coupling."""
    session = solver.Session(obj)
    try:
        obj.pose.bones["Spine"].rotation_mode = "QUATERNION"
        obj.pose.bones["Spine"].rotation_quaternion = Quaternion((1, 0, 0), 0.075)
        obj.pose.bones["Chest"].rotation_mode = "QUATERNION"
        obj.pose.bones["Chest"].rotation_quaternion = Quaternion((0, 1, 0), -0.055)
        obj.pose.bones["LeftLowerArm"].rotation_mode = "QUATERNION"
        obj.pose.bones["LeftLowerArm"].rotation_quaternion = Quaternion((1, 0, 0), 0.095)
        obj.pose.bones["RightLowerLeg"].rotation_mode = "QUATERNION"
        obj.pose.bones["RightLowerLeg"].rotation_quaternion = Quaternion((0, 1, 0), -0.065)
        posing._update(obj)
        return session.world_points(session.points())
    finally:
        session.cancel()


def run_profile(manifest_row):
    scene, obj, mesh = imported_asset(manifest_row)
    action = assign_disposable_action(obj)
    source_pose = workflow.raw_pose(obj)
    source_signature = action_signature(obj, action)
    source_vertices = evaluated_vertices(mesh)
    targets = target_pose(obj)
    body.begin(obj, scene)
    target_rows = body._target_rows(json.loads(obj.b4ml.body_payload))
    if target_rows != body.TARGETS_V3:
        raise AssertionError("Production probe did not expose the current torso target rows")
    for index, label in target_rows:
        item = obj.b4ml.body_targets[label]
        item.enabled = True
        item.target.location = targets[index]
    obj.b4ml.body_influence = 0.0
    body.solve(obj)
    record = body._read(obj)
    solved_vertices = evaluated_vertices(mesh)
    deformation_delta = float(np.max(np.linalg.norm(solved_vertices - source_vertices, axis=1)))
    metrics = record["metrics"]
    if metrics["pin_error"] >= 2e-4:
        raise AssertionError("pin error exceeded bound")
    if metrics["length_error"] >= 0.002:
        raise AssertionError("bone length error exceeded bound")
    if deformation_delta <= 1e-4:
        raise AssertionError("production mesh did not deform under solved pose")
    solved_pose = workflow.raw_pose(obj)
    body.finish(obj, scene, False)
    if workflow.raw_pose(obj) != source_pose:
        raise AssertionError("source pose was not restored")
    if obj.animation_data.action != action:
        raise AssertionError("source action identity was not restored")
    if action_signature(obj, action) != source_signature:
        raise AssertionError("source action curves changed")
    return {
        "id": manifest_row["id"],
        "variation": manifest_row["variation"],
        "fbx_sha256": manifest_row["fbx_sha256"],
        "detected_profile": "Unity Humanoid",
        "target_rows": len(target_rows),
        "enabled_target_rows": len(target_rows),
        "pin_error": float(metrics["pin_error"]),
        "length_error": float(metrics["length_error"]),
        "deformation_delta": deformation_delta,
        "coupled_torso": metrics.get("torso_coupling", {}),
        "source_pose_restored": workflow.raw_pose(obj) == source_pose,
        "source_action_restored": obj.animation_data.action == action,
        "source_action_curves_restored": action_signature(obj, action) == source_signature,
        "solved_pose_changed": solved_pose != source_pose,
        "human_review": False,
        "learned_temporal_claim": False,
        "production_universal_claim": False,
    }


def native_probe_action(obj, binding):
    """Attach a tiny real action so native fixture recovery is observable."""
    action = bpy.data.actions.new(obj.name + " - native production probe source")
    workflow.assign_action(obj, action)
    curves = workflow.action_curves(action, ensure=True, obj=obj)
    if hasattr(action, "slots") and len(action.slots) == 1:
        obj.animation_data.action_slot = action.slots[0]
    root = obj.pose.bones[binding["root"]]
    root_curves = [
        curves.new(data_path=root.path_from_id("location"), index=index)
        for index in range(3)
    ]
    for frame in (1, 9, 17):
        values = (0.008 * frame, -0.003 * frame, 0.0)
        for curve, value in zip(root_curves, values):
            curve.keyframe_points.insert(frame, value)
    bpy.context.scene.frame_set(1)
    posing._update(obj)
    return action


def native_probe_mesh(obj, binding, label):
    """Create a disposable weighted triangle to prove the solved pose deforms."""
    from mathutils import Vector

    deform = (
        "hand.def-L"
        if label == "boneforge"
        else "DEF-hand.L"
        if label.startswith("rigify")
        else binding["names"][7]
    )
    data = bpy.data.meshes.new(obj.name + " - native production probe mesh")
    point = obj.data.bones[deform].head_local.copy()
    data.from_pydata(
        [point, point + Vector((0.01, 0, 0)), point + Vector((0, 0.01, 0))],
        [],
        [(0, 1, 2)],
    )
    mesh = bpy.data.objects.new(obj.name + " - native production probe mesh", data)
    bpy.context.scene.collection.objects.link(mesh)
    mesh.vertex_groups.new(name=deform).add([0, 1, 2], 1.0, "REPLACE")
    mesh.modifiers.new("Armature", "ARMATURE").object = obj
    return mesh


def native_target_pose(obj, label, pose_factor=0.5):
    """Author a reachable target from the post-action native source pose."""
    from context_rig import _quat, _set_quat

    session = solver.Session(obj)
    try:
        body_name = "spine.01" if label == "boneforge" else "chest"
        bone = obj.pose.bones[body_name]
        _set_quat(
            bone,
            _quat(bone) @ Quaternion((1, 0, 0), 0.12 * pose_factor),
        )
        for name in session.binding["rotations"][-8:]:
            bone = obj.pose.bones[name]
            _set_quat(
                bone,
                _quat(bone) @ Quaternion((1, 0, 0), 0.18 * pose_factor),
            )
        obj.pose.bones[session.binding["root"]].location.z -= 0.015 * pose_factor
        posing._update(obj)
        return session.world_points(session.points())
    finally:
        session.cancel()


def run_native_profile(profile_id):
    """Run the same bounded body solve against a generated project-owned rig."""
    from test_b4artists_ml_context_rig import ContextRigTests

    label = profile_id.removesuffix("_generated")
    fixture = ContextRigTests()
    obj, _source, source_session, targets, _ = fixture.fixture(label)
    scene = bpy.context.scene
    binding = source_session.binding
    source_session.cancel()
    action = native_probe_action(obj, binding)
    source_pose = workflow.raw_pose(obj)
    source_signature = action_signature(obj, action)
    targets = native_target_pose(obj, label)
    mesh = native_probe_mesh(obj, binding, label)
    mesh_name = mesh.name
    mesh_data_name = mesh.data.name
    source_vertices = evaluated_vertices(mesh)
    try:
        bpy.context.view_layer.objects.active = obj
        body.begin(obj, scene)
        target_rows = body._target_rows(json.loads(obj.b4ml.body_payload))
        if target_rows != body.TARGETS_V3:
            raise AssertionError(
                "Native production probe did not expose the current torso target rows"
            )
        for index, target_label in target_rows:
            item = obj.b4ml.body_targets[target_label]
            item.enabled = target_label in NATIVE_ENABLED_TARGETS
            item.target.location = targets[index]
        obj.b4ml.body_influence = 0.0
        body.solve(obj)
        record = body._read(obj)
        solved_vertices = evaluated_vertices(mesh)
        deformation_delta = float(
            np.max(np.linalg.norm(solved_vertices - source_vertices, axis=1))
        )
        metrics = record["metrics"]
        if metrics["pin_error"] >= 2e-4:
            raise AssertionError("native pin error exceeded bound")
        if metrics["length_error"] >= 0.002:
            raise AssertionError("native bone length error exceeded bound")
        if deformation_delta <= 1e-4:
            raise AssertionError("native production probe mesh did not deform")
        solved_pose = workflow.raw_pose(obj)
        body.finish(obj, scene, False)
        if workflow.raw_pose(obj) != source_pose:
            raise AssertionError("native source pose was not restored")
        if obj.animation_data.action != action:
            raise AssertionError("native source action identity was not restored")
        if action_signature(obj, action) != source_signature:
            raise AssertionError("native source action curves changed")
        return {
            "id": profile_id,
            "character_kind": "generated_native_rig",
            "adapter": label,
            "variation": "project-owned generated fixture",
            "fbx_sha256": None,
            "detected_profile": label,
            "target_rows": len(target_rows),
            "enabled_target_rows": len(NATIVE_ENABLED_TARGETS),
            "enabled_target_slice": sorted(NATIVE_ENABLED_TARGETS),
            "pin_error": float(metrics["pin_error"]),
            "length_error": float(metrics["length_error"]),
            "deformation_delta": deformation_delta,
            "coupled_torso": metrics.get("torso_coupling", {}),
            "source_pose_restored": workflow.raw_pose(obj) == source_pose,
            "source_action_restored": obj.animation_data.action == action,
            "source_action_curves_restored": action_signature(obj, action)
            == source_signature,
            "solved_pose_changed": solved_pose != source_pose,
            "human_review": False,
            "learned_temporal_claim": False,
            "production_universal_claim": False,
        }
    finally:
        if obj.b4ml.body_payload:
            body.finish(obj, scene, False)
        mesh_current = bpy.data.objects.get(mesh_name)
        if mesh_current is not None:
            bpy.data.objects.remove(mesh_current, do_unlink=True)
        mesh_data = bpy.data.meshes.get(mesh_data_name)
        if mesh_data is not None:
            bpy.data.meshes.remove(mesh_data)


def authored_target_pose(obj, roles, pose_factor=0.5):
    """Author a reachable target from an imported authored-FBX source pose."""
    session = solver.Session(obj)
    try:
        for bone_name, axis, angle in (
            (roles["spine.01"], (1, 0, 0), 0.09 * pose_factor),
            (roles["forearm.fk-L"], (1, 0, 0), 0.10 * pose_factor),
        ):
            bone = obj.pose.bones[bone_name]
            bone.rotation_mode = "QUATERNION"
            bone.rotation_quaternion = Quaternion(axis, angle)
        posing._update(obj)
        return session.world_points(session.points())
    finally:
        session.cancel()


def run_authored_profile(profile_id, variant):
    """Run the bounded endpoint solve against an authored FBX roundtrip fixture."""
    from test_b4artists_ml_imported_humanoids import authored

    label = profile_id.removesuffix("_authored")
    obj, mesh, roles = authored(label, variant)
    scene = bpy.context.scene
    source_pose = workflow.raw_pose(obj)
    action = obj.animation_data.action
    source_signature = action_signature(obj, action)
    source_vertices = evaluated_vertices(mesh)
    targets = authored_target_pose(obj, roles)
    try:
        bpy.context.view_layer.objects.active = obj
        body.begin(obj, scene)
        target_rows = body._target_rows(json.loads(obj.b4ml.body_payload))
        if target_rows != body.TARGETS_V3:
            raise AssertionError(
                "Authored-import production probe did not expose the current torso target rows"
            )
        for index, target_label in target_rows:
            item = obj.b4ml.body_targets[target_label]
            item.enabled = target_label in NATIVE_ENABLED_TARGETS
            item.target.location = targets[index]
        obj.b4ml.body_influence = 0.0
        body.solve(obj)
        record = body._read(obj)
        solved_vertices = evaluated_vertices(mesh)
        deformation_delta = float(
            np.max(np.linalg.norm(solved_vertices - source_vertices, axis=1))
        )
        metrics = record["metrics"]
        if metrics["pin_error"] >= 2e-4:
            raise AssertionError("authored-import pin error exceeded bound")
        if metrics["length_error"] >= 0.002:
            raise AssertionError("authored-import bone length error exceeded bound")
        if deformation_delta <= 1e-4:
            raise AssertionError("authored-import production probe mesh did not deform")
        solved_pose = workflow.raw_pose(obj)
        body.finish(obj, scene, False)
        if workflow.raw_pose(obj) != source_pose:
            raise AssertionError("authored-import source pose was not restored")
        if obj.animation_data.action != action:
            raise AssertionError("authored-import source action identity was not restored")
        if action_signature(obj, action) != source_signature:
            raise AssertionError("authored-import source action curves changed")
        return {
            "id": profile_id,
            "character_kind": "authored_import_fixture",
            "fixture_origin": "project-authored FBX roundtrip; not an external production asset",
            "adapter": label,
            "variation": f"project-authored imported fixture variant {variant}",
            "fbx_sha256": None,
            "detected_profile": label,
            "target_rows": len(target_rows),
            "enabled_target_rows": len(NATIVE_ENABLED_TARGETS),
            "enabled_target_slice": sorted(NATIVE_ENABLED_TARGETS),
            "pin_error": float(metrics["pin_error"]),
            "length_error": float(metrics["length_error"]),
            "deformation_delta": deformation_delta,
            "coupled_torso": metrics.get("torso_coupling", {}),
            "source_pose_restored": workflow.raw_pose(obj) == source_pose,
            "source_action_restored": obj.animation_data.action == action,
            "source_action_curves_restored": action_signature(obj, action)
            == source_signature,
            "solved_pose_changed": solved_pose != source_pose,
            "human_review": False,
            "learned_temporal_claim": False,
            "production_universal_claim": False,
        }
    finally:
        if obj.b4ml.body_payload:
            body.finish(obj, scene, False)


class ProductionCharacterGeneralizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        b4artists_ml.register()
        from test_b4artists_ml_context_rig import ContextRigTests

        ContextRigTests.setUpClass()
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8-sig"))
        if cls.manifest["schema"] != "b4ml-portable-comparison-character-manifest-v1":
            raise ValueError("Portable character manifest changed")
        cls.rows = {row["id"]: row for row in cls.manifest["assets"]}
        cls.results = []

    @classmethod
    def tearDownClass(cls):
        report = {
            "schema": "b4ml-production-character-generalization-host-v1",
            "complete": len(cls.results) == len(ALL_PROFILE_IDS),
            "asset_manifest": "training/b4artists_ml/reference-assets-v1/manifest.json",
            "asset_manifest_sha256": sha(MANIFEST_PATH),
            "profiles": cls.results,
            "passed": len(cls.results),
            "expected": len(ALL_PROFILE_IDS),
            "scope": "Three frozen project-owned Unity Humanoid FBX characters, three project-owned generated BoneForge/Rigify fixtures, and three project-authored imported Mocap/Unity/Unreal FBX roundtrips; native and authored-import cases use the bounded six-endpoint target slice; existing procedural coupled solver only.",
            "human_review_not_run": True,
            "learned_temporal_quality_not_claimed": True,
            "universal_production_compatibility_not_claimed": True,
            "cascadeur_comparison_not_run": True,
            "full_goal_complete": False,
        }
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")

    def tearDown(self):
        body.reset_runtime()
        for obj in list(bpy.data.objects):
            if obj.type == "ARMATURE" and obj.b4ml.body_payload:
                body.finish(obj, bpy.context.scene, False)

    def test_all_frozen_proportions_support_coupled_body_solve_and_recovery(self):
        self.assertEqual(set(self.rows), set(PROFILE_IDS))
        for profile_id in PROFILE_IDS:
            with self.subTest(profile=profile_id):
                result = run_profile(self.rows[profile_id])
                self.results.append(result)
                self.assertTrue(result["source_pose_restored"])
                self.assertTrue(result["source_action_restored"])
                self.assertTrue(result["source_action_curves_restored"])

    def test_generated_native_rigs_support_coupled_body_solve_and_recovery(self):
        for profile_id in NATIVE_PROFILE_IDS:
            with self.subTest(profile=profile_id):
                result = run_native_profile(profile_id)
                self.results.append(result)
                self.assertTrue(result["source_pose_restored"])
                self.assertTrue(result["source_action_restored"])
                self.assertTrue(result["source_action_curves_restored"])

    def test_authored_import_families_support_endpoint_solve_and_recovery(self):
        for variant, profile_id in enumerate(AUTHORED_PROFILE_IDS):
            with self.subTest(profile=profile_id):
                result = run_authored_profile(profile_id, variant)
                self.results.append(result)
                self.assertTrue(result["source_pose_restored"])
                self.assertTrue(result["source_action_restored"])
                self.assertTrue(result["source_action_curves_restored"])


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(
        ProductionCharacterGeneralizationTests
    )
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    print(
        "B4ML_PRODUCTION_GENERALIZATION_RESULT:",
        "PASS" if result.wasSuccessful() else "FAIL",
        flush=True,
    )
    if not result.wasSuccessful():
        raise SystemExit(1)
