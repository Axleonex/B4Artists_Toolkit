"""Real-GUI check that Timeline row hover text is never cut off.

Run:  bforartists --factory-startup --enable-event-simulate --python tooltip_check.py
with BLENDER_USER_SCRIPTS holding the package as B4_anim_assist and AA_STAGE_OUT set.
For every control on each stage row (240 px Timeline), the wrapped hover text must hold
every word of the hover paragraphs and fit the Timeline. Then a greyed Deliver tool, a
Deliver tool and a Spline slider are hovered with simulated mouse moves and captured.
"""
import os
import sys
import traceback
from pathlib import Path

import addon_utils
import blf
import bpy

OUT = Path(os.environ["AA_STAGE_OUT"])
OUT.mkdir(parents=True, exist_ok=True)
log = open(OUT / "tooltip-log.txt", "w", encoding="utf-8", buffering=1)
addon_utils.enable("B4_anim_assist", default_set=True, persistent=False)
bpy.context.preferences.use_preferences_save = False
bpy.context.preferences.view.show_splash = False
PROP = "animassist_timeline_stage"
results = []


def check(name, ok):
    results.append((name, bool(ok)))
    log.write(("PASS " if ok else "FAIL ") + name + "\n")


def overlay():
    return sys.modules["B4_anim_assist.ui.timeline_overlay"]


def model():
    return sys.modules["B4_anim_assist.ui.timeline_config"]


def window():
    return bpy.context.window_manager.windows[0]


def timeline():
    return next(a for a in window().screen.areas
                if a.type == "DOPESHEET_EDITOR" and a.spaces.active.mode == "TIMELINE")


def region():
    return next(r for r in timeline().regions if r.type == "WINDOW")


def setup():
    win = window()
    small = timeline()
    view = max((a for a in win.screen.areas if a.type == "VIEW_3D"), key=lambda a: a.width * a.height)
    before = {a.as_pointer() for a in win.screen.areas}
    with bpy.context.temp_override(window=win, area=view):
        bpy.ops.screen.area_split(direction="HORIZONTAL", factor=240 / view.height)
    lower = min((a for a in win.screen.areas if a.as_pointer() not in before), key=lambda a: a.y)
    small.type = "INFO"
    lower.type = "DOPESHEET_EDITOR"
    lower.spaces.active.mode = "TIMELINE"
    obj = bpy.data.objects.get("Cube") or bpy.data.objects.new("Mover", None)
    if obj.name not in bpy.context.view_layer.objects:
        bpy.context.scene.collection.objects.link(obj)
    for frame, x in ((1, 0.0), (12, 2.0), (24, 0.0)):
        obj.location.x = x
        obj.keyframe_insert("location", index=0, frame=frame)
    from B4_anim_assist.core.fcurve_compat import get_fcurves
    for fc in get_fcurves(obj.animation_data.action, anim_data=obj.animation_data):
        for key in fc.keyframe_points:
            key.select_control_point = True  # key-type tools are available, so icons draw at full strength
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.context.scene.frame_set(30)


def items():
    with bpy.context.temp_override(window=window(), area=timeline(), region=region()):
        return overlay()._items(bpy.context)[0]


def audit(stage):
    setattr(window().workspace, PROP, stage)
    scale = bpy.context.preferences.system.ui_scale
    reg = region()
    bad, count = [], 0
    with bpy.context.temp_override(window=window(), area=timeline(), region=reg):
        for item in overlay()._items(bpy.context)[0]:
            paragraphs = overlay()._tooltip_paragraphs(bpy.context, item)
            blf.size(0, round(11 * scale))
            lines, width, height = model().fit_tooltip(
                paragraphs, reg.width, reg.height, lambda t: blf.dimensions(0, t)[0],
                scale, 15 * scale, 7 * scale, 420 * scale)
            words_in = " ".join(t for t, _ in paragraphs).split()
            words_out = " ".join(t for t, _ in lines).split()
            count += 1
            if words_in != words_out or height > reg.height or width > reg.width:
                bad.append(f"{item[0]}:{item[1]} ({len(words_out)}/{len(words_in)} words, h {height:.0f}/{reg.height})")
    log.write(f"{stage}: {count} controls; region {reg.width}x{reg.height}\n")
    for line in bad:
        log.write("  cut: " + line + "\n")
    check(f"{stage}: every hover text shows in full", count > 0 and not bad)


def hover(stage, key, name):
    setattr(window().workspace, PROP, stage)
    item = next(i for i in items() if i[1].split(":", 1)[0] == key)
    x, y, w, h = item[3]
    window().event_simulate(type="MOUSEMOVE", value="NOTHING",
                            x=round(region().x + x + w / 2), y=round(region().y + y + h / 2))
    state["shot"] = name


