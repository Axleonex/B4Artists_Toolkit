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

## Owner decisions, 2026-10-05 (asked for Round B, which approves design §8)

- **B3:** keep the per-path "in front" toggle (cube icon on each list row) **and** add
  popover buttons "All in front" / "All behind", like All on / All off. The default keeps
  today's look (see the B3 outcome below).
- **G1:** Draw to Keys reads annotation strokes exactly as the Draw to Keys extension
  does (Annotate tool; longest stroke = path, crossing dashes = keys). The "fall back to a
  Grease Pencil object" branch is dropped.
- **E0:** answered "No": the owner's rigs do not trip the slow warning. Round E (fast
  sampling, 3.8.0) is skipped. It can be reopened if a rig ever shows the warning.
- **X1:** closed. Motion Path Pro's "reference line", "timeline visualization",
  "handle setup" and "editable path with rotation" are listed under "Future update" on its
  Superhive page and in its extension version history; nothing released to copy. Its
  released features map to Ghost Tool: edit in the 3D view = Markers on Paths; rotation =
  Tail-path rotation markers; control handles = Round F; paths list = pinned list + Round C.
- **Release line-up:** 3.5.1 (cache fixes + Round A), 3.6.0 (B + C), 3.7.0 (D vertex
  paths), 4.0.0 (F handles), 4.1.0 (G Draw to Keys).

## Round B — look (→ 3.6.0 with Round C)

Branch `work/ghost-tool-paths-round-b` from `work/ghost-tool-paths-gaps` (`65ec0cf`).

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
**Probe (resolved from source, not by eye):** Blender 5.1's
`drw_callbacks_post_scene` (`source/blender/draw/intern/draw_context.cc`, branch
`blender-v5.1-release`) calls `GPU_depth_test(GPU_DEPTH_NONE)` and `GPU_apply_state()`
right before `ED_region_draw_cb_draw(..., REGION_DRAW_POST_VIEW)`, and binds
`overlay_fb`, whose depth attachment is the viewport depth texture
(`gpu_viewport.cc`). So today's paths draw through geometry, and a depth test of
`LESS_EQUAL` does hide them behind it.
- Property `in_front` default **True** (today's look); when False, that path draws with
  `gpu.state.depth_test_set('LESS_EQUAL')`; the handler restores `'NONE'` at the end.
Test: `_depth_mode(target)` returns `'NONE'` / `'LESS_EQUAL'` for the two settings.
List row gets the cube icon toggle (`'XRAY'` in front, `'MESH_CUBE'` behind) via
`paths_toggle_front(action='ONE', index)`; the popover gets "All in front" / "All behind"
(`action='ALL_ON'` / `'ALL_OFF'`).
**Commit:** `Ghost Tool paths: draw in front per path`.

### Task B4: glow on the list's active entry
**Steps:** `paths_active_glow` BoolProperty default True; in `draw_motion_paths`,
when `target.key` is the key of `motion_paths[motion_paths_index]`, draw the
segments once with width `thickness + 4` and alpha 0.25 before the normal pass.
Test: `_passes_for(target, is_list_active, glow_on)` returns 2 passes with the
wide one first, 1 otherwise. **Commit:** `Ghost Tool paths: active entry glow`.

**Done 2026-10-05 (B1–B4, one commit).** Findings while executing:
- B1: the planned test was inconsistent: with Every = 1 the playhead (frame 10) is a
  sample, so no segment straddles it and the path keeps 6 segments. The test now checks
  that case (3 before, 3 after) and Every = 2 (samples 7, 9, 11, 13: the 9–11 segment
  is split, 4 segments). The split point is interpolated on the drawn straight segment,
  not taken from the cache: with Every > 1 the cache has no sample at the playhead, and a
  cached point off the straight line would put a kink in the path only in Split style.
- B1/B2: Colour Before (style Split only) and Dot Size are in the Path Settings dialog;
  `dialog_props(entry)` lists them, so the "write only what the caller set" rule from A1
  covers them.
- B3: outcome above (default in front, from Blender 5.1 source). The handler now resets
  depth test and point size at the end.
- B4: Glow is a toggle in the popover's Markers / Key dots / Frame # row. Only pinned
  paths glow; a Follow path with the same key does not exist (Follow skips pinned keys).
- Not checked headless (owner's 3.6.0 checklist): every GPU draw (Split colours while
  scrubbing, dot size, a path behind a cube hidden when the cube button is off, the glow
  under the list-selected path), and the list row (cube icon swaps XRAY / MESH_CUBE),
  the "All in front" / "All behind" row, and the dialog fields.

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

**Done 2026-10-05 (B5).** Findings while executing:
- Step 4 changed: the entry's range properties use `_on_path_window_changed` (keeps the
  cache), not `_on_path_setting_changed` (clears it). Since A5 only `paths_enabled` clears
  the whole cache; one path's range change samples only the frames new to that path.
