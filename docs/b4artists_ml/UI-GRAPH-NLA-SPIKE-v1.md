# B4Artists ML UI Graph Editor / NLA spike v1 (Phase 5 / W4)

Status: complete (Phase 5 goal W4 pre-spike of `UI-PHASE5-GOAL-v1.md` §W4). Lane `graphnla`, session
`811c8c60-8a6f-4427-bf68-fd6677b95071`.
Date: 2026-09-22. Host: NUCBOX_M6ULTRA (AMD Ryzen 5 7640HS), Windows 11 26200.
Executable: `C:\Program Files\Bforartists\5.1.2\bforartists.exe` — Bforartists **5.1.2**,
`bpy.app.version_string = 5.2.0 Alpha` (build 2026-06-01).
Invocation: `bforartists.exe --background --factory-startup --disable-autoexec --python <script>`.
Scripts `gn1`–`gn4` are reproduced in the appendix. Raw output is inline.

The factory startup contains no `GRAPH_EDITOR` or `NLA_EDITOR` areas — all factory screens are
`DOPESHEET_EDITOR` / `VIEW_3D` / `NODE_EDITOR`. Items that require a live area (view2d pixel
coordinates) are therefore marked **UNKNOWN** with the exact windowed command needed.

| # | Item | Verdict | Evidence |
|---|------|---------|----------|
| 1 | Panel registration: `bl_space_type='GRAPH_EDITOR'` and `bl_space_type='NLA_EDITOR'`, `bl_region_type='UI'` | **VERIFIED** | `gn1_panel_registration.py`: both panels register and unregister without exception. `graph_panel_registered=True`, `graph_panel_unregistered=True`, `nla_panel_registered=True`, `nla_panel_unregistered=True`. Same code path as the Dope Sheet panel in `editor_dopesheet.py:79`. |
| 2 | Header extension: `GRAPH_HT_header` / `NLA_HT_header` existence and `.append`/`.remove` | **VERIFIED** | `gn2_header_classes.py`: `GRAPH_HT_header`, `GRAPH_HT_playback_controls`, `NLA_HT_header`, `NLA_HT_playback_controls` — all four have `.append` and `.remove`. Live round-trip (`append` then `remove`) succeeded on `GRAPH_HT_header` and `NLA_HT_header`. No counterpart mismatch: unlike the Dope Sheet case where `TIME_HT_editor_buttons` was absent, both editors have their own properly named header class and no expected class is missing. |
| 3 | Overlay drawing: `SpaceGraphEditor` / `SpaceNLA` `draw_handler_add`; `view_to_region` behavior with value-axis Y | **VERIFIED** (draw handler); **UNKNOWN** (pixel coords); **VERIFIED-BY-ANALOGY** (X-axis frame mapping); **DIFFERS** (Y axis semantics) | `gn3_draw_handler.py`: `SpaceGraphEditor.draw_handler_add(_cb, (), 'WINDOW', 'POST_PIXEL')` returns a handle; remove OK. `SpaceNLA.draw_handler_add` likewise. CAUTION: the type is `bpy.types.SpaceNLA` — capital N, capital L, capital A — not `SpaceNla` or `SpaceNlaEditor`. The factory startup has no `GRAPH_EDITOR` or `NLA_EDITOR` windows, so `view_to_region` pixel values could not be confirmed. By analogy with all Blender timeline editors, the X axis maps time/frames to pixels and `view_to_region(frame, 0, clip=False)[0]` will return the correct X pixel for a frame. The Y argument is irrelevant since only [0] is used by the band drawing code. DIFFERS: in the Graph Editor, Y is a **curve value** axis (float, e.g. −1.0–2.0 for typical FCurves), not a track-row axis. The `_rect(x1, x2, color)` helper in `editor_dopesheet.py:193` draws a full-height rectangle (y=0 to y=region.height) and already ignores Y meaning — the same code produces a full-height vertical stripe in the Graph Editor. To confirm actual pixel positions: run `gn3_view2d_windowed.py` (provided below) in a non-background session that has a Graph Editor area open. |
| 4 | Semantic fit: does the contract's marker/range/band vocabulary carry over unchanged? | **VERIFIED** (markers); **DIFFERS** (band row meaning in Graph Editor); **NO-GO** (NLA semantic mismatch) | `gn4_space_props.py`: `SpaceGraphEditor.show_markers=True` in props; `SpaceNLA.show_markers=True`. So scene timeline markers are displayable in both editors — the `B4ML Pose 1` / `B4ML Contact L` markers from `markers.sync` would appear in both. DIFFERS (Graph Editor): a "band" in the Dope Sheet means "this row of channels spans this frame range". In the Graph Editor there are no rows — all FCurves share one Y-value space. A band overlay becomes a full-height vertical stripe across all curves simultaneously. The frame range meaning is preserved ("contact occurs in these frames"), but the per-track/per-rig row isolation is lost. Contact ranges still map directly to X frame coordinates and the color vocabulary remains valid. DIFFERS more severely (NLA): the NLA editor's job is composing action stacks via strips, not inspecting key poses. B4ML keeps the active result in `animation_data.action` directly; it creates no NLA strips. "Contact range" has no meaning in an NLA strip timeline — the overlap would visually contaminate the strip layout with unrelated markings. An animator in the NLA editor is doing action composition, not B4ML capture/review. The vocabulary does **not** carry over for NLA: a "B4ML range band" in the NLA editor has no natural referent. |
| 5 | Cost and risk | (summary item, no single verdict) | The Graph Editor module would be ~140–180 lines (panel + header append + band overlay), comparable to the Dope Sheet half of `editor_dopesheet.py` (319 lines covers both Dope Sheet and Timeline). The NLA module would be ~100 lines for panel + header alone if the overlay is dropped. Risks shared with the Dope Sheet work: `GRAPH_HT_header` / `NLA_HT_header` class names are Bforartists-specific and change risk is identical to `DOPESHEET_HT_header`; re-run `gn2_header_classes.py` after any host upgrade. Additional Graph Editor risk: future code must never try to position bands at a specific Y value in the Graph Editor — the view coordinate means curve value, not row index, and silent wrong-pixel results would occur. The `SpaceNLA` capitalisation (`NLA` not `Nla`) must be matched exactly in any code that references it. |

