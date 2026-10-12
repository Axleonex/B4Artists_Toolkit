# bonecraft/tests/test_gesture_tools_host.py
"""In-Bforartists test: gesture first (UI critique, 2026-10-10).

Two BoneCraft tools sit in the 3D Viewport tool bar, so the day-to-day action is a click in the
viewport and its options are in the tool header:

- Place Rig Markers (Object Mode): during the Auto-Rig Wizard, a click on the mesh places the next
  marker of the current step.
- Build Mechanism (Object and Pose Mode): a click on a part starts a joint or link of the type
  chosen in the tool header; that first click is the first pick.
"""
import bpy
from mathutils import Vector

import boneforge


def _flat(items):
    for it in items:
        if it is None or callable(it):
            continue
        if type(it) is tuple:                       # a group; a ToolDef is a named tuple, not a group
            yield from _flat(it)
        else:
            yield it


def _count(mode, idname):
    from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active
    return sum(getattr(t, "idname", None) == idname for t in _flat(VIEW3D_PT_tools_active._tools.get(mode, ())))


def _in_toolbar(mode, idname):
    return _count(mode, idname) > 0


def _reload():
    """An add-on reload makes new tool classes: each tool still appears once, and unregister removes it."""
    import importlib
    from boneforge.autorig import tools as rig_tools
    from boneforge.mechanisms import tools as mech_tools
    for module in (rig_tools, mech_tools):
        importlib.reload(module).register()
    for mode, idname in (('OBJECT', "boneforge.place_rig_markers"), ('OBJECT', "boneforge.build_mechanism"),
                         ('POSE', "boneforge.build_mechanism")):
        assert _count(mode, idname) == 1, (mode, idname, _count(mode, idname))


def _op_rna(idname):
    cat, name = idname.split(".", 1)
    return getattr(getattr(bpy.ops, cat), name).get_rna_type()


def _tools_registered():
    assert _in_toolbar('OBJECT', "boneforge.place_rig_markers"), "Place Rig Markers is in the Object tool bar"
    for mode in ('OBJECT', 'POSE'):
        assert _in_toolbar(mode, "boneforge.build_mechanism"), (mode, "Build Mechanism is in the tool bar")
    from boneforge.autorig import tools as rig_tools
    from boneforge.mechanisms import tools as mech_tools
    (op, event, props), = rig_tools.BF_WT_place_rig_markers.bl_keymap
    assert op == "boneforge.autorig_place_marker_click" and event["type"] == 'LEFTMOUSE', (op, event)
    (op, event, props), = mech_tools.BC_WT_build_mechanism.bl_keymap
    assert op == "boneforge.mech_guide" and ("from_tool", True) in props["properties"], (op, props)
    prop = _op_rna("boneforge.mech_guide").properties["from_tool"]
    assert prop.is_hidden and prop.is_skip_save, "from_tool: set by the tool only, never remembered"


def _markers():
    from boneforge.autorig import constants as C, tools
    from boneforge.autorig.session import get_body_marker
    ctx = bpy.context
    bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.0, 1.0))
    mesh = ctx.active_object
    assert bpy.ops.boneforge.autorig_wizard_start() == {'FINISHED'}
    s = ctx.scene.boneforge_autorig_session
    s.mesh_object_name = mesh.name
    assert not bpy.ops.boneforge.autorig_place_marker_click.poll(), "only on a marker step"
    s.wizard_step = C.STEP_BODY_MARKERS
    assert bpy.ops.boneforge.autorig_place_marker_click.poll()
    mtype, first = tools.next_marker(s)
    assert mtype == 'BODY' and first not in C.OPTIONAL_BODY_MARKERS, (mtype, first)
    placed = tools.place_next_marker(ctx, Vector((0.0, -1.0, 1.0)))
    assert placed == first and get_body_marker(s, first).confirmed, (placed, first)
    after = tools.next_marker(s)[1]
    assert after is not None and after != first, after
    # the finger step lists the right hand too when the hands are not mirrored
    s.wizard_step = C.STEP_FINGER_MARKERS
    s.finger_symmetry = False
    mtype, names = tools.marker_order(s)
    assert mtype == 'FINGER' and any(n.endswith("_R") for n in names), names
    bpy.ops.boneforge.autorig_wizard_cancel()


def run():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    boneforge.register()
    try:
        _tools_registered()
        _markers()
        _reload()
    finally:
        boneforge.unregister()
    for mode, idname in (('OBJECT', "boneforge.place_rig_markers"), ('OBJECT', "boneforge.build_mechanism"),
                         ('POSE', "boneforge.build_mechanism")):
        assert not _in_toolbar(mode, idname), (mode, idname, "left behind after unregister")
    print("PASS gesture tools: Place Rig Markers and Build Mechanism are tool-bar tools")
