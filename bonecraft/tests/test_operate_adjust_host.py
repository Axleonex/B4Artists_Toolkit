# bonecraft/tests/test_operate_adjust_host.py
"""In-Bforartists test: act first, tune after (UI critique, 2026-10-10; Blender HIG "Operate, then Settings").

An action runs at once with the values it was last used with. Its options are the operator's own
properties, tuned afterwards in Adjust Last Operation, not settings drawn before the click. What a
button passes in (which rig, which item) is hidden there and not remembered.
"""
import bpy

import boneforge
from mech_draw_stubs import Ctx, Rec


class Shim:
    def __init__(self):
        self.layout = Rec([])


def _op_rna(idname):
    cat, name = idname.split(".", 1)
    return getattr(getattr(bpy.ops, cat), name).get_rna_type()


def _check_operator(idname, tunable, passed_in=()):
    rna = _op_rna(idname)
    cls = getattr(bpy.types, rna.identifier)
    assert {'REGISTER', 'UNDO'} <= set(cls.bl_options), (idname, "needs Adjust Last Operation", cls.bl_options)
    for name in tunable:
        prop = rna.properties[name]
        assert not prop.is_hidden, (idname, name, "an option shows in Adjust Last Operation")
        assert not prop.is_skip_save, (idname, name, "an option is remembered for the next run")
        assert prop.description, (idname, name, "an option has a tooltip")
    for name in passed_in:
        prop = rna.properties[name]
        assert prop.is_hidden and prop.is_skip_save, (idname, name, "what the button passes in is hidden, not kept")


def _sets(log):
    return {a for n, a, v in log if n == "set"}


def _quick_rig():
    _check_operator("boneforge.add_quick_rig",
                    ("fit_to_active_mesh", "parent_with_auto_weights", "generate_control_rig", "initial_pose"),
                    ("rig_op_id", "rig_label"))
    _check_operator("boneforge.fit_dropped_rig", ("fit_to_mesh", "auto_weight"))
    # the panel shows the rigs to add; it no longer asks for options first
    shim = Shim()
    panel = bpy.types.BF_PT_sb_quick_rig
    shim._draw_group = lambda *a: panel._draw_group(shim, *a)   # the Rigify rig grid draws too
    panel._draw_quick_rig(shim, bpy.context)
    log = shim.layout.log
    drawn = [a[1] for n, a, k in log if n == "prop" and len(a) == 2]
    assert not [p for p in drawn if p.startswith("boneforge_quick_rig_")], ("options drawn before the click", drawn)
    buttons = [a[0] for n, a, k in log if n == "operator"]
    assert "boneforge.add_quick_rig" in buttons, buttons
    assert not _sets(log) & {"fit_to_active_mesh", "parent_with_auto_weights", "generate_control_rig",
                             "initial_pose"}, ("a button must not override the last-used options", _sets(log))
    # the header menu's Quick Rig entries behave the same
    shim = Shim()
    bpy.types.BC_MT_add_quick_rig.draw(shim, bpy.context)
    assert not _sets(shim.layout.log) & {"fit_to_active_mesh", "parent_with_auto_weights",
                                         "generate_control_rig", "initial_pose"}, shim.layout.log


def _panel_props(idname):
    shim = Shim()
    getattr(bpy.types, idname).draw(shim, Ctx())
    return {a[1] for n, a, k in shim.layout.log if n == "prop" and len(a) == 2}


