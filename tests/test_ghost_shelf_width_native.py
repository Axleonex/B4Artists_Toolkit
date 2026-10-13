"""Actual default widening, reference/fallback widths and override preservation.

Disposable native Bforartists GUI only; GHOST_SHELF_OUTPUT selects evidence.
Controlled native width writes create resize fixtures. Matching is performed
by the registered addon timer, without a manual divider drag or host-gate patch.
"""
import json
import os
from pathlib import Path
import sys
import traceback

import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import ghost_tool
from ghost_tool import ui_panel as ui, shelf_width as sw
from ghost_tool.ghost_data import GhostStore

OUTPUT = Path(os.environ['GHOST_SHELF_OUTPUT'])
OUTPUT.mkdir(parents=True, exist_ok=True)
state = {'step': 0, 'waits': 0}
checks = []


def check(name, condition):
    assert condition, name
    checks.append(name)


def regions(area):
    return {r.type: r for r in area.regions if r.type in {'UI', 'TOOLS'}}


def capture(name):
    bpy.ops.screen.screenshot(filepath=str(OUTPUT / (name + '.png')))


def await_width(tools, expected):
    if abs(tools.width - expected) <= 1:
        state['waits'] = 0
        return False
    state['waits'] += 1
    assert state['waits'] <= 10, f"width {tools.width} did not reach {expected}; done={sw._done}"
    return True


