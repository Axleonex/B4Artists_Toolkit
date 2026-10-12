"""Disposable GUI engine checks and actual viewport/popover captures.

Run with --factory-startup --enable-event-simulate. The test runner supplies
an isolated add-on/config, window size, screenshot prefix and result path.
"""
import json
import os
from pathlib import Path
import traceback

import bpy
import ghost_tool
from ghost_tool import ui_panel as ui

OUTPUT = Path(os.environ['GHOST_TOOLBAR_TEST_OUTPUT'])
PREFIX = os.environ['GHOST_TOOLBAR_SCREEN_PREFIX']
SCALE = float(os.environ.get('GHOST_TOOLBAR_TEST_SCALE', '1'))
state = {'step': 0}
checks = []


def check(name, condition):
    assert condition, name
    checks.append(name)


def capture(label):
    bpy.ops.screen.screenshot(filepath=PREFIX + '-' + label + '.png')


def tick():
    try:
        window = bpy.context.window_manager.windows[0]
        area = max((a for a in window.screen.areas if a.type == 'VIEW_3D'), key=lambda a:a.width)
        region = next(r for r in area.regions if r.type == 'WINDOW')
        with bpy.context.temp_override(window=window, area=area, region=region):
            step = state['step']
            if step == 0:
                assert not bpy.app.background
                bpy.context.preferences.view.show_splash = False
                bpy.context.preferences.view.ui_scale = SCALE
                # Setting show_splash stops future splashes; Escape dismisses
                # the splash already queued at factory startup.
                window.event_simulate(type='ESC', value='PRESS')
                window.event_simulate(type='ESC', value='RELEASE')
                if float(os.environ.get('GHOST_TOOLBAR_TEST_MAXIMIZE', '0')) and not state.get('maximized'):
                    # The OS clamps oversized windows to the physical screen.
                    # Maximize the native area to exercise the full layout.
                    bpy.ops.screen.screen_full_area(use_hide_panels=False)
                    # Maximize replaces the Area RNA object. Reacquire it on
                    # the next tick before testing the new native regions.
                    state['maximized'] = True
                    return 0.6
                # Direct registration keeps the stand-in gate patch intact;
                # addon_enable would reload the package and reset that patch.
                ghost_tool.register()
                if 'ghost_tool' not in bpy.context.preferences.addons:
                    bpy.context.preferences.addons.new().module = 'ghost_tool'
                prefs = bpy.context.preferences.addons['ghost_tool'].preferences
                prefs.display_location = 'TOOLBAR'
                prefs.show_toolbar = True
                state['prefs'] = prefs
                check('Toolbar preference reveals native row', area.spaces.active.show_region_tool_header)
                check('Native header append registered once', sum(
                    f is ui._draw_viewport_tool_header for f in
                    bpy.types.VIEW3D_HT_tool_header.draw._draw_funcs) == 1)
                cube = bpy.context.active_object
                for frame, value in ((1, 0), (20, 5)):
                    cube.location.x = value
                    cube.keyframe_insert('location', frame=frame)
                bpy.context.scene.frame_set(10)
                bpy.context.scene.ghost_tool['is_active'] = True
                bpy.ops.ghost_tool.generate_ghosts()
                bpy.ops.ghost_tool.generate_mesh_ghosts()
                check('Live options remain disabled', not bpy.context.scene.ghost_tool.live_point_ghosts
                      and not bpy.context.scene.ghost_tool.live_mesh_ghosts)
            elif step == 1:
                header = next(r for r in area.regions if r.type == 'TOOL_HEADER')
                state['geometry'] = dict(window_width=window.width, area_width=area.width,
                    header_width=header.width, scale=bpy.context.preferences.view.ui_scale)
                with bpy.context.temp_override(region=header):
                    state['geometry']['tier'] = ui._toolbar_tier(bpy.context)
                expected = os.environ.get('GHOST_TOOLBAR_TEST_TIER')
                check('Native viewport reaches the requested layout tier',
                      state['geometry']['tier'] == expected)
                capture('object')
                bpy.ops.object.armature_add()
                rig = bpy.context.active_object
                for frame, value in ((1, 0), (20, 3)):
                    rig.pose.bones[0].location.x = value
                    rig.pose.bones[0].keyframe_insert('location', frame=frame)
                bpy.ops.object.mode_set(mode='POSE')
                bpy.context.scene.frame_set(10)
            elif step == 2:
                capture('pose')
                window.event_simulate(type='MOUSEMOVE', value='NOTHING',
                                      x=area.x + area.width // 2, y=area.y + area.height // 2)
            elif step == 3:
                bpy.ops.wm.call_panel('INVOKE_DEFAULT', name='GHOST_PT_marker_options', keep_open=True)
            elif step == 4:
                capture('marker-options')
                window.event_simulate(type='ESC', value='PRESS')
                window.event_simulate(type='ESC', value='RELEASE')
                check('Opening options does not change the frame', bpy.context.scene.frame_current == 10)
            elif step == 5:
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = None
                check('Target action reports unavailable without selection', not bpy.ops.ghost_tool.generate_ghosts.poll())
            elif step == 6:
                capture('missing-target')
                from ghost_tool.ghost_data import GhostStore
                state['markers'] = tuple(g.uid for g in GhostStore.get(bpy.context.scene))
                state['skin_objects'] = tuple(o.as_pointer() for o in bpy.data.objects
                    if o.get('ghost_tool_mesh_ghost'))
                bpy.ops.ghost_tool.set_toolbar_visibility(show=False)
                check('Hide leaves the native row visible', area.spaces.active.show_region_tool_header)
            elif step == 7:
                capture('hidden')
                bpy.ops.wm.call_panel('INVOKE_DEFAULT', name='GHOST_PT_header_menu', keep_open=True)
            elif step == 8:
                capture('recovery-menu')
                window.event_simulate(type='ESC', value='PRESS')
                window.event_simulate(type='ESC', value='RELEASE')
            elif step == 9:
                area.spaces.active.show_region_tool_header = False
                bpy.ops.ghost_tool.set_toolbar_visibility(show=True)
                check('Show recovers a manually hidden native row', area.spaces.active.show_region_tool_header)
                from ghost_tool.ghost_data import GhostStore
                check('Hide/show preserves marker identity', state['markers'] == tuple(
                    g.uid for g in GhostStore.get(bpy.context.scene)))
                check('Hide/show preserves skin identity', state['skin_objects'] == tuple(
                    o.as_pointer() for o in bpy.data.objects if o.get('ghost_tool_mesh_ghost')))
                check('Main-header recovery remains available', ui.GHOST_PT_header_menu.poll(bpy.context))
                state['prefs'].display_location = 'HEADER'
                check('Leaving toolbar preserves native region choice', area.spaces.active.show_region_tool_header)
                ghost_tool.unregister()
                check('Unregister removes native append', ui._draw_viewport_tool_header not in
                      bpy.types.VIEW3D_HT_tool_header.draw._draw_funcs)
                ghost_tool.register()
                check('Reload appends exactly once', sum(f is ui._draw_viewport_tool_header for f in
                    bpy.types.VIEW3D_HT_tool_header.draw._draw_funcs) == 1)
                OUTPUT.write_text(json.dumps(dict(status='PASS', checks=checks,
                    geometry=state['geometry'], host=bpy.app.version_string), indent=2), encoding='utf-8')
                bpy.ops.wm.quit_blender()
                return None
            state['step'] += 1
        return 0.6
    except Exception:
        error = traceback.format_exc()
        OUTPUT.write_text(json.dumps(dict(status='FAIL', checks=checks, step=state['step'],
                                          error=error), indent=2), encoding='utf-8')
        print(error, flush=True)
        bpy.ops.wm.quit_blender()
        return None


bpy.app.timers.register(tick, first_interval=1.5)
