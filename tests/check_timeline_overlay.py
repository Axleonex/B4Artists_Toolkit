"""Native GUI acceptance steps, run by observe_timeline_overlay's request API."""
import importlib
import json
import traceback

overlay = importlib.import_module('B4_anim_assist.ui.timeline_overlay')
tools = importlib.import_module('B4_anim_assist.ui.timeline_strip')
prefs_mod = importlib.import_module('B4_anim_assist.prefs')
compat = importlib.import_module('B4_anim_assist.core.fcurve_compat')
results = []
steps = []


def area_region():
    a = next(a for a in bpy.context.window.screen.areas if tools.is_timeline(a))
    return a, next(r for r in a.regions if r.type == 'WINDOW')


def event(kind, value='PRESS', **kwargs):
    bpy.context.window.event_simulate(type=kind, value=value, **kwargs)


def click(kind, key=''):
    a, r = area_region()
    with bpy.context.temp_override(area=a, region=r):
        items, band = overlay._items(bpy.context)
    item = next(item for item in items if item[:2] == (kind, key))
    x, y, w, h = item[3]
    xy = dict(x=round(r.x+x+w/2), y=round(r.y+y+h/2))
    event('MOUSEMOVE', 'NOTHING', **xy)
    event('LEFTMOUSE', **xy)
    event('LEFTMOUSE', 'RELEASE', **xy)


def screenshot(name):
    bpy.ops.screen.screenshot(filepath=str(root/(name+'.png')))


def fixture():
    global obj, before_area_count
    assert bpy.app.use_event_simulate
    assert not tools.native_available()
    a, r = area_region()
    assert a.height >= 110, a.height
    assert r.height > 50, r.height
    before_area_count = len(bpy.context.window.screen.areas)
    # Repeatable fixture: isolate this object's data from the previous run.
    for old in list(bpy.context.selected_objects):
        old.select_set(False)
    obj = bpy.data.objects.new('Toolbar Acceptance', None)
    bpy.context.scene.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    for frame, value in [(1, 0), (11, 10)]:
        obj.location.x = value
        obj.keyframe_insert(data_path='location', frame=frame)
    bpy.context.scene.frame_set(6)
    (root/'fresh-start.json').write_text(json.dumps(state(), indent=2))


def breakdown_check():
    assert bpy.context.scene.frame_current == 6
    assert abs(obj.location.x-2.5) < .001, list(obj.location)


def modal_begin():
    global modal_before, modal_keys
    modal_before = list(obj.location)
    modal_keys = [[list(k.co) for k in c.keyframe_points]
                  for c in compat.get_fcurves(obj.animation_data.action, anim_data=obj.animation_data)]
    a, r = area_region()
    with bpy.context.temp_override(area=a, region=r):
        items, _band = overlay._items(bpy.context)
    x, y, w, h = next(item[3] for item in items if item[:2] == ('ACTION', 'DRAG'))
    xy = dict(x=round(r.x+x+w/2), y=round(r.y+y+h/2))
    event('MOUSEMOVE', 'NOTHING', **xy)
    event('LEFTMOUSE', **xy)  # Drag Breakdown is a hold/release gesture.


def modal_move():
    a, r = area_region()
    event('MOUSEMOVE', 'NOTHING', x=r.x+650, y=r.y+10)


def modal_cancel():
    event('ESC')


def modal_cancel_check():
    keys = [[list(k.co) for k in c.keyframe_points]
            for c in compat.get_fcurves(obj.animation_data.action, anim_data=obj.animation_data)]
    assert keys == modal_keys, (keys, modal_keys)
    assert list(obj.location) == modal_before, (list(obj.location), modal_before)
    event('LEFTMOUSE', 'RELEASE')


def hide():
    prefs_mod.get_prefs().timeline_toolbar_row = False


def show():
    prefs_mod.get_prefs().timeline_toolbar_row = True


def key_row_click():
    """With the header on top, the band must leave the native key row clickable."""
    a, r = area_region()
    h = next(r for r in a.regions if r.type == 'HEADER')
    assert h.y > r.y
    scale = bpy.context.preferences.system.ui_scale
    with bpy.context.temp_override(area=a, region=r):
        items, band = overlay._items(bpy.context)
    assert band[1]+band[3] <= r.height-46*scale, (band, r.height)
    for curve in compat.get_fcurves(obj.animation_data.action, anim_data=obj.animation_data):
        for key in curve.keyframe_points:
            key.select_control_point = False
    x = r.x+r.view2d.view_to_region(11, 0, clip=False)[0]
    y = r.y+r.height-round(34*scale)
    event('MOUSEMOVE', 'NOTHING', x=x, y=y)
    event('LEFTMOUSE', x=x, y=y)
    event('LEFTMOUSE', 'RELEASE', x=x, y=y)


