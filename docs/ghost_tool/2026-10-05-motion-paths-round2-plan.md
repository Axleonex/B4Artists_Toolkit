# Ghost Tool Motion Paths — Round 2 Implementation Plan

> **For the executing agent:** work task by task. Rounds A–C on branch
> `work/ghost-tool-paths-gaps` (already holds the two cache fixes, `228a946`);
> rounds D–G each on their own `work/ghost-tool-paths-<round>` branch from `main`.
> Commit after every task with the Axlbot identity
> (`-c user.name=Axlbot -c user.email=57645501+Axleonex@users.noreply.github.com`),
> never a co-author line, never touch `bl_info["description"]`.
> Route with `prime-code-execute.py` and every path the round touches **before the
> first edit of that round**, and re-route before touching an undeclared file.

**Goal:** Give Ghost Tool the motion-path features of Draw to Keys, Real-Time Paths,
MotionPath and QuickPath RKNZ, as specified in
`2026-10-05-motion-paths-design.md` §8. The owner approves §8 before Round B starts.

**How to read this plan:** the 3.5.0 plan (`2026-10-05-motion-paths-plan.md`) spelled
out every line of code. This plan fixes *what* each task does, *where*, and *which test
proves it*; the code is written at execution time in the same style (tests first,
`motion_paths.py` owns paths, `ghost_data.py` owns scene data, `ui_panel.py` owns UI).
Where a task depends on a fact about Bforartists 5.1.2 that was not checked while
planning, it starts with a **Probe** and says what to do for each outcome.

**Run tests with:**
```bash
cd "G:/LapArt/Projects/Blender_Addons/B4Artists_Tools" && "/c/Program Files/Bforartists/5.1.2/bforartists.exe" --background --factory-startup --python tests/test_ghost_paths.py 2>&1 | grep -E "^Ran |^OK|^FAILED|^FAIL:|^ERROR:|Error:|Traceback"
```
After every task also run `test_ghost_header_ui.py`, `test_ghost_correctness.py`,
`test_ghost_regressions.py`, `test_tooltip_coverage.py` and `smoke_bforartists.py`
(exit 0), then `rm -rf ghost_tool/__pycache__`. Every new operator gets a
`bl_description`; every new property gets a `description` (the tooltip suite fails
otherwise).

Baseline when this plan was written: paths 56 OK, header 16, correctness 46,
regressions 20.

---

## Round A — finish the 3.5.0 design (→ 3.5.1)

### Task A1: Head/Tail anchor in the UI
**Objective:** expose `GhostPathEntry.anchor`, which exists but has no control.
**Files:** `ghost_tool/ui_panel.py`, `ghost_tool/motion_paths.py`, `tests/test_ghost_paths.py`.
**Steps:**
1. Failing test `test_set_color_dialog_edits_anchor`: `paths_set_color` gets an
   `anchor` property; `bpy.ops.ghost_tool.paths_set_color(index=0, anchor='TAIL')`
   on a bone entry sets `entry.anchor == 'TAIL'`; on an object entry the operator
   leaves anchor `'HEAD'` and the dialog hides the field (assert via a `draw`
   helper `_dialog_rows(entry)` that returns the property names it would draw).
2. Add `anchor` to `GHOST_OT_paths_set_color` (init from the entry in `invoke`,
   write in `execute`), rename the operator label to "Path Settings".
3. In `GHOST_UL_paths.draw_item`, after the name, a small `H`/`T` label for bone
   entries (`emboss=False` operator calling `paths_set_color` with the opposite
   anchor, so one click flips it). Tooltip: "Trace the bone head / tail".
4. Help topic text: add "Bones can trace their head or their tail."
**Commit:** `Ghost Tool paths: Head/Tail in the list and settings dialog`.

### Task A2: active-bone row highlight
**Objective:** §4 "Active bone's row highlighted".
**Steps:**
1. Failing test `test_active_bone_row_is_flagged`: `mp.active_entry_index(context)`
   returns the index of the entry matching `_active_key(context)` or -1.
2. In `draw_item`, when `index == active_entry_index`, draw icon `'RADIOBUT_ON'`
   in place of the kind icon (Blender UIList cannot colour a row; the icon swap is
   the visible cue). Add a test that `_row_icon(entry, is_active)` returns
   `'RADIOBUT_ON'` for the active one.
**Commit:** `Ghost Tool paths: mark the active bone's row`.