## Consequences

### Graph Editor

**W4 call: GO WITH CONDITIONS.**

The extension points all verify. `GRAPH_HT_header.append`, `SpaceGraphEditor.draw_handler_add`,
and panel registration on `GRAPH_EDITOR / UI` all work. The semantic degradation (band becomes a
full-height vertical stripe, losing per-row isolation) is acceptable for the animator's task: when
editing FCurves after a preview, seeing colored vertical stripes for "contact zone" and "key pose
span" is still useful context, even without per-curve row isolation.

**Conditions before W4 code for the Graph Editor:**

1. **Animator session confirms Graph Editor use.** The animator session (W5 gate) must show that
   the animator actually opens the Graph Editor during or after a B4ML preview/keep cycle. If the
   session shows they never leave the Dope Sheet, Graph Editor integration has zero incremental
   value and this condition fails.

2. **Windowed `view_to_region` confirmation.** Run `gn3_view2d_windowed.py` in a non-background
   session with a `GRAPH_EDITOR` area and confirm that `view_to_region(frame, 0, clip=False)[0]`
   returns the expected X pixel for a known frame number. The Dope Sheet spike (UI-SPIKE-v1.md §4)
   confirmed this pattern works there; the Graph Editor must be re-confirmed independently.

3. **Band drawn as full-height stripe only.** The overlay must draw `_rect(x1, x2, color)` with
   y-span `(0, region.height)` as in `editor_dopesheet.py:195` — never attempt to position the
   band at a specific Y value based on curve position or rig index, since Y means curve value in
   this editor.

### NLA Editor

**W4 call: NO-GO.**

The NLA editor is for composing action stacks. B4ML does not create NLA strips and the animator's
B4ML task (key pose capture, preview, keep/discard) is entirely on `animation_data.action` — NLA
strips are a separate layer. Adding B4ML panel controls and range bands to the NLA editor would
annotate an unrelated workflow surface and produce confusing markings with no actionable referent.

