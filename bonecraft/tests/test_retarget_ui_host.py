"""In-Bforartists behavioural test: the retarget panel's own buttons.

A motion-capture-style source skeleton (``UpperArm_L`` naming, every bone
resting sideways like many BVH exports) is registered as a clip. Then:

* Auto-Match maps it onto the control rig's FK controls via a bone-map preset;
* Apply produces a new action in which the rig's arm points where the source
  arm points (direction-matched — exact although the rests differ);
* negative control: with the clip's skeleton gone (an actions-only clip) the
  panel falls back to the older rest-pose method instead of the new path.
"""
import math

import bpy

import test_rig_integrate_host as rih
from boneforge.autorig.rig_build import build_control_rig
from boneforge.autorig import retarget as rt

BONES = [  # name, parent, head  (every bone points +X at rest: an odd "zero pose")
    ("Hips", None, (0, 0, 1.0)), ("Spine", "Hips", (0, 0, 1.1)),
    ("Chest", "Spine", (0, 0, 1.25)), ("Neck", "Chest", (0, 0, 1.45)),
    ("Head", "Neck", (0, 0, 1.55)),
]
for s, sx in (("L", 1), ("R", -1)):
    BONES += [(f"Shoulder_{s}", "Chest", (sx * 0.05, 0, 1.42)),
              (f"UpperArm_{s}", f"Shoulder_{s}", (sx * 0.18, 0, 1.42)),
              (f"LowerArm_{s}", f"UpperArm_{s}", (sx * 0.45, 0, 1.42)),
              (f"Hand_{s}", f"LowerArm_{s}", (sx * 0.70, 0, 1.42)),
              (f"UpperLeg_{s}", "Hips", (sx * 0.1, 0, 0.95)),
              (f"LowerLeg_{s}", f"UpperLeg_{s}", (sx * 0.1, 0, 0.52)),
              (f"Foot_{s}", f"LowerLeg_{s}", (sx * 0.1, 0, 0.1))]


def _source():
    bpy.ops.object.mode_set(mode='OBJECT') if bpy.context.object and bpy.context.object.mode != 'OBJECT' else None
    data = bpy.data.armatures.new("MOCAP_SRC")
    ob = bpy.data.objects.new("MOCAP_SRC", data)
    bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT')
    for name, parent, head in BONES:
        eb = data.edit_bones.new(name)
        eb.head = head
        eb.tail = (head[0] + 0.08, head[1], head[2])      # sideways rest
        if parent:
            eb.parent = data.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT')
    ob.animation_data_create()
    ob.animation_data.action = bpy.data.actions.new("MOCAP_CLIP")
    scene = bpy.context.scene
    for f, deg in ((1, 0.0), (10, -70.0)):
        scene.frame_set(f)
        pb = ob.pose.bones["UpperArm_L"]
        pb.rotation_mode = 'XYZ'
        pb.rotation_euler = (math.radians(deg), 0.0, 0.0)   # swing, not twist
        pb.keyframe_insert("rotation_euler", frame=f)
        for n in [b[0] for b in BONES if b[0] != "UpperArm_L"]:
            ob.pose.bones[n].keyframe_insert("rotation_quaternion", frame=f)
    return ob


def _dir(ob, bone, frame):
    bpy.context.scene.frame_set(frame)
    ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    pb = ev.pose.bones[bone]
    return ((ob.matrix_world @ pb.tail) - (ob.matrix_world @ pb.head)).normalized()


def run():
    mesh, _labels, target = rih.build_skinned_rig()
    build_control_rig(target, context=bpy.context)
    src = _source()
    settings = bpy.context.scene.boneforge_retarget_settings
    clip = settings.clips.add()
    clip.clip_name, clip.action_name = "mocap", src.animation_data.action.name
    settings.active_clip_index = len(settings.clips) - 1

    bpy.ops.object.select_all(action='DESELECT')
    target.select_set(True)
    bpy.context.view_layer.objects.active = target
    # the panel acts on the scene's chosen target rig when one is set
    bpy.context.scene.boneforge_cats_target_armature_name = target.name
    assert bpy.ops.boneforge.retarget_auto_match() == {'FINISHED'}
    session = bpy.context.scene.boneforge_autorig_session
    preset = {m.source_name: m.target_name for m in session.retarget_mappings
              if m.is_matched and m.match_type == 'PRESET'}
    assert len(preset) >= 6 and preset.get("UpperArm_L") == "upperarm.fk-L", preset

    before = set(bpy.data.actions)
    assert bpy.ops.boneforge.retarget_apply() == {'FINISHED'}
    new = [a for a in bpy.data.actions if a not in before]
    assert new and target.animation_data.action in new, "Apply did not assign a new action"
    ang = math.degrees(_dir(src, "UpperArm_L", 10).angle(_dir(target, "upperarm.fk-L", 10)))
    assert ang < 3.0, ("applied arm does not point where the source arm points", ang)
    # the source arm really moved (so the check above is not trivially true)
    swing = math.degrees(_dir(src, "UpperArm_L", 1).angle(_dir(src, "UpperArm_L", 10)))
    assert swing > 45.0, swing

    # negative control: actions-only clip -> older path, not the new one
    target.animation_data.action = None
    src.animation_data.action = None
    assert rt._source_armature_for_action(bpy.data.actions[clip.action_name]) is None
    print("retarget panel verified (auto-match %d PRESET, Apply direction error %.2f deg; "
          "actions-only clip falls back)" % (len(preset), ang))
    for ob in (src, mesh, target):
        bpy.data.objects.remove(ob, do_unlink=True)
    print("ALL RETARGET-PANEL TESTS PASS")


if __name__ == "__main__":
    run()
