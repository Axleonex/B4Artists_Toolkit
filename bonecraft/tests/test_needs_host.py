# bonecraft/tests/test_needs_host.py
"""In-Bforartists test: show, don't hide (owner, 2026-10-10).

A section or sub-panel whose tools need a certain object stays visible when that object is not
selected, and says what to select instead of vanishing. When exactly one suitable object is in the
scene, a Select button selects it. A section hidden by its tab switch (Preferences > Tabs) still hides.
"""
import bpy

import boneforge
from mech_draw_stubs import Ctx, Rec

# panel id -> (what it needs, an object kind that satisfies it)
GATED = {
    "BF_PT_sb_overview": "ARMATURE",
    "BF_PT_sb_skin": "ARMATURE",            # an armature or a mesh; the button offers the armature
    "BF_PT_mech": "MESH",                   # a mesh or a Mechanism Rig; this rig has no mechanisms
    "BF_PT_sb_animate": "ARMATURE",
    "BF_PT_sb_retarget": "ARMATURE",
    "BF_PT_sb_rigify": "ARMATURE",
    "BF_PT_sb_correctives": "ARMATURE",
    "BONEFORGE_PT_p2b_delta_mush": "MESH",
    "BONEFORGE_PT_p2b_proximity_wrap": "MESH",
    "BONEFORGE_PT_profile_export": "ARMATURE",
    "BONEFORGE_PT_p2c_viseme_library": "ARMATURE",
    "BF_PT_sb_vrchat": "ARMATURE",          # CATS tab: Avatar Tools (an armature or a mesh)
    "BF_PT_cats_vrc_tools": "ARMATURE",     # CATS tab: VRChat Tools
}


class Shim:
    def __init__(self):
        self.layout = Rec([])


def _texts(log):
    return [k.get("text") for n, a, k in log if n == "label"]


def _draw(idname, context):
    shim = Shim()
    getattr(bpy.types, idname).draw(shim, context)
    return shim.layout.log


def _registered():
    seen = set()

    def walk(c):
        for s in c.__subclasses__():
            seen.add(s)
            walk(s)
    walk(bpy.types.Panel)
    return [c for c in seen if getattr(c, "is_registered", False) and getattr(c, "bl_space_type", "") == 'VIEW_3D']


def _poll(cls):
    try:
        return bool(cls.poll(Ctx())) if hasattr(cls, "poll") else True
    except Exception:                                      # noqa: BLE001 - a panel that cannot poll here is hidden
        return False


def _header(cls):
    shim = Shim()
    if hasattr(cls, "draw_header"):
        cls.draw_header(shim, bpy.context)
    texts = [x for x in _texts(shim.layout.log) if x]
    return texts[0] if texts else cls.bl_label