### Task A3: Custom range fields in the popover
**Steps:**
1. Failing test `test_popover_lists_custom_range_props`: a pure helper
   `_range_props(settings)` returns `("custom_range_start", "custom_range_end")`
   when `paths_range_mode == 'CUSTOM'`, `("paths_before", "paths_after")` for
   `AROUND_CURSOR`, `()` for `SCENE`.
2. `_draw_motion_paths` draws whatever `_range_props` returns.
**Commit:** `Ghost Tool paths: custom range fields in the popover`.

### Task A4: full slow warning
**Steps:** label text becomes `"paths are slow — reduce range"`, icon `'ERROR'`,
only when `last_refresh_ms() > 200`. Test: `_slow_label(ms)` returns `""` at 199
and the text at 201. **Commit:** `Ghost Tool paths: slow warning text`.

### Task A5: the §6 tests not yet written
Add, in `tests/test_ghost_paths.py` (fix any behaviour they expose):
- `test_rename_marks_missing_and_rename_back_restores` — rename `lower` → `foo`:
  `entry_is_missing` True, `pinned_targets` skips it, `draw`-side builder
  `path_segments` returns `[]` with no exception; rename back: path draws again
  after `refresh_paths`.
- `test_deleted_bone_draws_nothing_without_exception` — delete the bone in Edit
  mode; `request_missing_samples` and `path_segments` run clean.
- `test_follow_deselect_removes_only_follow_paths` — pin `upper`, follow on,
  select `upper`+`lower`; deselect all → `all_targets` has only `upper`, pinned.
- `test_range_change_samples_only_new_frames` — count `_sample` calls with
  `patch.object(mp, "_sample", wraps=mp._sample)`: `paths_after 3 → 5` samples
  exactly 2 per target.
- `test_z_save_reload_keeps_list_and_rebuilds_cache` — save to a
  `tempfile.TemporaryDirectory`, `wm.open_mainfile`, assert the list survived,
  `_cache == {}` after `_on_file_load`, then `refresh_paths` refills it. The `test_z_`
  name makes it run last (unittest sorts by name), the same pattern as
  `test_ghost_correctness.py:test_z_file_load_retains_handlers_and_clears_runtime_state`;
  read the reloaded scene from `bpy.context`, never from `self.scene`.
**Commit:** `Ghost Tool paths: design §6 tests`.

**Done 2026-10-05 (A1–A5, one commit).** Findings while executing:
- A1: `paths_set_color` writes only the properties the caller set
  (`is_property_set`); otherwise the list's one-click H/T button would have reset the
  colour to black. Skipping an unchanged anchor avoids a needless re-sample.
- A5's range test exposed waste: every range, step, Follow or anchor change emptied the
  whole cache, so widening the window by 2 frames re-sampled 9. Only `paths_enabled`
  still clears everything (edits made while paths are off are never marked dirty);
  window changes keep the cache; an anchor change forgets only that path
  (`motion_paths.forget`).
- The other four §6 tests passed on first run: that behaviour already worked.
- Not checked by eye: the list row drawing (icon, H/T button) cannot run headless;
  it is on the A6 manual checklist.

### Task A6: release 3.5.1 (owner-gated)
Version `(3, 5, 1)`, zip, `releases/VERSIONS.md`, README rows, GitHub release
`ghost-v3.5.1`. Manual checklist in the commit message: Head/Tail flip visible in
the list and one click moves the path to the tail without changing its colour; the
active bone's row shows a dot; Custom shows Start/End; Ctrl+Z after a key move snaps the path back
(the open-loop probe for `228a946`); turning Ghost Tools off then on after a key
edit shows the new path. **Ask "Confirm merge update?" before merging to main.**

---

## Round B — look (→ 3.6.0 with Round C)

### Task B1: Split style (before/after colours)
**Files:** `ghost_data.py` (`color_before` on the entry, `'SPLIT'` in `paths_style`),
`motion_paths.py` (`path_segments`), `ui_panel.py` (dialog field, style row).
**Steps:**
1. Failing test `test_split_style_colours_before_and_after_playhead`: with the
   playhead at 10 and frames 7..13, segments whose midpoint < 10 carry
   `color_before`, the rest `color`; the segment straddling 10 is split at the
   playhead sample (so 7 segments, not 6).
2. `path_segments`: for `SPLIT`, split the straddling segment at the cached
   position of `frame_current` when it is in the window.
3. Default `color_before` on add = `tuple(c * 0.55 for c in color)`; a test asserts
   `paths_add_selected` sets it.
