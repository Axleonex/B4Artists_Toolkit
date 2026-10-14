"""Host regression: BoneCraft must not break native Grab/tool cycling.

Run with Bforartists --background --factory-startup --python-exit-code 1 --python.
"""
import importlib
import sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import addon_utils
import bpy
from bl_ui.space_toolsystem_toolbar import VIEW3D_PT_tools_active as Panel

CUSTOM = {
    'OBJECT': {'boneforge.place_rig_markers', 'boneforge.build_mechanism'},
    'POSE': {'boneforge.build_mechanism'},
}


def _groups():
    return [tuple(getattr(tool, 'idname', None) for tool in group)
            for group in Panel.tools_from_context(bpy.context) if type(group) is tuple]


def _native_cycle():
    for name in ('builtin.select_box', 'builtin.move', 'builtin.rotate', 'builtin.scale',
                 'builtin.breakdowner', 'builtin.push', 'builtin.relax'):
        for _ in range(2):
            assert bpy.ops.wm.tool_set_by_id(name=name, cycle=True) == {'FINISHED'}, name
            if name == 'builtin.move':
                active = bpy.context.workspace.tools.from_space_view3d_mode(bpy.context.mode)
                assert active.idname == name, active.idname


def run():
    bpy.ops.object.armature_add()
    area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
    region = next(region for region in area.regions if region.type == 'WINDOW')
    baseline = {}
    with bpy.context.temp_override(area=area, region=region):
        for mode in CUSTOM:
            bpy.ops.object.mode_set(mode=mode)
            baseline[mode] = _groups()
            _native_cycle()
        bpy.ops.object.mode_set(mode='OBJECT')

        def check(enabled):
            for mode, names in CUSTOM.items():
                bpy.ops.object.mode_set(mode=mode)
                # Exercise the actual operator from the reported traceback first.
                _native_cycle()
                assert _groups() == baseline[mode], (mode, _groups())
                tools = list(Panel.tools_from_context(bpy.context))
                for name in names:
                    top_level = [tool for tool in tools if getattr(tool, 'idname', None) == name]
                    assert len(top_level) == int(enabled), (mode, name, top_level)
                    if enabled:
                        for _ in range(2):
                            assert bpy.ops.wm.tool_set_by_id(name=name, cycle=True) == {'FINISHED'}
                        active = bpy.context.workspace.tools.from_space_view3d_mode(mode)
                        assert active.idname == name, active.idname
                    else:
                        assert Panel._tool_get_by_id(bpy.context, name)[0] is None
            bpy.ops.object.mode_set(mode='OBJECT')

        try:
            assert addon_utils.enable('boneforge', default_set=True) is not None
            check(True)
            from boneforge.autorig import tools as rig_tools
            from boneforge.mechanisms import tools as mech_tools
            for module in (rig_tools, mech_tools):
                importlib.reload(module).register()
            check(True)
            # Emulate an older enabled copy, then reload the fixed registrations.
            from boneforge.core import toolbar
            for tool in (rig_tools.BF_WT_place_rig_markers, *mech_tools.TOOLS):
                toolbar.drop(tool)
                bpy.utils.register_tool(tool, after={'builtin.relax'}, separator=True, group=False)
            assert any(None in group for group in _groups())
            for module in (rig_tools, mech_tools):
                importlib.reload(module).register()
            check(True)
            addon_utils.disable('boneforge', default_set=True)
            check(False)
            assert addon_utils.enable('boneforge', default_set=True) is not None
            check(True)
        finally:
            bpy.ops.object.mode_set(mode='OBJECT')
            addon_utils.disable('boneforge', default_set=True)
        check(False)
    print('PASS toolbar cycling: native Grab/Move and grouped tools; standalone BoneCraft tools; '
          'Object/Pose modes; reload; legacy separator cleanup; disable/re-enable; native groups restored')


if __name__ == '__main__':
    run()
