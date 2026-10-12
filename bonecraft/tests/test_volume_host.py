"""In-Bforartists behavioural test: joint volume options actually work.

* Preserve Volume (dual-quaternion skinning): a 110 degree elbow bend loses
  far less arm volume than plain skinning (measured on the same rig).
* The Bind Delta Mush button really binds the Corrective Smooth modifier —
  it used to only set a flag, leaving the modifier unbound (no effect).
"""
import math

import bmesh
import bpy

import test_rig_integrate_host as rih
from boneforge.autorig.rig_build import build_control_rig

ARM_VOLUME = 0.54 * 0.10 * 0.10     # the test figure's box arm


def _volume(ob):
    bm = bmesh.new()
    bm.from_object(ob, bpy.context.evaluated_depsgraph_get())
    bm.transform(ob.matrix_world)
    v = bm.calc_volume(signed=False)
    bm.free()
    return v


def _elbow_loss(mesh, arm):
    pb = arm.pose.bones
    pb["properties"]["IK_FK-arm-L"] = 0.0
    arm.update_tag(); bpy.context.view_layer.update()
    v0 = _volume(mesh)
    fore = pb["forearm.fk-L"]
    fore.rotation_mode = 'XYZ'
    fore.rotation_euler = (0.0, 0.0, math.radians(110.0))
    bpy.context.view_layer.update()
    v1 = _volume(mesh)
    fore.rotation_euler = (0.0, 0.0, 0.0)
    bpy.context.view_layer.update()
    return (v0 - v1) / ARM_VOLUME * 100


def run():
    mesh, _labels, arm = rih.build_skinned_rig()
    build_control_rig(arm, context=bpy.context)
    amod = next(m for m in mesh.modifiers if m.type == 'ARMATURE')
    plain = _elbow_loss(mesh, arm)
    amod.use_deform_preserve_volume = True
    kept = _elbow_loss(mesh, arm)
    amod.use_deform_preserve_volume = False
    assert plain > 3.0, ("baseline shows no joint collapse to fix", plain)
    assert kept < plain * 0.3, ("preserve volume did not help", plain, kept)

    bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True)
    bpy.context.view_layer.objects.active = mesh
    assert bpy.ops.boneforge.add_delta_mush() == {'FINISHED'}
    mod = mesh.modifiers["DeltaMush"]
    assert not mod.is_bind
    assert bpy.ops.boneforge.bind_delta_mush() == {'FINISHED'}
    assert mod.is_bind, "Bind Delta Mush did not bind"
    assert bpy.ops.boneforge.bind_delta_mush() == {'FINISHED'} and mod.is_bind, "rebind lost the bind"
    print("volume verified (elbow loss %.1f%% plain -> %.1f%% preserved; delta mush binds)" % (plain, kept))
    bpy.data.objects.remove(mesh, do_unlink=True)
    bpy.data.objects.remove(arm, do_unlink=True)
    print("ALL VOLUME TESTS PASS")


if __name__ == "__main__":
    run()
