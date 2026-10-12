"""Isolated real-window shelf preview; never saves user preferences.

Run Bforartists --factory-startup --python tests/preview_starter_shelf.py.
"""
import json
import os
import sys

import bpy
bpy.context.preferences.view.show_splash = False

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from boneforge.autorig import quick_human as qh, rig_assets as ra

qh.register()
ra.register()
OUT = os.path.join(os.path.dirname(ROOT), 'docs', 'bonecraft', 'starter-shelf-implementation')
os.makedirs(OUT, exist_ok=True)
error_file = os.path.join(OUT, 'preview-error.log')
if os.path.exists(error_file):
    # Keep failed-run evidence separately; a successful rerun must not look failed.
    os.replace(error_file, os.path.join(OUT, 'preview-previous-error.log'))


def capture():
    areas = [a for a in bpy.context.screen.areas if a.type == 'VIEW_3D']
    states = []
    for area in areas:
        area.spaces.active.show_region_asset_shelf = True
        for region in area.regions:
            if region.type in {'ASSET_SHELF', 'ASSET_SHELF_HEADER'}:
                with bpy.context.temp_override(area=area, region=region):
                    shelf = bpy.context.asset_shelf
                    states.append({'region': region.type, 'shelf': shelf.bl_idname if shelf else None,
                                   'libraries': [(l.name, l.path) for l in bpy.context.preferences.filepaths.asset_libraries]})
                    if shelf:
                        shelf.show_names = True
                        shelf.preview_size = 96
    with open(os.path.join(OUT, 'window-state.json'), 'w') as f:
        json.dump(states, f, indent=2)
    bpy.ops.screen.screenshot(filepath=os.path.join(OUT, 'shelf-window.png'))
    if '--drag-only' in sys.argv:
        start_native_drag(156)
        bpy.app.timers.register(release_dependent_drag, first_interval=2)
        return
    area = areas[0]
    region = next(r for r in area.regions if r.type == 'WINDOW')
    with bpy.context.temp_override(area=area, region=region):
        bpy.ops.wm.call_asset_shelf_popover('INVOKE_DEFAULT', name=ra.SHELF_IDNAME)
    bpy.app.timers.register(capture_popup, first_interval=5)


def capture_popup():
    bpy.ops.screen.screenshot(filepath=os.path.join(OUT, 'shelf-popover.png'))
    bpy.context.window.event_simulate(type='ESC', value='PRESS')
    bpy.context.window.event_simulate(type='ESC', value='RELEASE')
    bpy.app.timers.register(show_dependency, first_interval=2)


