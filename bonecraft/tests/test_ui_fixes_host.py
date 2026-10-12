"""In-Bforartists behavioural test: UI defects found while writing the manual.

* Shape Library panel draws (its draw raised NameError: T was never imported).
* A VRChat viseme slot button opens a shape-key search (it had no picker, so
  a click ran execute with no shape key and cleared the slot).
* The Control Picker panel offers Mirror Selection and the pop-up picker
  (both were reachable from nowhere).
* Attach Clothing's steps leave the base armature active, as Merge Clothing
  needs (they had the user select it first, which makes the clothing active).
"""
import bpy

import boneforge
from mech_draw_stubs import Rec


def _draw(panel_cls, context=None):
    log = []
    panel_cls.draw(type("P", (), {"layout": Rec(log)})(), context or bpy.context)
    return log


def _ops(log):
    return [a[0] for name, a, k in log if name == "operator"]


def _labels(log):
    return [k.get("text", "") for name, a, k in log if name == "label"]


def _armature_with_mesh():
    arm = bpy.data.objects.new("VisemeRig", bpy.data.armatures.new("VisemeRig"))
    bpy.context.scene.collection.objects.link(arm)
    me = bpy.data.meshes.new("VisemeHead")
    me.from_pydata([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [], [(0, 1, 2)])
    mesh = bpy.data.objects.new("VisemeHead", me)
    bpy.context.scene.collection.objects.link(mesh)
    mesh.parent = arm
    mesh.shape_key_add(name="Basis")
    mesh.shape_key_add(name="mouth_a")
    mesh.shape_key_add(name="mouth_o")
    bpy.context.view_layer.objects.active = arm
    # the add-on's target armature wins over the active object; an earlier
    # suite may have left one set, so point it at this rig
    scene = bpy.context.scene
    if hasattr(scene, "boneforge_cats_target_armature_name"):
        scene.boneforge_cats_target_armature_name = arm.name
    if hasattr(scene, "boneforge_cats_target_armature"):
        scene.boneforge_cats_target_armature = arm
    return arm


def run():
    try:
        boneforge.register()
    except Exception as exc:  # already registered by an earlier suite
        print("register note:", exc)

    # Shape Library
    from boneforge.weights import shapes
    log = _draw(shapes.BONEFORGE_PT_p2b_shape_library)
    assert "Control Shapes:" in _labels(log), _labels(log)

    # viseme slot picker
    from boneforge.vrchat.visemes import vrchat_mapper as vm
    op_cls = vm.BF_OT_VRC_MapSingleViseme
    assert hasattr(op_cls, "invoke"), "slot button has no picker"
    assert getattr(op_cls, "bl_property", None) == "shape_key_choice"
    arm = _armature_with_mesh()
    ids = [i[0] for i in vm._shape_key_items(None, bpy.context)]
    assert "mouth_a" in ids and "mouth_o" in ids and vm.CLEAR_SLOT in ids, ids
    assert bpy.ops.boneforge.vrc_map_single_viseme(viseme_name="aa", shape_key_choice="mouth_a") == {'FINISHED'}
    assert vm.get_viseme_mapping(arm).get("aa") == "mouth_a", (vm.get_viseme_mapping(arm), bpy.context.active_object, [o.name for o in arm.children])
    assert bpy.ops.boneforge.vrc_map_single_viseme(viseme_name="aa", shape_key_choice=vm.CLEAR_SLOT) == {'FINISHED'}
    assert "aa" not in vm.get_viseme_mapping(arm)
    # scripts that pass a name keep working
    assert bpy.ops.boneforge.vrc_map_single_viseme(viseme_name="O", shape_key_name="mouth_o") == {'FINISHED'}
    assert vm.get_viseme_mapping(arm).get("O") == "mouth_o"
    # no slot name (F3 search) maps nothing
    try:                       # an ERROR report raises in background mode
        result = bpy.ops.boneforge.vrc_map_single_viseme(shape_key_name="mouth_o")
    except RuntimeError as exc:
        result = {'CANCELLED'} if "Not a VRChat viseme slot" in str(exc) else exc
    assert result == {'CANCELLED'}, result
    assert "" not in vm.get_viseme_mapping(arm)

    # face control shapes are created (hide_set on an unlinked object raised,
    # so every face bone fell back to the default shape)
    from boneforge.autorig import face_gen
    shapes = face_gen._create_face_bone_shapes()
    assert shapes, "no face control shapes"
    for ob in shapes.values():
        assert ob.hide_render
        bpy.data.objects.remove(ob)

    # Control Picker panel
    from boneforge.control_ui import picker
    arm.data.collections.new("Controls")
    picker.ensure_layout(arm)
    ops = _ops(_draw(picker.BONEFORGE_PT_picker))
    assert "boneforge.picker_mirror_selection" in ops, ops
    assert "boneforge.picker_popup" in ops, ops

    # Attach Clothing steps: base armature selected last (active)
    from boneforge.vrchat.clothing import merge
    labels = _labels(_draw(merge.BONEFORGE_PT_vrc_clothing_merge))
    steps = [t for t in labels if t[:2] in ("1.", "2.", "3.")]
    assert len(steps) == 3, labels
    assert "clothing" in steps[0].lower() and "base" not in steps[0].lower(), steps
    assert "base" in steps[1].lower() and "active" in steps[1].lower(), steps
    assert "Merge Clothing" in steps[2], steps
    print("PASS UI fixes: Shape Library, viseme picker, picker buttons, clothing steps")