- `PathTarget.frames` is filled by `pinned_targets` (own range or the shared global one,
  computed once per call) and `follow_targets` (global). `refresh_paths`, `path_segments`
  (frames now optional, default `target.frames`), `draw_motion_paths`,
  `draw_frame_numbers`, `sync_markers` and `request_missing_samples` all read it.
  `sync_markers` groups bones by (object, anchor, frames), so each window gets its own
  marker job.
- Dialog: Own Range block (mode, Before/After or Start/End, Every). Added
  `own_range_seed`: a path without its own range opens the dialog with the global
  values, so ticking Own Range changes nothing until a field is edited (otherwise the
  entry defaults 12 / 12 would jump in).
- Perf gate with 10 overrides on: 500 samples in ~5 ms (limit 50).
- Not checked headless: the dialog layout (fields appear when Own Range is ticked),
  and the drawn paths/frame numbers following each path's own window.

**Round B results (2026-10-05):** paths 71 OK (64 + 7), header 16, correctness 46,
regressions 20, tooltip coverage OK, smoke exit 0. Owner's 3.6.0 checklist additions
from Round B (all GPU or list drawing, none checkable headless): Split flips colour at
the playhead while scrubbing (also with Every 2); dot size visibly changes per path; the
cube button hides one path behind a cube and "All in front" / "All behind" flip every
row's icon; the glow follows the list selection and Glow off removes it; a path with
its own wider range keeps its extra frames and frame numbers; the dialog shows the Own
Range fields as soon as the box is ticked.

**Done 2026-10-05 (Round B evidence review, branch `work/ghost-tool-paths-round-b-reviewed`).**
Round B was re-applied in three routed parts so the change review saw it. Findings:
- Part 1 (run `6eb8b9dc`), F1, advisory: `color_before` had a fixed gold default
  (gold × 0.55) while §8.2 says "default = color × 0.55". Add Selected already set it per
  path, but a path saved before 3.6 has no stored value and drew Split in dim gold
  whatever its colour. Fix: `color_before` is a get/set property. Until set it reads as
  the path's own colour × 0.55 (and follows colour changes); once set (the dialog in
  Split style, Add Selected) the stored value stays. get/set rather than
  `get_transform`, because `get_transform` does not exist before Blender 5.0 and
  `ghost_tool` declares 4.0. Test `test_path_colour_before_follows_colour_until_set`
  (regressions 21; correctness 47, since it reruns the regression cases).
- Part 2 (run `e1877198`), advisory: the in-front and glow tests check the draw logic
  (`_depth_mode`, `_passes_for`), not the pixels. No change: headless Bforartists cannot
  render GPU drawing, and both are on the owner's 3.6.0 checklist above.

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

**Done 2026-10-05 (C1–C3, branch `work/ghost-tool-paths-round-c` from `2630bcd`, two routed
parts).** Decisions and findings while executing:
- Folder identity: a folder row keeps a fixed `folder_key` (8 hex chars) and its paths store that
  key in `folder`, not the folder's name as §8.2 wrote. The list renames a folder inline
  (`row.prop(item, "object_name")`), and a name reference would drop its paths on rename.
  A path whose folder is gone is a top-level path.