def show_dependency():
    area = next(a for a in bpy.context.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    bpy.context.window.event_simulate(type='MOUSEMOVE', value='NOTHING', x=600, y=500)
    with bpy.context.temp_override(area=area, region=region):
        bpy.ops.boneforge.add_starter_asset('INVOKE_DEFAULT',
                                          relative_asset_identifier='quick_rigs.blend/Object/Full Human')
    bpy.app.timers.register(capture_dependency, first_interval=3)


def capture_dependency():
    bpy.ops.screen.screenshot(filepath=os.path.join(OUT, 'rigify-prompt.png'))
    bpy.context.window.event_simulate(type='ESC', value='PRESS')
    bpy.context.window.event_simulate(type='ESC', value='RELEASE')
    bpy.app.timers.register(check_cancel, first_interval=2)


def check_cancel():
    assert not [ob for ob in bpy.context.scene.objects if ob.type == 'ARMATURE']
    assert not qh.is_rigify_available()
    with open(os.path.join(OUT, 'popup-cancel.json'), 'w') as f:
        json.dump({'rig_count': 0, 'rigify_active': False, 'cancel_verified': True}, f)
    area = next(a for a in bpy.context.screen.areas if a.type == 'VIEW_3D')
    shelf_region = next(r for r in area.regions if r.type == 'ASSET_SHELF')
    window_region = next(r for r in area.regions if r.type == 'WINDOW')
    with bpy.context.temp_override(area=area, region=window_region):
        bpy.ops.ed.undo_push(message='Before starter shelf click')
    # Click the actual first thumbnail, through the native shelf's activation routing.
    x, y = shelf_region.x + 52, shelf_region.y + shelf_region.height - 52
    for event_type, value in [('MOUSEMOVE', 'NOTHING'), ('LEFTMOUSE', 'PRESS'), ('LEFTMOUSE', 'RELEASE')]:
        bpy.context.window.event_simulate(type=event_type, value=value, x=x, y=y)
    bpy.app.timers.register(check_click, first_interval=3)


def check_click():
    rigs = [ob for ob in bpy.context.scene.objects if ob.type == 'ARMATURE']
    assert len(rigs) == 1 and len(rigs[0].data.bones) == 19, [(r.name, len(r.data.bones)) for r in rigs]
    area = next(a for a in bpy.context.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    with bpy.context.temp_override(area=area, region=region):
        bpy.ops.ed.undo()
    bpy.app.timers.register(check_undo, first_interval=2)


def check_undo():
    assert not [ob for ob in bpy.context.scene.objects if ob.type == 'ARMATURE']
    area = next(a for a in bpy.context.screen.areas if a.type == 'VIEW_3D')
    region = next(r for r in area.regions if r.type == 'WINDOW')
    with bpy.context.temp_override(area=area, region=region):
        bpy.ops.ed.redo()
    bpy.app.timers.register(check_redo, first_interval=2)


def check_redo():
    rigs = [ob for ob in bpy.context.scene.objects if ob.type == 'ARMATURE']
    assert len(rigs) == 1 and len(rigs[0].data.bones) == 19
    with open(os.path.join(OUT, 'native-click-undo-redo.json'), 'w') as f:
        json.dump({'native_thumbnail_click': True, 'undo': True, 'redo': True}, f)
    area = next(a for a in bpy.context.screen.areas if a.type == 'VIEW_3D')
    shelf_region = next(r for r in area.regions if r.type == 'ASSET_SHELF')
    x, y = shelf_region.x + 156, shelf_region.y + shelf_region.height - 52
    for event_type, value in [('MOUSEMOVE', 'NOTHING'), ('LEFTMOUSE', 'PRESS'), ('LEFTMOUSE', 'RELEASE')]:
        bpy.context.window.event_simulate(type=event_type, value=value, x=x, y=y)
    bpy.app.timers.register(check_native_prompt, first_interval=3)


def check_native_prompt():
    assert not qh.is_rigify_available(), 'Native thumbnail must prompt before enabling Rigify'
    assert len([ob for ob in bpy.context.scene.objects if ob.type == 'ARMATURE']) == 1
    bpy.ops.screen.screenshot(filepath=os.path.join(OUT, 'native-rigify-prompt.png'))
    bpy.context.window.event_simulate(type='RET', value='PRESS')
    bpy.context.window.event_simulate(type='RET', value='RELEASE')
    bpy.app.timers.register(check_native_accept, first_interval=5)


def check_native_accept():
    rigs = [ob for ob in bpy.context.scene.objects if ob.type == 'ARMATURE']
    assert qh.is_rigify_available() and len(rigs) == 2
    assert bpy.context.active_object.name.startswith('FullHuman')
    assert qh._is_rigify_metarig(bpy.context.active_object)
    with open(os.path.join(OUT, 'native-rigify-accept.json'), 'w') as f:
        json.dump({'native_dependency_prompt': True, 'enable_and_add': True,
                   'selected_starter': 'Full Human', 'rig_count': 2}, f)
    bpy.ops.wm.quit_blender()


def start_native_drag(offset):
    area = next(a for a in bpy.context.screen.areas if a.type == 'VIEW_3D')
    shelf_region = next(r for r in area.regions if r.type == 'ASSET_SHELF')
    x, y = shelf_region.x + offset, shelf_region.y + shelf_region.height - 52
    for event_type, value, dx in [('MOUSEMOVE', 'NOTHING', 0), ('LEFTMOUSE', 'PRESS', 0),
                                  ('MOUSEMOVE', 'NOTHING', 22)]:
        bpy.context.window.event_simulate(type=event_type, value=value, x=x + dx, y=y)


def release_drag():
    for event_type, value in [('MOUSEMOVE', 'NOTHING'), ('LEFTMOUSE', 'RELEASE')]:
        bpy.context.window.event_simulate(type=event_type, value=value, x=550, y=450)


def release_dependent_drag():
    assert not [ob for ob in bpy.context.scene.objects if ob.type == 'ARMATURE']
    assert not qh.is_rigify_available()
    release_drag()
    bpy.app.timers.register(cancel_dependent_drag, first_interval=3)


def cancel_dependent_drag():
    assert not [ob for ob in bpy.context.scene.objects if ob.type == 'ARMATURE']
    assert not qh.is_rigify_available()
    bpy.ops.screen.screenshot(filepath=os.path.join(OUT, 'native-drag-rigify-prompt.png'))
    bpy.context.window.event_simulate(type='ESC', value='PRESS')
    bpy.context.window.event_simulate(type='ESC', value='RELEASE')
    bpy.app.timers.register(start_basic_drag, first_interval=2)


def start_basic_drag():
    assert not [ob for ob in bpy.context.scene.objects if ob.type == 'ARMATURE']
    start_native_drag(52)
    bpy.app.timers.register(release_basic_drag, first_interval=2)


def release_basic_drag():
    assert not [ob for ob in bpy.context.scene.objects if ob.type == 'ARMATURE']
    release_drag()
    bpy.app.timers.register(check_basic_drag, first_interval=3)


def check_basic_drag():
    rigs = [ob for ob in bpy.context.scene.objects if ob.type == 'ARMATURE']
    assert len(rigs) == 1 and len(rigs[0].data.bones) == 19
    assert not qh.is_rigify_available()
    with open(os.path.join(OUT, 'native-drag.json'), 'w') as f:
        json.dump({'dependency_prompt_before_insertion': True, 'cancel_adds_nothing': True,
                   'basic_drag_adds_19_bones_without_rigify': True, 'location': list(rigs[0].location)}, f)
    bpy.ops.wm.quit_blender()


def guarded(fn):
    def call():
        try:
            return fn()
        except Exception:
            import traceback
            with open(os.path.join(OUT, 'preview-error.log'), 'w') as f:
                f.write(traceback.format_exc())
            traceback.print_exc()
            bpy.ops.wm.quit_blender()
    return call


for name in ('capture', 'capture_popup', 'show_dependency', 'capture_dependency',
             'check_cancel', 'check_click', 'check_undo', 'check_redo',
             'check_native_prompt', 'check_native_accept', 'release_dependent_drag',
             'cancel_dependent_drag', 'start_basic_drag', 'release_basic_drag', 'check_basic_drag'):
    globals()[name] = guarded(globals()[name])
bpy.app.timers.register(capture, first_interval=120)