def sample_icons(shot_name):
    """{action: (drawn RGB, theme RGB, label)} for Block's key-type icons in a capture."""
    with bpy.context.temp_override(window=window(), screen=window().screen):
        bpy.ops.screen.screenshot(filepath=str(OUT / shot_name))
    image = bpy.data.images.load(str(OUT / shot_name))
    width = image.size[0]
    pixels = image.pixels[:]
    reg = region()
    out = {}
    for item in items():
        if item[1] in overlay()._KEY_ICONS:
            x, y, w, h = item[3]
            i = (round(reg.y + y + h / 2) * width + round(reg.x + x + w / 2)) * 4
            out[item[1]] = (pixels[i:i + 3], overlay().key_icon_style(bpy.context, item[1])[0], item[2])
    bpy.data.images.remove(image)
    return out


def icon_faded():
    """With no keys selected the key-type tools are unavailable and their icons fade."""
    from B4_anim_assist.core.fcurve_compat import get_fcurves
    obj = bpy.context.view_layer.objects.active
    for fc in get_fcurves(obj.animation_data.action, anim_data=obj.animation_data):
        for key in fc.keyframe_points:
            key.select_control_point = False
    for a in window().screen.areas:
        a.tag_redraw()
    state["faded"] = True


def icon_faded_check():
    strip = sys.modules["B4_anim_assist.ui.timeline_strip"]
    with bpy.context.temp_override(window=window(), area=timeline(), region=region()):
        reason = strip._unavailable(bpy.context, timeline(), "TYPE_KEYFRAME")
        obj = bpy.context.object
    log.write(f"  reason now: {reason!r}; object {obj and obj.name}" + chr(10))
    samples = sample_icons("block-icons-unavailable.png")
    for action, (got, fill, _label) in samples.items():
        log.write(f"  {action} unavailable: drawn {tuple(round(v, 2) for v in got)}" + chr(10))
    check("Unavailable key-type icons are drawn faded",
          len(samples) == 4 and all(max(fill) - max(got) > .2 for got, fill, _l in samples.values()))


def icon_colours():
    """Block's key-type icons are drawn in the theme's key colours (sampled from a capture)."""
    setattr(window().workspace, PROP, "BLOCK")
    shot_name = "block-icons.png"
    with bpy.context.temp_override(window=window(), screen=window().screen):
        bpy.ops.screen.screenshot(filepath=str(OUT / shot_name))
    image = bpy.data.images.load(str(OUT / shot_name))
    width, height = image.size
    pixels = image.pixels[:]
    reg = region()
    bad = []
    for item in items():
        if item[1] not in overlay()._KEY_ICONS:
            continue
        x, y, w, h = item[3]
        px, py = round(reg.x + x + w / 2), round(reg.y + y + h / 2)
        i = (py * width + px) * 4
        got = pixels[i:i + 3]
        fill = overlay().key_icon_style(bpy.context, item[1])[0]
        log.write(f"  {item[1]}: drawn {tuple(round(v, 2) for v in got)} theme {tuple(round(v, 2) for v in fill)}" + chr(10))
        if item[2] or any(abs(a - b) > .12 for a, b in zip(got, fill)):
            bad.append(item[1])
    check("Block key-type icons drawn in the theme's key colours", len(bad) == 0 and image is not None)
    bpy.data.images.remove(image)


def shot():
    with bpy.context.temp_override(window=window(), screen=window().screen):
        bpy.ops.screen.screenshot(filepath=str(OUT / state["shot"]))


state = {}


def plan():
    yield setup, 1.5
    for stage in ("ALL", "BLOCK", "SPLINE", "POLISH", "DELIVER"):
        yield (lambda s=stage: audit(s)), 0.3
    yield (lambda: setattr(window().workspace, PROP, "BLOCK")), 0.6
    yield icon_colours, 0.3
    yield icon_faded, 0.8
    yield icon_faded_check, 0.3
    for stage in ("ALL", "BLOCK", "SPLINE", "POLISH", "DELIVER"):
        yield (lambda s=stage: setattr(window().workspace, PROP, s)), 0.6
        yield (lambda s=stage: (state.__setitem__("shot", f"row-{s.lower()}.png"), shot())), 0.3
    for stage, key, name in (("DELIVER", "BAKE_PREVIEW", "tooltip-deliver-greyed.png"),
                             ("DELIVER", "PROXY_BAKE", "tooltip-deliver-proxy-bake.png"),
                             ("SPLINE", "EASE", "tooltip-spline-ease.png")):
        yield (lambda s=stage, k=key, n=name: hover(s, k, n)), 1.2
        yield shot, 0.3
        yield (lambda: window().event_simulate(type="MOUSEMOVE", value="NOTHING", x=5, y=5)), 0.4


def runner():
    it = plan()

    def tick():
        try:
            fn, delay = next(it)
            fn()
            return delay
        except StopIteration:
            failed = [n for n, ok in results if not ok]
            log.write(f"RESULT {len(results) - len(failed)}/{len(results)} passed\n")
            log.close()
            bpy.ops.wm.quit_blender()
            return None
        except Exception:
            log.write(traceback.format_exc())
            log.close()
            bpy.ops.wm.quit_blender()
            return None
    return tick


bpy.app.timers.register(runner(), first_interval=2.0)
