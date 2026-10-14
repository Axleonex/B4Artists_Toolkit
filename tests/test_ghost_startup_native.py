"""Disposable saved-preference startup check; never use the owner's profile.

GHOST_STARTUP_PHASE=seed writes isolated preferences; gui verifies the addon
was already enabled during startup, before this script executes.
"""
import json
import os
from pathlib import Path
import traceback

OUTPUT = Path(os.environ['GHOST_STARTUP_OUTPUT'])
PHASE = os.environ['GHOST_STARTUP_PHASE']
OUTPUT.mkdir(parents=True, exist_ok=True)
OUTPUT.joinpath('startup-' + PHASE + '-entered.txt').write_text('Python script entered', encoding='utf-8')

import bpy
import addon_utils
import ghost_tool
from ghost_tool import ui_panel as ui


def seed():
    addon_utils.enable('ghost_tool', default_set=True, persistent=True)
    assert addon_utils.check('ghost_tool')[1]
    assert ghost_tool._is_bforartists()
    prefs = bpy.context.preferences.addons['ghost_tool'].preferences
    prefs.auto_widen_shelf = False  # Isolate startup initialization from width writes.
    prefs.display_location = 'TOOLS'
    bpy.ops.wm.save_userpref()
    OUTPUT.joinpath('startup-seed-result.json').write_text(json.dumps(dict(
        status='PASS', enabled=True, location=prefs.display_location,
        host=bpy.app.version_string, build_hash=bpy.app.build_hash.decode())), encoding='utf-8')


checks = []
state = {'step': 0}


def check(name, condition):
    assert condition, name
    checks.append(name)


def tick():
    try:
        area = next(a for a in bpy.context.window.screen.areas if a.type == 'VIEW_3D')
        region = next(r for r in area.regions if r.type == 'WINDOW')
        prefs = bpy.context.preferences.addons['ghost_tool'].preferences
        with bpy.context.temp_override(area=area, region=region):
            space = area.spaces.active
            step = state['step']
            if step == 0:
                check('Ghost enabled automatically from saved startup preferences', addon_utils.check('ghost_tool')[1])
                check('Native host gate is unchanged', ghost_tool._is_bforartists())
                check('Saved Tools location applied after startup', prefs.display_location == 'TOOLS' and space.show_region_toolbar)
                check('Deferred startup callback completed', not bpy.app.timers.is_registered(ui._apply_display_location_update))
                prefs.display_location = 'SIDEBAR'
            elif step == 1:
                check('Sidebar preference still reveals the native panel', space.show_region_ui)
                prefs.display_location = 'TOOLBAR'
                prefs.show_toolbar = False
                space.show_region_tool_header = False
            elif step == 2:
                check('Hidden toolbar choice does not reopen the row', not space.show_region_tool_header)
                prefs.show_toolbar = True
            elif step == 3:
                check('Explicit show reveals the row after deferral', space.show_region_tool_header)
                ui.schedule_display_location_update()
                old = ui._apply_display_location_update
                addon_utils.disable('ghost_tool', default_set=True)
                check('Disabling addon cancels queued UI access', not bpy.app.timers.is_registered(old))
                OUTPUT.joinpath('startup-result.json').write_text(json.dumps(dict(
                    status='PASS', checks=checks, host=bpy.app.version_string,
                    build_hash=bpy.app.build_hash.decode(), startup_auto_enabled=True,
                    shelf_memory_writes_disabled_for_isolation=True), indent=2), encoding='utf-8')
                bpy.ops.wm.quit_blender()
                return None
            state['step'] += 1
        return 1.0
    except Exception:
        OUTPUT.joinpath('startup-result.json').write_text(json.dumps(dict(
            status='FAIL', checks=checks, state=state, error=traceback.format_exc()), indent=2), encoding='utf-8')
        bpy.ops.wm.quit_blender()
        return None


if PHASE == 'seed':
    seed()
else:
    assert PHASE == 'gui'
    bpy.app.timers.register(tick, first_interval=2.0)
