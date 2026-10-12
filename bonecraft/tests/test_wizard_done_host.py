"""In-Bforartists behavioural test: the Auto-Rig wizard's Done step.

* Close Wizard after a successful Generate Rig keeps everything the rig
  generated (face_gen logs its control-shape objects in the change log
  that Cancel rolls back; closing used to delete them).
* Cancel before generating still reverts what the wizard created.
* The Done step offers Build Control Rig, which builds the engine control
  rig on the generated armature while the review-step options still exist,
  and is not offered again once the control rig is built.
"""
import bpy

import test_rig_integrate_host as rih
from mech_draw_stubs import Rec
from boneforge.autorig import wizard
from boneforge.autorig import rig_integrate
from boneforge.autorig.session import log_scene_change


def _shape(name):
    ob = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(ob)
    return ob.name


def _done_ops(session):
    log = []
    wizard.BF_PT_WizardPanel._draw_step_done(None, Rec(log), bpy.context, session)
    return [a[0] for name, a, k in log if name == "operator"]


def run():
    mesh, _labels, arm = rih.build_skinned_rig()
    s = bpy.context.scene.boneforge_autorig_session
    assert s.wizard_step == wizard.STEP_DONE, s.wizard_step

    # a successful generate leaves nothing to roll back, and the Done step
    # offers no way back into the generate step or a Cancel that reverts
    import json
    assert json.loads(s.snapshot_blend_data or "{}").get('objects_created', []) == [], s.snapshot_blend_data
    assert not bpy.ops.boneforge.autorig_wizard_back.poll(), "Back offered on the Done step"
    log = []
    wizard.BF_PT_WizardPanel.draw(type("P", (), {"layout": Rec(log)})(), bpy.context)
    drawn = [a[0] for name, a, k in log if name == "operator"]
    assert "boneforge.autorig_wizard_back" not in drawn, drawn
    assert drawn.count("boneforge.autorig_wizard_cancel") == 1, drawn
    tip = wizard.BF_OT_WizardCancel.description(bpy.context, None)
    assert "keep" in tip.lower() and "revert" not in tip.lower(), tip

    # a generated object logged the way face_gen logs its control shapes
    kept = _shape("BF_TestFaceShape")
    log_scene_change(s, 'objects_created', kept)

    ops = _done_ops(s)
    assert "boneforge.autorig_build_control_rig" in ops, ops
    assert ops.index("boneforge.autorig_build_control_rig") < ops.index("boneforge.autorig_wizard_cancel"), ops

    s.twist_bones = True
    s.twist_segments = 2
    assert bpy.ops.boneforge.autorig_build_control_rig() == {'FINISHED'}
    names = {b.name for b in arm.data.bones}
    assert not rig_integrate.is_wizard_skeleton(names), "control rig not built"
    assert any("twist" in n for n in names), "Twist Bones option not applied"
    assert not bpy.ops.boneforge.autorig_build_control_rig.poll(), "offered twice"

    assert bpy.ops.boneforge.autorig_wizard_cancel() == {'FINISHED'}
    assert kept in bpy.data.objects, "Close Wizard deleted a generated object"
    assert arm.name in bpy.data.objects, "Close Wizard deleted the rig"
    assert any(m.type == 'ARMATURE' and m.object == arm for m in mesh.modifiers)
    assert not s.is_active

    # cancelling an unfinished wizard still reverts its changes
    bpy.context.view_layer.objects.active = mesh
    bpy.ops.boneforge.autorig_wizard_start()
    gone = _shape("BF_TestUnfinished")
    log_scene_change(s, 'objects_created', gone)
    assert bpy.ops.boneforge.autorig_wizard_cancel() == {'FINISHED'}
    assert gone not in bpy.data.objects, "Cancel kept an unfinished wizard's object"
    print("PASS wizard Done step: Close keeps the result, Build Control Rig offered once")
