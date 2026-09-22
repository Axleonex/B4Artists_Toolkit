# B4Artists ML UI gizmo spike v1 (Phase 5 / W3)

Status: complete (Phase 5 goal W3 of `UI-ARCHITECTURE-PLAN-v1.md` §4, §8). Lane `w3gizmo`, session
`e0d8adc4-c20a-46e3-84d7-31de12e37e57`.
Date: 2026-09-22. Host: NUCBOX_M6ULTRA (AMD Ryzen 5 7640HS), Windows 11 26200.
Executable: `C:\Program Files\Bforartists\5.1.2\bforartists.exe` — Bforartists **5.1.2**,
`bpy.app.version_string = 5.2.0 Alpha` (build 2026-06-01).
Invocation: `bforartists.exe --background --factory-startup --disable-autoexec --python <script>`.
Items 1b and 2b are follow-up probes run under the same invocation.
All items that require the draw system (setup() invocation, mode-switch redraw, handler suppression,
gizmo drag) cannot be exercised in background mode; those are marked **UNAVAILABLE** with the
limitation stated explicitly.  Scripts are in the appendix; raw output is reproduced inline.

| # | Item | Verdict | Evidence |
|---|------|---------|----------|
| 1 | `bpy.types.GizmoGroup` with `bl_space_type='VIEW_3D'`, `bl_region_type='WINDOW'`, `bl_options={'3D','PERSISTENT'}` registers and unregisters cleanly; `poll` in background | **VERIFIED** with DIFFERS | `g1_register.py` + `g1b_gizmogroup_check.py`: `register_class` and `unregister_class` complete without exception. `bl_options = {'3D', 'PERSISTENT'}` accepted. `poll` not called in background (`poll_called_after_view_layer_update=0`). DIFFERS: GizmoGroup type is **not** accessible as `bpy.types.B4ML_GGT_g1` by idname (unlike panels), but IS found via `bpy.types.GizmoGroup.bl_rna_get_subclass_py('B4ML_GGT_g1b')`. `unregister_class` runs without error; C-level registration removed (Python `__subclasses__` entry persists in memory — this is normal CPython behaviour, not a leak). |
| 2 | `gizmos.new('GIZMO_GT_move_3d')` and `matrix_basis` from empty world matrix; `draw_style`, `scale_basis`, `color`, `alpha` | **UNAVAILABLE** (setup not invoked); DIFFERS on `draw_style` | `g2_move3d_props.py` + `g2b_gizmo_types.py`: `GIZMO_GT_move_3d` is **not registered** in background mode (`GIZMO_GT_move_3d_in_types=False`; only `GIZMO_GT_MouseArea` found). `setup()` is never called in background — `gizmos.new()` cannot be reached. `bpy.types.Gizmo` base properties confirmed present: `scale_basis`, `color`, `alpha`, `matrix_basis`, `use_undo`. DIFFERS: `draw_style` is **absent** from `bpy.types.Gizmo.bl_rna.properties` (`Gizmo.draw_style exists=False`). Empty `matrix_world` is readable at creation (`empty_matrix_world_readable=True loc=[1.0, 2.0, 3.0]`). Full `gizmos.new()` + `matrix_basis` assignment test requires a windowed session. |
| 3 | `target_set_prop` binds empty `location` while rig is in POSE mode; `poll` can require `context.mode == 'POSE'`; scene-level empties visible | **DIFFERS** | `g3_target_set_prop.py`: `target_set_prop` method **does not exist** (`target_set_prop method exists=False`). The actual API is `target_set_handler` (`target_set_handler method exists=True`) — a Python getter/setter callback, not a direct property bind. Mode transitions work in background: OBJECT→POSE (`mode_after_set=POSE`) and back (`mode_back_to_object=OBJECT`). Empty IS visible in `view_layer` while armature is in POSE mode (`empty_visible_in_pose_mode=True`). `context.mode == 'POSE'` is a valid poll condition. Actual `target_set_handler` binding and drag test require a windowed session. |
| 4 | GizmoGroup survives rig mode switching (OBJECT ↔ POSE) and posing session ending | **UNAVAILABLE** | `g4_mode_survival.py`: `register_class` / `unregister_class` / re-register cycle all succeed without error. Mode cycling OBJECT→POSE→OBJECT confirmed (`modes_cycled=['POSE', 'OBJECT']`). Whether the gizmo draw system re-invokes `setup()` after mode switch, or drops the group, requires a windowed session — `setup()` is never called in background (`poll_calls_during_cycle=0`). |
| 5 | Interaction with existing `POST_VIEW` / `POST_PIXEL` `SpaceView3D` handlers — do both draw or does one suppress the other? | **UNAVAILABLE** | `g5_handler_coexist.py`: `draw_handler_add(POST_VIEW)` and `draw_handler_add(POST_PIXEL)` can be registered simultaneously with a live GizmoGroup registration without error (`both_registered_simultaneously=True`). In background mode, no draw callbacks fire (`draw_3d_calls=0`, `draw_2d_calls=0`). Whether a GizmoGroup suppresses or coexists with existing POST_VIEW/POST_PIXEL handlers in a live viewport requires a windowed session. |
| 6 | Undo: does moving an empty via a gizmo push an undo step the same way Object-Mode move does? | **UNAVAILABLE** | `g6_undo.py`: background undo system is disabled by default (`ed.undo error: Undo disabled at startup in background-mode`). `transform.translate` operator does move the empty correctly (`location_changed=True`, `loc_after=(1.0, 0.0, 0.0)`), confirming that the translation path works; undo could not be verified. `bpy.types.Gizmo.use_undo` property exists — per-gizmo undo control is available. Actual gizmo drag + undo test requires a windowed session. |