def tick():
    try:
        window = bpy.context.window
        area = max((a for a in window.screen.areas if a.type == 'VIEW_3D'), key=lambda a: a.width * a.height)
        region = next(r for r in area.regions if r.type == 'WINDOW')
        with bpy.context.temp_override(window=window, area=area, region=region):
            step = state['step']
            if step == 0:
                window.event_simulate(type='ESC', value='PRESS')
                window.event_simulate(type='ESC', value='RELEASE')
                ghost_tool.register()
                bpy.ops.screen.screen_full_area()
            else:
                prefs = bpy.context.preferences.addons['ghost_tool'].preferences
                regs = regions(area)
                tools, sidebar = regs['TOOLS'], regs['UI']
                scale = bpy.context.preferences.system.ui_scale
                if step == 1:
                    check('Native host gate remains unpatched', ghost_tool._is_bforartists())
                    check('Auto widening defaults on', prefs.auto_widen_shelf)
                    area.spaces.active.show_region_ui = True
                    check('Reference fixture uses verified native width field', sw.set_width(area, sidebar, 360))
                    check('Narrow baseline uses verified native width field', sw.set_width(area, tools, 132))
                    bpy.ops.mesh.primitive_cube_add()
                    cube = bpy.context.active_object
                    for frame, x in ((1, 0), (15, 3)):
                        cube.location.x = x
                        cube.keyframe_insert('location', frame=frame)
                    bpy.context.scene.frame_set(8)
                    bpy.context.scene.ghost_tool['is_active'] = True
                    bpy.ops.ghost_tool.generate_ghosts()
                    state['markers'] = tuple(g.uid for g in GhostStore.get(bpy.context.scene))
                elif step == 2:
                    check('Before: left shelf is narrower than open N-panel', tools.width < sidebar.width)
                    state['before'] = dict(left=tools.width, right=sidebar.width, scale=scale)
                    prefs.display_location = 'TOOLS'
                    ui.update_display_location(bpy.context)
                elif step == 3:
                    if await_width(tools, sidebar.width):
                        return 0.7
                    check('Default timer matches open N-panel width', abs(tools.width - sidebar.width) <= 1)
                    check('Ghost shelf panel is available in selected left home', ui.GHOST_PT_tool_shelf.poll(bpy.context))
                    with bpy.context.temp_override(region=tools):
                        tools.active_panel_category = 'Ghost Tool'
                    state['matched'] = dict(left=tools.width, right=sidebar.width, scale=scale)
                elif step == 4:
                    check('Actual widened Ghost shelf category is visible', tools.active_panel_category == 'Ghost Tool')
                    capture('shelf-matched')
                    check('Manual resize fixture can narrow the shelf', sw.set_width(area, tools, 150))
                elif step == 5:
                    state['manual'] = tools.width
                    sw.widen_all()
                elif step == 6:
                    sw.widen_all()
                    check('Timer preserves later manually narrowed shelf', tools.width == state['manual'] and tools.width < sidebar.width)
                    prefs.auto_widen_shelf = False
                    prefs.auto_widen_shelf = True
                elif step == 7:
                    if await_width(tools, sidebar.width):
                        return 0.7
                    check('Explicit preference reset rechecks the default width', abs(tools.width - sidebar.width) <= 1)
                    prefs.auto_widen_shelf = False
                    check('Disabled fixture narrows the shelf', sw.set_width(area, tools, 132))
                elif step == 8:
                    sw.widen_all()
                    check('Disabling widening preserves the narrow shelf', tools.width <= 133)
                    area.spaces.active.show_region_ui = False
                    prefs.auto_widen_shelf = True
                elif step == 9:
                    if await_width(tools, round(sw.DEFAULT_MIN * scale)):
                        return 0.7
                    check('Closed N-panel uses BoneCraft 240px fallback', abs(tools.width - sw.DEFAULT_MIN * scale) <= 1)
                    state['fallback'] = dict(left=tools.width, scale=scale)
                    capture('shelf-fallback')
                    prefs.auto_widen_shelf = False
                    area.spaces.active.show_region_ui = True
                    bpy.context.preferences.view.ui_scale = 1.5
                elif step == 10:
                    check('Scale fixture changes native UI scale', scale > 1)
                    check('Scaled narrow fixture is verified', sw.set_width(area, tools, 132))
                    prefs.auto_widen_shelf = True
                elif step == 11:
                    if await_width(tools, sidebar.width):
                        return 0.7
                    check('Scaled default timer matches N-panel width', abs(tools.width - sidebar.width) <= 1)
                    state['scaled'] = dict(left=tools.width, right=sidebar.width, scale=scale)
                    capture('shelf-scaled')
                    bpy.context.preferences.view.ui_scale = 1.0
                elif step == 12:
                    check('Width changes preserve animation frame', bpy.context.scene.frame_current == 8)
                    check('Width changes preserve cached marker identities', state['markers'] == tuple(g.uid for g in GhostStore.get(bpy.context.scene)))
                    check('Width changes leave live updates disabled', not bpy.context.scene.ghost_tool.live_point_ghosts and not bpy.context.scene.ghost_tool.live_mesh_ghosts)
                    prefs.display_location = 'TOOLBAR'
                    check('No Ghost callback in main header row', not any(
                        getattr(f, '__module__', '') == ui.__name__
                        for f in getattr(bpy.types.VIEW3D_MT_editor_menus.draw, '_draw_funcs', ())))
                    check('One widening timer is registered', bpy.app.timers.is_registered(sw._tick))
                    check('One file-load reset is registered', bpy.app.handlers.load_post.count(sw.forget_all) == 1)
                    old_timer, old_reset = sw._tick, sw.forget_all
                    ghost_tool.unregister()
                    check('Unregister removes width timer', not bpy.app.timers.is_registered(old_timer))
                    check('Unregister removes width load handler and state', old_reset not in bpy.app.handlers.load_post and not sw._done)
                    ghost_tool.register()
                    check('Re-register has one fresh width timer', bpy.app.timers.is_registered(sw._tick))
                    check('Re-register has one file-load reset', bpy.app.handlers.load_post.count(sw.forget_all) == 1)
                    OUTPUT.joinpath('shelf-result.json').write_text(json.dumps(dict(
                        status='PASS', checks=checks, measurements=state,
                        host=bpy.app.version_string, automatic_timer=True,
                        native_gui_host_gate_patched=False), indent=2), encoding='utf-8')
                    bpy.ops.wm.quit_blender()
                    return None
            state['step'] += 1
        return 0.7
    except KeyError:
        # Preferences become available only after registration in step zero.
        if state['step'] == 1 and 'ghost_tool' not in bpy.context.preferences.addons:
            bpy.context.preferences.addons.new().module = 'ghost_tool'
            return 0.7
        return fail()
    except Exception:
        return fail()


def fail():
    error = traceback.format_exc()
    OUTPUT.joinpath('shelf-result.json').write_text(json.dumps(dict(
        status='FAIL', checks=checks, step=state['step'], error=error), indent=2), encoding='utf-8')
    print(error, flush=True)
    bpy.ops.wm.quit_blender()
    return None


bpy.app.timers.register(tick, first_interval=2.0)
