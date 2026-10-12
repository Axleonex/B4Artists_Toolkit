"""In-Bforartists behavioural test: bend-driven corrective shape keys.

On an integrated rig, ``generate_joint_corrective`` builds an elbow key.
Measured independently of the generator:
* at rest the key is 0 and the mesh does not move (<= 0.1 mm),
* at a 110 degree bend the arm keeps its volume (loss <= 1.5% of the arm,
  against the plain-skinning baseline measured first),
* the key ramps 0 -> ~0.5 -> 1 at 0 / 55 / 110 degrees,
* a game-profile export keeps the shape key.
"""
import math
import os
import tempfile

import bmesh
import bpy

import test_rig_integrate_host as rih
from boneforge.autorig.rig_build import build_control_rig
from boneforge.autorig import joint_correctives as jc

ARM_VOLUME = 0.54 * 0.10 * 0.10


def _vol(ob):
    bm = bmesh.new()
    bm.from_object(ob, bpy.context.evaluated_depsgraph_get())
    bm.transform(ob.matrix_world)
    v = bm.calc_volume(signed=False)
    bm.free()
    return v


def _positions(ob):
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices
    return [ob.matrix_world @ v.co for v in ev]


def run():
    mesh, _labels, arm = rih.build_skinned_rig()
    build_control_rig(arm, context=bpy.context)
    pb = arm.pose.bones
    pb["properties"]["IK_FK-arm-L"] = 0.0
    arm.update_tag(); bpy.context.view_layer.update()
    rest_plain = _positions(mesh)

    name, info = jc.generate_joint_corrective(mesh, arm, "elbow", "L")
    assert name, info
    key = mesh.data.shape_keys.key_blocks[name]
    sign = info["bend_sign"]
    fore = pb["forearm.fk-L"]
    fore.rotation_mode = 'XYZ'

    def bend(deg):
        fore.rotation_euler = (sign * math.radians(deg), 0.0, 0.0)
        bpy.context.scene.frame_set(bpy.context.scene.frame_current)
        bpy.context.view_layer.update()

    bend(0)
    shift = max((a - b).length for a, b in zip(rest_plain, _positions(mesh)))
    assert key.value < 1e-6 and shift <= 1e-4, ("corrective changes the rest pose", key.value, shift)

    # baseline without the key, then with it (driver on)
    v0 = _vol(mesh)
    key.mute = True
    bend(110)
    loss_plain = (v0 - _vol(mesh)) / ARM_VOLUME * 100
    key.mute = False
    bend(110)
    loss_fixed = (v0 - _vol(mesh)) / ARM_VOLUME * 100
    assert loss_plain > 3.0, ("no collapse to correct", loss_plain)
    assert loss_fixed <= 1.5, ("corrective did not keep the volume", loss_plain, loss_fixed)

    # the local cross-section fix alone (what open, multi-piece avatars get)
    # must still recover a good share of the collapse
    bend(0)
    name2, info2 = jc.generate_joint_corrective(mesh, arm, "elbow", "L", volume_match=False)
    bend(110)
    loss_local = (v0 - _vol(mesh)) / ARM_VOLUME * 100
    assert loss_local <= loss_plain * 0.6, ("local fix too weak", loss_plain, loss_local)
    bend(0)
    name, info = jc.generate_joint_corrective(mesh, arm, "elbow", "L")   # back to volume-matched
    key = mesh.data.shape_keys.key_blocks[name]

    ramp = []
    for deg in (0, 55, 110):
        bend(deg)
        ramp.append(key.value)
    assert ramp[0] < 0.05 and 0.3 < ramp[1] < 0.7 and ramp[2] > 0.95, ("driver ramp", ramp)
    bend(0)

    path = os.path.join(tempfile.gettempdir(), "bf_corrective_export.fbx")
    bpy.ops.object.select_all(action='DESELECT')
    arm.select_set(True); mesh.select_set(True)
    bpy.context.view_layer.objects.active = arm
    assert bpy.ops.boneforge.profile_export(filepath=path, profile_id="vrchat",
                                            action_mode='NONE') == {'FINISHED'}
    before = set(bpy.data.objects)
    bpy.ops.import_scene.fbx(filepath=path)
    new_mesh = [o for o in bpy.data.objects if o not in before and o.type == 'MESH']
    keys = new_mesh[0].data.shape_keys.key_blocks.keys() if new_mesh and new_mesh[0].data.shape_keys else []
    assert name in keys, ("export dropped the corrective key", keys)
    for o in [o for o in bpy.data.objects if o not in before]:
        bpy.data.objects.remove(o, do_unlink=True)
    try:
        os.remove(path)
    except OSError:
        pass
    print("correctives verified (elbow loss %.1f%% -> %.1f%% volume-matched, %.1f%% local-only; "
          "rest shift %.1e m, ramp %s, kept on export)"
          % (loss_plain, loss_fixed, loss_local, shift, [round(r, 2) for r in ramp]))
    bpy.data.objects.remove(mesh, do_unlink=True)
    bpy.data.objects.remove(arm, do_unlink=True)
    print("ALL CORRECTIVE TESTS PASS")


if __name__ == "__main__":
    run()