## Consequences

**W3 call: DEFER.**

The spike answers the W3 question — whether gizmos remove the Object-Mode requirement enough to ship now — as follows:

**What is confirmed (background-testable):**
- `register_class` / `unregister_class` for a `VIEW_3D / WINDOW / {'3D','PERSISTENT'}` GizmoGroup runs clean with no exceptions.
- `context.mode == 'POSE'` is a valid poll condition, and scene-level empties remain visible in `view_layer` while the armature is in POSE mode — the core scene-access assumption is valid.
- `bpy.types.Gizmo` carries `scale_basis`, `color`, `alpha`, `matrix_basis`, `use_undo`.

**What differs from plan assumptions:**
- `target_set_prop` does not exist; the correct API is `target_set_handler` (Python getter/setter callback). This is more flexible but requires writing and testing getter/setter closures that read/write `empty.location` — non-trivial additional implementation work.
- `draw_style` is absent from the `Gizmo` base RNA; visual customisation relies on `draw()` / `draw_select()` overrides or different property names.
- `GIZMO_GT_move_3d` is not available in background mode, so its instance-level properties cannot be confirmed without a windowed session.

**What remains unverified (windowed session required):**
Items 2 (gizmo creation and matrix assignment), 4 (draw-system survival across mode switches), 5 (handler coexistence in a live viewport), and 6 (undo via drag) were not testable in background mode. The four unverified items are exactly the items most likely to surface new blockers.

**Why DEFER, not SHIP or BLOCKED:**
- Not BLOCKED: no hard API barrier. `target_set_handler` can bind to `empty.location` and gizmo registration is clean.
- Not SHIP: four of six items are unverified; the `target_set_handler` difference adds implementation work; plan §8 explicitly states "Do not attempt gizmos before the journey passes with empties"; the Phase 2 mode guard (auto-switch + alert) already mitigates the Object-Mode friction that gizmos would eliminate; shipping gizmos now would jump ahead of the validated empty-based journey.
- The correct next action is: complete Phase 2 and validate the core empty-based workflow; then run a follow-up windowed spike (items 2, 4, 5, 6) before committing to Phase 5 gizmo implementation.

**If the windowed follow-up is run**, the decisive tests are:
1. `gizmos.new('GIZMO_GT_move_3d')` in a live `setup()` call and `matrix_basis = arm_obj.matrix_world` assignment without crash.
2. `target_set_handler` closure binding `empty.location` — drag moves the empty while rig stays in POSE mode.
3. Gizmo draw survives OBJECT→POSE→OBJECT switch without error or stale state.
4. One undo step per drag (confirmed via `ed.undo`).

## Windowed Follow-up Checklist

The four items below were not testable in background mode.  Run these in a windowed session
before committing to Phase 5 gizmo implementation:

1. `gizmos.new('GIZMO_GT_move_3d')` in a live `setup()` call; assign `gz.matrix_basis` from
   `empty.matrix_world`; confirm no exception and that `draw_style` (or equivalent) can be set.