**Commit:** `Ghost Tool paths: Split style`.

### Task B2: per-path dot size
**Steps:** `dot_size` IntProperty 1–12 default 6 on the entry; `draw_motion_paths`
uses `gpu.state.point_size_set(float(target.dot_size))` per target (`PathTarget`
gains `dot_size`); dialog field. Test: `pinned_targets` carries `dot_size`; the
dialog helper lists `dot_size`. **Commit:** `Ghost Tool paths: dot size per path`.

### Task B3: draw in front, per path
**Probe first:** in Bforartists, pin a path that passes behind a cube. If the line
shows through the cube, today's handler has no depth test (`draw_motion_paths`
never calls `depth_test_set`) and "in front" is the current look.
- Probe says *shows through* → property `in_front` default **True**; when False,
  wrap that path's draw in `gpu.state.depth_test_set('LESS_EQUAL')` … `'NONE'`.
- Probe says *hidden* → default **False**; when True, set `depth_test_set('NONE')`.
Record the outcome in the commit message. Test: `_depth_mode(target)` returns
`'NONE'` / `'LESS_EQUAL'` for the two settings. List row gets the cube icon toggle
(`'XRAY'`) via `paths_toggle_front(index)`.
**Commit:** `Ghost Tool paths: draw in front per path`.

### Task B4: glow on the list's active entry
**Steps:** `paths_active_glow` BoolProperty default True; in `draw_motion_paths`,
when `target.key` is the key of `motion_paths[motion_paths_index]`, draw the
segments once with width `thickness + 4` and alpha 0.25 before the normal pass.
Test: `_passes_for(target, is_list_active, glow_on)` returns 2 passes with the
wide one first, 1 otherwise. **Commit:** `Ghost Tool paths: active entry glow`.

### Task B5: per-path range override
**Files:** `ghost_data.py` (entry: `use_own_range`, `own_range_mode`, `own_before`,
`own_after`, `own_step`, `own_start`, `own_end`), `motion_paths.py`
(`desired_frames(settings, scene, entry=None)`, `refresh_paths`, `draw_*`,
`sync_markers`, `request_missing_samples` all go per target), `ui_panel.py` (dialog block).
**Steps:**
1. Failing test `test_entry_range_override`: entry A default, entry B
   `use_own_range=True, own_before=1, own_after=1` → `frames_for(target_B)` is
   `[9,10,11]` while A keeps 7 frames; `refresh_paths` samples 7 + 3; the cache
   keeps A's frame 7 and has no B frame 7.
2. `PathTarget` gains `frames: tuple[float, ...]`, filled by `pinned_targets`/
   `follow_targets`; every consumer reads `target.frames` instead of calling
   `desired_frames` itself. `wanted` in `refresh_paths` is built per target.
3. Perf gate `test_refresh_budget_500_samples` stays < 50 ms with 10 overrides on.
4. `_on_path_setting_changed` also fires on the new entry properties.
5. Checked ▾ menu item "Reset range" (Task C3) clears `use_own_range`.
**Commit:** `Ghost Tool paths: per-path range`.

---

## Round C — organise (→ 3.6.0)

### Task C1: folders as rows
**Files:** `ghost_data.py` (entry: `is_folder`, `folder`, `collapsed`), `motion_paths.py`
(`pinned_targets` skips folders; visibility = entry AND folder; `entry_is_missing`
False for folders), `ui_panel.py` (`GHOST_UL_paths.filter_items` + folder row draw),
operators `paths_add_folder`, `paths_remove` (folder: move children to root first).
**Steps:**
1. Failing tests: `test_folder_rows_group_and_hide_children` (`filter_items`
   order puts each folder's children right after it; a collapsed folder hides
   them: flag bit cleared), `test_folder_visibility_gates_children`
   (folder `visible=False` → no child in `pinned_targets`),
   `test_removing_folder_keeps_paths` (children end up with `folder == ""`).
2. `filter_items` returns `(flags, order)`; children sort by (folder row index,
   own index). Root paths come first, then folders with their children.
3. Folder row: `▸/▾` operator `paths_toggle_folder(index)`, eye, name
   (`row.prop(item, "object_name", text="", emboss=False)` — folders store their
   name in `object_name`), ✕.
**Commit:** `Ghost Tool paths: folders`.