The extension points technically work (NLA panel registers, `NLA_HT_header.append` works,
`SpaceNLA.draw_handler_add` works), so this is not a hard API barrier. The no-go is semantic and
use-case based. If the animator session (W5 gate) reveals a concrete case where an animator
uses the NLA editor to inspect B4ML output — for example, because they keep the result as a
separate action and layer it in the NLA — this decision should be revisited with that evidence.
Until that evidence exists, the NLA workstream is not worth opening.

### Authorization statement

**This spike does NOT authorise W4 code.** The animator session gate stated in
`UI-PHASE5-GOAL-v1.md` §W4 — "do not start until the animator session confirms the Timeline/Dope
Sheet integration landed" — is still unmet. This spike delivers only the go/no-go evidence that
will inform the decision when that session runs. W4 Graph Editor code may begin only after both
the animator session outcome and the three conditions above are satisfied.

---

## Appendix — scripts as run

Invocation: `bforartists.exe --background --factory-startup --disable-autoexec --python <script>`

### `gn1_panel_registration.py`

```python
# Item 1: Panel registration for GRAPH_EDITOR and NLA_EDITOR
import bpy
results = {}
class B4ML_PT_graph_spike(bpy.types.Panel):
    bl_space_type='GRAPH_EDITOR'; bl_region_type='UI'; bl_category='B4ML'; bl_label='Spike Graph'
    def draw(self, ctx): self.layout.label(text='graph')
try:
    bpy.utils.register_class(B4ML_PT_graph_spike)
    results['graph_panel_registered'] = hasattr(bpy.types,'B4ML_PT_graph_spike')
    bpy.utils.unregister_class(B4ML_PT_graph_spike)
    results['graph_panel_unregistered'] = not hasattr(bpy.types,'B4ML_PT_graph_spike')
except Exception as e:
    results['graph_panel_error'] = str(e)
class B4ML_PT_nla_spike(bpy.types.Panel):
    bl_space_type='NLA_EDITOR'; bl_region_type='UI'; bl_category='B4ML'; bl_label='Spike NLA'
    def draw(self, ctx): self.layout.label(text='nla')
try:
    bpy.utils.register_class(B4ML_PT_nla_spike)
    results['nla_panel_registered'] = hasattr(bpy.types,'B4ML_PT_nla_spike')
    bpy.utils.unregister_class(B4ML_PT_nla_spike)
    results['nla_panel_unregistered'] = not hasattr(bpy.types,'B4ML_PT_nla_spike')
except Exception as e:
    results['nla_panel_error'] = str(e)
print('ITEM1 results=%s' % results)
```

Raw output:
```text
ITEM1 results={'graph_panel_registered': True, 'graph_panel_unregistered': True, 'nla_panel_registered': True, 'nla_panel_unregistered': True}
```

### `gn2_header_classes.py`

```python
# Item 2: header class names for Graph Editor and NLA Editor
import bpy
hdrs_graph = sorted(c.__name__ for c in bpy.types.Header.__subclasses__() if 'GRAPH' in c.__name__)
hdrs_nla   = sorted(c.__name__ for c in bpy.types.Header.__subclasses__() if 'NLA' in c.__name__)
print('ITEM2 graph_headers=%s' % hdrs_graph)
print('ITEM2 nla_headers=%s' % hdrs_nla)
for cls_name in hdrs_graph + hdrs_nla:
    cls = getattr(bpy.types, cls_name, None)
    print('ITEM2 %s append=%s remove=%s' % (cls_name, hasattr(cls,'append'), hasattr(cls,'remove')))
def _draw_g(self, ctx): pass
def _draw_n(self, ctx): pass
bpy.types.GRAPH_HT_header.append(_draw_g); bpy.types.GRAPH_HT_header.remove(_draw_g)
print('ITEM2 graph_header_append_remove=OK first_header=%s' % hdrs_graph[0])
bpy.types.NLA_HT_header.append(_draw_n); bpy.types.NLA_HT_header.remove(_draw_n)
print('ITEM2 nla_header_append_remove=OK first_header=%s' % hdrs_nla[0])
```

