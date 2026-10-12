# bonecraft/tests/test_mech_guide_host.py
"""In-Bforartists test: guided build sessions — picking, building, preview, Enter keeps, Esc removes."""
import bmesh
import bpy
from mathutils import Matrix

import boneforge


def _cube(name, loc):
    bpy.ops.mesh.primitive_cube_add(size=0.2, location=loc)
    bpy.context.object.name = name
    return bpy.context.object


def run():
    bpy.ops.wm.read_factory_settings(use_empty=True)   # an empty scene: no names or modes left by earlier tests
    boneforge.register()
    try:
        from boneforge.mechanisms import build, guide, parts, records          # after register
        objs = [_cube(n, (i, 0, 0)) for i, n in enumerate(("Base", "Lid", "Seg1", "Seg2"))]
        stray = _cube("Stray", (9, 0, 0))
        bpy.ops.object.select_all(action='DESELECT')
        for ob in objs:
            ob.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        arm, pids, _ = parts.add_parts_from_selection(bpy.context)
        rec = arm.data.bonecraft_mech
        base, lid, s1, s2 = pids

        # a click outside the rig is refused; the hinge builds and previews once the axis is chosen
        s = guide.GuideSession(bpy.context, arm, "HINGE")
        assert not s.pick(stray) and "not a part" in s.message
        assert s.pick(objs[1]) and s.built is None
        s.key("X")
        assert s.built is not None and s.sweep is not None, "built and previewing"
        rig = records.to_model(arm)
        before = [c.copy() for c in s.outline_now(lid)]
        build.set_value(arm, rig, s.built, 90.0)
        bpy.context.view_layer.update()
        assert len(before) == 8 and max((a - b).length for a, b in zip(s.outline_now(lid), before)) > 0.05,             "the outline follows the part as it moves"
        build.set_value(arm, rig, s.built, 0.0)
        for _ in range(5):
            s.tick()
        hinge_id = s.confirm()
        assert records.find(arm.data, hinge_id).type == "HINGE" and abs(build.get_value(arm, records.to_model(arm), hinge_id)) < 1e-6, \
            "Enter keeps it, and the preview leaves the pose at rest"

        # Esc removes it again, and puts back the parents a Telescope changed
        t = guide.GuideSession(bpy.context, arm, "TELESCOPE")
        t.pick(objs[0])
        t.pick(objs[2])
        t.pick(objs[3])
        t.key("ENTER")
        t.key("Z")
        assert t.built is not None and records.find(arm.data, s2).parent == s1
        t.tick()
        t.cancel()
        assert records.find(arm.data, t.built) is None and records.find(arm.data, s2).parent == "" and len(rec.mechanisms) == 1

        # a failing build.delete does not escape cancel(): the message says why and the parents still come back
        t2 = guide.GuideSession(bpy.context, arm, "TELESCOPE")
        for ob in (objs[0], objs[2], objs[3]):
            t2.pick(ob)
        t2.key("ENTER")
        t2.key("Z")
        assert t2.built is not None and records.find(arm.data, s2).parent == s1
        real_delete = build.delete

        def _failing_delete(*_a, **_k):
            build.delete = real_delete                   # fail once, then behave
            raise build.BuildError("delete failed")
        build.delete = _failing_delete
        try:
            t2.cancel()
        finally:
            build.delete = real_delete
        assert "delete failed" in t2.message and records.find(arm.data, s2).parent == "", "parents restored despite the failure"
        real_delete(arm, t2.built)                       # the failed delete left the mechanism; remove it for the next checks

        # clicks count only inside the viewport region (edges included)
        w, h = 400, 300
        assert guide.inside_region(w, h, 10, 10) and guide.inside_region(w, h, 0, 0) and guide.inside_region(w, h, w, h)
        assert guide.inside_region(w, h, 0, h) and guide.inside_region(w, h, w, 0)
        assert not guide.inside_region(w, h, -1, 10) and not guide.inside_region(w, h, 10, -1)
        assert not guide.inside_region(w, h, w + 1, 10) and not guide.inside_region(w, h, 10, h + 1)

        # a click over the sidebar is not a pick even when the sidebar overlaps the WINDOW region
        from types import SimpleNamespace as NS
        win = NS(type='WINDOW', x=0, y=0, width=400, height=300)
        side = NS(type='UI', x=300, y=0, width=100, height=300)
        view = NS(type='VIEW_3D', regions=[win, side], width=400, height=300)
        assert guide._click_in_viewport(view, win, NS(mouse_x=100, mouse_y=100))
        assert not guide._click_in_viewport(view, win, NS(mouse_x=350, mouse_y=100)), "over the sidebar"
        assert not guide._click_in_viewport(view, win, NS(mouse_x=450, mouse_y=100)), "outside the region"

        # started from another region or editor (the sidebar's Add menu, the Scene tab), clicks still map to the viewport
        moved = NS(type='WINDOW', x=50, y=20, width=400, height=300, data=object())
        assert guide.region_coords(moved, NS(mouse_x=150, mouse_y=120)) == (100, 100), "window coordinates minus the region's corner"
        assert guide._click_in_viewport(NS(regions=[moved]), moved, NS(mouse_x=60, mouse_y=30))
        assert not guide._click_in_viewport(NS(regions=[moved]), moved, NS(mouse_x=40, mouse_y=30)), "left of the moved region"
        small = NS(type='VIEW_3D', regions=[NS(type='UI'), moved], width=200, height=100)
        big = NS(type='VIEW_3D', regions=[moved], width=800, height=600)
        props = NS(type='PROPERTIES', regions=[], width=300, height=900)
        screen = NS(areas=[small, props, big])
        assert guide.target_area(NS(area=small, screen=screen)) is small, "the current 3D Viewport first"
        assert guide.target_area(NS(area=props, screen=screen)) is big, "from the Scene tab: the largest 3D Viewport"
        assert guide.target_area(NS(area=None, screen=screen)) is big
        assert guide.target_area(NS(area=props, screen=NS(areas=[props]))) is None, "no 3D Viewport on the screen"
        assert guide.target_area(NS(area=None, screen=None)) is None
        assert guide.window_region(small) is moved and guide.window_region(None) is None
        assert guide._drawing_ours(NS(_area=big), big) and not guide._drawing_ours(NS(_area=big), small),             "outlines and labels draw only in the viewport the build works in"
        seen, real_ours = [], guide._drawing_ours
        guide._drawing_ours = lambda op_, area_: seen.append(area_) or False
        try:                                             # started from the Scene tab: the handlers' own context is PROPERTIES
            for fn in (guide._draw_outlines, guide._draw_labels):
                fn(NS(_area=big), NS(area=props))
        finally:
            guide._drawing_ours = real_ours
        assert seen == [bpy.context.area] * 2 and props not in seen,             "the draw handlers read the area being drawn now, not the invoking editor"

        # Blender cancels the modal (window closed, file loaded): the session is cancelled, timer and texts removed
        op = guide.BC_OT_mech_guide
        assert "cancel" in op.__dict__, "the Guide defines cancel()"
        calls = []
        area = NS(header_text_set=lambda t: calls.append(("header", t)), tag_redraw=lambda: calls.append("redraw"))
        ctx = NS(window_manager=NS(event_timer_remove=lambda t: calls.append(("timer", t))), area=None,
                 workspace=NS(status_text_set=lambda t: calls.append(("status", t))))
        for fails in (False, True):
            calls.clear()

            def _cancel(fails=fails):
                calls.append("session.cancel")
                if fails:
                    raise RuntimeError("cancel failed")
            fake = NS(session=NS(cancel=_cancel), _handles=(), _timer="T", _area=area)
            fake._end = lambda c, r, fake=fake: op._end(fake, c, r)
            op.cancel(fake, ctx)
            assert calls[0] == "session.cancel" and ("timer", "T") in calls and ("header", None) in calls                 and ("status", None) in calls, (fails, calls)

        # a Gear Link needs a hinge on the driving part; a failed build steps back and says why
        g = guide.GuideSession(bpy.context, arm, "GEAR")
        assert not g.pick(objs[0]) and "needs a Hinge" in g.message
        assert g.pick(objs[1])
        assert not g.pick(objs[1]) and "already picked" in g.message

        # loose pieces are picked by the face that was clicked
        mesh = bpy.data.meshes.new("Pieces")
        bm = bmesh.new()
        for off in (0.0, 2.0):
            bmesh.ops.create_cube(bm, size=0.2, matrix=Matrix.Translation((off, 3, 0)))
        bm.to_mesh(mesh)
        bm.free()
        pieces = bpy.data.objects.new("Pieces", mesh)
        bpy.context.scene.collection.objects.link(pieces)
        bpy.ops.object.select_all(action='DESELECT')
        pieces.select_set(True)
        arm.select_set(True)
        bpy.context.view_layer.objects.active = arm
        _, loose, _ = parts.add_parts_from_selection(bpy.context)
        far_face = next(f.index for f in mesh.polygons if f.center.x > 1.0)
        assert guide.part_at(arm, pieces, far_face) == loose[1] and guide.part_at(arm, pieces, 0) == loose[0]
        assert guide.part_at(arm, stray, 0) is None
        box = guide.part_corners(arm, loose[1])
        assert len(box) == 8 and abs(min(c.x for c in box) - 1.9) < 1e-4 and abs(max(c.x for c in box) - 2.1) < 1e-4,             "a loose piece is outlined around its own vertices"
        lp = guide.GuideSession(bpy.context, arm, "PISTON")
        assert lp.pick(pieces, far_face) and len(lp.outline_now(loose[1])) == 8, "a picked loose piece gets an outline"
        assert len(guide.part_corners(arm, base)) == 8

        # renamed part objects are still picked and outlined
        objs[0].name, pieces.name = "Base Renamed", "Pieces Renamed"
        assert guide.part_at(arm, objs[0], 0) == base and guide.part_at(arm, pieces, far_face) == loose[1]
        assert len(guide.part_corners(arm, base)) == 8 and len(guide.part_corners(arm, loose[1])) == 8
        rp = guide.GuideSession(bpy.context, arm, "HINGE")
        assert rp.pick(objs[0]) and len(rp.outline_now(base)) == 8, rp.message

        assert hasattr(bpy.types, "BONEFORGE_OT_mech_guide"), "registered (bpy.types uses the idname form)"
        assert bpy.context.area is None and bpy.ops.boneforge.mech_guide.poll(),             "outside a 3D Viewport (here: no area at all) any screen with one will do; the background screen has one"
    finally:
        boneforge.unregister()
    print("PASS mechanisms guided build: picks, preview, Enter keeps, Esc removes, loose pieces")
