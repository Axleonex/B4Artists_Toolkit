"""Native multi-viewport toolbar regression; run in a disposable GUI config.

GHOST_SPLIT_OUTPUT is the evidence directory. The harness launches with
--factory-startup --enable-event-simulate and this script on the Python path.
"""
import json
import os
from pathlib import Path
import sys
import traceback
from types import SimpleNamespace as NS

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))
import ghost_tool
from ghost_tool import ui_panel as ui
from ghost_tool.ghost_data import GhostStore
from test_ghost_toolbar_ui import Layout

OUTPUT = Path(os.environ['GHOST_SPLIT_OUTPUT'])
OUTPUT.mkdir(parents=True, exist_ok=True)
EXPECTED = ['GHOST_PT_toolbar_menu', 'GHOST_PT_marker_options',
            'GHOST_PT_skin_options', 'GHOST_PT_paths_popover',
            'GHOST_PT_edit_popover', 'GHOST_PT_compare_popover',
            'GHOST_PT_physics_popover', 'GHOST_PT_look_popover',
            'GHOST_PT_settings_popover']
state = {'step': 0}
checks = []


def check(name, condition):
    assert condition, name
    checks.append(name)


def capture(name):
    bpy.ops.screen.screenshot(filepath=str(OUTPUT / (name + '.png')))


def draw(window, area):
    header = next(r for r in area.regions if r.type == 'TOOL_HEADER')
    with bpy.context.temp_override(window=window, area=area, region=header):
        layout = Layout()
        ui._draw_viewport_tool_header(NS(layout=layout), bpy.context)
    return layout.calls


def assert_full(window, areas, label):
    for index, area in enumerate(areas):
        calls = draw(window, area)
        check(f'{label}: viewport {index + 1} has every feature in order',
              [c[1] for c in calls if c[0] == 'popover'] == EXPECTED)
        names = {c[1]: c[2].get('text') for c in calls if c[0] == 'popover'}
        master = [c for c in calls if c[0] == 'prop' and c[1] == 'is_active']
        check(f'{label}: viewport {index + 1} names sections and shows the master switch',
              names['GHOST_PT_marker_options'] == 'Marker options'
              and names['GHOST_PT_skin_options'] == 'Onion Skin options'
              and len(master) == 1 and master[0][2]['text'] == 'Ghosts On')