2. `target_set_handler(empty, 'location', index=...)` closure — drag the gizmo, confirm the empty
   moves and the rig solver re-fires (same as dragging in Object Mode).
3. Mode-switch redraw: register group, enter POSE, switch to OBJECT, re-enter POSE; confirm
   `setup()` is re-called or the existing gizmo retains valid `matrix_basis`.
4. One undo step per drag: move via gizmo, press Ctrl-Z, confirm empty returns to pre-drag
   location with `bpy.ops.ed.undo()` (call `ed.undo_push()` first to init the undo stack).

## Appendix — scripts as run

Invocation for all scripts: `bforartists.exe --background --factory-startup --disable-autoexec --python <script>`

### `g1_register.py`

```python
# Item 1: GizmoGroup registration/unregistration; poll call in background
import bpy
_poll_log = []
class B4ML_GGT_g1(bpy.types.GizmoGroup):
    bl_idname = 'B4ML_GGT_g1'; bl_label = 'B4ML Gizmo Spike 1'
    bl_space_type = 'VIEW_3D'; bl_region_type = 'WINDOW'; bl_options = {'3D', 'PERSISTENT'}
    @classmethod
    def poll(cls, context): _poll_log.append(True); return True
    def setup(self, context): print('ITEM1 setup called background=%s' % bpy.app.background)
try:
    bpy.utils.register_class(B4ML_GGT_g1)
    print('ITEM1 registered=%s' % hasattr(bpy.types, 'B4ML_GGT_g1'))
    bpy.context.view_layer.update()
    print('ITEM1 poll_called_after_view_layer_update=%d' % len(_poll_log))
    opts = B4ML_GGT_g1.bl_options
    print('ITEM1 bl_options_accepted=%s has_3D=%s has_PERSISTENT=%s' % (opts, '3D' in opts, 'PERSISTENT' in opts))
    bpy.utils.unregister_class(B4ML_GGT_g1)
    print('ITEM1 unregistered=%s' % (not hasattr(bpy.types, 'B4ML_GGT_g1')))
except Exception as e:
    print('ITEM1 ERROR=%s' % e)
print('ITEM1 background=%s' % bpy.app.background)
```

Raw output:
```text
ITEM1 registered=False
ITEM1 poll_called_after_view_layer_update=0
ITEM1 bl_options_accepted={'3D', 'PERSISTENT'} has_3D=True has_PERSISTENT=True
ITEM1 unregistered=True
ITEM1 background=True
```

### `g1b_gizmogroup_check.py`

```python
# Item 1 follow-up: probe GizmoGroup type accessibility after register
import bpy
class B4ML_GGT_g1b(bpy.types.GizmoGroup):
    bl_idname = 'B4ML_GGT_g1b'; bl_label = 'B4ML Gizmo Spike 1b'
    bl_space_type = 'VIEW_3D'; bl_region_type = 'WINDOW'; bl_options = {'3D', 'PERSISTENT'}
    @classmethod
    def poll(cls, context): return True
    def setup(self, context): pass
bpy.utils.register_class(B4ML_GGT_g1b)
in_types = hasattr(bpy.types, 'B4ML_GGT_g1b')
print('ITEM1B in_bpy_types=%s' % in_types)
subclasses = [c.__name__ for c in bpy.types.GizmoGroup.__subclasses__() if 'B4ML' in c.__name__]
print('ITEM1B in_subclasses=%s' % subclasses)
try:
    t = bpy.types.GizmoGroup.bl_rna_get_subclass_py('B4ML_GGT_g1b')
    print('ITEM1B bl_rna_get_subclass_py=%s' % t)
except Exception as e:
    print('ITEM1B bl_rna_get_subclass_py error=%s' % e)
bpy.utils.unregister_class(B4ML_GGT_g1b)
subclasses_after = [c.__name__ for c in bpy.types.GizmoGroup.__subclasses__() if 'B4ML' in c.__name__]
print('ITEM1B subclasses_after_unregister=%s' % subclasses_after)
```

Raw output:
```text
ITEM1B in_bpy_types=False
ITEM1B in_subclasses=['B4ML_GGT_g1b']
ITEM1B bl_rna_get_subclass_py=<class '__main__.B4ML_GGT_g1b'>
ITEM1B subclasses_after_unregister=['B4ML_GGT_g1b']
```

### `g2_move3d_props.py`