def run():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    boneforge.register()
    try:
        from boneforge.core import needs
        empty = bpy.data.objects.new("Pivot: test", None)
        bpy.context.scene.collection.objects.link(empty)
        bpy.context.view_layer.objects.active = empty
        # nothing usable selected and nothing in the scene: every gated panel shows, and says what it needs
        for idn in GATED:
            cls = getattr(bpy.types, idn)
            assert cls.poll(Ctx()), (idn, "vanished instead of explaining")
            log = _draw(idn, bpy.context)
            assert set(_texts(log)) & needs.NOTES, (idn, "says what to select", _texts(log))
            assert not any(n == "operator" and a and a[0] == "boneforge.select_object" for n, a, k in log), \
                (idn, "no Select button when nothing suitable exists")
            assert not any(x and x.startswith("Inside: ") for x in _texts(log)), (idn, "sub-panels show, not a list")
        # Viseme Library's Lip Sync stays a visible fold that says what it needs
        lip = bpy.types.BONEFORGE_PT_p2c_lip_sync
        assert lip.poll(Ctx()), "Lip Sync vanished"
        assert set(_texts(_draw("BONEFORGE_PT_p2c_lip_sync", bpy.context))) & needs.NOTES
        # section headers carry no icon, so their titles still show in the 132 px default Tool Shelf
        for idn in ("BF_PT_sb_overview", "BF_PT_sb_setup", "BF_PT_sb_skin", "BF_PT_mech", "BF_PT_sb_animate"):
            shim = Shim()
            getattr(bpy.types, idn).draw_header(shim, bpy.context)
            heads = [(k.get("text"), k.get("icon")) for n, a, k in shim.layout.log if n == "label"]
            assert heads and heads[0][0] and heads[0][1] in (None, 'NONE'), (idn, heads)
        # the tab switch still hides the BoneCraft tab's sections
        for idn in ("BF_PT_sb_overview", "BF_PT_sb_skin", "BF_PT_mech", "BF_PT_sb_animate"):
            assert not getattr(bpy.types, idn).poll(Ctx(tab=False)), (idn, "the tab switch hides it")

        # exactly one suitable object: a Select button names it, and clicking it selects it
        bpy.ops.mesh.primitive_cube_add()
        cube = bpy.context.active_object
        cube.name = "Body"
        bpy.ops.object.armature_add()
        rig = bpy.context.active_object
        rig.name = "Avatar Rig"
        cube.parent = rig
        bpy.context.view_layer.objects.active = empty
        for idn, kind in GATED.items():
            if idn in ("BF_PT_sb_vrchat", "BF_PT_cats_vrc_tools"):
                continue                                   # the CATS Armature picker already finds the one rig
            log = _draw(idn, bpy.context)
            ops = [(a[0], k.get("text")) for n, a, k in log if n == "operator" and a and a[0] == "boneforge.select_object"]
            want = {"MESH": "Body", "ARMATURE": "Avatar Rig"}[kind]      # the name alone fits the 132 px shelf
            assert ops and ops[0][1] == want, (idn, ops)
        assert bpy.ops.boneforge.select_object(name="Avatar Rig") == {'FINISHED'}
        assert bpy.context.view_layer.objects.active == rig and rig.select_get()

        # the right object selected: the tools draw, not the note
        for idn, kind in GATED.items():
            target = cube if kind == "MESH" else rig
            bpy.context.view_layer.objects.active = target
            log = _draw(idn, bpy.context)
            assert not set(_texts(log)) & needs.NOTES, (idn, _texts(log))

        # Lip Sync only works in Pose Mode: outside it, Viseme Library says so instead of Lip Sync vanishing
        bpy.context.view_layer.objects.active = rig
        assert bpy.context.mode == 'OBJECT'
        assert any(x and "Lip Sync" in x for x in _texts(_draw("BONEFORGE_PT_p2c_viseme_library", bpy.context)))
        bpy.ops.object.mode_set(mode='POSE')
        assert not any(x and "Lip Sync:" in x for x in _texts(_draw("BONEFORGE_PT_p2c_viseme_library", bpy.context)))
        bpy.ops.object.mode_set(mode='OBJECT')

        # nothing vanishes: a sub-panel under a visible section stays a fold and says what to select
        bpy.context.view_layer.objects.active = empty
        panels = [c for c in _registered() if getattr(c, "bl_category", "") in ("BoneCraft", "CATS", "Rig Builder")]
        def polls(ob):
            bpy.context.view_layer.objects.active = ob
            return {c.bl_idname: _poll(c) for c in panels}
        p_mesh, p_rig, p_empty = polls(cube), polls(rig), polls(empty)
        by_id = {c.bl_idname: c for c in panels}
        bpy.context.view_layer.objects.active = empty
        shown = 0
        for c in panels:
            par = getattr(c, "bl_parent_id", "")
            if not par or par not in by_id or not p_empty[par]:
                continue
            if not (p_mesh[c.bl_idname] or p_rig[c.bl_idname]):
                continue                                   # a hidden panel a hub draws: never shown on its own
            assert p_empty[c.bl_idname], (c.bl_idname, _header(c), "vanished under", par)
            if not set(_texts(_draw(par, bpy.context))) & needs.NOTES:
                continue                                   # the section is usable: nothing waits
            shown += 1                                     # a fold under a waiting section waits too
            assert set(_texts(_draw(c.bl_idname, bpy.context))) & needs.NOTES, (c.bl_idname, "says what to select")
        assert shown >= 13, ("Task Board, Rig Notes, Weight Tools, Review's 6, Mechanisms' 4", shown)

        # Overview lists Task Board first, then Rig Notes, whatever order their modules register in
        assert bpy.types.BONEFORGE_PT_taskboard.bl_order < bpy.types.BF_PT_sb_rig_notes.bl_order

        # wrapping patches panels in place: a re-registered panel would jump below its siblings
        from bpy.types import Panel
        made = []
        for idn, order_ in (("BF_PT_test_gate", None), ("BF_PT_test_kid_a", 1), ("BF_PT_test_kid_b", 2)):
            ns = {"bl_idname": idn, "bl_label": idn, "bl_space_type": 'VIEW_3D', "bl_region_type": 'UI',
                  "bl_category": "BoneCraft", "draw": lambda self, context: self.layout.label(text="tools")}
            if order_ is not None:
                ns.update(bl_parent_id="BF_PT_test_gate", poll=classmethod(lambda cls, context: False))
            made.append(type(idn, (Panel,), ns))
            bpy.utils.register_class(made[-1])
        needs.GATES["BF_PT_test_gate"] = (lambda c: False, "Select an armature to use this.")
        calls, real = [], (bpy.utils.register_class, bpy.utils.unregister_class)
        bpy.utils.register_class = lambda c: calls.append(("reg", c))
        bpy.utils.unregister_class = lambda c: calls.append(("unreg", c))
        try:
            needs.keep_children_visible()
        finally:
            bpy.utils.register_class, bpy.utils.unregister_class = real
            del needs.GATES["BF_PT_test_gate"]
        assert not calls, ("re-registered, so the panel order changes", calls)
        for kid in made[1:]:
            assert kid.poll(Ctx()) and "Select an armature to use this." in _texts(_draw(kid.bl_idname, bpy.context))
        for c in reversed(made):
            bpy.utils.unregister_class(c)

        # the Select button never targets an object that cannot be selected, and never guesses
        rig.hide_select = True
        log = _draw("BF_PT_sb_animate", bpy.context)
        assert not any(n == "operator" and a and a[0] == "boneforge.select_object" for n, a, k in log),             "an unselectable armature is not offered"
        rig.hide_select = False
        bpy.ops.object.armature_add()                      # two armatures, one mesh: Skin offers the mesh
        bpy.context.view_layer.objects.active = empty
        ops = [k.get("text") for n, a, k in _draw("BF_PT_sb_skin", bpy.context)
               if n == "operator" and a and a[0] == "boneforge.select_object"]
        assert ops == ["Body"], ops
        bpy.ops.mesh.primitive_cube_add()                  # two candidates of every kind: a note, no guess
        bpy.context.view_layer.objects.active = empty
        log = _draw("BONEFORGE_PT_p2b_delta_mush", bpy.context)
        assert not any(n == "operator" and a and a[0] == "boneforge.select_object" for n, a, k in log)

        # Rig Builder lists the Auto-Rig Wizard first, then Quick Rig, then Mannequin
        from boneforge.taskboard import sidebar as sb
        assert sb.BF_PT_sb_wizard.bl_order < sb.BF_PT_sb_quick_rig.bl_order < sb.BF_PT_rb_mannequin.bl_order
        shelf = [getattr(bpy.types, n + "_Shelf").bl_order for n in ("BF_PT_sb_wizard", "BF_PT_sb_quick_rig",
                                                                      "BF_PT_rb_mannequin")]
        assert shelf[0] < shelf[1] < shelf[2], ("the viewport copies keep that order", shelf)

        # the rig is deleted: nothing in the BoneCraft, CATS or Rig Builder tab that shows while it exists
        # vanishes; it stays and says what to select
        def shown(table, idn):
            c = by_id[idn]
            while True:
                if not table[c.bl_idname]:
                    return False
                parent = getattr(c, "bl_parent_id", "")
                if not parent or parent not in by_id:
                    return True
                c = by_id[parent]
        for ob in list(bpy.data.objects):
            bpy.data.objects.remove(ob)
        p_gone = {c.bl_idname: _poll(c) for c in panels}
        vanished = sorted(i for i in by_id if shown(p_rig, i) and not shown(p_gone, i))
        assert not vanished, ("hidden once the rig is gone", vanished)
        for idn in ("BF_PT_sb_vrchat", "BF_PT_cats_vrc_tools"):
            assert set(_texts(_draw(idn, bpy.context))) & needs.NOTES, (idn, "says what to select")
        for c in panels:                                   # every fold under the CATS tools says what it needs
            if getattr(c, "bl_parent_id", "") == "CATS_PT_main" and c.bl_idname != "CATS_PT_target_armature":
                assert set(_texts(_draw(c.bl_idname, bpy.context))) & needs.NOTES, (c.bl_idname, "says what to select")

        # only a mesh, no armature: Avatar Tools shows, and its armature-only sections stay and say so
        bpy.ops.mesh.primitive_cube_add()
        bpy.context.view_layer.objects.active = bpy.context.active_object
        p_mesh_only = {c.bl_idname: _poll(c) for c in panels}
        for idn in ("BF_PT_sb_vrc_humanoid", "BF_PT_sb_vrc_hair", "BF_PT_sb_vrc_export"):
            assert shown(p_mesh_only, idn), (idn, "vanished with only a mesh")
            assert "Select an armature to use this." in _texts(_draw(idn, bpy.context)), idn
    finally:
        boneforge.unregister()
    print("PASS show-don't-hide: 10 gated panels stay visible with a 'needs' note, a Select button for a single "
          "candidate, their tools when satisfied; the tab switch still hides")