def key_row_check():
    selected = {round(k.co.x) for c in compat.get_fcurves(obj.animation_data.action, anim_data=obj.animation_data)
                for k in c.keyframe_points if k.select_control_point}
    assert selected == {11}, selected


def flip_header():
    a, _r = area_region()
    h = next(r for r in a.regions if r.type == 'HEADER')
    with bpy.context.temp_override(area=a, region=h):
        bpy.ops.screen.region_flip()


def bottom_check():
    a, r = area_region()
    h = next(r for r in a.regions if r.type == 'HEADER')
    assert h.y < r.y
    with bpy.context.temp_override(area=a, region=r):
        items, band = overlay._items(bpy.context)
    assert band[1] == 0


def resize(height):
    a, _r = area_region()
    with bpy.context.temp_override(area=a):
        bpy.ops.screen.area_move(x=a.x+a.width//2, y=a.y+a.height, delta=height-a.height)


def resize_edge():
    a, _r = area_region()
    event('MOUSEMOVE', 'NOTHING', x=a.x+a.width//2, y=a.y+a.height)


def short_check():
    a, _r = area_region()
    assert a.height == 85, a.height
    assert len(bpy.context.window.screen.areas) == before_area_count


def maximize():
    a, r = area_region()
    with bpy.context.temp_override(area=a, region=r):
        bpy.ops.screen.screen_full_area(use_hide_panels=False)


def native_scrub():
    a, r = area_region()
    event('MOUSEMOVE', 'NOTHING', x=r.x+400, y=r.y+r.height-10)
    event('LEFTMOUSE', x=r.x+400, y=r.y+r.height-10)
    event('LEFTMOUSE', 'RELEASE', x=r.x+400, y=r.y+r.height-10)


def scrub_check():
    assert bpy.context.scene.frame_current != 6, bpy.context.scene.frame_current


def save_preferences():
    cat = importlib.import_module('B4_anim_assist.ui.timeline_catalog')
    prefs = prefs_mod.get_prefs()
    setattr(prefs, cat.quick_property_name('COPY_KEYS'), True)
    bpy.ops.wm.save_userpref()
    bpy.ops.wm.save_as_mainfile(filepath=str(root/'toolbar-layout.blend'))


steps = [
    ('dismiss startup popup', lambda: event('ESC')),
    ('fresh default row and fixture', fixture),
    ('direct breakdown click', lambda: click('ACTION', 'B25')),
    ('direct action effect', breakdown_check),
    ('Search click', lambda: click('SEARCH')),
    ('Search rendered', lambda: screenshot('search-popup')),
    ('close Search', lambda: event('ESC')),
    ('Tween family click', lambda: click('MENU', 'tween')),
    ('family menu rendered', lambda: screenshot('family-menu')),
    ('close family', lambda: event('ESC')),
    ('Settings click', lambda: click('SETTINGS')),
    ('Settings rendered', lambda: screenshot('quick-settings')),
    ('close settings', lambda: event('ESC')),
    ('modal drag begin', modal_begin),
    ('modal drag move', modal_move),
    ('modal cancel', modal_cancel),
    ('modal cancellation effect', modal_cancel_check),
    ('hide row', hide),
    ('hidden render', lambda: screenshot('hidden')),
    ('show row', show),
    ('top header render', lambda: screenshot('top-header')),
    ('click native key under top header', key_row_click),
    ('native key row selection', key_row_check),
    ('flip native header', lambda: flip_header() if next(r for r in area_region()[0].regions if r.type=='HEADER').y > area_region()[1].y else None),
    ('bottom alignment', bottom_check),
    ('bottom header render', lambda: screenshot('bottom-header')),
    ('move pointer to native resize border', resize_edge),
    ('reduce Timeline height', lambda: resize(85)),
    ('manual height remains after discovery timer', short_check),
    ('small Timeline rendered', lambda: screenshot('small-timeline')),
    ('move pointer to border again', resize_edge),
    ('expand Timeline', lambda: resize(230)),
    ('maximize Timeline', maximize),
    ('maximized render', lambda: screenshot('maximized')),
    ('restore Timeline', maximize),
    ('native scrub', native_scrub),
    ('native scrub effect', scrub_check),
    ('pin and save preferences/layout', save_preferences),
    ('final rendered row', lambda: screenshot('final-row')),
]


def run_step():
    if not steps:
        return None
    label, operation = steps.pop(0)
    try:
        operation()
        results.append(dict(label=label, ok=True))
    except Exception:
        results.append(dict(label=label, ok=False, error=traceback.format_exc()))
    (root/'acceptance.json').write_text(json.dumps(dict(binary=bpy.app.binary_path,
        build_hash=bpy.app.build_hash.decode(), results=results), indent=2))
    return 1.2


bpy.app.timers.register(run_step, first_interval=1)