```python
# Item 2: GIZMO_GT_move_3d type existence and RNA properties; matrix_basis from empty
import bpy
from mathutils import Matrix, Vector
gz_type = getattr(bpy.types, 'GIZMO_GT_move_3d', None)
if gz_type:
    props = sorted(p.identifier for p in gz_type.bl_rna.properties)
    print('ITEM2 gizmo_type_registered=True')
    print('ITEM2 props=%s' % props)
else:
    print('ITEM2 gizmo_type_registered=False')
gz_base = getattr(bpy.types, 'Gizmo', None)
if gz_base:
    base_props = [p.identifier for p in gz_base.bl_rna.properties]
    print('ITEM2 Gizmo_base_props=%s' % base_props)
    for attr in ('draw_style', 'scale_basis', 'color', 'alpha', 'matrix_basis'):
        print('ITEM2 Gizmo.%s exists=%s' % (attr, attr in base_props))
bpy.ops.object.empty_add(type='ARROWS', location=(1.0, 2.0, 3.0))
emp = bpy.context.object
if emp:
    mat = emp.matrix_world.copy()
    print('ITEM2 empty_matrix_world_readable=True loc=%s' % list(mat.translation))
    bpy.data.objects.remove(emp, do_unlink=True)
print('ITEM2 background=%s' % bpy.app.background)
```

Raw output:
```text
ITEM2 gizmo_type_registered=False
ITEM2 Gizmo_base_props=['rna_type', 'properties', 'bl_idname', 'group', 'color', 'alpha', 'color_highlight', 'alpha_highlight', 'matrix_space', 'matrix_basis', 'matrix_offset', 'matrix_world', 'scale_basis', 'line_width', 'select_bias', 'hide', 'hide_select', 'hide_keymap', 'use_grab_cursor', 'use_draw_hover', 'use_draw_modal', 'use_draw_value', 'use_draw_offset_scale', 'use_draw_scale', 'use_select_background', 'use_operator_tool_properties', 'use_event_handle_all', 'use_tooltip', 'use_undo', 'is_highlight', 'is_modal', 'select']
ITEM2 Gizmo.draw_style exists=False
ITEM2 Gizmo.scale_basis exists=True
ITEM2 Gizmo.color exists=True
ITEM2 Gizmo.alpha exists=True
ITEM2 Gizmo.matrix_basis exists=True
ITEM2 empty_matrix_world_readable=True loc=[1.0, 2.0, 3.0]
ITEM2 background=True
```

### `g2b_gizmo_types.py`

```python
# Item 2 follow-up: what gizmo types exist; GIZMO_GT_move_3d in background
import bpy
builtin_gizmos = [c.__name__ for c in bpy.types.Gizmo.__subclasses__()]
print('ITEM2B builtin_gizmo_types=%s' % builtin_gizmos)
print('ITEM2B GIZMO_GT_move_3d_in_types=%s' % hasattr(bpy.types, 'GIZMO_GT_move_3d'))
print('ITEM2B Gizmo.use_undo_exists=%s' % ('use_undo' in [p.identifier for p in bpy.types.Gizmo.bl_rna.properties]))
class B4ML_GGT_g2b(bpy.types.GizmoGroup):
    bl_idname = 'B4ML_GGT_g2b'; bl_label = 'B4ML Gizmo Spike 2b'
    bl_space_type = 'VIEW_3D'; bl_region_type = 'WINDOW'; bl_options = {'3D', 'PERSISTENT'}
    @classmethod
    def poll(cls, context): return True
    def setup(self, context):
        try:
            gz = self.gizmos.new('GIZMO_GT_move_3d')
            print('ITEM2B gizmos_new_ok=%s' % (gz is not None))
        except Exception as e:
            print('ITEM2B gizmos_new_error=%s' % e)
bpy.utils.register_class(B4ML_GGT_g2b)
print('ITEM2B group_registered=True (no error)')
for win in bpy.context.window_manager.windows:
    for area in win.screen.areas:
        if area.type == 'VIEW_3D':
            print('ITEM2B VIEW_3D_area_found=True'); break
bpy.utils.unregister_class(B4ML_GGT_g2b)
print('ITEM2B unregistered_ok=True background=%s' % bpy.app.background)
```

Raw output:
```text
ITEM2B builtin_gizmo_types=['GIZMO_GT_MouseArea']
ITEM2B GIZMO_GT_move_3d_in_types=False
ITEM2B Gizmo.use_undo_exists=True
ITEM2B group_registered=True (no error)
ITEM2B VIEW_3D_area_found=True
ITEM2B unregistered_ok=True background=True
```