### Task C2: checkboxes and Apply to Checked
**Steps:** `checked` BoolProperty on the entry (not saved: `options={'SKIP_SAVE'}`
is for operators; use a plain property and clear it on file load in
`reset_for_new_file` via a scene walk — or accept it is saved; decide at task
start, record in the commit). Operator `paths_apply_to_checked` copies
`color, color_before, thickness, dot_size, in_front, anchor` (+ range override
when `include_range`) from the list's active entry to every checked path row.
Test: three entries, two checked, apply → both match the active; the unchecked
one is unchanged; folders are never written to.
**Commit:** `Ghost Tool paths: checkboxes and Apply to Checked`.

### Task C3: batch operators on checked rows
`paths_checked_action(action=SHOW|HIDE|REMOVE|RESET_RANGE|MOVE)`, `MOVE` takes
`folder: StringProperty` and offers existing folders in the dialog. Test per
action; `REMOVE` also drops cache keys and re-syncs markers; `MOVE` to a missing
folder name cancels with a report. Popover: `Checked ▾` menu (`GHOST_MT_paths_checked`).
**Commit:** `Ghost Tool paths: batch actions on checked rows`.

### Task C4: release 3.6.0 (owner-gated)
Manual checklist: Split style flips colour at the playhead while scrubbing;
dot size and in-front toggles visible; the glow follows the list selection;
a folder collapses and hides its rows; Apply to Checked recolours three paths at
once; a per-path range wider than the global one keeps its extra frames.
**"Confirm merge update?"**

---

## Round D — vertex paths (→ 3.7.0)

### Task D1: `PathKey` gains `vertex_index`
**Files:** `motion_paths.py` (every `(o, b)` key becomes `(o, b, v)`; cache keys
`(o, b, v, f)`), `ghost_data.py` (`vertex_index` IntProperty default -1 on the
entry), `tests/test_ghost_paths.py` (update every key literal — ~40 sites; do it
with a helper `K(obj, bone="", v=-1)`), `ghost_pipeline.py` (`mark_dirty_for_id`
unchanged in meaning).
**Steps:** mechanical, then the full suite green. **Commit:** `Ghost Tool paths: vertex index in the path key`.

### Task D2: sampling and adding vertices
**Steps:**
1. Failing tests: `test_vertex_path_samples_evaluated_vertex` (animated cube,
   vertex 0: cached position == `ev.matrix_world @ ev.data.vertices[0].co` at
   frame 13), `test_vertex_path_missing_when_topology_changes` (add a Subdivision
   modifier → evaluated count differs → `entry_is_missing` True; remove it →
   False), `test_add_selected_in_edit_mode_adds_vertices` (Edit mode, 3 verts
   selected → 3 entries with `vertex_index` set; 60 selected → 50 added and a
   report).
2. `_sample`: `if vertex_index >= 0: ev.data.vertices[vertex_index].co` via the
   evaluated object; `_resolve` checks `len(ev.data.vertices) == len(obj.data.vertices)`
   and `vertex_index < len`.
3. `selected_keys` in `'EDIT_MESH'` mode reads `bmesh.from_edit_mesh(obj.data)`
   selected verts (indices are stable in edit mode; `bm.verts.ensure_lookup_table()`).
4. `key_frames` for a vertex target: object location keys (the vertex moves with
   the object) plus shape-key `value` curves if the mesh has shape keys.
5. Markers on Paths: vertex paths get **no** markers (nothing to drag); `sync_markers`
   skips them; a test asserts it.
6. UI: kind icon `'VERTEXSEL'`, label `Object · v123`.
**Commit:** `Ghost Tool paths: vertex paths`.

### Task D3: release 3.7.0 (owner-gated). Checklist: a vertex path follows a
deforming (armature-modified) mesh vertex; a Subdivision modifier greys it.

---

## Round E — fast sampling (→ 3.8.0, gated)

### Task E0: gate
Open the owner's heaviest production rig in Bforartists, pin 20 bones, Around
Playhead 12/12, scrub. Read `last_refresh_ms()` from the Python console after
a scrub. **If it never exceeds 200 ms, stop here and record the number in
`releases/VERSIONS.md` notes; Round E is not needed.** Otherwise continue.

### Task E1: eligibility and the pure-math sampler
**Files:** new `ghost_tool/path_fast_sampler.py`, `motion_paths.py` (`_sample`
dispatch), tests.
**Steps:**
1. Failing tests: `test_fast_sampler_matches_frame_set_on_fixture_rig` (both
   bones, all 20 frames, max error < 1e-4 using
   `motion_channels.rest_channel_matrix` for the chain), `test_fast_sampler_refuses_constraints`
   (Copy Location on `lower` → `fast_eligible(target)` False; an animated parent
   object → False; a driver on any chain channel → False; a non-armature parent
   → False), `test_cache_records_sampler` (each cache value carries which sampler
   made it, so a target that becomes ineligible is marked dirty and re-stepped).
