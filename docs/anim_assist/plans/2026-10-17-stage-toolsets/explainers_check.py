"""Real-GUI check of the Hover Explainers preference (Full, Short, Off) and shortcuts.

Run:  bforartists --factory-startup --enable-event-simulate --python explainers_check.py
with BLENDER_USER_SCRIPTS holding the package as B4_anim_assist and AA_STAGE_OUT set.
Operators register with an empty static description, so their hover text follows the
preference; a shortcut line appears only when a key is bound to that very tool. Row and
native button hovers are captured in each mode.
"""
import os
import sys
import traceback
from pathlib import Path
from types import SimpleNamespace

import addon_utils
import bpy

OUT = Path(os.environ["AA_STAGE_OUT"])
OUT.mkdir(parents=True, exist_ok=True)
log = open(OUT / "explainers-log.txt", "w", encoding="utf-8", buffering=1)
addon_utils.enable("B4_anim_assist", default_set=True, persistent=False)
bpy.context.preferences.use_preferences_save = False
bpy.context.preferences.view.show_splash = False
PROP = "animassist_timeline_stage"
results = []
state = {}


def check(name, ok):
    results.append((name, bool(ok)))
    log.write(("PASS " if ok else "FAIL ") + name + "\n")


def mod(name):
    return sys.modules["B4_anim_assist." + name]


def prefs():
    return mod("prefs").get_prefs(bpy.context)


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
    setattr(win.workspace, PROP, "ALL")
    # A native Anim Assist button at the left of the 3D View header, for a real tooltip.
    def draw(self, context):
        self.layout.operator("animassist.breakdown_percentage", text="AA 25%").percent = 25
    state["header_draw"] = draw
    bpy.types.VIEW3D_HT_header.prepend(draw)


def item(key):
    """The row control for key, or a stand-in button when the row does not show it."""
    with bpy.context.temp_override(window=window(), area=timeline(), region=region()):
        # Tool controls only: the All tab and the All Keys tool share the key "ALL".
        return next((i for i in mod("ui.timeline_overlay")._items(bpy.context)[0]
                     if i[1] == key and i[0] in {"ACTION", "SLIDER", "POPOUT"}),
                    ("ACTION", key, "", (0, 0, 24, 24)))


def shaped(key):
    overlay = mod("ui.timeline_overlay")
    with bpy.context.temp_override(window=window(), area=timeline(), region=region()):
        found = item(key)
        return overlay._shape_tooltip(bpy.context, found, overlay._tooltip_paragraphs(bpy.context, found))


def static_checks():
    explainers = mod("core.explainers")
    op = mod("core.explainers")._by_idname["animassist.breakdown_percentage"]
    full = explainers.operator_text("animassist.breakdown_percentage")
    rna = bpy.ops.animassist.breakdown_percentage.get_rna_type().description
    log.write(f"  rna description: {rna!r}; class bl_description kept: {op.bl_description == full}\n")
    check("Operators register with no static description; the Python text is kept",
          rna in {"", "(undocumented operator)"} and op.bl_description == full and full)
    props = SimpleNamespace(percent=25)
    prefs().explainer_mode = "FULL"
    check("Full: a native button's hover text is the full description", op.description(bpy.context, props) == full)
    prefs().explainer_mode = "SHORT"
    brief = op.description(bpy.context, props)
    log.write(f"  full: {full!r}\n  short: {brief!r}\n")
    check("Short: one line, at most 120 characters, shorter than Full, not cut mid-word",
          brief and len(brief) <= 120 and len(brief) < len(full) and full.startswith(brief) and "…" not in brief)
    prefs().explainer_mode = "OFF"
    check("Off: only the tool's name (Bforartists always prints a description line)",
          op.description(bpy.context, props) == op.bl_label)
    tool = mod("ui.timeline_strip").ANIMASSIST_OT_timeline_tool
    prefs().explainer_mode = "SHORT"
    with bpy.context.temp_override(window=window(), area=timeline(), region=region()):
        line = tool.description(bpy.context, SimpleNamespace(action="COPY_KEYS"))
    check("Short: a Timeline tool button gives its purpose, not its scope", line and not line.startswith("Scope:"))
    prefs().explainer_mode = "FULL"
    full_lines = shaped("B25")
    check("No shortcut line when no key is bound to the tool", not any(t.startswith("Shortcut:") for t, _ in full_lines))
    # Bind Ctrl+Alt+2 to 25% Breakdown only (the same operator with 50% stays unbound).
    keymap = bpy.context.window_manager.keyconfigs.addon.keymaps.new(name="Dopesheet", space_type="DOPESHEET_EDITOR")
    kmi = keymap.keymap_items.new("animassist.breakdown_percentage", "TWO", "PRESS", ctrl=True, alt=True)
    kmi.properties.percent = 25
    state["kmi"] = (keymap, kmi)
    copy_kmi = keymap.keymap_items.new("animassist.copy_selected_keys", "C", "PRESS", ctrl=True, alt=True)
    state["copy_kmi"] = copy_kmi
    explainers.clear()
    lines = shaped("B25")
    shortcut = [t for t, _ in lines if t.startswith("Shortcut:")]
    log.write(f"  B25 shortcut line: {shortcut}\n")
    check("A bound key shows as a Shortcut line", shortcut and "Ctrl" in shortcut[0] and "Alt" in shortcut[0])
    check("A binding with other settings is not shown for this tool",
          not any(t.startswith("Shortcut:") for t, _ in shaped("B50")))
    prefs().explainer_mode = "SHORT"
    short_lines = shaped("B25")
    log.write(f"  short: {short_lines}\n")
    roles = [r for _, r in short_lines]
    check("Short row hover: name, one line, why it is greyed (if so) and the shortcut",
          roles in (["TITLE", "BODY", "DETAIL"], ["TITLE", "BODY", "WARNING", "DETAIL"])
          and short_lines[-1][0].startswith("Shortcut:") and not any(t.endswith("..") for t, _ in short_lines))
    prefs().explainer_mode = "OFF"
    check("Off row hover: nothing to draw", shaped("B25") == [])
    prefs().explainer_mode = "FULL"
    native_checks()