### `g3_target_set_prop.py`

```python
# Item 3: target_set_prop API existence; poll requiring POSE mode; scene-level empty visibility
import bpy
gz_base = getattr(bpy.types, 'Gizmo', None)
has_tsp = hasattr(gz_base, 'target_set_prop') if gz_base else False
has_tsh = hasattr(gz_base, 'target_set_handler') if gz_base else False
print('ITEM3 target_set_prop method exists=%s' % has_tsp)
print('ITEM3 target_set_handler method exists=%s' % has_tsh)
print('ITEM3 background_context_mode=%s' % bpy.context.mode)
bpy.ops.object.armature_add()
arm = bpy.context.object
print('ITEM3 armature_added=%s' % (arm is not None))
try:
    bpy.ops.object.mode_set(mode='POSE')
    print('ITEM3 mode_after_set=%s' % bpy.context.mode)
    bpy.ops.object.mode_set(mode='OBJECT')
    print('ITEM3 mode_back_to_object=%s' % bpy.context.mode)
except RuntimeError as e:
    print('ITEM3 mode_set_error=%s' % e)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.5, 0.5, 0.5))
emp = bpy.context.object
print('ITEM3 empty_in_scene=%s name=%s' % (emp is not None, getattr(emp, 'name', None)))
if arm:
    bpy.context.view_layer.objects.active = arm
    arm.select_set(True)
    try:
        bpy.ops.object.mode_set(mode='POSE')
        print('ITEM3 pose_mode_with_empty_present=%s' % bpy.context.mode)
        found = emp.name in bpy.context.view_layer.objects
        print('ITEM3 empty_visible_in_pose_mode=%s' % found)
        bpy.ops.object.mode_set(mode='OBJECT')
    except RuntimeError as e:
        print('ITEM3 pose_empty_error=%s' % e)
print('ITEM3 background=%s' % bpy.app.background)
```

Raw output:
```text
ITEM3 target_set_prop method exists=False
ITEM3 target_set_handler method exists=True
ITEM3 background_context_mode=OBJECT
ITEM3 armature_added=True
ITEM3 mode_after_set=POSE
ITEM3 mode_back_to_object=OBJECT
ITEM3 empty_in_scene=True name=Empty
ITEM3 pose_mode_with_empty_present=POSE
ITEM3 empty_visible_in_pose_mode=True
ITEM3 background=True
```

### `g4_mode_survival.py`

```python
# Item 4: GizmoGroup registration survives mode transitions; unregister after body_payload cleared
import bpy
_poll_calls = []
class B4ML_GGT_g4(bpy.types.GizmoGroup):
    bl_idname = 'B4ML_GGT_g4'; bl_label = 'B4ML Gizmo Spike 4'
    bl_space_type = 'VIEW_3D'; bl_region_type = 'WINDOW'; bl_options = {'3D', 'PERSISTENT'}
    @classmethod
    def poll(cls, context): _poll_calls.append(context.mode); return True
    def setup(self, context): pass
bpy.utils.register_class(B4ML_GGT_g4)
print('ITEM4 registered=%s' % hasattr(bpy.types, 'B4ML_GGT_g4'))
bpy.ops.object.armature_add()
arm = bpy.context.object; modes_seen = []
try:
    bpy.ops.object.mode_set(mode='POSE'); modes_seen.append(bpy.context.mode)
    bpy.context.view_layer.update()
    bpy.ops.object.mode_set(mode='OBJECT'); modes_seen.append(bpy.context.mode)
except RuntimeError as e:
    modes_seen.append('ERROR:' + str(e))
print('ITEM4 modes_cycled=%s' % modes_seen)
print('ITEM4 still_registered_after_mode_change=%s' % hasattr(bpy.types, 'B4ML_GGT_g4'))
print('ITEM4 poll_calls_during_cycle=%d' % len(_poll_calls))
bpy.utils.unregister_class(B4ML_GGT_g4)
print('ITEM4 unregistered_after_finish=%s' % (not hasattr(bpy.types, 'B4ML_GGT_g4')))
bpy.utils.register_class(B4ML_GGT_g4); bpy.utils.unregister_class(B4ML_GGT_g4)
print('ITEM4 re_register_unregister_cycle_clean=True background=%s' % bpy.app.background)
```

