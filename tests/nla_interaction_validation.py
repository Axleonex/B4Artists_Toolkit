"""Native NLA interaction checks after nla_sidebar_validation's fixture setup."""
import bpy
import json
import importlib
from pathlib import Path


def run(output):
    area = max(bpy.context.screen.areas, key=lambda a: a.width * a.height)
    area.type = "NLA_EDITOR"
    area.spaces.active.show_region_ui = True
    area.spaces.active.dopesheet.show_only_selected = True
    region = next(r for r in area.regions if r.type == "WINDOW")
    owner = bpy.data.objects["NLA Walk"]
    ad = owner.animation_data
    source_track = ad.nla_tracks[0]
    source = source_track.strips[0]
    for obj in bpy.context.selected_objects:
        obj.select_set(False)
    owner.select_set(True)
    bpy.context.view_layer.objects.active = owner
    ad.nla_tracks.active = source_track
    results = []

    def check(name, fn):
        try:
            fn()
            results.append(dict(name=name, passed=True))
        except Exception:
            import traceback
            results.append(dict(name=name, passed=False, error=traceback.format_exc()))
        Path(output).write_text(json.dumps(results, indent=2))

    with bpy.context.temp_override(area=area, region=region):
        bpy.ops.nla.view_all()
        bpy.ops.nla.click_select(mouse_x=500, mouse_y=region.height-88, deselect_all=True)
        assert bpy.context.active_nla_strip == source, "Native clip activation failed"

        def tweak():
            for mapped in (False, True):
                if mapped:
                    source.scale, source.repeat, source.use_reverse = 2, 2, True
                nc = importlib.import_module("B4_anim_assist.core.nla_context")
                references = nc.source_references(source.action)
                assert bpy.ops.animassist.nla_native(command="EDIT") == {"FINISHED"}
                assert nc.source_references(source.action) == references, "Tweak assignment caused a false shared-source warning"
                assert bpy.context.scene.is_nla_tweakmode
                assert bpy.ops.animassist.nla_time(operation="NUDGE") == {"CANCELLED"}
                assert bpy.ops.animassist.nla_native(command="FINISH") == {"FINISHED"}
                assert not bpy.context.scene.is_nla_tweakmode
        check("native Tweak Mode: shifted/scaled/repeated/reversed clips and arrangement guard", tweak)

        def tracks():
            middle = ad.nla_tracks.new()
            middle.name = "Reorder Empty Track"
            top = ad.nla_tracks.new()
            top.name = "Upper Empty Track"
            for track in ad.nla_tracks:
                track.select = track == middle
                for strip in track.strips:
                    strip.select = False
            before = list(ad.nla_tracks)
            with bpy.context.temp_override(selected_nla_strips=[]):
                assert bpy.ops.animassist.nla_native(command="UP") == {"FINISHED"}
            assert list(ad.nla_tracks) != before, "Track order did not change"
            assert source in list(source_track.strips), "Track command moved a clip between tracks"
            ad.nla_tracks.remove(middle)
            ad.nla_tracks.remove(top)
            ad.nla_tracks.active = source_track
            source.select = True
        check("native track reordering works with no selected clips", tracks)

        def duplicate():
            for track in ad.nla_tracks:
                for strip in track.strips:
                    strip.select = strip == source
            original_action = source.action
            assert bpy.ops.animassist.nla_native(command="DUPLICATE") == {"FINISHED"}
            created = [s for t in ad.nla_tracks for s in t.strips if s != source]
            assert len(created) == 1 and created[0].action != original_action
            for track in ad.nla_tracks:
                for strip in track.strips:
                    strip.select = strip == source
            assert bpy.ops.animassist.nla_native(command="LINKED") == {"FINISHED"}
            assert sum(s.action == original_action for t in ad.nla_tracks for s in t.strips) == 2
        check("native linked and independent duplication have distinct Action ownership", duplicate)

        def stash_and_push():
            for command in ("STASH", "PUSHDOWN"):
                obj = bpy.data.objects.new(f"{command} Owner", None)
                bpy.context.scene.collection.objects.link(obj)
                for other in bpy.context.selected_objects:
                    other.select_set(False)
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                obj.keyframe_insert("location", frame=1)
                obj.keyframe_insert("location", frame=20)
                original = obj.animation_data.action
                if command == "PUSHDOWN":
                    obj.animation_data.use_nla = False
                    assert bpy.ops.animassist.nla_native(command=command) == {"CANCELLED"}
                    assert obj.animation_data.action == original and not obj.animation_data.nla_tracks
                    obj.animation_data.use_nla = True
                assert bpy.ops.animassist.nla_native(command=command) == {"FINISHED"}
                assert obj.animation_data.action is None
                assert obj.animation_data.nla_tracks[-1].strips[0].action == original
                assert obj.animation_data.nla_tracks[-1].mute == (command == "STASH")
        check("native Push Down and preserved muted Stash", stash_and_push)

        def existing_clip():
            obj = bpy.data.objects.new("Existing Action Owner", None)
            bpy.context.scene.collection.objects.link(obj)
            for other in bpy.context.selected_objects:
                other.select_set(False)
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            action = source.action
            assert bpy.ops.animassist.nla_add_clip(action_name=action.name) == {"FINISHED"}
            assert obj.animation_data.nla_tracks[-1].strips[0].action == action
            assert obj.animation_data.action is None
        check("empty-owner existing Action clip creation", existing_clip)
    return results
