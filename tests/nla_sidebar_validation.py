"""Focused native-host checks. Run inside an isolated Bforartists process."""
import bpy
import importlib
import json
import math
from pathlib import Path


def run(package="B4_anim_assist", output=None):
    nc = importlib.import_module(f"{package}.core.nla_context")
    cu = importlib.import_module(f"{package}.core.context_utils")
    area = max(bpy.context.window.screen.areas, key=lambda a: a.width * a.height)
    area.type = "NLA_EDITOR"
    scene = bpy.context.scene
    scene.frame_start, scene.frame_end = 1, 20
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for action in list(bpy.data.actions):
        bpy.data.actions.remove(action)
    results = []

    def check(name, fn):
        try:
            fn()
            results.append(dict(name=name, passed=True))
        except Exception:
            import traceback
            results.append(dict(name=name, passed=False, error=traceback.format_exc()))
        if output:
            Path(output).write_text(json.dumps(results, indent=2))

    def expect(value, message):
        assert value, message

    def fixture(name, rotation="XYZ", parent=None):
        obj = bpy.data.objects.new(name, None)
        scene.collection.objects.link(obj)
        obj.rotation_mode = rotation
        obj.parent = parent
        for frame, x in ((1, 2), (20, 7)):
            obj.location.x = x
            obj.scale = (1.2, .8, 1.5)
            obj.keyframe_insert("location", frame=frame)
            obj.keyframe_insert("scale", frame=frame)
            path = "rotation_quaternion" if rotation == "QUATERNION" else "rotation_euler"
            if rotation == "QUATERNION":
                from mathutils import Quaternion
                obj.rotation_quaternion = Quaternion((0, 0, 1), x / 10)
            else:
                obj.rotation_euler.z = x / 10
            obj.keyframe_insert(path, frame=frame)
        ad = obj.animation_data
        action, slot = ad.action, ad.action_slot
        ad.action = None
        track = ad.nla_tracks.new()
        strip = track.strips.new(name, 1, action)
        strip.action_slot = slot
        strip.extrapolation = "NOTHING"
        return obj, track, strip

    def override(obj, strip, selected=None):
        bpy.context.view_layer.objects.active = obj
        for other in bpy.context.selected_objects:
            other.select_set(False)
        obj.select_set(True)
        obj.animation_data.nla_tracks.active = next(t for t in obj.animation_data.nla_tracks if strip in list(t.strips))
        return bpy.context.temp_override(area=area, region=next(r for r in area.regions if r.type == "WINDOW"),
            active_nla_strip=strip, selected_nla_strips=selected if selected is not None else [strip])

    def matrices(obj, frames=(1, 5, 10, 20)):
        result = []
        for frame in frames:
            scene.frame_set(frame)
            bpy.context.view_layer.update()
            evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
            result.append([tuple(v for row in evaluated.matrix_world for v in row),
                           *([tuple(v for row in b.matrix for v in row) for b in evaluated.pose.bones] if evaluated.pose else [])])
        return result

    def close(a, b):
        return all(abs(x-y) < 2e-4 for fa, fb in zip(a, b) for ma, mb in zip(fa, fb) for x, y in zip(ma, mb))

    obj, track, strip = fixture("NLA Walk")
    obj2, track2, strip2 = fixture("NLA Run")
    before_keys = [(fc.data_path, tuple(tuple(k.co) for k in fc.keyframe_points)) for fc in nc.strip_curves(strip)]

    def timing():
        with override(obj, strip, [strip, strip2]):
            expect(bpy.ops.animassist.nla_time(operation="NUDGE", frames=3) == {"FINISHED"}, "Nudge failed")
            expect(strip.frame_start == 4 and strip2.frame_start == 4, "Multi-owner nudge scope")
            expect(strip.frame_end == 23 and strip2.frame_end == 23, "Duration changed")
            expect(bpy.ops.animassist.nla_time(operation="SEQUENCE", gap=2) == {"FINISHED"}, "Sequence failed")
            expect(sorted([strip.frame_start, strip2.frame_start]) == [4, 25], "Sequence order/gap")
            expect(bpy.ops.animassist.nla_time(operation="END") == {"FINISHED"}, "Align ends failed")
            expect(strip.frame_end == strip2.frame_end, "Align target")
            track2.lock = True
            old = (strip.frame_start, strip2.frame_start)
            expect(bpy.ops.animassist.nla_time(operation="NUDGE", frames=9) == {"CANCELLED"}, "Locked batch accepted")
            expect(old == (strip.frame_start, strip2.frame_start), "Partial locked batch")
            track2.lock = False
            bpy.ops.animassist.nla_time(operation="NUDGE", frames=-3)
        expect(before_keys == [(fc.data_path, tuple(tuple(k.co) for k in fc.keyframe_points)) for fc in nc.strip_curves(strip)], "Source keys changed")
    check("timing: multi-owner, sequence, alignment, locked atomicity, source preservation", timing)

    def collision():
        second = track.strips.new("Neighbor", 100, strip.action)
        second.action_slot = strip.action_slot
        old = (strip.frame_start, second.frame_start)
        with override(obj, strip, [strip, second]):
            expect(bpy.ops.animassist.nla_time(operation="START") == {"CANCELLED"}, "Overlap accepted")
            expect(old == (strip.frame_start, second.frame_start), "Partial overlap mutation")
        track.strips.remove(second)
        with override(obj, strip, []):
            expect(bpy.ops.animassist.nla_time(operation="NUDGE") == {"CANCELLED"}, "Empty selected-strip fallback")
    check("timing: overlap and empty selection reject without mutation", collision)

    def unique():
        second = track2.strips.new("Linked", 50, strip.action)
        second.action_slot = strip.action_slot
        source = strip.action
        expect(nc.source_references(source) >= 2, "Missing shared reference")
        with override(obj2, second):
            expect(bpy.ops.animassist.nla_unique() == {"FINISHED"}, "Make Unique failed")
        expect(second.action != source and strip.action == source, "Sources still shared")
        expect(len(nc.strip_curves(second)) == len(nc.strip_curves(strip)), "Slot lost")
        track2.strips.remove(second)
    check("shared Actions: Make Unique preserves the assigned slot", unique)

    def correction(rotation):
        owner, _t, source = fixture(f"Correction {rotation}", rotation)
        baseline = matrices(owner)
        with override(owner, source):
            expect(bpy.ops.animassist.nla_correction() == {"FINISHED"}, "Correction creation failed")
        correction_strip = owner.animation_data.nla_tracks[-1].strips[0]
        expect(correction_strip.blend_type == "COMBINE", "Wrong blend mode")
        expect(close(baseline, matrices(owner)), "Neutral correction changed motion")
        fc = next(fc for fc in nc.strip_curves(correction_strip) if fc.data_path == "location" and fc.array_index == 0)
        for key in fc.keyframe_points:
            key.co.y = 2
        fc.update()
        correction_strip.action.update_tag()
        shifted = matrices(owner)
        expect(not close(baseline, shifted), "Authored correction did not affect motion")
        expect(abs(shifted[2][0][3] - baseline[2][0][3] - 2) < 2e-4, "Authored location delta incorrect")
        from mathutils import Euler, Matrix, Quaternion, Vector
        rotation_path = "rotation_quaternion" if rotation == "QUATERNION" else "rotation_euler"
        delta_rotation = Quaternion((1, 0, 0), .3) if rotation == "QUATERNION" else Euler((.3, 0, 0))
        for curve in nc.strip_curves(correction_strip):
            if curve.data_path == rotation_path:
                for key in curve.keyframe_points:
                    key.co.y = delta_rotation[curve.array_index]
                curve.update()
            if curve.data_path == "scale" and curve.array_index == 0:
                for key in curve.keyframe_points:
                    key.co.y = 2
                curve.update()
        correction_strip.action.update_tag()
        authored = matrices(owner)
        for initial, actual in zip(baseline, authored):
            original = Matrix([initial[0][i:i+4] for i in range(0, 16, 4)])
            location, rotation_value, scale = original.decompose()
            location.x += 2
            if rotation == "QUATERNION":
                rotation_value = rotation_value @ delta_rotation
            else:
                euler = rotation_value.to_euler("XYZ")
                euler.x += .3
                rotation_value = euler.to_quaternion()
            scale.x *= 2
            expected = Matrix.LocRotScale(location, rotation_value, scale)
            expect(all(abs(x-y) < 3e-4 for row, index in zip(expected, range(0,16,4))
                       for x,y in zip(row, actual[0][index:index+4])), "Authored rotation/scale correction differs from transform composition")
        with override(owner, correction_strip):
            expect(bpy.ops.animassist.nla_influence(value=0) == {"FINISHED"}, "Influence key failed")
        expect(close(baseline, matrices(owner)), "Zero influence did not restore base")
        with override(owner, correction_strip):
            bpy.ops.animassist.nla_influence(value=1)
    check("correction: neutral, authored delta, zero influence (Euler)", lambda: correction("XYZ"))
    check("correction: neutral, authored delta, zero influence (quaternion)", lambda: correction("QUATERNION"))

    def constraints():
        owner, t, source = fixture("Constrained")
        owner.constraints.new("LIMIT_LOCATION")
        count = (len(owner.animation_data.nla_tracks), len(bpy.data.actions))
        with override(owner, source):
            expect(bpy.ops.animassist.nla_correction() == {"CANCELLED"}, "Unsupported constraints accepted")
        expect(count == (len(owner.animation_data.nla_tracks), len(bpy.data.actions)), "Failed correction left data")
    check("correction: constrained owner blocked without creating data", constraints)

    def pose_correction():
        arm = bpy.data.armatures.new("Correction Rig")
        rig = bpy.data.objects.new("Correction Rig", arm)
        scene.collection.objects.link(rig)
        bpy.context.view_layer.objects.active = rig
        rig.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        bone = arm.edit_bones.new("Control")
        bone.head, bone.tail = (0,0,0), (0,0,1)
        bpy.ops.object.mode_set(mode="OBJECT")
        pb = rig.pose.bones["Control"]
        pb.rotation_mode = "QUATERNION"
        for frame, value in ((1, .2), (20, 1.1)):
            pb.location.x = value
            pb.rotation_quaternion = __import__('mathutils').Quaternion((0, 0, 1), value)
            pb.scale = (1.1, .9, 1.2)
            for path in ("location", "rotation_quaternion", "scale"):
                pb.keyframe_insert(path, frame=frame)
        ad = rig.animation_data
        action, slot = ad.action, ad.action_slot
        ad.action = None
        track = ad.nla_tracks.new()
        source = track.strips.new("Rig Motion", 1, action)
        source.action_slot = slot
        baseline = matrices(rig)
        with override(rig, source):
            expect(bpy.ops.animassist.nla_correction() == {"FINISHED"}, "Pose correction rejected")
        expect(close(baseline, matrices(rig)), "Neutral pose correction changed motion")
        correction_strip = ad.nla_tracks[-1].strips[0]
        fc = next(f for f in nc.strip_curves(correction_strip) if f.data_path.endswith(".location") and f.array_index == 0)
        for key in fc.keyframe_points:
            key.co.y = .5
        fc.update()
        correction_strip.action.update_tag()
        expect(not close(baseline, matrices(rig)), "Pose correction has no evaluated contribution")
        with override(rig, correction_strip):
            expect(bpy.ops.animassist.nla_influence(value=0) == {"FINISHED"}, "Pose influence key failed")
        expect(close(baseline, matrices(rig)), "Pose zero weight changed base")
    check("correction: quaternion pose-bone neutral, authored offset and zero weight", pose_correction)

    def bake():
        owner, t, source = fixture("Bake Target", "QUATERNION")
        baseline = matrices(owner)
        tracks = tuple(owner.animation_data.nla_tracks)
        action = source.action
        slot = source.action_slot
        frame = scene.frame_current
        with override(owner, source):
            expect(bpy.ops.animassist.nla_bake(start=1, end=20, step=1) == {"FINISHED"}, "Bake failed")
        ad = owner.animation_data
        expect(ad.action is None and tuple(ad.nla_tracks) == tracks and source.action == action and source.action_slot == slot, "Source assignment/stack changed")
        expect(scene.frame_current == frame, "Frame not restored")
        output_action = next(a for a in bpy.data.actions if a.get("animassist_nla_bake_owner") == owner.name)
        expect(output_action.use_fake_user and output_action.users == 1, "Output not retained/unassigned")
        expect(close(baseline, matrices(owner)), "Source motion changed after bake")
        owner.name = "Renamed Bake Target"
        expect(nc.latest_bake(owner) == output_action, "Bake ownership lost on rename")
        impostor = bpy.data.objects.new("Bake Target", None)
        scene.collection.objects.link(impostor)
        expect(nc.latest_bake(impostor) is None, "Old name received another owner's bake")
        with override(owner, source):
            expect(bpy.ops.animassist.nla_activate_bake() == {"FINISHED"}, "Activation failed")
        expect(ad.action == output_action and not ad.use_nla, "Bake double-evaluates stack")
        expect(close(baseline, matrices(owner)), "Baked motion differs from evaluated source")
    check("bake: retained output, preserved stack, activation and evaluated motion", bake)

    def invalid_bake():
        owner, t, source = fixture("Invalid Bake")
        with override(owner, source):
            expect(bpy.ops.animassist.nla_bake(start=1, end=2) == {"FINISHED"}, "Fixture bake failed")
            output_action = nc.latest_bake(owner)
            for slot in list(output_action.slots):
                output_action.slots.remove(slot)
            expect(bpy.ops.animassist.nla_activate_bake() == {"CANCELLED"}, "Invalid bake slot accepted")
            expect(owner.animation_data.action is None and owner.animation_data.use_nla, "Invalid bake changed source assignment")
    check("bake: invalid output slot rejects without partial assignment", invalid_bake)

    def scopes():
        area.type = "GRAPH_EDITOR"
        owner = bpy.data.objects.new("Scope Mesh", None)
        scene.collection.objects.link(owner)
        owner.keyframe_insert("location", frame=1)
        owner.location.x = 4
        owner.keyframe_insert("location", frame=20)
        bpy.context.view_layer.objects.active = owner
        for other in bpy.context.selected_objects:
            other.select_set(False)
        owner.select_set(True)
        area.spaces.active.dopesheet.show_only_selected = True
        from bpy_extras.anim_utils import action_get_channelbag_for_slot
        bag = action_get_channelbag_for_slot(owner.animation_data.action, owner.animation_data.action_slot)
        for fc in bag.fcurves:
            fc.select = True
            for key in fc.keyframe_points:
                key.select_control_point = False
                key.interpolation = "BEZIER"
        chosen = bag.fcurves[0].keyframe_points[0]
        chosen.select_control_point = True
        with bpy.context.temp_override(area=area, region=next(r for r in area.regions if r.type == "WINDOW")):
            expect(len(list(cu.iter_visible_fcurves(bpy.context))) == 3, "Editor selected-owner filter ignored")
            expect(bpy.ops.animassist.batch_interpolation(interp_type="LINEAR") == {"FINISHED"}, "Selected interpolation failed")
            expect(bag.fcurves[0].keyframe_points[0].interpolation == "LINEAR", "Selected key unchanged")
            expect(sum(k.interpolation == "LINEAR" for fc in bag.fcurves for k in fc.keyframe_points) == 1, "Unselected keys changed")
            with bpy.context.temp_override(editable_fcurves=[]):
                expect(not list(cu.iter_visible_fcurves(bpy.context)), "Empty editor scope fell back")
            area.spaces.active.mode = "DRIVERS"
            expect(not list(cu.iter_visible_fcurves(bpy.context)), "Drivers treated as Action keys")
            area.spaces.active.mode = "FCURVES"
        area.type = "NLA_EDITOR"
    check("Graph: native owner filters, selected-only interpolation, empty scope and drivers", scopes)

    def mesh_keying():
        mesh = bpy.data.meshes.new("Keying Mesh")
        owner = bpy.data.objects.new("Keying Mesh", mesh)
        scene.collection.objects.link(owner)
        bpy.context.view_layer.objects.active = owner
        for other in bpy.context.selected_objects:
            other.select_set(False)
        owner.select_set(True)
        with bpy.context.temp_override(area=area, region=next(r for r in area.regions if r.type == "WINDOW")):
            for frame in (1, 12, 26):
                scene.frame_set(frame)
                owner.location.x = frame / 10
                expect(bpy.ops.anim.keyframe_insert_by_name(type="LocRotScale") == {"FINISHED"}, "Native mesh keying failed")
        for editor in ("GRAPH_EDITOR", "DOPESHEET_EDITOR"):
            area.type = editor
            if editor == "DOPESHEET_EDITOR":
                area.spaces.active.mode = "DOPESHEET_EDITOR"
            area.spaces.active.dopesheet.show_only_selected = True
            with bpy.context.temp_override(area=area, region=next(r for r in area.regions if r.type == "WINDOW")):
                bpy.ops.anim.channels_expand(all=True)
                curves = list(cu.iter_visible_fcurves(bpy.context))
                expect(len(curves) == 9, f"Mesh keys unavailable in {editor}")
                expect(all(len(f.keyframe_points) == 3 for _o,_a,f in curves), "Missing newly inserted mesh keys")
        area.type = "NLA_EDITOR"
    check("native mesh keying: three frames visible in Graph and Dope Sheet with add-on enabled", mesh_keying)

    return results


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