def native_lines(key):
    return [t for t, _ in shaped(key) if t.startswith("Bforartists key:")]


def native_checks():
    """Bforartists' own keys for the same job, labelled as such, only when bound."""
    catalog = mod("ui.timeline_catalog")
    table = catalog.NATIVE_EQUIVALENTS
    missing = [(a, i) for a, pairs in table.items() for i, _p in pairs
               if a not in catalog.ACTIONS or not hasattr(getattr(bpy.ops, i.split(".")[0]), i.split(".")[1])]
    log.write(f"  native table: {len(table)} tools; missing: {missing}\n")
    check("Every native equivalent names a row tool and an existing Bforartists command", not missing)
    lines = {key: native_lines(key) for key in ("COPY_KEYS", "PASTE_KEYS", "ALL", "GROW_BOTH", "T80", "NUDGE_LEFT",
                                                 "TYPE_KEYFRAME", "HANDLE_VECTOR", "TO_SPLINE", "INBETWEEN")}
    for key, value in lines.items():
        log.write(f"  {key}: {value}\n")
    check("Copy shows Bforartists' Ctrl C in the Dope Sheet and Graph Editor",
          lines["COPY_KEYS"] and "Ctrl C (Dope Sheet, Graph Editor" in lines["COPY_KEYS"][0])
    check("Paste shows Ctrl V, not the flipped Shift Ctrl V", lines["PASTE_KEYS"] and "Ctrl V" in lines["PASTE_KEYS"][0]
          and "Shift" not in lines["PASTE_KEYS"][0] and "Paste Keyframes)" in lines["PASTE_KEYS"][0])
    check("All Keys shows A; a double-click binding is not a key hint",
          lines["ALL"] and lines["ALL"][0].startswith("Bforartists key: A (") and "dbl" not in lines["ALL"][0])
    check("Timing and nudge tools show the Dope Sheet time keys (R scale, W move, no mouse drag)",
          lines["T80"] and "R (Dope Sheet" in lines["T80"][0] and "Scale Keys in Time" in lines["T80"][0] and lines["NUDGE_LEFT"]
          and "W (Dope Sheet" in lines["NUDGE_LEFT"][0] and "drag" not in lines["NUDGE_LEFT"][0].lower())
    check("No Bforartists key line where Bforartists binds none (key types, handles, interpolation, Inbetween)",
          not any(lines[k] for k in ("TYPE_KEYFRAME", "HANDLE_VECTOR", "TO_SPLINE", "INBETWEEN")))
    # A key the user binds to Bforartists' own Keyframe Type command then appears for Mark as Keyframe.
    keymap = bpy.context.window_manager.keyconfigs.user.keymaps["Dopesheet"]
    item = keymap.keymap_items.new("action.keyframe_type", "K", "PRESS", shift=True, alt=True)
    item.properties.type = "KEYFRAME"
    mod("core.explainers").clear()
    bound = native_lines("TYPE_KEYFRAME")
    log.write(f"  TYPE_KEYFRAME after binding: {bound}\n")
    check("A key bound later to Bforartists' Keyframe Type shows for Mark as Keyframe only",
          bound and "Shift Alt K" in bound[0] and not native_lines("TYPE_BREAKDOWN"))
    keymap.keymap_items.remove(item)
    mod("core.explainers").clear()
    prefs().explainer_mode = "SHORT"
    check("Short keeps the Bforartists key line", native_lines("COPY_KEYS"))
    prefs().explainer_mode = "OFF"
    check("Off drops it with everything else", shaped("COPY_KEYS") == [])
    prefs().explainer_mode = "FULL"


def hover_row(key):
    found = item(key)
    x, y, w, h = found[3]
    xy = dict(x=round(region().x + x + w / 2), y=round(region().y + y + h / 2))
    window().event_simulate(type="MOUSEMOVE", value="NOTHING", x=xy["x"] - 3, y=xy["y"])
    window().event_simulate(type="MOUSEMOVE", value="NOTHING", **xy)


def hover_header():
    window().event_simulate(type="MOUSEMOVE", value="NOTHING", x=40, y=933)
    window().event_simulate(type="MOUSEMOVE", value="NOTHING", x=44, y=933)


def away():
    window().event_simulate(type="MOUSEMOVE", value="NOTHING", x=900, y=500)


def shot(name):
    with bpy.context.temp_override(window=window(), screen=window().screen):
        bpy.ops.screen.screenshot(filepath=str(OUT / name))


def plan():
    yield setup, 1.5
    yield static_checks, 0.3
    for current in ("FULL", "SHORT", "OFF"):
        yield (lambda m=current: setattr(prefs(), "explainer_mode", m)), 0.2
        yield away, 0.5
        yield (lambda: hover_row("COPY_KEYS")), 1.5
        yield (lambda m=current: shot(f"explainer-row-{m.lower()}.png")), 0.4
        yield away, 0.5
        yield hover_header, 1.8
        yield (lambda m=current: shot(f"explainer-button-{m.lower()}.png")), 0.4


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