- C2 decision: `checked` is a plain saved property, like Blender's own selection. No load-time
  clearing.
- Add Folder moves the checked paths into the new folder (and unchecks them); with none checked
  it adds an empty folder. Folder names are "Folder", "Folder 2", ….
- "Move to folder…" is a submenu of the Checked menu (Top Level plus each folder), not a dialog.
  The Checked menu also has "Apply to Checked with Range".
- Apply to Checked copies colour, thickness, dot size and in front, the anchor only between bone
  paths (an object origin has no tail), and the colour-before *choice*: a source that follows
  its colour leaves the targets following theirs.
- The list order and filtering live in `motion_paths.list_rows`; `GHOST_UL_paths.filter_items`
  turns them into Blender's flags and new positions. The header count shows paths, not folders.
- Review C1 (run `8c2a6333`), F1: with Follow on, a pinned path hidden by its eye or its folder
  came back as a grey Follow path when selected. Follow is for unpinned selections (§2 tests),
  so `all_targets` now passes every pinned key. This also fixes eye-hidden paths from 3.5.
  F2: the checked Remove test only checked that sync ran; it now reads the marker store
  (review `e5217051` pointed out that `owned_markers` filters by ownership and cannot see a leak).
- Tests: `tests/test_ghost_paths_folders.py` (16), run without re-running `test_ghost_paths`.
  The UI tests draw into a recording layout and check every icon name against
  `UILayout.operator`'s icon enum, because a wrong icon only fails when Blender draws.
- Drawing the folder name with `prop(item, "object_name")` made `test_tooltip_coverage` require
  hover text on every property named `object_name`; two in `anim_assist/core/properties.py` had
  none. Fixed in a separate routed run (`d766142a`), because that file was not declared in part 2.
- Review C2 (run `27ec4c4e`), F1: a folder row has a checkbox (design §8.3) but path actions
  ignored a checked folder. Now a checked folder stands for its paths in the path actions
  (`checked_paths`: Apply to Checked, Reset Range, Move, Add Folder). Show, Hide and Remove act on
  rows, so a checked folder shows, hides or is removed as a whole (its paths move to the top
  level). Test `test_checked_folder_stands_for_its_paths`.
- Review `d766142a`, advisory: Add Folder moved a checked folder's paths but left that folder
  checked and empty, so a second Add Folder moved nothing. Add Folder now unchecks the folders it
  emptied. Test `test_add_folder_unchecks_the_folder_it_emptied`.
