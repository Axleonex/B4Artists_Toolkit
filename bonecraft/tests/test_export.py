"""Tests for R5 profile-driven export.

Headless (``python tests/test_export.py``): the pure profile -> exporter
kwargs mappers and action-mode resolution, loaded directly so io_hub/__init__
(bpy) is not triggered.

In-host (``run()`` under Bforartists): export an engine rig + skinned mesh per
profile, re-import the file, and confirm a deform-only hierarchy + actions.
"""
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


def _load_direct(modname, relpath):
    path = os.path.join(ROOT, *relpath)
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def headless():
    profiles = _load_direct("bf_profiles", ("boneforge", "io_hub", "profiles.py"))
    px = _load_direct("bf_profile_export",
                      ("boneforge", "io_hub", "profile_export.py"))

    for pid in profiles.available_profiles():
        prof = profiles.get_profile(pid)
        if prof["container"] == 'FBX':
            kw = px.profile_to_fbx_kwargs(prof)
            assert kw["use_armature_deform_only"] == prof["deform_only"]
            assert kw["axis_up"] == prof["axis_up"]
            assert kw["add_leaf_bones"] == prof["add_leaf_bones"]
        else:
            kw = px.profile_to_gltf_kwargs(prof)
            assert kw["export_format"] == 'GLB'
            assert kw["export_def_bones"] == prof["deform_only"]

    assert px.resolve_action_kwargs('NONE') == {"bake_anim": False}
    assert px.resolve_action_kwargs('ALL')["bake_anim_use_all_actions"] is True
    assert px.resolve_action_kwargs('ACTIVE')["bake_anim_use_all_actions"] is False
    # interpolation modes + shape-key validation surface exist
    assert {m[0] for m in px.INTERP_MODES} == {'BEZIER', 'LINEAR', 'CONSTANT'}
    assert px.check_shape_keys([]) == []           # nothing to flag, pure call
    print("test_export PASS  (profile kwargs + action/interp modes for %d "
          "profiles)" % len(profiles.available_profiles()))


# ── in-host ──────────────────────────────────────────────────

