"""Native header-removal evidence and installed width-API measurement.

Run in a disposable GUI config with --enable-event-simulate.
GHOST_PANEL_OUTPUT is the output directory. Width measurements document the
host limitation, not an automatic addon resizing implementation.
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
from test_ghost_toolbar_ui import Layout

OUTPUT = Path(os.environ['GHOST_PANEL_OUTPUT'])
OUTPUT.mkdir(parents=True, exist_ok=True)
state = {'step': 0}
checks = []


def check(name, condition):
    assert condition, name
    checks.append(name)


def capture(name):
    bpy.ops.screen.screenshot(filepath=str(OUTPUT / (name + '.png')))


def tick():
    try:
        window = bpy.context.window
        area = next(a for a in window.screen.areas if a.type == 'VIEW_3D')
        region = next(r for r in area.regions if r.type == 'WINDOW')
        with bpy.context.temp_override(window=window, area=area, region=region):
            step = state['step']
            if step == 0:
                window.event_simulate(type='ESC', value='PRESS')
                window.event_simulate(type='ESC', value='RELEASE')
                ghost_tool.register()
                bpy.context.preferences.addons.new().module = 'ghost_tool'
                bpy.ops.screen.screen_full_area()
            elif step == 1:
                check('No Ghost callback in main viewport menu row', not any(
                    getattr(f, '__module__', '') == ui.__name__
                    for f in getattr(bpy.types.VIEW3D_MT_editor_menus.draw, '_draw_funcs', ())))
                layout = Layout()
                ui._draw_viewport_tool_header(NS(layout=layout), bpy.context)
                check('Lower toolbar still contains all nine destinations',
                      len([c for c in layout.calls if c[0] == 'popover']) == 9)
                check('Lower toolbar retains master toggle and generation actions',
                      any(c[0] == 'prop' and c[1] == 'is_active' for c in layout.calls)
                      and {c[1] for c in layout.calls if c[0] == 'operator'} >=
                      {'ghost_tool.generate_ghosts', 'ghost_tool.generate_mesh_ghosts'})
                capture('header-clean-toolbar-preserved')
            elif step == 2:
                tools = next(r for r in area.regions if r.type == 'TOOLS')
                sidebar = next(r for r in area.regions if r.type == 'UI')
                check('Installed host width API is read-only',
                      bpy.types.Region.bl_rna.properties['width'].is_readonly)
                state['native_tools_width'] = tools.width
                state['right_width'] = sidebar.width
                bpy.ops.ghost_tool.set_toolbar_visibility(show=False)
                layout = Layout()
                ui._draw_viewport_view_menu(NS(layout=layout), bpy.context)
                check('Hidden toolbar has View-menu recovery',
                      any(c[0] == 'operator' and c[1] == 'ghost_tool.set_toolbar_visibility'
                          and c[4].show for c in layout.calls))
                bpy.ops.ghost_tool.set_toolbar_visibility(show=True)
                check('Recovery reveals native row', area.spaces.active.show_region_tool_header)
                area.spaces.active.show_region_tool_header = False
            elif step == 3:
                layout = Layout()
                ui._draw_viewport_view_menu(NS(layout=layout), bpy.context)
                check('Native-hidden row also has View-menu recovery',
                      any(c[0] == 'operator' and c[1] == 'ghost_tool.set_toolbar_visibility'
                          and c[4].show for c in layout.calls))
                bpy.ops.ghost_tool.set_toolbar_visibility(show=True)
            elif step == 4:
                layout = Layout()
                ui._draw_viewport_view_menu(NS(layout=layout), bpy.context)
                check('Recovery does not duplicate visible toolbar', not layout.calls)
                capture('header-clean-after-recovery')
                OUTPUT.joinpath('result.json').write_text(json.dumps(dict(
                    status='PASS', checks=checks, measurements=state,
                    shelf_width_fixed_automatically=False,
                    shelf_resize='Not implemented: installed width API is read-only',
                    host=bpy.app.version_string), indent=2), encoding='utf-8')
                bpy.ops.wm.quit_blender()
                return None
            state['step'] += 1
        return 0.7
    except Exception:
        error = traceback.format_exc()
        OUTPUT.joinpath('result.json').write_text(json.dumps(dict(
            status='FAIL', checks=checks, step=state['step'], error=error), indent=2), encoding='utf-8')
        print(error, flush=True)
        bpy.ops.wm.quit_blender()
        return None


bpy.app.timers.register(tick, first_interval=2.0)
