# bonecraft/tests/test_mech_ui_host.py
"""In-Bforartists test: the Mechanisms section — placement, permanent Scene-tab copy, polls, draws, tool switch."""
import addon_utils
import bpy

import boneforge
from mech_draw_stubs import Ctx, Rec


class Shim:
    def __init__(self):
        self.layout = Rec([])


def _cube(name, loc):
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=loc)
    bpy.context.object.name = name
    return bpy.context.object


def _texts(log):
    return [k.get("text") for n, a, k in log if n == "label"]


def _target_ops(log):
    """[(operator id, target)]: each drawn operator with the target set on it right after."""
    out = []
    for i, (n, a, k) in enumerate(log):
        if n == "operator":
            nxt = log[i + 1] if i + 1 < len(log) else None
            out.append((a[0], nxt[2] if nxt and nxt[0] == "set" and nxt[1] == "target" else None))
    return out


def run():
    bpy.ops.wm.read_factory_settings(use_empty=True)   # an empty scene: no names or modes left by earlier tests
    addon_utils.enable("rigify")
    boneforge.register()
    try:
        from boneforge.core import scene_tab_mirror as stm                        # after register
        from boneforge.core.tool_registry import get_registry
        from boneforge.core.tool_toggle_operator import BF_OT_ToggleTool
        from boneforge.mechanisms import build, model as M, records, ui
        root = bpy.types.BF_PT_mech
        assert (root.bl_space_type, root.bl_region_type, root.bl_category, root.bl_order) == ('VIEW_3D', 'TOOLS', 'BoneCraft', 30)   # the BoneCraft tab defaults to the left Tool Shelf
        kids = ("BF_PT_mech_parts", "BF_PT_mech_links", "BF_PT_mech_sequences", "BF_PT_mech_controls")
        assert [getattr(bpy.types, k).bl_parent_id for k in kids] == ["BF_PT_mech"] * 4
        copy = getattr(bpy.types, "BF_PT_mech" + stm.SUFFIX)
        assert (copy.bl_space_type, copy.bl_region_type, copy.bl_context) == ("PROPERTIES", "WINDOW", "scene")
        orders = {r: getattr(bpy.types, r + stm.SUFFIX).bl_order
                  for r in ("BF_PT_mech", "CATS_PT_main", "BF_PT_sb_vrchat", "BF_PT_cats_vrc_tools", "BF_PT_sb_io")}
        assert orders == {"BF_PT_mech": 2, "CATS_PT_main": 3, "BF_PT_sb_vrchat": 4, "BF_PT_cats_vrc_tools": 5,
                          "BF_PT_sb_io": 6}, orders
        assert bpy.types.BF_PT_rb_setup.bl_order == 1, "Rig Builder stays first"

        # M6: every generic root panel folds under one collapsed Other Tools parent; curated sections stay on top
        curated = {"BF_PT_sb_overview", "BF_PT_sb_setup", "BF_PT_sb_skin", "BF_PT_mech", "BF_PT_sb_animate", "BF_PT_sb_other"}
        other = getattr(bpy.types, "BF_PT_sb_other", None)
        assert other is not None and other.bl_order == 45 and 'DEFAULT_CLOSED' in other.bl_options
        strays = [c.bl_idname for c in bpy.types.Panel.__subclasses__()
                  if getattr(c, "is_registered", False) and getattr(c, "bl_space_type", "") == 'VIEW_3D'
                  and getattr(c, "bl_category", "") == 'BoneCraft' and not getattr(c, "bl_parent_id", "")
                  and getattr(c, "bl_idname", "") not in curated
                  and not c.bl_idname.startswith("BONEFORGE_PT_vrc_")]          # hidden; VRChat Tools draws them
        assert not strays, strays
        assert bpy.types.BONEFORGE_PT_bone_merge.bl_parent_id == "BF_PT_sb_other"
        # ...except the VRChat utilities: one VRChat Tools section in the CATS tab draws them, in the owner's order
        from boneforge.taskboard import sidebar
        vrc = getattr(bpy.types, "BF_PT_cats_vrc_tools", None)
        assert vrc is not None and vrc.bl_category == "CATS" and vrc.bl_order == 36 and 'DEFAULT_CLOSED' in vrc.bl_options
        assert not getattr(vrc, "bl_parent_id", ""), "a section of its own, not a VRChat sub-panel"
        assert [c for _group, tools_ in sidebar.VRC_TOOL_GROUPS for _m, c in tools_] == [
            "BONEFORGE_PT_vrc_performance", "BONEFORGE_PT_vrc_decimation", "BONEFORGE_PT_vrc_optimizer",
            "BONEFORGE_PT_vrc_bone_match", "BONEFORGE_PT_vrc_collision", "BONEFORGE_PT_vrc_clothing_merge",
            "BONEFORGE_PT_vrc_naming_detect", "BONEFORGE_PT_vrc_naming_presets", "BONEFORGE_PT_vrc_batch_rename"]
        for gone in ("BF_PT_sb_vrc_naming", "BF_PT_sb_vrc_clothing", "BF_PT_sb_vrc_perf"):
            assert getattr(bpy.types, gone, None) is None, (gone, "would draw the same tools twice")
        tools = [c for _group, tools_ in sidebar.VRC_TOOL_GROUPS for _m, c in tools_]
        for idn in tools:
            cls = getattr(bpy.types, idn)
            assert cls.is_registered and not getattr(cls, "bl_parent_id", "") and not cls.poll(bpy.context), \
                (idn, "stays a hidden panel: VRChat Tools draws it, so it never shows twice")
        bpy.ops.object.armature_add()
        assert vrc.poll(Ctx()), "an active armature shows the section"
        shim = Shim()
        vrc.draw(shim, bpy.context)
        groups = [g for g, _tools in sidebar.VRC_TOOL_GROUPS]
        heads = [k for n, a_, k in shim.layout.log if n == "label" and k.get("text") in groups]
        assert [k["text"] for k in heads] == ["Performance", "Clothing", "Naming"], heads
        assert not [k for k in heads if k.get("icon", 'NONE') != 'NONE'], "headings carry no topic icon"
        assert not [k.get("text") for n, a_, k in shim.layout.log if n == "label" and k.get("icon") in ('ERROR', 'QUESTION')]
        drawn = []                                         # every one of the nine draws, in order, through its own draw()
        real = {idn: getattr(bpy.types, idn).draw for idn in tools}
        try:
            for idn in tools:
                getattr(bpy.types, idn).draw = (lambda name: lambda self, ctx: drawn.append(name))(idn)
            vrc.draw(Shim(), bpy.context)
        finally:
            for idn, fn in real.items():
                getattr(bpy.types, idn).draw = fn
        assert drawn == tools, drawn
        # a VRChat tool switched off (its panel unregistered) is not drawn; with none left the section hides
        off = getattr(bpy.types, tools[0])
        bpy.utils.unregister_class(off)
        drawn = []
        try:
            for idn in tools:                              # the unregistered class is patched too: drawing it would show
                cls = off if idn == tools[0] else getattr(bpy.types, idn)
                cls.draw = (lambda name: lambda self, ctx: drawn.append(name))(idn)
            vrc.draw(Shim(), bpy.context)
            assert drawn == tools[1:], drawn
        finally:
            for idn, fn in real.items():
                (off if idn == tools[0] else getattr(bpy.types, idn)).draw = fn
            bpy.utils.register_class(off)
        hidden = [getattr(bpy.types, idn) for idn in tools]
        for cls in hidden:
            bpy.utils.unregister_class(cls)
        try:
            assert not vrc.poll(Ctx()), "no VRChat tool registered: no empty section"
        finally:
            for cls in hidden:
                bpy.utils.register_class(cls)
        assert vrc.poll(Ctx())
        # an empty selected (a Mechanisms pivot marker): the CATS Armature picker still drives Avatar Tools
        picked = bpy.context.view_layer.objects.active
        bpy.context.scene.boneforge_cats_target_armature_name = picked.name
        empty = bpy.data.objects.new("Pivot: test", None)
        bpy.context.scene.collection.objects.link(empty)
        bpy.context.view_layer.objects.active = empty
        try:
            for idn in ("BF_PT_sb_vrchat", "BF_PT_cats_vrc_tools", "BF_PT_sb_vrc_humanoid", "BF_PT_sb_vrc_hair",
                        "BF_PT_sb_vrc_visemes", "BF_PT_sb_vrc_export"):
                assert getattr(bpy.types, idn).poll(Ctx()), (idn, "hidden while the picker has an armature")
            shim = Shim()
            vrc.draw(shim, bpy.context)
            assert "Select the armature to use these tools." not in _texts(shim.layout.log), \
                "the picker's armature counts as the armature"
            shim = Shim()
            bpy.types.BF_PT_sb_vrchat.draw(shim, bpy.context)
            assert picked.name in _texts(shim.layout.log), "Avatar Tools names the armature it works on"
        finally:
            bpy.context.view_layer.objects.active = picked
            bpy.data.objects.remove(empty)
        bpy.data.objects.remove(bpy.context.view_layer.objects.active)
        assert not [c for c in bpy.types.Panel.__subclasses__() if c.__name__.startswith("BF_PT_mech") and c.__name__.endswith("_Prop")], \
            "Mechanisms is not copied into Armature data"

        # nothing active: the Scene-tab copy and the sidebar both show and say how to start (show, don't hide)
        bpy.context.view_layer.objects.active = None
        assert copy.poll(bpy.context) and root.poll(Ctx())
        shim = Shim()
        copy.draw(shim, bpy.context)
        assert "Select a mesh to start, or an armature with mechanisms." in _texts(shim.layout.log)
        # an armature with no records: same line, no subsections
        bpy.ops.object.armature_add()
        bpy.context.view_layer.objects.active.name = "Plain Rig"
        shim = Shim()
        copy.draw(shim, bpy.context)
        assert "Select a mesh to start, or an armature with mechanisms." in _texts(shim.layout.log)
        assert not any(getattr(bpy.types, k + stm.SUFFIX).poll(bpy.context) for k in kids)
        bpy.context.view_layer.objects.active = None
        for k in ("BF_PT_mech",) + kids:                      # drawn with nothing active, poll or not: no errors
            for cls in (getattr(bpy.types, k), getattr(bpy.types, k + stm.SUFFIX)):
                cls.draw(Shim(), bpy.context)

        # a mesh: Add Parts from Selection; the BoneCraft tab switch hides only the sidebar copy
        a, b, c, d, e = (_cube(n, (i, 0, 0)) for i, n in enumerate(("Frame", "Blade", "Cover", "Mast", "Seg")))
        bpy.context.view_layer.objects.active = a
        assert root.poll(Ctx(tab=True)) and not root.poll(Ctx(tab=False)) and copy.poll(Ctx(tab=False))
        shim = Shim()
        copy.draw(shim, bpy.context)
        assert any(n == "operator" and a_[0] == "boneforge.mech_add_parts" for n, a_, k in shim.layout.log)

        # a full rig: every panel, list and menu draws (helpers on and off), settings show only their type's fields
        data = bpy.data.armatures.new("UI Rig")
        arm = bpy.data.objects.new("UI Rig", data)
        bpy.context.scene.collection.objects.link(arm)
        for x in (M.Part("fr", "Frame", object_name="Frame"), M.Part("bl", "Blade", object_name="Blade", parent="fr", pivot=(1, 0, 0)),
                  M.Part("co", "Cover", object_name="Cover", parent="fr", pivot=(2, 0, 0)), M.Part("ma", "Mast", object_name="Mast", pivot=(3, 0, 0)),
                  M.Part("sg", "Seg", object_name="Seg", parent="ma", pivot=(4, 0, 0)),
                  M.Mechanism("h1", "HINGE", "Blade Hinge", parts=["bl"], min=0, max=90),
                  M.Mechanism("s1", "SLIDE", "Cover Slide", parts=["co"], axis=(0, 1, 0), min=0, max=0.3),
                  M.Mechanism("t1", "TELESCOPE", "Mast Telescope", parts=["ma", "sg"], axis=(0, 0, 1), length=0.5),
                  M.Mechanism("f1", "FOLLOW", "Cover Follow", source="h1", target="s1", source_range=(0, 90), target_range=(0, 0.3)),
                  M.Mechanism("g1", "GEAR", "Cover Gear", source="h1", target="s1", gear_kind="RACK", pinion_radius=0.05),
                  M.Sequence("q1", "Unfold", steps=[M.Step("h1", 60.0)])):
            records.add(data, x)
        build.rebuild(arm)
        data.bonecraft_mech.forms.add().name = "Stowed"
        bpy.context.view_layer.objects.active = arm
        panels = [getattr(bpy.types, k) for k in ("BF_PT_mech",) + kids]
        panels += [getattr(bpy.types, k + stm.SUFFIX) for k in ("BF_PT_mech",) + kids]
        rec = data.bonecraft_mech

        # M: once mechanisms exist, sections 1-3 fold to a one-line summary (runtime flags, nothing saved)
        wm = bpy.context.window_manager
        assert (wm.bonecraft_mech_show_parts, wm.bonecraft_mech_show_links, wm.bonecraft_mech_show_seqs) == (False, False, False)
        for panel, flag in (("BF_PT_mech_parts", "bonecraft_mech_show_parts"),
                            ("BF_PT_mech_links", "bonecraft_mech_show_links"),
                            ("BF_PT_mech_sequences", "bonecraft_mech_show_seqs")):
            shim = Shim()
            getattr(bpy.types, panel).draw(shim, bpy.context)
            log = shim.layout.log
            props = [a_[1] for n, a_, k in log if n == "prop"]
            assert props == [flag], (panel, props)
            assert not any(n in ("operator", "menu", "template_list") for n, a_, k in log), (panel, "folded to one line")
        wm.bonecraft_mech_show_parts = wm.bonecraft_mech_show_links = wm.bonecraft_mech_show_seqs = True

        for helpers in (True, False):
            ctx = Ctx(helpers=helpers)
            for i, m in enumerate(rec.mechanisms):
                rec.active_mech = i
                for cls in panels:
                    assert cls.poll(ctx), cls.__name__
                    shim = Shim()
                    cls.draw(shim, ctx)
                    if cls.__name__.startswith("BF_PT_mech_links"):
                        drawn = {a_[1] for n, a_, k in shim.layout.log if n == "prop" and a_ and a_[0] == m}
                        allowed = set(M.FIELDS[m.type]) | {"handle_widget_ui", "handle_size", "handle_color_ui", "show_note"}
                        assert set(M.FIELDS[m.type]) <= drawn <= allowed, (m.type, drawn)
                        assert not {"handle_widget", "handle_color"} & drawn, (m.type, drawn)
                        if "axis" in M.FIELDS[m.type]:
                            ax = [(k.get("index"), k.get("text")) for n, a_, k in shim.layout.log
                                  if n == "prop" and a_ and a_[1] == "axis"]
                            assert ax == [(0, "X"), (1, "Y"), (2, "Z")], ax
                    infos = [k for n, a_, k in shim.layout.log if n == "label" and k.get("icon") == 'INFO']
                    assert helpers or not infos, ("helpers off still shows teaching text", cls.__name__)
            for menu in (bpy.types.BC_MT_mech_add_joint, bpy.types.BC_MT_mech_add_link):
                shim = Shim()
                menu.draw(shim, ctx)
                ops_ = [k for n, a_, k in shim.layout.log if n == "operator"]
                assert ops_ and len([t for t in _texts(shim.layout.log) if t and t.strip()]) == (len(ops_) if helpers else 0)
        for ul, coll in ((ui.BC_UL_mech_parts, rec.parts), (ui.BC_UL_mechs, rec.mechanisms),
                         (ui.BC_UL_mech_sequences, rec.sequences), (ui.BC_UL_mech_forms, rec.forms)):
            for item in coll:
                ul.draw_item(None, bpy.context, Rec([]), rec, item, 0, rec, "", 0)
        log = []
        ui.BC_UL_mechs.draw_item(None, bpy.context, Rec(log), rec, rec.mechanisms[0], 0, rec, "", 0)
        row_ops = [a_[0] for n, a_, k in log if n == "operator"]
        assert "boneforge.mech_edit" not in row_ops and "boneforge.mech_delete" in row_ops, row_ops
        assert [k.get("translate") for n, a_, k in log if n == "label"] == [False], "mechanism names are never machine-translated"
        log = []
        ui.BC_UL_mech_parts.draw_item(None, bpy.context, Rec(log), rec, rec.parts[0], 0, rec, "", 0)
        assert [k.get("translate") for n, a_, k in log if n == "label"] == [False], "part names are never machine-translated"

        rec.active_mech = 0
        rec.mechanisms[0].show_note = True
        notes = ui.explain(arm, "h1")
        assert notes and all(bone in arm.pose.bones for _, bone in notes)
        assert any("BC·h1·limit" in text and "Min and Max" in text for text, _ in notes)

        # M: the Capture button names each click; the armed state and the step-window overlap show in the panel
        seq_panel = bpy.types.BF_PT_mech_sequences
        rec.active_seq = 0
        rig_now = records.to_model(arm)
        assert abs(build.get_value(arm, rig_now, "q1")) < 1e-4
        shim = Shim()
        seq_panel.draw(shim, bpy.context)
        caps = [k.get("text") for n, a_, k in shim.layout.log if n == "operator" and a_ and a_[0] == "boneforge.mech_capture_step"]
        assert caps == ["Move Slider to End"], caps
        build.set_value(arm, rig_now, "q1", 1.0)
        shim = Shim()
        seq_panel.draw(shim, bpy.context)
        caps = [k.get("text") for n, a_, k in shim.layout.log if n == "operator" and a_ and a_[0] == "boneforge.mech_capture_step"]
        assert caps == ["Record Step 2"], caps
        armed = " ".join(x for x in _texts(shim.layout.log) if x)
        assert "Record Step 2" in armed, "the armed line says what the next click records"
        assert "overlaps step 1" in armed, "q1 only step ends at 1.0, so the reused 0.75-1.0 window overlaps it"
        with records.quiet():
            records.find(data, "q1").steps[0].end = 0.25
        shim = Shim()
        seq_panel.draw(shim, bpy.context)
        assert "overlaps" not in " ".join(x for x in _texts(shim.layout.log) if x)
        with records.quiet():
            records.find(data, "q1").steps[0].end = 1.0

        # X1: the armed capture shows in the mode line, and Cancel restores the slider
        shim = Shim()
        bpy.types.BF_PT_mech.draw(shim, bpy.context)
        assert any(x and "Capture armed" in x for x in _texts(shim.layout.log))
        assert bpy.ops.boneforge.mech_cancel_capture(target="q1") == {'FINISHED'}
        assert abs(build.get_value(arm, records.to_model(arm), "q1")) < 1e-4

        # M: a Sequence everyday slider is a percentage, stored nowhere (get/set through the handle bone)
        seq_pg = records.find(data, "q1")
        seq_pg.progress = 100.0
        assert abs(build.get_value(arm, records.to_model(arm), "q1") - 1.0) < 1e-3
        seq_pg.progress = 0.0
        assert abs(build.get_value(arm, records.to_model(arm), "q1")) < 1e-3
        shim = Shim()
        bpy.types.BF_PT_mech_controls.draw(shim, bpy.context)
        log = shim.layout.log
        assert any(n == "prop" and a_ and a_[1] == "progress" and k.get("translate") is False for n, a_, k in log), "Sequences get the % slider"
        assert any(n == "prop" and a_ and a_[1] == "rotation_euler" and k.get("translate") is False for n, a_, k in log)
        assert any(n == "operator" and a_ and a_[0] == "boneforge.mech_merge_vrchat" for n, a_, k in log), "Merge for VRChat ends 4. Controls"
        shim = Shim()
        bpy.types.BF_PT_mech_parts.draw(shim, bpy.context)
        assert not any(n == "operator" and a_ and a_[0] == "boneforge.mech_merge_vrchat" for n, a_, k in shim.layout.log), "...and left 1. Parts"

        # X8: the Delete confirmation names what depends on the record
        from boneforge.mechanisms import ops as mech_ops
        assert mech_ops.delete_impact(arm, "h1") == "Used by 2 links and 1 sequence step."
        assert mech_ops.delete_impact(arm, "co") == "Used by 1 mechanism."
        assert mech_ops.delete_impact(arm, "q1") == "Has 1 step."
        assert mech_ops.delete_impact(arm, "g1") == ""
        assert callable(getattr(mech_ops.BC_OT_mech_delete, "invoke", None)), "Delete asks first"

        # review fixes: a pickable Default handle shape, honest colour view, refusals before the dialog
        h1pg = records.find(data, "h1")
        assert h1pg.handle_widget == "" and h1pg.handle_widget_ui == "DEFAULT"
        h1pg.handle_widget_ui = "gear"
        assert h1pg.handle_widget == "gear"
        h1pg.handle_widget_ui = "DEFAULT"
        assert h1pg.handle_widget == ""
        with records.quiet():
            h1pg.handle_color = ""
        assert h1pg.handle_color_ui == "special", "empty colour means the planner's special"
        with records.quiet():
            h1pg.handle_color = "weird"
        assert h1pg.handle_color_ui == "weird"
        with records.quiet():
            h1pg.handle_color = "special"
        assert not records.BC_PG_MechSequence.bl_rna.properties['progress'].is_animatable, \
            "keying the % view would key nothing; key the handle bone or use Go and Key"
        assert mech_ops.delete_refusal(arm, "h1").startswith("Can't delete"), "a used record is refused before the dialog"
        assert mech_ops.delete_refusal(arm, "q1") == "" and mech_ops.delete_refusal(arm, "g1") == ""
        assert other.poll(Ctx(tab=True)) and not other.poll(Ctx(tab=False)), "Other Tools follows the tab switch"
        lip = getattr(bpy.types, "BONEFORGE_PT_p2c_lip_sync", None)
        if lip is not None:
            assert lip.is_registered and lip.bl_parent_id == "BONEFORGE_PT_p2c_viseme_library"
            assert bpy.types.BONEFORGE_PT_p2c_viseme_library.bl_parent_id == "BF_PT_sb_other"

        # X4: adding into a folded section reopens it
        wm.bonecraft_mech_show_seqs = False
        assert bpy.ops.boneforge.mech_add_sequence(name="Extra") == {'FINISHED'}
        assert wm.bonecraft_mech_show_seqs is True
        extra = rec.sequences[len(rec.sequences) - 1].id
        assert bpy.ops.boneforge.mech_delete(target=extra) == {'FINISHED'}

        # a held Sequence shows its message and Restore; Detach and Delete are always there
        rec.active_seq = 0
        with records.quiet():
            q = records.find(data, "q1")
            q.state, q.message = "CHANGED_BY_HAND", "Unfold was changed by hand."
        shim = Shim()
        seq_panel.draw(shim, bpy.context)
        drawn = _target_ops(shim.layout.log)
        for op in ("boneforge.mech_restore", "boneforge.mech_detach", "boneforge.mech_delete"):
            assert (op, "q1") in drawn, (op, drawn)
        assert "Unfold was changed by hand." in _texts(shim.layout.log)
        with records.quiet():
            q = records.find(data, "q1")
            q.state, q.message = "OK", ""
        shim = Shim()
        seq_panel.draw(shim, bpy.context)
        drawn = _target_ops(shim.layout.log)
        assert ("boneforge.mech_restore", "q1") not in drawn and ("boneforge.mech_delete", "q1") in drawn, drawn
        assert bpy.ops.boneforge.mech_delete(target="q1") == {'FINISHED'}
        assert records.find(data, "q1") is None and not len(rec.sequences), "Delete removes a Sequence"

        # the pivot marker belongs to its rig, so Apply Pivot stays reachable
        from boneforge.mechanisms import parts
        rec.active_part = 0                                     # the list shows another part...
        marker = parts.start_pivot(bpy.context, arm, "bl")
        assert records.active_rig(bpy.context) == arm
        shim = Shim()
        bpy.types.BF_PT_mech_parts.draw(shim, bpy.context)
        assert "Pivot marker for: Blade" in _texts(shim.layout.log), "...but the panel shows the marker's part"
        assert any(a_[0] == "boneforge.mech_apply_pivot" for n, a_, k in shim.layout.log if n == "operator")
        # X1: the pivot mode shows in the mode line even when the marker is not selected
        bpy.context.view_layer.objects.active = arm
        shim = Shim()
        bpy.types.BF_PT_mech.draw(shim, bpy.context)
        assert any(x and "Editing pivot: Blade" in x for x in _texts(shim.layout.log))
        bpy.context.view_layer.objects.active = marker
        # X3: the Rides on menu draws part names with translation off
        shim = Shim()
        bpy.types.BC_MT_mech_parent.draw(shim, bpy.context)
        items = [(k.get("text"), k.get("translate")) for n, a_, k in shim.layout.log if n == "operator"]
        assert items and items[0][0] == "The rig" and ("Frame", False) in items[1:], items
        assert all(tr is False for _x, tr in items[1:]), items
        try:                                                     # Blade drives Cover, so riding on it would loop
            bpy.ops.boneforge.mech_set_parent(parent="co")
            raise AssertionError("a loop must be refused")
        except RuntimeError as exc:
            assert "would loop" in str(exc)
        assert records.find(data, "bl").parent == "fr" and not rec.last_error, "a refused parent leaves the part as it was"
        assert bpy.ops.boneforge.mech_set_parent(parent="ma") == {'FINISHED'}
        assert (records.find(data, "bl").parent, records.find(data, "fr").parent) == ("ma", ""),             "Rides on changes the marker's part, not the list's part"
        parts.apply_pivot(bpy.context, marker)
        parts.start_pivot(bpy.context, arm, "co")
        assert bpy.ops.boneforge.mech_cancel_pivot() == {'FINISHED'}
        assert not [o for o in bpy.data.objects if o.get(parts.PIVOT_PROP) is not None], "Cancel removes the marker"
        assert bpy.context.view_layer.objects.active == arm
        shim = Shim()
        bpy.types.BF_PT_mech.draw(shim, bpy.context)
        assert not any(x and "Editing pivot" in x for x in _texts(shim.layout.log))

        # the tool switch removes the section everywhere, and brings it back
        bpy.context.view_layer.objects.active = a
        started = get_registry().is_enabled("mechanisms")
        assert started
        BF_OT_ToggleTool._deferred_work({"tool_id": "mechanisms"})
        assert getattr(bpy.types, "BF_PT_mech", None) is None and getattr(bpy.types, "BF_PT_mech" + stm.SUFFIX, None) is None
        BF_OT_ToggleTool._deferred_work({"tool_id": "mechanisms"})
        assert bpy.types.BF_PT_mech.poll(Ctx()) and getattr(bpy.types, "BF_PT_mech" + stm.SUFFIX).poll(bpy.context)
        assert records.has_records(data), "switching the tool off and on keeps the records"
    finally:
        boneforge.unregister()
    print("PASS mechanisms UI: folded summaries, mode line, named capture clicks, % sliders, "
          "untranslated names, delete impact, sidebar order 30, Scene tab after Rig Builder, not in Armature data, "
          "polls, draws with helpers on/off, fields per type, tool switch")
