# B4Artists ML UI API spike v1 (Phase 0)

Status: complete (Phase 0 of `UI-ARCHITECTURE-PLAN-v1.md`). Baseline commit `ccc9f61`.
Date: 2026-09-21. Host: NUCBOX_M6ULTRA (AMD Ryzen 5 7640HS), Windows 11 26200.
Executable: `C:\Program Files\Bforartists\5.1.2\bforartists.exe` — Bforartists **5.1.2**, `bpy.app.version_string`
= `5.2.0 Alpha` (build 2026-06-01). The earlier evidence docs name `X:/5.1.0/bforartists.exe` (the previous
development machine); the project now lives on this machine and 5.1.2 is the native host for this milestone.
Invocation: `bforartists.exe --background --factory-startup --disable-autoexec --python <script>`; items 5b/7b
ran without `--background` and produced screenshots. Scripts are reproduced in full in the appendix (each ≤ 15 lines); raw output and screenshots are kept at
`G:/LapArt/.planning/b4ml-ui-slice-1/phase0-spike/` (outside the repository; evidence, not source).

| # | Item | Verdict | Evidence |
|---|------|---------|----------|
| 1 | `bl_parent_id` subpanels in `VIEW_3D` / `UI` | **VERIFIED** | `s1_subpanel.py`: child registered, `bl_parent_id` resolves, unregister clean. Bforartists ships its own (`VIEW3D_PT_view3d_camera_lock`, `VIEW3D_PT_annotation_onion`). The `B4Artists ML` tab shows in the sidebar tab strip (screenshot 1). |
| 2 | Dope Sheet `UI` region exists in Timeline mode | **VERIFIED, with a DIFFERS note** | `s2_timeline_ui_region.py`: every factory `DOPESHEET_EDITOR` area (Timeline in *Main*/*Nodes*, Dope Sheet in *Animation*) has regions `CHANNELS, FOOTER, HEADER, UI, WINDOW`. A `DOPESHEET_EDITOR / UI / 'B4ML'` panel registers. DIFFERS: `SpaceDopeSheetEditor.ui_mode` enum is `DOPESHEET_EDITOR, ACTION, SHAPEKEY, GPENCIL, MASK, CACHEFILE` — no `TIMELINE`; the Timeline areas report `ui_mode == ''`. Poll on `space.mode == 'TIMELINE'` (not `ui_mode`) if the panel must know it is in a Timeline. |
| 3 | Bforartists header class names for Dope Sheet / Timeline | **DIFFERS** | `s3_header_classes.py`: headers are `DOPESHEET_HT_header` and `DOPESHEET_HT_playback_controls`. Blender's `TIME_HT_editor_buttons` **does not exist**. `DOPESHEET_HT_header.append/remove` works. Menus available: `DOPESHEET_MT_marker`, `TIME_MT_marker`, `DOPESHEET_MT_editor_menus`, `TIME_MT_editor_menus`. Alternative: append to `DOPESHEET_HT_header` for both modes, or add items to `DOPESHEET_MT_marker` / `TIME_MT_marker`. |
| 4 | `SpaceDopeSheetEditor.draw_handler_add` + `region.view2d.view_to_region` | **VERIFIED** | `s4_draw_handler_view2d.py`: `draw_handler_add(cb, (), 'WINDOW', 'POST_PIXEL')` returns a handle; remove OK. `view2d.view_to_region(1,0,clip=False) → (79,42)`, `(50,0) → (467,42)` on the Animation screen (2131×43 px region in background; sizes are real only in a windowed session). |
| 5 | Timeline marker rendering | **VERIFIED (API + visual)** | `s5_markers.py`: `scene.timeline_markers.new(name, frame=)`, `.frame`, `.select`, `.camera`; `SpaceDopeSheetEditor.show_markers / show_pose_markers / use_marker_sync`. `new()` returns markers **selected by default**. Screenshot 2 (`spike_shot2.png`, Animation workspace): three `B4ML Pose n` markers render as dashed lines with labels in the Dope Sheet marker lane; preview range 10–55 draws as the lit band. DIFFERS (copy): `◆` (U+25C6) renders as `�` in the viewport info text (screenshot 1) and labels are truncated to the gap before the next marker — use ASCII names ≤ ~12 chars (`B4ML Pose 1`). DIFFERS (layout): Bforartists' factory *Main* workspace collapses the Timeline to the playback strip; markers are only visible in an expanded Timeline/Dope Sheet (e.g. *Animation* workspace). The Motion panel must offer a way to reveal one. |
| 6 | `context.temp_override` for `view3d.view_selected` | **VERIFIED** | `s6_temp_override_view_selected.py`: with `temp_override(window, area, region)` poll is True and the operator returns `{'FINISHED'}` even in `--background`. |
| 7 | `bpy.app.timers` cost at 0.25 s | **VERIFIED** | `s7_timer_cost.py`: register/unregister OK; the reconciliation body (tuple of `(name, frame, select)` over 20 `B4ML` markers) costs mean 18 µs, max 279 µs per tick. `s8_nonbackground_screenshot.py`: timer fired 8 times in 2.40 s at 0.25 s (windowed run). Timers do **not** fire in `--background --python` after the script returns — native tests must call the sync function directly. |

## Consequences for Phases 1–3
- Phase 1 may use `bl_parent_id` subpanels as planned.
- Phase 3 header buttons: append to `DOPESHEET_HT_header` (covers Timeline + Dope Sheet); do not reference `TIME_HT_editor_buttons`.
- Phase 3 marker names: ASCII only, short; role goes in a suffix (`B4ML Pose 1`, `B4ML Contact L`). Handle "new marker is selected" so a freshly synced marker does not read as user-selected.
- Phase 3 timer: fine at 0.25 s; unregister when no rig has anchors; tests call `markers.sync()` directly.
- Phase 2/3 QA: the factory *Main* workspace hides the marker lane. Plan §5.4's Dope Sheet panel or a "Show Timeline" affordance is not optional.
- Item 3 (header class names) is the one most likely to differ across Bforartists builds; re-run `s3_header_classes.py` after any host upgrade.

## Screenshots
- `spike_shot.png` — factory Main workspace: `B4Artists ML` tab present; viewport info text shows the marker name with `◆` → `�`; Timeline collapsed.
- `spike_shot2.png` — Animation workspace: markers + preview range in the Dope Sheet.

## Appendix — scripts as run

Invocation for s1–s7: `bforartists.exe --background --factory-startup --disable-autoexec --python <script>`; s8–s9 without `--background`.

### `s1_subpanel.py`

```python
# Item 1: bl_parent_id subpanels in VIEW_3D / UI
import bpy
class B4ML_PT_spike_parent(bpy.types.Panel):
    bl_space_type='VIEW_3D'; bl_region_type='UI'; bl_category='B4Artists ML'; bl_label='Spike Parent'
    def draw(self, ctx): self.layout.label(text='parent')
class B4ML_PT_spike_child(bpy.types.Panel):
    bl_space_type='VIEW_3D'; bl_region_type='UI'; bl_category='B4Artists ML'; bl_label='Spike Child'
    bl_parent_id='B4ML_PT_spike_parent'; bl_options={'DEFAULT_CLOSED'}
    def draw(self, ctx): self.layout.label(text='child')
bpy.utils.register_class(B4ML_PT_spike_parent); bpy.utils.register_class(B4ML_PT_spike_child)
ok = bpy.types.B4ML_PT_spike_child.bl_parent_id == 'B4ML_PT_spike_parent'
native = [c.__name__ for c in bpy.types.Panel.__subclasses__() if getattr(c,'bl_space_type','')=='VIEW_3D' and getattr(c,'bl_region_type','')=='UI' and getattr(c,'bl_parent_id','')][:3]
print('ITEM1 subpanel registered=%s parent_ok=%s native_examples=%s' % (hasattr(bpy.types,'B4ML_PT_spike_child'), ok, native))
bpy.utils.unregister_class(B4ML_PT_spike_child); bpy.utils.unregister_class(B4ML_PT_spike_parent)
print('ITEM1 unregistered=%s' % (not hasattr(bpy.types,'B4ML_PT_spike_child')))
```

### `s2_timeline_ui_region.py`

```python
# Item 2: does the Dope Sheet editor in TIMELINE mode have a UI (sidebar) region?
import bpy
rows=[]
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='DOPESHEET_EDITOR':
            sp=area.spaces.active
            rows.append((screen.name, sp.ui_mode if hasattr(sp,'ui_mode') else sp.mode, sorted({r.type for r in area.regions})))
print('ITEM2 dopesheet_areas=%s' % rows)
print('ITEM2 SpaceDopeSheetEditor.ui_mode_items=%s' % [i.identifier for i in bpy.types.SpaceDopeSheetEditor.bl_rna.properties['ui_mode'].enum_items])
class B4ML_PT_spike_ds(bpy.types.Panel):
    bl_space_type='DOPESHEET_EDITOR'; bl_region_type='UI'; bl_category='B4ML'; bl_label='Spike DS'
    def draw(self, ctx): self.layout.label(text='ds')
bpy.utils.register_class(B4ML_PT_spike_ds); print('ITEM2 DOPESHEET UI panel registered=%s' % hasattr(bpy.types,'B4ML_PT_spike_ds')); bpy.utils.unregister_class(B4ML_PT_spike_ds)
```

### `s3_header_classes.py`

```python
# Item 3: actual header/menu class names Bforartists uses for Dope Sheet / Timeline
import bpy
hdrs=sorted(c.__name__ for c in bpy.types.Header.__subclasses__() if 'DOPESHEET' in c.__name__ or 'TIME' in c.__name__)
menus=sorted(c.__name__ for c in bpy.types.Menu.__subclasses__() if 'DOPESHEET' in c.__name__ or 'TIME' in c.__name__)
print('ITEM3 headers=%s' % hdrs)
print('ITEM3 menus=%s' % menus)
print('ITEM3 DOPESHEET_HT_header exists=%s append=%s' % (hasattr(bpy.types,'DOPESHEET_HT_header'), hasattr(getattr(bpy.types,'DOPESHEET_HT_header',None),'append')))
print('ITEM3 TIME_HT_editor_buttons exists=%s' % hasattr(bpy.types,'TIME_HT_editor_buttons'))
print('ITEM3 bforartists_version=%s' % getattr(bpy.app,'version_string',''), 'bfa attrs:', [a for a in dir(bpy.app) if 'bfa' in a.lower() or 'bforartists' in a.lower()])
def _draw(self, ctx): self.layout.operator('wm.splash', text='', icon='ARMATURE_DATA')
bpy.types.DOPESHEET_HT_header.append(_draw); print('ITEM3 append ok'); bpy.types.DOPESHEET_HT_header.remove(_draw); print('ITEM3 remove ok')
```

### `s4_draw_handler_view2d.py`

```python
# Item 4: SpaceDopeSheetEditor.draw_handler_add + region.view2d.view_to_region
import bpy
def _cb(): pass
h=bpy.types.SpaceDopeSheetEditor.draw_handler_add(_cb, (), 'WINDOW', 'POST_PIXEL')
print('ITEM4 draw_handler_add handle=%s' % (h is not None))
bpy.types.SpaceDopeSheetEditor.draw_handler_remove(h, 'WINDOW'); print('ITEM4 draw_handler_remove ok')
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='DOPESHEET_EDITOR':
            reg=[r for r in area.regions if r.type=='WINDOW'][0]
            v2d=reg.view2d
            print('ITEM4 %s region %dx%d view_to_region(f=1)=%s (f=50)=%s region_to_view(0,0)=%s' % (screen.name, reg.width, reg.height, v2d.view_to_region(1,0,clip=False), v2d.view_to_region(50,0,clip=False), v2d.region_to_view(0,0)))
            break
```

### `s5_markers.py`

```python
# Item 5: timeline markers API (rendering needs a non-background screenshot)
import bpy
sc=bpy.context.scene
m1=sc.timeline_markers.new('B4ML \u25c6 Rig: Pose 1', frame=10); m2=sc.timeline_markers.new('B4ML \u25c6 Rig: Pose 2', frame=30)
m2.select=True; m1.frame=12
print('ITEM5 markers=%s' % [(m.name, m.frame, m.select) for m in sc.timeline_markers if m.name.startswith('B4ML ')])
print('ITEM5 marker props=%s' % [p.identifier for p in bpy.types.TimelineMarker.bl_rna.properties])
print('ITEM5 show_markers on dopesheet space: %s' % [p.identifier for p in bpy.types.SpaceDopeSheetEditor.bl_rna.properties if 'marker' in p.identifier])
sc.timeline_markers.remove(m1); sc.timeline_markers.remove(m2); print('ITEM5 removed count=%d' % len(sc.timeline_markers))
```

### `s6_temp_override_view_selected.py`

```python
# Item 6: context.temp_override for view3d.view_selected
import bpy
bpy.ops.mesh.primitive_cube_add(location=(5,5,5))
res='UNAVAILABLE'
for win in bpy.context.window_manager.windows:
    for area in win.screen.areas:
        if area.type=='VIEW_3D':
            region=[r for r in area.regions if r.type=='WINDOW'][0]
            with bpy.context.temp_override(window=win, area=area, region=region):
                print('ITEM6 poll=%s' % bpy.ops.view3d.view_selected.poll())
                res=bpy.ops.view3d.view_selected()
print('ITEM6 windows=%d result=%s background=%s' % (len(bpy.context.window_manager.windows), res, bpy.app.background))
```

### `s7_timer_cost.py`

```python
# Item 7: bpy.app.timers at 0.25 s — registration + per-tick body cost (firing needs the event loop)
import bpy, time
sc=bpy.context.scene
for i in range(20): sc.timeline_markers.new('B4ML \u25c6 Rig: Pose %d' % i, frame=i*5)
_last=None; ticks=[]
def _tick():
    global _last
    t=time.perf_counter(); cur=tuple((m.name,m.frame,m.select) for m in sc.timeline_markers if m.name.startswith('B4ML '))
    changed = cur != _last; _last=cur; ticks.append(time.perf_counter()-t); return 0.25
bpy.app.timers.register(_tick, first_interval=0.25, persistent=False)
print('ITEM7 registered=%s' % bpy.app.timers.is_registered(_tick))
for _ in range(200): _tick()
print('ITEM7 body_cost_us mean=%.1f max=%.1f over %d calls, 20 markers' % (sum(ticks)/len(ticks)*1e6, max(ticks)*1e6, len(ticks)))
bpy.app.timers.unregister(_tick); print('ITEM7 unregistered=%s' % (not bpy.app.timers.is_registered(_tick)))
```

### `s8_nonbackground_screenshot.py`

```python
# Item 5/7 visual: markers render in Timeline + timers fire; screenshot then quit (non-background)
import bpy, time, os
OUT = os.environ.get('B4ML_SPIKE_SHOT', 'spike_shot.png')
sc = bpy.context.scene
for i, f in enumerate((10, 30, 55)): sc.timeline_markers.new('B4ML \u25c6 Rig: Pose %d' % (i + 1), frame=f)
sc.use_preview_range = True; sc.frame_preview_start = 10; sc.frame_preview_end = 55; sc.frame_current = 30
class B4ML_PT_spike_parent(bpy.types.Panel):
    bl_space_type='VIEW_3D'; bl_region_type='UI'; bl_category='B4Artists ML'; bl_label='Spike Parent'
    def draw(self, ctx): self.layout.label(text='parent card', icon='ARMATURE_DATA')
class B4ML_PT_spike_child(bpy.types.Panel):
    bl_space_type='VIEW_3D'; bl_region_type='UI'; bl_category='B4Artists ML'; bl_label='Spike Child'; bl_parent_id='B4ML_PT_spike_parent'
    def draw(self, ctx): self.layout.label(text='child row')
bpy.utils.register_class(B4ML_PT_spike_parent); bpy.utils.register_class(B4ML_PT_spike_child)
_t = [time.perf_counter()]; _n = [0]
def _tick():
    _n[0] += 1
    if _n[0] < 8: return 0.25
    print('ITEM7 timer fired %d times in %.2fs (0.25s interval)' % (_n[0], time.perf_counter() - _t[0]))
    for a in bpy.context.screen.areas:
        if a.type == 'VIEW_3D':
            for r in a.regions:
                if r.type == 'UI': 
                    with bpy.context.temp_override(area=a, region=r): bpy.ops.wm.context_set_string(data_path='space_data.show_region_ui', value='True') if False else None
            a.spaces.active.show_region_ui = True
    bpy.ops.screen.screenshot(filepath=OUT); print('ITEM5 screenshot ->', OUT); bpy.ops.wm.quit_blender(); return None
bpy.app.timers.register(_tick, first_interval=0.25)
```

### `s9_animation_workspace_shot.py`

```python
# Visual: Animation workspace, markers with ASCII vs unicode names, preview range, N-panel subpanel
import bpy, os
OUT = os.environ.get('B4ML_SPIKE_SHOT', 'spike_shot2.png'); sc = bpy.context.scene
sc.timeline_markers.new('B4ML Pose 1 (unicode \u25c6)', frame=10); sc.timeline_markers.new('B4ML Pose 2', frame=30); sc.timeline_markers.new('B4ML Pose 3', frame=55)
sc.use_preview_range = True; sc.frame_preview_start = 10; sc.frame_preview_end = 55; sc.frame_current = 30
class B4ML_PT_spike_parent(bpy.types.Panel):
    bl_space_type='VIEW_3D'; bl_region_type='UI'; bl_category='B4Artists ML'; bl_label='Setup'
    def draw(self, ctx): self.layout.label(text='Character: (none)  -  Check Rig', icon='ARMATURE_DATA')
class B4ML_PT_spike_child(bpy.types.Panel):
    bl_space_type='VIEW_3D'; bl_region_type='UI'; bl_category='B4Artists ML'; bl_label='Advanced'; bl_parent_id='B4ML_PT_spike_parent'; bl_options={'DEFAULT_CLOSED'}
    def draw(self, ctx): self.layout.label(text='subpanel body')
bpy.utils.register_class(B4ML_PT_spike_parent); bpy.utils.register_class(B4ML_PT_spike_child)
def _go():
    bpy.context.window.workspace = bpy.data.workspaces['Animation']; return None
def _shot():
    for a in bpy.context.screen.areas:
        if a.type == 'VIEW_3D': a.spaces.active.show_region_ui = True
        if a.type == 'DOPESHEET_EDITOR': a.spaces.active.show_region_ui = True
    return None
def _end(): bpy.ops.screen.screenshot(filepath=OUT); print('SHOT2 ->', OUT); bpy.ops.wm.quit_blender(); return None
bpy.app.timers.register(_go, first_interval=0.3); bpy.app.timers.register(_shot, first_interval=0.8); bpy.app.timers.register(_end, first_interval=1.8)
```

### Raw background output

```text
===== s1_subpanel =====
ITEM1 subpanel registered=True parent_ok=True native_examples=['VIEW3D_PT_view3d_camera_lock', 'VIEW3D_PT_annotation_onion', 'VIEW3D_PT_copy_global_transform_fix_to_camera']
ITEM1 unregistered=True
===== s2_timeline_ui_region =====
ITEM2 dopesheet_areas=[('Animation', '', ['CHANNELS', 'FOOTER', 'HEADER', 'UI', 'WINDOW']), ('Animation', 'DOPESHEET_EDITOR', ['CHANNELS', 'FOOTER', 'HEADER', 'HUD', 'UI', 'WINDOW']), ('Main', '', ['CHANNELS', 'FOOTER', 'HEADER', 'UI', 'WINDOW']), ('Nodes', '', ['CHANNELS', 'FOOTER', 'HEADER', 'UI', 'WINDOW'])]
ITEM2 SpaceDopeSheetEditor.ui_mode_items=['DOPESHEET_EDITOR', 'ACTION', 'SHAPEKEY', 'GPENCIL', 'MASK', 'CACHEFILE']
ITEM2 DOPESHEET UI panel registered=True
===== s3_header_classes =====
ITEM3 headers=['DOPESHEET_HT_header', 'DOPESHEET_HT_playback_controls']
ITEM3 menus=['DOPESHEET_MT_action', 'DOPESHEET_MT_cache', 'DOPESHEET_MT_channel', 'DOPESHEET_MT_channel_context_menu', 'DOPESHEET_MT_channel_extrapolation', 'DOPESHEET_MT_context_menu', 'DOPESHEET_MT_delete', 'DOPESHEET_MT_editor_menus', 'DOPESHEET_MT_gpencil_channel', 'DOPESHEET_MT_key', 'DOPESHEET_MT_key_snap', 'DOPESHEET_MT_key_transform', 'DOPESHEET_MT_marker', 'DOPESHEET_MT_select', 'DOPESHEET_MT_select_more_less', 'DOPESHEET_MT_snap_pie', 'DOPESHEET_MT_view', 'DOPESHEET_MT_view_pie', 'DOPESHEET_MT_view_pie_menus', 'TIME_MT_editor_menus', 'TIME_MT_marker', 'TIME_MT_view']
ITEM3 DOPESHEET_HT_header exists=True append=True
ITEM3 TIME_HT_editor_buttons exists=False
ITEM3 bforartists_version=5.2.0 Alpha bfa attrs: ['bfa_version_string']
ITEM3 append ok
ITEM3 remove ok
===== s4_draw_handler_view2d =====
ITEM4 draw_handler_add handle=True
ITEM4 draw_handler_remove ok
ITEM4 Animation region 2131x43 view_to_region(f=1)=(79, 42) (f=50)=(467, 42) region_to_view(0,0)=(-9.0, -43.0)
ITEM4 Main region 2131x2 view_to_region(f=1)=(58, 1) (f=50)=(346, 1) region_to_view(0,0)=(-9.0, -2.0)
ITEM4 Nodes region 2131x2 view_to_region(f=1)=(58, 20) (f=50)=(346, 20) region_to_view(0,0)=(-9.0, -21.0)
===== s5_markers =====
ITEM5 markers=[('B4ML ◆ Rig: Pose 1', 12, True), ('B4ML ◆ Rig: Pose 2', 30, True)]
ITEM5 marker props=['rna_type', 'name', 'frame', 'select', 'camera']
ITEM5 show_markers on dopesheet space: ['show_pose_markers', 'show_markers', 'use_marker_sync']
ITEM5 removed count=0
===== s6_temp_override_view_selected =====
ITEM6 poll=True
ITEM6 windows=1 result={'FINISHED'} background=True
===== s7_timer_cost =====
ITEM7 registered=True
ITEM7 body_cost_us mean=18.4 max=279.4 over 200 calls, 20 markers
ITEM7 unregistered=True
```