Raw output:
```text
ITEM2 graph_headers=['GRAPH_HT_header', 'GRAPH_HT_playback_controls']
ITEM2 nla_headers=['NLA_HT_header', 'NLA_HT_playback_controls']
ITEM2 GRAPH_HT_header append=True remove=True
ITEM2 GRAPH_HT_playback_controls append=True remove=True
ITEM2 NLA_HT_header append=True remove=True
ITEM2 NLA_HT_playback_controls append=True remove=True
ITEM2 graph_header_append_remove=OK first_header=GRAPH_HT_header
ITEM2 nla_header_append_remove=OK first_header=NLA_HT_header
```

### `gn3_draw_handler.py`

```python
# Item 3: SpaceGraphEditor and SpaceNLA draw_handler_add / remove
import bpy
for sp_name in ('SpaceGraphEditor', 'SpaceNLA'):
    sp_cls = getattr(bpy.types, sp_name, None)
    print('ITEM3 %s exists=%s draw_handler_add=%s' % (sp_name, sp_cls is not None, hasattr(sp_cls,'draw_handler_add') if sp_cls else False))
    if sp_cls and hasattr(sp_cls,'draw_handler_add'):
        def _cb(): pass
        try:
            h = sp_cls.draw_handler_add(_cb, (), 'WINDOW', 'POST_PIXEL')
            print('ITEM3 %s handler_add ok handle=%s' % (sp_name, h is not None))
            sp_cls.draw_handler_remove(h, 'WINDOW')
            print('ITEM3 %s handler_remove ok' % sp_name)
        except Exception as e:
            print('ITEM3 %s handler_error=%s' % (sp_name, e))
# Note: SpaceNla (lowercase) does not exist — the correct identifier is SpaceNLA
print('ITEM3 SpaceNla_lowercase_exists=%s SpaceNLA_uppercase_exists=%s' % (
    hasattr(bpy.types,'SpaceNla'), hasattr(bpy.types,'SpaceNLA')))
# Factory areas — no GRAPH_EDITOR or NLA_EDITOR present in factory startup
area_types = sorted({area.type for screen in bpy.data.screens for area in screen.areas})
print('ITEM3 factory_area_types=%s' % area_types)
print('ITEM3 GRAPH_EDITOR_in_factory=%s NLA_EDITOR_in_factory=%s' % (
    'GRAPH_EDITOR' in area_types, 'NLA_EDITOR' in area_types))
print('ITEM3 background=%s' % bpy.app.background)
```

Raw output:
```text
ITEM3 SpaceGraphEditor exists=True draw_handler_add=True
ITEM3 SpaceGraphEditor handler_add ok handle=True
ITEM3 SpaceGraphEditor handler_remove ok
ITEM3 SpaceNLA exists=True draw_handler_add=True
ITEM3 SpaceNLA handler_add ok handle=True
ITEM3 SpaceNLA handler_remove ok
ITEM3 SpaceNla_lowercase_exists=False SpaceNLA_uppercase_exists=True
ITEM3 factory_area_types=['DOPESHEET_EDITOR', 'FILE_BROWSER', 'NODE_EDITOR', 'OUTLINER', 'PROPERTIES', 'SPREADSHEET', 'TEXT_EDITOR', 'VIEW_3D']
ITEM3 GRAPH_EDITOR_in_factory=False NLA_EDITOR_in_factory=False
ITEM3 background=True
```

### `gn4_space_props.py`