def tick():
    try:
        window = bpy.context.window_manager.windows[0]
        areas = sorted((a for a in window.screen.areas if a.type == 'VIEW_3D'),
                       key=lambda a: a.x)
        area = areas[0]
        region = next(r for r in area.regions if r.type == 'WINDOW')
        with bpy.context.temp_override(window=window, area=area, region=region):
            step = state['step']
            if step == 0:
                check('Actual native Bforartists host', ghost_tool._is_bforartists())
                bpy.context.preferences.view.show_splash = False
                window.event_simulate(type='ESC', value='PRESS')
                window.event_simulate(type='ESC', value='RELEASE')
                ghost_tool.register()
                bpy.context.preferences.addons.new().module = 'ghost_tool'
                prefs = bpy.context.preferences.addons['ghost_tool'].preferences
                check('Default is visible Top Toolbar',
                      prefs.display_location == 'TOOLBAR' and prefs.show_toolbar)
                animation = bpy.data.workspaces.get('Animation')
                if animation:
                    window.workspace = animation
                else:
                    bpy.ops.screen.area_split(direction='VERTICAL', factor=0.4)
            elif step == 1:
                check('Multiple native 3D viewports', len(areas) >= 2)
                ui.update_display_location(bpy.context)
                bpy.ops.mesh.primitive_cube_add()
                cube = bpy.context.active_object
                for frame, value in ((1, 0), (20, 5)):
                    cube.location.x = value
                    cube.keyframe_insert('location', frame=frame)
                bpy.context.scene.frame_set(10)
                bpy.context.scene.ghost_tool['is_active'] = True
                bpy.ops.ghost_tool.generate_ghosts()
                state['markers'] = tuple(g.uid for g in GhostStore.get(bpy.context.scene))
                state['geometry'] = [dict(width=a.width, height=a.height) for a in areas]
            elif step == 2:
                capture('split-object')
                check('Split viewports exercise the old collapsing widths',
                      any(a.width < 1150 for a in areas))
                assert_full(window, areas, 'Object mode')
                check('Native Tool Settings remains visible in every viewport',
                      all(a.spaces.active.show_region_tool_header for a in areas))
                bpy.ops.object.armature_add()
                bpy.ops.object.mode_set(mode='POSE')
            elif step == 3:
                capture('split-pose')
                assert_full(window, areas, 'Pose mode')
                bpy.context.preferences.view.ui_scale = 1.5
            elif step == 4:
                capture('split-scaled')
                assert_full(window, areas, 'Scaled Pose mode')
                bpy.context.preferences.view.ui_scale = 1.0
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.ghost_tool.set_toolbar_visibility(show=False)
                check('Hide applies to every viewport',
                      all(not draw(window, a) for a in areas))
                check('Hide keeps native Tool Settings',
                      all(a.spaces.active.show_region_tool_header for a in areas))
                bpy.ops.ghost_tool.set_toolbar_visibility(show=True)
                assert_full(window, areas, 'Show recovery')
            elif step == 5:
                header = next(r for r in area.regions if r.type == 'TOOL_HEADER')
                state['pan_before'] = header.view2d.region_to_view(0, 0)[0]
                state['pan_y'] = header.y + header.height // 2
                window.event_simulate(type='MOUSEMOVE', value='NOTHING',
                                      x=area.x + area.width - 30, y=state['pan_y'])
                window.event_simulate(type='MIDDLEMOUSE', value='PRESS',
                                      x=area.x + area.width - 30, y=state['pan_y'])
            elif step == 6:
                window.event_simulate(type='MOUSEMOVE', value='NOTHING',
                                      x=area.x + 30, y=state['pan_y'])
            elif step == 7:
                window.event_simulate(type='MIDDLEMOUSE', value='RELEASE',
                                      x=area.x + 30, y=state['pan_y'])
            elif step == 8:
                header = next(r for r in area.regions if r.type == 'TOOL_HEADER')
                state['pan_after'] = header.view2d.region_to_view(0, 0)[0]
                check('Native horizontal panning exposes overflowing controls',
                      abs(state['pan_after'] - state['pan_before']) > 1)
                capture('split-panned')
                bpy.ops.screen.area_split(direction='VERTICAL', factor=0.5)
            elif step == 9:
                check('Newly split viewport inherits visible native row',
                      len(areas) >= 3 and all(a.spaces.active.show_region_tool_header for a in areas))
                assert_full(window, areas, 'New split')
                capture('split-three')
                check('Drawing and layout actions preserve the frame',
                      bpy.context.scene.frame_current == 10)
                check('Drawing and hide/show preserve cached marker identities',
                      state['markers'] == tuple(g.uid for g in GhostStore.get(bpy.context.scene)))
                check('Layout does not enable live updates',
                      not bpy.context.scene.ghost_tool.live_point_ghosts
                      and not bpy.context.scene.ghost_tool.live_mesh_ghosts)
                check('Native header append remains registered exactly once', sum(
                    f is ui._draw_viewport_tool_header for f in
                    bpy.types.VIEW3D_HT_tool_header.draw._draw_funcs) == 1)
                OUTPUT.joinpath('result.json').write_text(json.dumps(dict(
                    status='PASS', checks=checks, geometry=state['geometry'],
                    pan_before=state['pan_before'], pan_after=state['pan_after'],
                    host=bpy.app.version_string), indent=2), encoding='utf-8')
                bpy.ops.wm.quit_blender()
                return None
            state['step'] += 1
        return 0.7
    except Exception:
        error = traceback.format_exc()
        OUTPUT.joinpath('result.json').write_text(json.dumps(dict(
            status='FAIL', checks=checks, step=state['step'], error=error), indent=2),
            encoding='utf-8')
        print(error, flush=True)
        bpy.ops.wm.quit_blender()
        return None


bpy.app.timers.register(tick, first_interval=2.0)