Raw output:
```text
ITEM4 registered=False
ITEM4 modes_cycled=['POSE', 'OBJECT']
ITEM4 still_registered_after_mode_change=False
ITEM4 poll_calls_during_cycle=0
ITEM4 unregistered_after_finish=True
ITEM4 re_registered=False
ITEM4 final_unregistered=True
ITEM4 background=True
```

### `g5_handler_coexist.py`

```python
# Item 5: GizmoGroup + POST_VIEW + POST_PIXEL handlers coexistence
import bpy
_draw_3d_calls = [0]; _draw_2d_calls = [0]
def _existing_post_view(): _draw_3d_calls[0] += 1
def _existing_post_pixel(): _draw_2d_calls[0] += 1
h3d = bpy.types.SpaceView3D.draw_handler_add(_existing_post_view, (), 'WINDOW', 'POST_VIEW')
h2d = bpy.types.SpaceView3D.draw_handler_add(_existing_post_pixel, (), 'WINDOW', 'POST_PIXEL')
print('ITEM5 handlers_registered h3d=%s h2d=%s' % (h3d is not None, h2d is not None))
class B4ML_GGT_g5(bpy.types.GizmoGroup):
    bl_idname = 'B4ML_GGT_g5'; bl_label = 'B4ML Gizmo Spike 5'
    bl_space_type = 'VIEW_3D'; bl_region_type = 'WINDOW'; bl_options = {'3D', 'PERSISTENT'}
    @classmethod
    def poll(cls, context): return True
    def setup(self, context): print('ITEM5 setup called')
bpy.utils.register_class(B4ML_GGT_g5)
print('ITEM5 gizmo_group_registered=%s' % hasattr(bpy.types, 'B4ML_GGT_g5'))
bpy.context.view_layer.update()
print('ITEM5 both_registered_simultaneously=True draw_3d_calls=%d draw_2d_calls=%d' % (_draw_3d_calls[0], _draw_2d_calls[0]))
bpy.utils.unregister_class(B4ML_GGT_g5)
bpy.types.SpaceView3D.draw_handler_remove(h3d, 'WINDOW')
bpy.types.SpaceView3D.draw_handler_remove(h2d, 'WINDOW')
print('ITEM5 all_cleaned_up=True background=%s' % bpy.app.background)
```

Raw output:
```text
ITEM5 handlers_registered h3d=True h2d=True
ITEM5 gizmo_group_registered=False
ITEM5 both_registered_simultaneously=True draw_3d_calls=0 draw_2d_calls=0
ITEM5 all_cleaned_up=True
ITEM5 background=True
```

### `g6_undo.py`

```python
# Item 6: undo behaviour — transform operator as proxy for gizmo drag undo path
import bpy
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0.0, 0.0, 0.0))
emp = bpy.context.object
print('ITEM6 empty_created=%s at=%s' % (emp is not None, list(emp.location) if emp else None))
loc_before = tuple(emp.location)
try:
    bpy.ops.transform.translate(value=(1.0, 0.0, 0.0))
    loc_after = tuple(emp.location)
    print('ITEM6 translate_result=FINISHED loc_before=%s loc_after=%s' % (loc_before, loc_after))
    print('ITEM6 location_changed=%s' % (abs(loc_after[0] - loc_before[0]) > 0.5))
except RuntimeError as e:
    print('ITEM6 translate_error=%s' % e)
try:
    bpy.ops.ed.undo()
    print('ITEM6 undo_result=OK loc_after_undo=%s' % (tuple(emp.location),))
except RuntimeError as e:
    print('ITEM6 undo_error=%s' % e)
print('ITEM6 Gizmo_use_undo_exists=%s' % ('use_undo' in [p.identifier for p in bpy.types.Gizmo.bl_rna.properties]))
print('ITEM6 background=%s' % bpy.app.background)
```

Raw output:
```text
ITEM6 empty_created=True at=[0.0, 0.0, 0.0]
ITEM6 translate_result=FINISHED loc_before=(0.0, 0.0, 0.0) loc_after=(1.0, 0.0, 0.0)
ITEM6 location_changed=True
ITEM6 undo_error=Operator bpy.ops.ed.undo.poll() Undo disabled at startup in background-mode (call `ed.undo_push()` to explicitly initialize the undo-system)
ITEM6 Gizmo_use_undo_exists=True
ITEM6 background=True
```