```python
# Item 4: SpaceGraphEditor and SpaceNLA property inspection for semantic fit
import bpy
sg = bpy.types.SpaceGraphEditor
sn = getattr(bpy.types, 'SpaceNLA', None)
print('ITEM4_GRAPH SpaceGraphEditor all_props=%s' % [p.identifier for p in sg.bl_rna.properties])
print('ITEM4_GRAPH show_markers=%s use_normalization=%s use_auto_normalization=%s' % (
    'show_markers' in [p.identifier for p in sg.bl_rna.properties],
    'use_normalization' in [p.identifier for p in sg.bl_rna.properties],
    'use_auto_normalization' in [p.identifier for p in sg.bl_rna.properties]))
mode_prop = sg.bl_rna.properties.get('mode')
print('ITEM4_GRAPH mode_items=%s' % ([i.identifier for i in mode_prop.enum_items] if mode_prop else None))
if sn:
    print('ITEM4_NLA SpaceNLA all_props=%s' % [p.identifier for p in sn.bl_rna.properties])
    print('ITEM4_NLA show_markers=%s show_local_markers=%s show_strip_curves=%s' % (
        'show_markers' in [p.identifier for p in sn.bl_rna.properties],
        'show_local_markers' in [p.identifier for p in sn.bl_rna.properties],
        'show_strip_curves' in [p.identifier for p in sn.bl_rna.properties]))
```

Raw output:
```text
ITEM4_GRAPH SpaceGraphEditor all_props=['rna_type', 'type', 'show_locked_time', 'show_region_header', 'show_region_footer', 'show_region_channels', 'show_region_ui', 'show_region_hud', 'mode', 'show_seconds', 'show_sliders', 'show_handles', 'use_auto_lock_translation_axis', 'use_only_selected_keyframe_handles', 'show_markers', 'show_extrapolation', 'use_auto_merge_keyframes', 'use_realtime_update', 'show_cursor', 'cursor_position_x', 'cursor_position_y', 'pivot_point', 'dopesheet', 'has_ghost_curves', 'use_normalization', 'use_auto_normalization']
ITEM4_GRAPH show_markers=True use_normalization=True use_auto_normalization=True
ITEM4_GRAPH mode_items=['FCURVES', 'DRIVERS']
ITEM4_NLA SpaceNLA all_props=['rna_type', 'type', 'show_locked_time', 'show_region_header', 'show_region_footer', 'show_region_channels', 'show_region_ui', 'show_region_hud', 'show_seconds', 'show_strip_curves', 'show_local_markers', 'show_markers', 'use_realtime_update', 'dopesheet']
ITEM4_NLA show_markers=True show_local_markers=True show_strip_curves=True
```

### `gn3_view2d_windowed.py` (not yet run — required for condition 2)

This script must be run **without** `--background` after opening a Graph Editor area. It settles
the UNKNOWN pixel-coordinate question from item 3.

```python
# Item 3 follow-up: view_to_region pixel coordinates in a live Graph Editor area
# Run: bforartists.exe --python gn3_view2d_windowed.py  (no --background)
import bpy, os
OUT = os.environ.get('B4ML_SPIKE_SHOT', 'gn3_view2d_shot.png')
def _probe():
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'GRAPH_EDITOR':
                regs = [r for r in area.regions if r.type == 'WINDOW']
                if regs:
                    r = regs[0]; v2d = r.view2d
                    p0  = v2d.view_to_region(0, 0, clip=False)
                    p1  = v2d.view_to_region(1, 0, clip=False)
                    p50 = v2d.view_to_region(50, 0, clip=False)
                    print('GN3_WINDOWED screen=%s GRAPH_EDITOR region=%dx%d '
                          'view_to_region(0,0)=%s (1,0)=%s (50,0)=%s' % (
                          screen.name, r.width, r.height, p0, p1, p50))
    bpy.ops.screen.screenshot(filepath=OUT)
    print('GN3_WINDOWED screenshot ->', OUT)
    bpy.ops.wm.quit_blender()
    return None
bpy.app.timers.register(_probe, first_interval=1.0)
```

Interpretation key: confirm that `view_to_region(1,0)[0] > view_to_region(0,0)[0]` (X increases
with frame), and that the X delta per frame matches the Dope Sheet result from UI-SPIKE-v1.md §4
(`(f=1)=(79,42)`, `(f=50)=(467,42)` on a 2131-px region → ~7.9 px/frame). Values will differ
since the Graph Editor may be zoomed differently, but the direction and linearity must hold.