- **3.6.0 checklist, captured 2026-10-06** in Bforartists 5.1.2 (GUI, add-on loaded from the
  worktree, script and 13 screenshots in `G:\LapArt\output\ghost-tool-3.6.0-eyecheck\`).
  Passed: Split flips at the playhead (pixel colours: after (54,151,254), before (61,95,140);
  with Every 2 one clean change between samples); a path with no stored colour-before draws a
  dim version of its own colour, not gold; dot size 3 vs 12 px; a path behind a wall is hidden
  with in front off and drawn over it with in front on; the glow follows the list selection and
  Glow off removes it (pixel diff only around the selected path); a per-path scene range keeps
  frames 1–30 while the global window is 6–24; folder open/closed, indent, checkboxes; Apply to
  Checked recolours a checked folder's two paths. Found: at `bl_ui_units_x = 14` the popover cut
  names to "Rig › ..." and "Apply to C…"; now 18. The width evidence is the re-captured
  `11_folders_open_checked_row.png` (same folder), which shows "Motion paths · 3",
  "Apply to Checked", "Rig › upper" and "Rig › lower" in full. Text width cannot be measured
  headless, so `test_popover_is_wide_enough_for_checkbox_rows` only guards against the width
  going back below 18 (review `b47d4c88`).
  Not captured: scrubbing feel and the Path Settings dialog (Own Range fields appear on tick).
- Review `b47d4c88`, advisory: Add Folder unchecked every folder, also a checked folder it took
  no path from. It now unchecks only the folders its moved paths came from.
- Not checked headless (owner's 3.6.0 checklist): the folder row look, the indent of a path in a
  folder, renaming a folder in the list, the Checked ▾ and Move to submenus.

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

**Done 2026-10-06 (D1–D2, branch `work/ghost-tool-paths-round-d` from `aefa1ca`, three routed parts).**
Decisions and findings while executing:
- Part 1 (`45cd3457`): `vertex_index` on the entry (-1 = none, clamped); the label reads
  `Object · v123`. Review: the save/load test read the active scene; it now reads the saved scene
  by name.
- Part 2 (`2be23ce9`): `PathKey = (object, bone, vertex)`, cache keys `(*key, frame)`, built by
  `entry_key`; tests use `K()` / `C()` helpers. `forget()` still takes an `(object, bone)` pair as
  vertex -1, the form `ghost_data`'s Head/Tail callback passes, so `ghost_data.py` did not change.
  Review: the key test never checked the vertex path's own cache key; it now does.
- Part 3 (`b1d2370a`): `_sample` reads the evaluated mesh (`ev.data.vertices[i].co`, so armature,
  shape keys and other deformers apply); `_vertex_usable` marks the path missing when the evaluated
  vertex count differs from the mesh's (a Subdivision modifier) or the index is out of range.
  Add Selected in Edit Mode reads `bmesh.from_edit_mesh` selections, at most 50 vertices per click
  with a warning. Additions not in the plan: Follow ignores Edit Mode selections (thousands of
  vertices would each get a path); deformer objects (any modifier `.object`) count as
  dependencies, and Mesh / shape-key Key / shape-key Action updates dirty the vertex paths of
  their objects. Key dots: the object's location keys plus shape-key `value` keys. No markers
  on vertex paths. Row icon `VERTEXSEL`.
- Tests: `tests/test_ghost_paths_vertex.py` (12), including an armature-deformed vertex that
  matches the evaluated mesh at frame 13.
- Review `b1d2370a` (3 advisory, all fixed in `23449ef1`): (1) topology can change per frame (an
  animated modifier), and `_sample` then returned the object origin; it now returns None, the
  frame becomes a gap (`_gaps`), and gaps are not re-requested until the path is dirtied, forgotten
  or leaves the window. (2) A vertex added in Edit Mode has index -1 until renumbered;
  `selected_keys` calls `bm.verts.index_update()`. (3) The no-markers test now reads the marker
  store. Both behaviour tests fail on `5ba22db`.
- Review `23449ef1` (2 findings, all three reviewers, fixed in `891c4152`): `path_segments` dropped
  missing frames and then joined what was left, so a gap (or a frame not yet sampled) was bridged
  by a straight line; it now joins only neighbouring frames that both have a point. `_cache_keys`
  read only `_cache`, so a path made only of gaps could never be dirtied; gap keys now count.
  Tests: the gap test puts the gap in the middle (frame 12) and checks the drawn segments; an
  all-gap path is dirtied by a mesh update and re-sampled. Both fail on `b608c94`. Vertex tests: 13.

### Task D3: release 3.7.0 (owner-gated). Checklist: a vertex path follows a
deforming (armature-modified) mesh vertex; a Subdivision modifier greys it.

---

## Round E — fast sampling (SKIPPED 2026-10-05)

> The owner answered the E0 gate "No": rigs do not trip the slow warning. Round E is
> not scheduled and has no release. The tasks stay below so it can be reopened if a
> rig ever shows the warning.

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

**Reopened and done 2026-10-06 (E1, branch `work/ghost-tool-paths-round-e` from `f8b5010`).** The owner
asked for Round E without the E0 gate. Decisions and findings:
- `ghost_tool/path_fast_sampler.py`: `fast_eligible` and `sample_fast` (object origin; bone head/tail up the
  chain; every rotation mode; location, rotation, scale and keyed delta location). Eligibility is strict;
  everything not modelled steps: constraints, drivers, NLA, Add/Multiply action blending, an animated,
  constrained or bone parent, delta rotation/scale (neutral and not keyed), bones that do not inherit
  rotation and full scale or use relative parent / non-local location, vertex paths, and Time Remapping
  (`frame_map_old != frame_map_new`: curves run at remapped time). Blender 5 creates actions in Combine;
  with no NLA underneath Combine equals Replace, so it is accepted. A connected bone ignores its location.
- Review `52c23eca` (HIGH advisory): a keyed delta location was read at its current value for every
  frame; it is now evaluated from its curves, and keyed delta rotation/scale is ineligible.
- `refresh_paths` samples eligible targets in one batch per path without `frame_set`, records them in
  `_fast_keys`, and re-steps a key that is no longer eligible (a constraint added without a depsgraph
  event). Handles and ineligible targets still step. `FAST_SAMPLING` is the switch.
- Measured (`test_fast_refresh_timing`, 100 samples): a light scene steps as fast as the fast sampler
  (2.6 vs 3.4 ms; 4.0 vs 4.8 ms for 500 cube samples), which is why the E0 rigs never tripped the slow
  warning. A heavy mesh whose geometry changes every frame (Subdivision 5 + Wave) costs stepping 68.9 ms,
  the fast sampler 4.0 ms. Moving a heavy object alone does not slow stepping: Blender keeps its
  evaluated geometry.
- Turning it on exposed that three path tests read the scene after a refresh and relied on frame stepping
  re-evaluating it at the playhead (two anchor tests, one Time Remapping test). The fast result was right
  (checked against the frame-10 pose); the tests read a stale pose. Part 3 (`9755d5eb`) switched
  `FAST_SAMPLING` on and those two anchor tests now `frame_set` the playhead themselves (the Time
  Remapping one passes because remapped scenes step).
- Switching it on unconditionally slowed the light fixture rig's 500-sample gate from ~5 to ~20 ms.
  Part 4 adds `FAST_AUTO`: a refresh measures the cost of each stepped frame (`_step_ms_per_frame`,
  reset when the cache's scene changes) and uses the fast sampler only once stepping costs
  `FAST_STEP_MS_PER_FRAME` (0.5 ms) or more per frame. Light rigs keep stepping (gate back to ~4 ms);
  a heavy scene steps once, measures, and then samples new frames with no `frame_set` (85 vs 3.5 ms).
  `FAST_AUTO = False` forces fast whenever eligible (the tests use it to compare samplers).
- Tests: `tests/test_ghost_paths_fast.py` (10), all compared against Blender's frame stepping within 1e-4;
  the auto test checks that a light scene keeps stepping and a heavy one switches after one measurement.
- Not checked headless (owner's 3.8.0 checklist): a real heavy production rig scrubbing without the
  slow warning; a Copy Location constraint added to a pinned bone makes its path step again.

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

**Done 2026-10-06 (F1–F2, branch `work/ghost-tool-paths-round-f` from `9f859e2`).** Decisions and findings:
- Part 1 (`paths_show_handles` + Handles toggle): its first review (`6817ec37`) was refused before
  dispatch, ~415 KB per reviewer request over the 393216 S3 limit (a request carries whole files plus
  diffs, ~2.6x the declared bytes). The owner raised S3/S4 to 512 KiB (hermes `bb8b4ea`); the identical
  re-route `8722d428` passed and `resolve_review_block` cleared the hold. Since then runs declare
  under ~140 KB, and `ghost_data.py` (108 KB) goes alone.
- F1: `handle_transform(target)` gives the location data path and the local → world map
  (object: parent world @ parent inverse, offset = delta location; bone head: armature world @
  `rest_channel_matrix(bone, posed parent)`); `key_handles` and the drag both use it. An axis without a
  key at the frame contributes its evaluated value. Handles are sampled during refresh at key frames in
  the window (scene at that frame), stored in `_handles` (None = no location key there), cleared with
  the path. No handles for tails, vertex paths and connected bones (they ignore location). Tests check
  handle points against Blender's own evaluation with the key moved onto its handle (object, object
  under a rotated parent with parent inverse and delta, posed bone).
- F1 review `47b90d36`: a one-frame path drew nothing (the loop skipped paths without segments before
  dots and handles); `draw_parts` now builds segments, dots and handles separately.
- F2: `path_handle_drag.py`. Shift+G or a click within 8 px of a handle end starts the drag; elsewhere
  the operator returns PASS_THROUGH so the marker drag (Shift+G) and selection keep working. Its keymap
  items register before `preferences` adds the marker drag's, which is how "picking prefers the handle
  end" is met. `fcurve_utils.set_handle_values` changes values only (times stay); Aligned keeps the pair
  collinear through the key, Free after Aligned unlinks both. The drag state is a `HandleDrag` class
  (tests drive it); the modal only feeds mouse, Alt, confirm and cancel.
- F2 reviews: `bf07774d` (Free after Aligned left one handle Aligned; confirm re-sampled only the
  dragged path, now every path that follows the object; Alt keeps the plan's toggle and the status bar
  shows Aligned on/off), `27d92547` (Alt before the first mouse move only changed the status; it now
  re-applies at the end's place).
- Not checkable headless (owner's 4.0.0 checklist): the undo step after confirming a drag (the undo
  stack needs a window), the drawn handles, the 8 px pick in a real viewport, Alt during a drag.
- Tests: `tests/test_ghost_paths_handles.py` (16).

### Task F3: release 4.0.0 (owner-gated). Checklist: drag a handle, the path
between keys bends and the Graph Editor shows the handle moved in value only;
Alt keeps the pair aligned; Esc restores.

---

## Round G — Draw to Keys (→ 4.1.0)

### Task G1: probe the annotation API
Owner decision 2026-10-05: read annotation strokes exactly as the Draw to Keys
extension does (Annotate tool; the longest stroke is the path, crossing dashes are
the keys). There is no Grease Pencil object fallback.
In Bforartists 5.1.2, draw an annotation with Placement = Surface on a plane,
then in the Python console: `type(bpy.context.scene.grease_pencil)` and
`bpy.context.scene.grease_pencil.layers.active.frames[0].strokes[0].points[0].co`.
Record which type (legacy `GreasePencil` annotation or GPv3) and the point
coordinate space, and check it against how the Draw to Keys extension reads its
strokes. The rest of the round reads strokes through one helper
`annotation_strokes(scene) -> list[list[Vector]]`. If annotations are not reachable
from Python at all, stop and report to the owner.

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

**Done 2026-10-06 (G1–G2, branch `work/ghost-tool-paths-round-g` from `cfd1512`).** Findings:
- G1 probe outcome (Bforartists 5.1.2, Blender 5.2 alpha base). The probe line above is out of date:
  the scene has no `grease_pencil`. Annotations are `bpy.types.Annotation` in `bpy.data.annotations`;
  the scene's is `scene.annotation`. Active layer: `layers[layers.active_index]` (`layers.active_note`
  is only its name, a string). `layer.frames[i].strokes[j].points[k].co`; `layer.active_frame` is None
  headless, so the reader takes the last frame at or before the playhead. `stroke.display_mode` is
  `3DSPACE` / `2DSPACE` ("locked to the camera view") / `2DIMAGE`: Surface and 3D Cursor strokes are
  world-space `3DSPACE`; a View-placed stroke in the 3D viewport is screen-locked, has no depth and is
  refused. Strokes are writable from Python (`frames.new`, `strokes.new`, `points.add`), so tests build
  them directly. Placement setting: `tool_settings.annotation_stroke_placement_view3d` (CURSOR, VIEW,
  SURFACE). The Draw to Keys extension's source was not available offline; the closest public
  description ("Draw to Animate": draw a path with the Annotate tool, crossings become keys) matches
  design §8 decision 15, which this round follows.
- G2: the math is `ghost_tool/draw_to_keys_math.py` (no bpy, so `tests/test_ghost_draw_to_keys.py` runs
  its math cases under plain Python too). Closest approach is segment–segment (Ericson); a dash counts
  once, at its first segment within `tolerance × path length`; ties for the longest stroke keep the
  first. `ghost_tool/draw_to_keys.py` holds the bpy reader `annotation_strokes(scene)`.
- Not checkable headless: that a View-placed stroke really is stored `2DSPACE` (drawing needs a viewport).

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

**Done 2026-10-06 (G3 and the G1–G2 review fixes).** Decisions and findings:
- Crossing rule, after three reviews (`85372dd9`, `976236d6`, `291dde18`): a dash's crossing is the path
  leg whose tolerance zone (within `tolerance × path length`) the dash enters first, walking from the
  dash's first point; it is reported at that leg's closest approach. The entry is exact: the distance
  from a point moving along a dash segment to a fixed leg is convex, so a bisection between the dash start
  and the leg's closest approach finds it. The earlier rules (closest distance; closest-approach position)
  are re-implemented in a test that shows each picks a different leg on its own geometry. One rule for
  every leg: a review example that compared one leg's zone entry with another's exact crossing mixed two
  rules. Before the first annotation frame nothing is read.
- G3: `GHOST_OT_paths_draw_to_keys` keys location on the chosen axes at Start, Start + Step, ... with the
  chosen interpolation, for the active object or pose bone. World points become channel values through
  `motion_paths.location_world_map` (split out of `handle_transform`, so handles, the handle drag and Draw
  to Keys share one map), read at each key's frame so an animated parent counts. Optional `stroke_value`
  (distance along the path) and Clear Strokes. Refuses fewer than two crossings, any View-placed stroke
  and connected bones. Dialog, one undo step, the playhead is restored, pinned paths re-sample.
  The Bezier/Linear/Constant choice sets each new key's interpolation; Preferences leaves Blender's.
- Reviews `07547b99` and `ec38136d`: Clear Strokes removes only the strokes it read (3D, two or more
  points) and never a hidden layer's (one `_active_layer_frame` lookup for reading and clearing); the
  operator tests skip outside Bforartists.
- UI: "Draw to Keys…" in Edit Motion and at the bottom of the paths popover; the Motion Paths help text
  covers folders, Apply to Checked, Handles and Draw to Keys.
- Tests: `tests/test_ghost_draw_to_keys.py` (22; the 9 math cases also run under plain Python). Keyed
  positions are checked against Blender's own evaluation (object; bone under a rotated, animated parent).
- Not checkable headless (owner's 4.1.0 checklist): drawing with the Annotate tool in each placement, the
  dialog, and the visible difference between Bezier and Constant.

### Task G4: release 4.1.0 (owner-gated). Checklist: draw a path and three dashes
on a plane, run Draw to Keys on a bone, scrub: the bone visits each crossing at
Start, Start+Step, Start+2·Step; Bezier vs Constant visibly differ; `stroke_value`
appears in the object's custom properties when enabled.

---

## Round X — investigate Motion Path Pro's "reference line" and "timeline visualisation"

> **Closed 2026-10-05.** The four features are listed under "Future update" on Motion
> Path Pro's Superhive page and in its extension version history: nothing released to
> copy. Its released features already map to Ghost Tool (see the owner decisions above
> Round B). The original task stays below for the record.

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
E0 gate answered "No" → Round E skipped (no 3.8.0)
F1 → F2 → F3 (4.0.0)
G1 probe → G2 → G3 → G4 (4.1.0)
X1 closed
```
Rounds D, F and G are independent of each other and can be reordered by the owner.
Each round's branch is rebased on `main` after the previous release merges.