2. `fast_eligible(obj, bone_name)`: object has no constraints, no parent or an
   unanimated parent, no `animation_data.drivers`; for a bone, the whole parent
   chain has no constraints and no IK; rotation modes handled: QUATERNION, XYZ
   and the other Euler orders (`Euler(...,order).to_matrix()`), AXIS_ANGLE.
3. `sample_fast(obj, bone_name, anchor, frame)`: evaluate loc/rot/scale curves of
   each chain bone with `fcurve.evaluate(frame)` (missing curves → rest value),
   compose `parent_pose @ (parent_rest⁻¹ @ rest) @ local`, return head or tail in
   world space.
4. `refresh_paths`: group missing frames by eligible/ineligible targets; eligible
   ones never call `frame_set`; the perf test prints both timings.
**Commit:** `Ghost Tool paths: fast sampler with stepped fallback`.

### Task E2: release 3.8.0 (owner-gated). Checklist: the heavy rig from E0
scrubs without the slow warning; add a Copy Location constraint to a pinned bone
and confirm its path still matches the bone (fallback took over).

---

## Round F — handles on paths (→ 4.0.0)

### Task F1: handle geometry
**Files:** `motion_paths.py` (`key_handles(target, frame)`), `ghost_data.py`
(`paths_show_handles`), tests.
**Steps:**
1. Failing test `test_handle_points_from_location_curves`: for a key at frame 10
   on location X/Y/Z, `key_handles` returns `(left, right)` world points built by
   running `(handle_left.y, …)` of the three curves through the same local → world
   transform `_sample` uses for the key value (object: `matrix_parent_inverse` and
   parent world; bone: `rest_channel_matrix` under the parent's posed matrix at
   that frame — reuse `modal_operator._solve_channel_values`' inverse). A curve
   without a key at that frame contributes its evaluated value, not a handle.
2. Draw: with `paths_show_handles` on, draw thin lines key → left, key → right in
   the path colour at alpha 0.6 and 4 px dots at the ends. Head paths only
   (tails have no location curve of their own); a test asserts `key_handles` is
   `None` for TAIL anchors and vertex targets.
**Commit:** `Ghost Tool paths: show Bezier handles on key dots`.

### Task F2: dragging a handle
**Files:** `motion_paths.py` or new `ghost_tool/path_handle_drag.py`
(`GHOST_OT_path_handle_drag`, modal; hover/pick reuses
`modal_operator._find_ghost_under_cursor`'s screen-distance approach),
`fcurve_utils.py` (`set_handle_values(fcurve, frame, side, value, aligned)`).
**Steps:**
1. Failing tests (no modal; test the helpers): `test_set_handle_values_keeps_time`
   (`handle_right.x` unchanged, `.y` set, type → `'FREE'`),
   `test_aligned_moves_opposite_handle` (`'ALIGNED'` on both, opposite handle
   mirrored through the key in value space, its time unchanged),
   `test_handle_drag_solve` (a world delta on the handle end → per-axis handle
   values via the Task F1 transform; the key value itself unchanged).
2. Modal: LMB on a handle end starts; mouse moves the end in the view plane at
   the key's depth (`_get_depth_plane`); Alt toggles aligned; Esc/RMB restores
   from `snapshot_fcurve`; confirm marks the path dirty and pushes one undo step.
3. Markers on Paths and handles coexist: a drag on a marker moves the key (sets
   AUTO_CLAMPED as today), a drag on a handle end never moves the key. Picking
   prefers the handle end when both are within 8 px.
**Commit:** `Ghost Tool paths: drag handles`.

### Task F3: release 4.0.0 (owner-gated). Checklist: drag a handle, the path
between keys bends and the Graph Editor shows the handle moved in value only;
Alt keeps the pair aligned; Esc restores.

---

## Round G — Draw to Keys (→ 4.1.0)

### Task G1: probe the annotation API
In Bforartists 5.1.2, draw an annotation with Placement = Surface on a plane,
then in the Python console: `type(bpy.context.scene.grease_pencil)` and
`bpy.context.scene.grease_pencil.layers.active.frames[0].strokes[0].points[0].co`.
Record which type (legacy `GreasePencil` annotation or GPv3) and the point
coordinate space. The rest of the round reads strokes through one helper
`annotation_strokes(scene) -> list[list[Vector]]` so the rest of the code does
not care which it is. If annotations are not reachable from Python at all, stop
and report; the owner decides whether to read a Grease Pencil object instead.

### Task G2: crossings → frames (pure math, no bpy)
**Files:** new `ghost_tool/draw_to_keys.py`, `tests/test_ghost_draw_to_keys.py`
(runs under plain Python too, like `test_b4artists_ml_*_math` suites do).
**Steps:**
1. Failing tests: `test_longest_stroke_is_the_path`,
   `test_crossings_sorted_along_path` (a path polyline and two dashes crossing it
   at 30 % and 70 % of its length → arclength parameters `[0.3, 0.7]` within
   tolerance), `test_dash_that_misses_is_ignored` (closest approach > tolerance),
   `test_frames_from_crossings` (start 1, step 4 → frames `[1, 5]`; one crossing
   per dash even if the dash wiggles across twice — take the first).
2. `crossings(path, dashes, tolerance)`: segment–segment closest approach in 3D;
   a dash counts when its minimum distance to the path is below
   `tolerance × path_length`; the crossing point is the path point of closest
   approach, reported as arclength `t ∈ [0, 1]` and the 3D point.
**Commit:** `Ghost Tool draw to keys: crossing math`.

### Task G3: the operator
**Files:** `ghost_tool/draw_to_keys.py` (`GHOST_OT_paths_draw_to_keys`),
`ui_panel.py` (Edit Motion section button; path popover bottom row), help topic.
Properties: `axes` (enum flag X/Y/Z, default all), `use_current_frame`,
`start_frame`, `frame_step` (default 4), `interpolation`
(CONSTANT/LINEAR/BEZIER/SCENE), `write_stroke_value`, `crossing_tolerance`
(0.02), `clear_annotations_after` (default False).
**Steps:**
1. Failing tests (build strokes in the test through the Task G1 helper's
   writer counterpart, or monkeypatch `annotation_strokes`): object target gets
   `location` keys on the chosen axes at the computed frames with the chosen
   interpolation; a bone target gets `pose.bones["..."].location` keys whose
   evaluated world position matches the crossing point within 1e-4 (the
   world → channel solve from `modal_operator._solve_channel_values`, lifted
   into `motion_channels.solve_location_for_world_point(obj, bone, world, frame)`
   so both callers share it); `write_stroke_value` keys a `stroke_value` custom
   property with the arclength distance; fewer than 2 crossings cancels with a
   report; a View-placed stroke (all points share the view depth → detected by
   the probe outcome in G1) is refused with a report.
2. `poll`: an active object or pose bone and at least one annotation stroke.
3. The operator is undoable (`'REGISTER', 'UNDO'`), opens as a dialog
   (`invoke_props_dialog`), and marks the pinned paths dirty afterwards so the
   new motion shows immediately.
**Commit:** `Ghost Tool draw to keys: operator`.

### Task G4: release 4.1.0 (owner-gated). Checklist: draw a path and three dashes
on a plane, run Draw to Keys on a bone, scrub: the bone visits each crossing at
Start, Start+Step, Start+2·Step; Bezier vs Constant visibly differ; `stroke_value`
appears in the object's custom properties when enabled.

---

## Round X — investigate Motion Path Pro's "reference line" and "timeline visualisation"

### Task X1 (owner performs the download)
The extension is GPL and free on extensions.blender.org, but downloading and
installing a third-party add-on is the owner's call. Owner installs Real-Time
Paths 3.1.0 in a scratch Blender 5 profile, turns on each feature and writes
three lines per feature in `docs/ghost_tool/motion-path-pro-notes.md`: what it
draws, where it is controlled, what it is for. Then the agent writes a §8.7 in
the design doc with a proposal, and the owner approves or drops it. No code
before that.

---

## Order and dependencies

```
A1–A5 → A6 (3.5.1)
B1 B2 B3 B4 (independent) → B5 → C1 → C2 → C3 → C4 (3.6.0)
D1 → D2 → D3 (3.7.0)
E0 gate → E1 → E2 (3.8.0)   (may be skipped by the gate)
F1 → F2 → F3 (4.0.0)
G1 probe → G2 → G3 → G4 (4.1.0)
X1 any time, owner-driven
```
Rounds D–G are independent of each other and can be reordered by the owner.
Each round's branch is rebased on `main` after the previous release merges.
