"""GUI screenshot of BoneCraft's sections in Properties > Scene tab (not part of CI).

Usage (from bonecraft/, GUI run, quits by itself):
    bforartists --window-geometry 0 0 1600 1000 --python tests/spikes/rb_placement_shots.py -- <outdir> <tag>

Run with BLENDER_USER_CONFIG pointing at a scratch folder whose userpref.blend
has the splash screen off, so the owner's own preferences are not touched.
Shoots the Scene tab scrolled to Rig Builder / CATS / VRChat / Import / Export
with nothing selected (they must show anyway). The asset shelf and the
preference switches are in the desktop hand check
(docs/bonecraft/rig-builder-placement-handcheck.md).
"""
import os
import sys

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
OUT, TAG = sys.argv[sys.argv.index("--") + 1:][:2]

import boneforge                                   # noqa: E402

boneforge.register()


def _win():
    return bpy.context.window_manager.windows[0]


def setup():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    bpy.ops.mesh.primitive_monkey_add(location=(0, 0, 1))
    bpy.context.view_layer.objects.active = None       # nothing selected on purpose
    for ob in bpy.context.selected_objects:
        ob.select_set(False)


def focus():
    for area in _win().screen.areas:
        if area.type == 'PROPERTIES':
            area.spaces.active.context = 'SCENE'
            region = [r for r in area.regions if r.type == 'WINDOW'][0]
            with bpy.context.temp_override(window=_win(), screen=_win().screen, area=area, region=region):
                for _ in range(6):
                    bpy.ops.view2d.scroll_down(page=True)
        area.tag_redraw()


def shoot():
    with bpy.context.temp_override(window=_win(), screen=_win().screen):
        bpy.ops.screen.screenshot(filepath=os.path.join(OUT, "rb_scene_tab_%s.png" % TAG))
    bpy.ops.wm.quit_blender()


bpy.app.timers.register(lambda: (setup(), None)[1], first_interval=1.5)
bpy.app.timers.register(lambda: (focus(), None)[1], first_interval=3.5)
bpy.app.timers.register(lambda: (shoot(), None)[1], first_interval=6.0)