def run():
    import bpy
    import test_rig_build as trb
    from boneforge.autorig.rig_build import RigSpec, build_control_rig
    from boneforge.io_hub import profile_export as px

    # build an engine rig + skinned mesh, select both
    arm = trb._fresh_armature()
    build_control_rig(arm, RigSpec())
    mesh = trb._skinned_mesh(arm)
    mesh.parent = arm
    mesh.parent_type = 'ARMATURE'
    bpy.context.view_layer.update()

    # profile checks run and are profile-specific
    findings = px.run_profile_checks(arm, "unreal_humanoid")
    assert findings, "no checks ran"
    assert all("check" in f and "status" in f for f in findings)
    print("export checks ran (%d findings for unreal_humanoid)" % len(findings))

    import boneforge
    registered = False
    try:
        boneforge.register()
        registered = True
        bpy.context.view_layer.objects.active = arm
        result = bpy.ops.boneforge.profile_check(profile_id="unreal_humanoid")
        assert result == {'FINISHED'}, result
        stored = bpy.context.window_manager.boneforge_profile_findings
        assert len(stored) == len(findings), "profile findings were not stored"
        assert all(r.message for r in stored), "stored finding missing message"
        print("profile export findings UI storage verified (%d rows)"
              % len(stored))
    finally:
        if registered:
            boneforge.unregister()

    deform_names = {b.name for b in arm.data.bones if b.use_deform}
    assert deform_names, "no deform bones tagged"

    tmp = bpy.app.tempdir or os.environ.get("TEMP") or "."

    def _select_rig():
        if bpy.context.object is not None and bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        arm.select_set(True)
        mesh.select_set(True)
        bpy.context.view_layer.objects.active = arm

    # 1) FBX deform-only export + re-import -> only deform bones present
    fbx_path = os.path.join(tmp, "bf_export_test.fbx")
    _select_rig()
    ok, msg = px.export_with_profile(bpy.context, "unreal_humanoid", fbx_path,
                                     action_mode='NONE')
    assert ok, msg
    assert os.path.exists(fbx_path), "FBX not written"
    before = set(bpy.data.objects.keys())
    bpy.ops.import_scene.fbx(filepath=fbx_path, ignore_leaf_bones=True)
    imported = [bpy.data.objects[n] for n in bpy.data.objects.keys()
                if n not in before]
    imp_arm = next((o for o in imported if o.type == 'ARMATURE'), None)
    assert imp_arm is not None, "no armature re-imported"
    imp_bones = {b.name for b in imp_arm.data.bones}
    # deform-only strips the animator controls (IK/pole/MCH/limb-FK) while
    # keeping the deform skeleton + the minimal connective root/COG ancestors.
    control_suffixes = (".ik-", ".pole-", ".mch_ik-")
    leaked_controls = {n for n in imp_bones
                       if any(s in n for s in control_suffixes)
                       or n in {"properties", "upperarm.fk-L", "forearm.fk-L",
                                "hand.fk-L", "thigh.fk-L", "shin.fk-L"}}
    assert not leaked_controls, ("control bones leaked into deform-only export",
                                 sorted(leaked_controls))
    # the deform bones survived
    assert deform_names & imp_bones, "no deform bones in the export"
    assert any(".def-" in n for n in imp_bones), "limb deform bones missing"
    print("FBX deform-only round-trip verified (%d bones, controls stripped, "
          "deform kept)" % len(imp_bones))

    # 2) GLB export round-trips
    glb_path = os.path.join(tmp, "bf_export_test.glb")
    _select_rig()
    ok, msg = px.export_with_profile(bpy.context, "godot_humanoid", glb_path,
                                     action_mode='NONE')
    assert ok, msg
    assert os.path.exists(glb_path), "GLB not written"
    print("GLB export verified (%s)" % os.path.basename(glb_path))

    # 3) single-action export carries animation
    import math
    arm.animation_data_create()
    fk = arm.pose.bones["upperarm.fk-L"]
    fk.rotation_mode = 'XYZ'
    bpy.context.scene.frame_set(1)
    fk.keyframe_insert("rotation_euler", frame=1)
    fk.rotation_euler = (0.0, 0.0, math.radians(40))
    fk.keyframe_insert("rotation_euler", frame=10)
    anim_path = os.path.join(tmp, "bf_export_anim.fbx")
    _select_rig()
    ok, msg = px.export_with_profile(bpy.context, "unreal_humanoid", anim_path,
                                     action_mode='ACTIVE')
    assert ok, msg
    assert os.path.exists(anim_path), "animated FBX not written"
    print("single-action export verified (%s)" % os.path.basename(anim_path))

    # 4) per-bone interpolation rewrites the exported action's keys
    _select_rig()
    px.export_with_profile(bpy.context, "unreal_humanoid",
                           os.path.join(tmp, "bf_export_interp.fbx"),
                           action_mode='ACTIVE', interpolation='LINEAR')
    act = arm.animation_data.action
    interps = {kp.interpolation for fc in px._action_fcurves(act)
               for kp in fc.keyframe_points}
    assert interps == {'LINEAR'}, ("interpolation not applied", interps)
    print("per-bone interpolation verified (keys -> %s)" % interps)

    # 5) root-motion export includes the custom root + re-imports
    rm_path = os.path.join(tmp, "bf_export_rootmotion.fbx")
    _select_rig()
    ok, msg = px.export_with_profile(bpy.context, "unreal_humanoid", rm_path,
                                     action_mode='ACTIVE', root_motion=True)
    assert ok, msg
    before = set(bpy.data.objects.keys())
    bpy.ops.import_scene.fbx(filepath=rm_path, ignore_leaf_bones=True)
    rm_arm = next((bpy.data.objects[n] for n in bpy.data.objects.keys()
                   if n not in before and bpy.data.objects[n].type == 'ARMATURE'),
                  None)
    assert rm_arm is not None and "root" in {b.name for b in rm_arm.data.bones}, \
        "root-motion export did not include the custom root bone"
    # and the temporary deform tag was restored on the source rig
    assert arm.data.bones["root"].use_deform is False, "root deform tag leaked"
    print("root-motion export verified (root bone present + re-imported)")

    # 6) multi-action export re-imports without corruption
    second = bpy.data.actions.new("BF_SECOND")
    arm.animation_data.action = second
    fk2 = arm.pose.bones["forearm.fk-L"]
    fk2.rotation_mode = 'XYZ'
    bpy.context.scene.frame_set(1); fk2.keyframe_insert("rotation_euler", frame=1)
    fk2.rotation_euler = (0.0, 0.0, math.radians(25))
    bpy.context.scene.frame_set(8); fk2.keyframe_insert("rotation_euler", frame=8)
    multi_path = os.path.join(tmp, "bf_export_multi.fbx")
    _select_rig()
    ok, msg = px.export_with_profile(bpy.context, "unreal_humanoid", multi_path,
                                     action_mode='ALL')
    assert ok, msg
    actions_pre = set(bpy.data.actions.keys())
    before = set(bpy.data.objects.keys())
    bpy.ops.import_scene.fbx(filepath=multi_path, ignore_leaf_bones=True)
    imp = [bpy.data.objects[n] for n in bpy.data.objects.keys() if n not in before]
    imp_arm = next((o for o in imp if o.type == 'ARMATURE'), None)
    assert imp_arm is not None, "multi-action FBX did not re-import an armature"
    # the takes must have come back as animation (new actions, or curves on the
    # re-imported armature) — not just "some object appeared"
    new_actions = set(bpy.data.actions.keys()) - actions_pre
    has_anim = bool(new_actions) or (
        imp_arm.animation_data is not None and (
            imp_arm.animation_data.action is not None
            or len(imp_arm.animation_data.nla_tracks) > 0))
    assert has_anim, "multi-action export re-imported no animation data"
    print("multi-action export verified (action_mode=ALL re-imports %d "
          "action take(s) / animation data)" % max(1, len(new_actions)))

    # 7) shape-key export validation flags morph meshes
    sk_mesh = trb._skinned_mesh(arm)
    sk_mesh.shape_key_add(name="Basis")
    sk_mesh.shape_key_add(name="smile")
    findings = px.run_profile_checks(arm, "vrchat")
    assert any(f["check"] == "shape_keys" for f in findings), \
        "shape-key validation did not flag the morph mesh"
    print("shape-key validation verified (%d shape-key finding(s))"
          % sum(1 for f in findings if f["check"] == "shape_keys"))

    from mathutils import Vector
    # 8) VRChat exports a T-pose copy: arms level, legs straight, shape keys
    #    kept, and the working scene (names, vertices) untouched.
    arm.animation_data.action = None
    for pb in arm.pose.bones:
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = (1, 0, 0, 0)
    fkA = arm.pose.bones["upperarm.fk-L"]
    fkA.rotation_mode = 'XYZ'
    fkA.rotation_euler = (0.0, math.radians(35), 0.0)   # posed, not rest: ignored
    bpy.context.view_layer.update()
    sk_mesh.parent = arm
    co_before = [v.co.copy() for v in mesh.data.vertices]
    names_before = set(bpy.data.objects.keys())
    tp_path = os.path.join(tmp, "bf_export_tpose.fbx")
    _select_rig()
    sk_mesh.select_set(True)
    ok, msg = px.export_with_profile(bpy.context, "vrchat", tp_path)
    assert ok and "T-pose" in msg, msg
    assert set(bpy.data.objects.keys()) == names_before, "T-pose copies leaked"
    assert all((v.co - c).length < 1e-6
               for v, c in zip(mesh.data.vertices, co_before)), "source mesh changed"
    before = set(bpy.data.objects.keys())
    bpy.ops.import_scene.fbx(filepath=tp_path, ignore_leaf_bones=True)
    imp = [bpy.data.objects[n] for n in bpy.data.objects.keys() if n not in before]
    tp_arm = next(o for o in imp if o.type == 'ARMATURE')
    for bone, want in (("upperarm.def-L", (1, 0, 0)), ("upperarm.def-R", (-1, 0, 0)),
                       ("thigh.def-L", (0, 0, -1))):
        b = tp_arm.data.bones[bone]
        d = (tp_arm.matrix_world.to_3x3() @ (b.tail_local - b.head_local)).normalized()
        assert d.dot(Vector(want)) > 0.999, ("not T-posed", bone, tuple(d))
    keyed = [o for o in imp if o.type == 'MESH' and o.data.shape_keys]
    assert keyed and len(keyed[0].data.shape_keys.key_blocks) == 2, \
        "shape keys lost in the T-pose export"
    print("T-pose export verified (arms level, legs straight, shape keys kept, "
          "scene untouched)")

    print("ALL EXPORT TESTS PASS")


if __name__ == "__main__":
    headless()