def _weights():
    _check_operator("boneforge.flood_to_custom", ("value", "normalize"))
    for idname in ("boneforge.mirror_all_weights", "boneforge.mirror_active_weight"):
        _check_operator(idname, ("axis", "direction", "search_distance"))
        assert "use_topology" not in _op_rna(idname).properties, (idname, "no option that does nothing")
    _check_operator("boneforge.transfer_weights", ("method", "bone_filter", "normalize"))
    _check_operator("boneforge.set_vertex_weight", ("weight_value",), ("vertex_index", "bone_name"))
    _check_operator("boneforge.add_vertex_influence", ("weight_value",), ("vertex_index", "bone_name"))
    # no popup before an undoable action
    for idname in ("boneforge.flood_to_one", "boneforge.set_vertex_weight"):
        cls = getattr(bpy.types, _op_rna(idname).identifier)
        assert "invoke" not in cls.__dict__, (idname, "runs at once; undo, don't ask")
    # the panels show actions, not their options
    for panel, options in (
            ("BONEFORGE_PT_p2b_flood_fill", {"boneforge_flood_custom_value", "boneforge_flood_normalize"}),
            ("BONEFORGE_PT_p2b_weight_mirror", {"boneforge_mirror_axis", "boneforge_mirror_direction",
                                                "boneforge_use_mirror_topology",
                                                "boneforge_mirror_search_distance"}),
            ("BONEFORGE_PT_p2b_weight_transfer", {"boneforge_transfer_method", "boneforge_transfer_bone_filter",
                                                  "boneforge_transfer_normalize"})):
        drawn = _panel_props(panel)
        assert not drawn & options, (panel, "options drawn before the click", drawn & options)
    # Add Influence passes the bone picked beside it (it used to pass none and always failed)
    mesh = bpy.data.meshes.new("bc_wt")
    mesh.from_pydata([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [], [(0, 1, 2)])
    obj = bpy.data.objects.new("bc_wt", mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.vertex_groups.new(name="Bone").add([0], 0.5, 'REPLACE')
    arm = bpy.data.objects.new("bc_wt_rig", bpy.data.armatures.new("bc_wt_rig"))
    bpy.context.scene.collection.objects.link(arm)
    obj.parent = arm
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    arm.data.edit_bones.new("Picked").tail = (0, 0, 1)
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = obj
    bpy.context.scene.boneforge_add_influence_bone = "Picked"
    shim = Shim()
    bpy.types.BONEFORGE_PT_p2b_weight_table._draw_single_vertex(shim, shim.layout, obj, mesh,
                                                                 mesh.vertices[0], bpy.context.scene)
    log = shim.layout.log
    at = [i for i, (n, a, k) in enumerate(log) if n == "operator" and a and a[0] == "boneforge.add_vertex_influence"]
    assert at, "the Add Influence button is drawn"
    passed = [v for n, a, v in log[at[0]:] if n == "set" and a == "bone_name"]
    assert passed == ["Picked"], ("Add passes the bone picked beside it", passed)
    bpy.data.objects.remove(obj)
    bpy.data.objects.remove(arm)


def _no_dialog(idname):
    import inspect
    cls = getattr(bpy.types, _op_rna(idname).identifier)
    invoke = cls.__dict__.get("invoke")
    if invoke is not None:
        src = inspect.getsource(invoke)
        assert "invoke_props_dialog" not in src and "invoke_confirm" not in src, (idname, "asks before it acts")


def _chain_rig(n=4):
    arm = bpy.data.objects.new("bc_chain", bpy.data.armatures.new("bc_chain"))
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode='EDIT')
    parent = None
    for i in range(n):
        b = arm.data.edit_bones.new(f"chain_{i}")
        b.head, b.tail = (0, 0, i), (0, 0, i + 1)
        b.parent, b.use_connect = parent, parent is not None
        parent = b
    bpy.ops.object.mode_set(mode='POSE')
    arm.data.bones.active = arm.data.bones["chain_0"]
    return arm


def _rig_tools():
    _check_operator("boneforge.generate_ribbon", ("control_count", "width"))
    _check_operator("boneforge.generate_spline_ik", ("chain_length", "curve_resolution", "stretch",
                                                     "volume_preservation"))
    _check_operator("boneforge.vrc_generate_hair_chains", ("density",))
    _check_operator("boneforge.pose_apply_blended", ("blend",))
    _check_operator("boneforge.corrective_edit", ("activation_angle", "falloff_range"))
    _check_operator("boneforge.preview_viseme", (), ("set_name", "viseme_name"))
    for idname in ("boneforge.vrc_generate_hair_chains", "boneforge.pose_apply_blended",
                   "boneforge.corrective_edit"):
        _no_dialog(idname)
    for panel, options in (
            ("BONEFORGE_PT_p2c_ribbon", {"boneforge_ribbon_control_count", "boneforge_ribbon_width"}),
            ("BONEFORGE_PT_p2c_spline_ik", {"boneforge_spline_chain_length", "boneforge_spline_curve_resolution",
                                            "boneforge_spline_stretch", "boneforge_spline_twist_distribution",
                                            "boneforge_spline_volume_preservation"}),
            ("BONEFORGE_PT_vrc_hair_generator", {"bf_hair_generation_density"})):
        drawn = _panel_props(panel)
        assert not drawn & options, (panel, "options drawn before the click", drawn & options)
    # Generate Spline IK runs (it used to set constraint settings that do not exist) and its options land
    arm = _chain_rig()
    assert bpy.ops.boneforge.generate_spline_ik(chain_length=3, stretch=True,
                                                volume_preservation=True) == {'FINISHED'}
    con = [c for c in arm.pose.bones["chain_2"].constraints if c.type == 'SPLINE_IK']
    assert con and con[0].chain_count == 3, [(b.name, [c.type for c in b.constraints]) for b in arm.pose.bones]
    assert con[0].y_scale_mode == 'FIT_CURVE' and con[0].xz_scale_mode == 'VOLUME_PRESERVE', \
        (con[0].y_scale_mode, con[0].xz_scale_mode)
    bpy.ops.object.mode_set(mode='OBJECT')
    # asked for more bones than the chain has: the constraint spans the bones that exist
    arm = _chain_rig(3)
    assert bpy.ops.boneforge.generate_spline_ik(chain_length=10) == {'FINISHED'}
    con = [c for c in arm.pose.bones["chain_2"].constraints if c.type == 'SPLINE_IK']
    assert con and con[0].chain_count == 3, [c.chain_count for c in con]
    bpy.ops.object.mode_set(mode='OBJECT')
    # each viseme preview button says which set it previews (it used to pass none: always empty)
    import json
    arm["boneforge_p2c_visemes"] = json.dumps({"sets": {"Main": {}}})
    bpy.context.view_layer.objects.active = arm
    shim = Shim()
    bpy.types.BONEFORGE_PT_p2c_viseme_library.draw(shim, Ctx())
    log = shim.layout.log
    starts = [i for i, (n, a, k) in enumerate(log) if n == "operator" and a and a[0] == "boneforge.preview_viseme"]
    assert starts, "the preview buttons are drawn"
    for i in starts:
        nxt = next((j for j in range(i + 1, len(log)) if log[j][0] != "set"), len(log))
        sets = {a: v for n, a, v in log[i + 1:nxt]}
        assert sets.get("set_name") == "Main" and sets.get("viseme_name"), ("button passes its set", sets)


def _mannequin():
    _check_operator("boneforge.add_mannequin", ("replace_existing",))
    _no_dialog("boneforge.add_mannequin")


def _cats():
    _check_operator("boneforge.cats_create_bone_root", ("root_name",))
    _check_operator("boneforge.cats_merge_bones", ("threshold",))
    drawn = _panel_props("CATS_PT_bone_tools")
    assert not drawn & {"root_bone_name", "merge_threshold"}, ("options drawn before the click", drawn)
    # both run with their own options
    arm = _chain_rig(3)
    bpy.ops.object.mode_set(mode='OBJECT')
    assert bpy.ops.boneforge.cats_create_bone_root(root_name="BC Root") == {'FINISHED'}
    from boneforge.core.armature import active_armature
    target = active_armature(bpy.context)                 # CATS works on its picked armature
    assert target is not None and "BC Root" in target.data.bones, [b.name for b in target.data.bones]
    assert bpy.context.mode == 'OBJECT'
    assert bpy.ops.boneforge.cats_merge_bones(threshold=0.5) in ({'FINISHED'}, {'CANCELLED'})


def run():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    boneforge.register()
    try:
        _quick_rig()
        _weights()
        _rig_tools()
        _cats()
        _mannequin()
    finally:
        boneforge.unregister()
    print("PASS operate, then adjust: options are the operator's, tuned after the click")
