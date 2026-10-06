# Ghost Tool — Motion Paths (design)

Date: 2026-10-05. Target release: Ghost Tool 3.5.0 (Bforartists only).
Status: §1–7 shipped as 3.5.0 (commit `35e7ebe`); the two cache bugs in §5
(Ghost Tools off, undo) were fixed on `work/ghost-tool-paths-gaps` (`228a946`).
§8 is the round-2 scope the owner asked for and approved on 2026-10-05; it shipped as
3.6.0 (Rounds A–C) and 4.0.0 (Rounds D, F, G, E; see §8.6). Its plan is
`2026-10-05-motion-paths-round2-plan.md`.

## 1. What this is

Per-bone and per-object motion paths drawn by Ghost Tool itself, live-updating,
toggleable one at a time or all at once, reachable from the Timeline / Dope
Sheet header and the Graph Editor header. Never from the N-panel.

Built from scratch on Ghost Tool's existing trail system (option "A+" in the
brainstorm): the trail samples the bone directly, so a path can be on while
ghost markers are off. Markers are an optional overlay on the same line and
remain the way motion is edited. Blender's native Motion Paths are not used,
not read, not written.

Rejected alternatives and why:

- Upgrade the arc trails only (A): no path without markers; density tied to
  marker count.
- A separate path layer (B): two trail systems drawing the same positions;
  editing stays on markers, so the path itself is a viewer.
- Wrap native Motion Paths (C): not live, not editable, no per-bone hide
  without recalculating.

## 2. Decisions

| # | Decision | Choice |
|---|---|---|
| 1 | Path engine | A+ — Ghost Tool samples and draws; markers optional on top |
| 2 | UI host | Header strip in Dope Sheet/Timeline **and** Graph Editor; full section in the viewport-header "Ghost Tool" popover; nothing in the N-panel |
| 3 | How a bone gets a path | C — explicit pinned list **plus** a "Follow selection" toggle |
| 4 | Add button | Icon + short label in the header (`〰 Paths · 🦴 Add · ⌖ Follow · ▾`); full text `+ Add Path for Selected` inside the popover |

## 3. Architecture and data

New module `ghost_tool/motion_paths.py` owns sampling, cache, operators and
draw. It reuses: the per-frame pose sampler and sampling guard
(`utils.scene_sampling`, playhead always restored), the arc batching and
styles in `viewport_draw.py`, and the header-strip draw function in
`ui_panel.py`.

Scene data (survives save/reload), all under `scene.ghost_tool`:

```
motion_paths              CollectionProperty[PathEntry]
  PathEntry: object_name, bone_name ("" = object origin), visible,
             color, use_custom_color, thickness, anchor ('HEAD'|'TAIL')
paths_enabled             master toggle (the 〰 Paths button); default False
paths_follow_selection    the Follow toggle; default False
paths_show_markers        overlay ghost markers on listed bones; default False
paths_show_key_dots       white dots at keyframes; default True
paths_show_frame_numbers  default False
paths_range_mode          AROUND_CURSOR | SCENE | CUSTOM (default AROUND_CURSOR)
paths_before / paths_after / paths_step   defaults 12 / 12 / 1
paths_style               SOLID | SPEED | FADE (reuses arc styles)
```

Sampling: cache keyed `(object_name, bone_name, frame) -> world position`.
Filled by evaluating the pose at each frame in the range. Incremental: only
frames that entered the window are sampled; frames that left are dropped.
Follow-selection entries are computed from `selected_pose_bones` /
`selected_objects` at refresh time, drawn in neutral grey, never written to the
list. A bone both followed and pinned draws once, with the pinned colour.

Drawing: one GPU batch per visible path; colour from the entry (auto palette:
fixed 8-colour cycle assigned on add); key dots; optional frame numbers; the
active bone's path 1 px thicker. With `paths_show_markers` on, ghost markers
are generated for exactly the listed bones and drawn on top; dragging them is
the existing behaviour.

Operators: `paths_add_selected`, `paths_remove`, `paths_clear`,
`paths_toggle_visible` (one / all on / all off), `paths_set_color`.

## 4. UI

Header strip, one draw function appended to `DOPESHEET_HT_header` and
`GRAPH_HT_header` (the Dope Sheet one extends the strip that exists today):

```
… | [〰 Paths] [🦴 Add] [⌖ Follow] [▾] | [Onion] …
```

- `〰 Paths` — `paths_enabled`. Off hides every path, keeps the list.
- `🦴 Add` — `paths_add_selected`. Pose mode: selected bones. Object mode:
  selected objects; an armature adds its root bone. Greyed when nothing is
  selected; tooltip "Select bones or objects first".
- `⌖ Follow` — `paths_follow_selection`, highlighted when on.
- `▾` — opens the path popover.

Path popover (`GHOST_PT_paths_popover`, ~280 px):

- Top: `+ Add Path for Selected` · "Motion paths · N" · All on / All off / Clear.
- One `UIList` row per entry: eye · colour swatch (click = colour + thickness
  picker) · `Object › bone` · ✕. Active bone's row highlighted; missing
  entries greyed with "(missing)".
- Bottom: Range (mode, Before/After/Every), Style (Solid/Speed/Fade),
  Markers on paths, Frame numbers, Key dots.

The viewport-header "Ghost Tool ▾" popover gains a collapsible "Motion Paths"
section with the same content. One draw function, three hosts.

Not included on purpose: per-path range, path handles beyond ghost markers,
a thickness slider in the list row.

## 5. Behaviour and edge cases

- Live refresh on the triggers the onion skins use: frame change, key edits
  (depsgraph), playback stop. Throttled by `live_throttle_ms`. During playback
  the last state is kept; it refreshes on stop.
- Edits mark only the affected bone dirty; only that bone re-samples.
- Bone or object deleted or renamed: entry stays, greyed "(missing)", draws
  nothing; ✕ removes it; the name coming back restores it.
- Entries are per scene. On file load the cache is empty and rebuilds on
  first draw.
- Ghost Tools off clears the cache, keeps the list.
- `paths_show_markers` is independent of the "Show Markers" button, which
  keeps working as today.
- Undo: add / remove / colour are undoable operators; the cache is not
  undo-tracked and rebuilds.
- Performance budget: 20 bones × 25 frames (500 samples) full refresh under
  50 ms on a mid rig; a scrub re-samples only new frames. A refresh over
  200 ms shows a small ⚠ on the strip with "paths are slow — reduce range".

## 6. Testing

Headless (Bforartists, `tests/test_ghost_paths.py`, same harness as the other
ghost suites):

- add selected → listed; add again → no duplicate; nothing selected → CANCELLED
- sampled positions equal `pose_bone.head` per frame (1e-5) on a 2-bone rig;
  object entry equals `matrix_world.translation`
- range change samples only the new frames (count sampler calls)
- key edit dirties only that bone
- hide one / all off / all on; `paths_enabled` off → zero batches, list intact
- follow: unpinned selected bone draws grey; pinning keeps colour; deselect
  removes only follow entries
- deleted bone → "(missing)", no exception on draw; rename back → draws
- save/reload keeps the list, cache rebuilds
- playhead restored after every sampling pass
- perf gate: 500-sample refresh under 50 ms, value recorded in the test log

Needs eyes (manual checklist in the PR): strip renders in both editors,
popover scrolls past 8 rows, colours and thickness, scrubbing feels live,
playback-stop refresh.

## 7. Rollout

- Branch `work/ghost-tool-paths` from `main` at 3.4.1.
- Ships as Ghost Tool **3.5.0**. `bl_info` description unchanged.
- `paths_enabled` defaults off: existing files open exactly as before.
- Release recipe as for 3.4.1: version tuple, README rows,
  `releases/VERSIONS.md`, zip byte-identical to `ghost_tool/`, GitHub release
  `ghost-v3.5.0`, Axleonex identity, no co-author lines.

## 8. Round 2 — the features of the four extensions

Owner request 2026-10-05: Ghost Tool should have the motion-path features of
Draw to Keys, Real-Time Paths (Motion Path Pro), MotionPath (Motion Path
Creator) and QuickPath RKNZ, as listed on extensions.blender.org. Anim Assist's
Trajectory Overlay stays a diagnostic tool and is not extended; Ghost Tool owns
motion paths in the toolkit.

### 8.1 Decisions

| # | Decision | Choice |
|---|---|---|
| 5 | Finish §1–7 first | Head/Tail in the UI, active-bone row highlight, Custom range fields, full slow warning, the §6 tests not yet written. Ships as 3.5.1 with the two cache fixes. |
| 6 | Per-path range | **Reverses §4.** Each entry may override the global range, Before/After/Every and mode. Default: follow the global settings, so nothing changes for existing files. |
| 7 | Organising many paths | Folders as rows in the same list (an entry with `is_folder`), a checkbox per row, and operators that act on checked rows. One list, no second collection. |
| 8 | Before/after colour | A fourth style, `SPLIT`: the entry's `color_before` up to the playhead, `color` after it. |
| 9 | Draw in front | Per entry (cube button on each row) plus popover buttons "All in front" / "All behind" (owner, 2026-10-05). Default **in front**, today's look: Blender 5.1 runs POST_VIEW draw callbacks with no depth test (plan Task B3 outcome); "behind" draws that path with depth test `LESS_EQUAL`. |
| 10 | Dot size | Per entry, default 6 px; in the colour dialog and in Apply to Checked. |
| 11 | Active glow | The entry selected in the list draws a wide, faint pass under its line. The 1 px thicker active-bone line from §3 stays. |
| 12 | Vertex paths | A third target kind. `PathKey` gains `vertex_index` (-1 for none). Added from Edit Mode with Add Selected; capped at 50 vertices per click with a report. |
| 13 | Fast sampling | Only when it provably matches frame stepping: object or bone whose chain has no constraints, drivers or animated parent object. Everything else keeps `frame_set`. Shipped only if a real rig trips the slow warning (plan Task E0 gate). **Skipped 2026-10-05:** the owner answered the gate "No"; can be reopened if a rig shows the warning. |
| 14 | Handles on paths | **Reverses §4 ("path handles beyond ghost markers").** With Handles on, each key dot shows its in/out Bezier handles as world points built from the location curves' handle values; dragging one writes the handle values, time stays. |
| 15 | Draw to Keys | A new operator, `ghost_tool.paths_draw_to_keys`, reading annotation strokes exactly as the Draw to Keys extension does (Annotate tool; no Grease Pencil object fallback, owner 2026-10-05): the longest stroke on the active annotation layer is the path, every other stroke is a timing dash; each crossing becomes a location key on the chosen axes at Start + n × Step, with the chosen interpolation; optional `stroke_value` custom property keyed with the distance along the path. |
| 16 | Reference line, timeline visualisation (Motion Path Pro) | **Closed 2026-10-05.** These, "handle setup" and "editable path with rotation" are listed under "Future update" on Motion Path Pro's Superhive page and extension version history: nothing released to copy. Its released features map to Ghost Tool: edit in the 3D view = Markers on Paths; rotation = Tail-path rotation markers; control handles = decision 14 (Round F); paths list = pinned list + Round C. |

Rejected: a second path system for vertices (one cache, one draw handler, one
list); a global dot size only (QuickPath users expect per path); fast sampling
without a fallback (a wrong path looks exactly like a right one).

### 8.2 Data additions (all on `scene.ghost_tool`, saved with the file)

```
PathEntry +
  is_folder, folder (parent folder name, "" = root), collapsed, checked
  vertex_index (-1 = none)
  color_before                 for style SPLIT; default = color × 0.55
  in_front                     per-path depth test
  dot_size                     1–12 px, default 6
  use_own_range, own_range_mode, own_before, own_after, own_step,
  own_start, own_end           range override, off by default
paths_style += 'SPLIT'
paths_show_handles           default False
paths_active_glow            default True
Draw to Keys operator properties (not saved): axes (X/Y/Z set), start_frame,
  use_current_frame, frame_step, interpolation (CONSTANT/LINEAR/BEZIER/SCENE),
  write_stroke_value, crossing_tolerance (fraction of path length, default 0.02)
```

### 8.3 UI additions

- List row: `[✓] eye · swatch · ⌖/🦴/• kind icon · Object › bone (or v123) · ▣ in front · ✕`;
  folder rows: `▸/▾ · [✓] · eye · name · ✕`. Rows inside a collapsed folder are hidden.
- Colour dialog gains Thickness, Dot size, Colour before (when style is SPLIT),
  Anchor (bones only), and the range override block.
- Popover toolbar gains: Add Folder · Apply to Checked · Checked ▾ (Show, Hide,
  Remove, Move to folder…, Reset range).
- Style row: Solid / Speed / Fade / Split. Toggles row gains Handles.
- Edit Motion section gains "Draw to Keys…" (opens the operator dialog). Also
  reachable from the path popover's bottom row.
- Still nothing in the N-panel.

### 8.4 Behaviour

- Per-path ranges: `desired_frames` takes the entry; the cache's wanted set is
  per target, so a path with a wider window keeps its extra frames.
- Folders: visibility is entry AND folder. Deleting a folder moves its paths to
  the root; it never deletes paths.
- Vertex paths sample the evaluated mesh. If the evaluated vertex count differs
  from the original (generative modifiers) the entry is "(missing)" until it
  matches again.
- Handles: handle world points use the handle *values* of location X/Y/Z at the
  key; the time component is untouched by a drag. A drag sets handle types to
  FREE; Alt keeps the opposite handle aligned (ALIGNED).
- Draw to Keys reads annotation strokes in 3D (Surface or 3D Cursor placement), the same
  strokes the Draw to Keys extension reads; there is no Grease Pencil object fallback.
  View-placed strokes are refused with a report. Keys go through the same
  world → channel solve the marker drag uses, so parented bones work.
- Fast sampling: eligibility is decided per target each refresh; a cache entry
  records which sampler produced it; the test suite asserts fast == stepped
  within 1e-4 on the fixture rig and that any constraint forces the stepped path.

### 8.5 Tests (added to `tests/test_ghost_paths.py` unless noted)

Per feature in the plan; every task names its failing test first. Cross-cutting:
existing 56 path tests, header 16, correctness 46, regressions 20, tooltip
coverage and smoke stay green; `paths_enabled` default off keeps old files
unchanged; the 500-sample perf gate stays under 50 ms with per-path ranges on.

### 8.6 Rollout

Release line-up set by the owner on 2026-10-05:

| Release | Rounds | Content |
|---|---|---|
| 3.5.1 | A | cache fixes + finish §1–7 |
| 3.6.0 | B, C | Split style, dot size, in front, glow, per-path range; folders, checkboxes, batch operators |
| 4.0.0 | D, F, G, E | vertex paths, handles on paths, Draw to Keys, automatic fast sampling |
| — | X | closed: nothing released to copy (decision 16) |

Owner decision 2026-10-06: the stacked Rounds D, F, G and E ship together as 4.0.0 (planned as 3.7.0,
4.0.0, 4.1.0 and, once E was reopened, 3.8.0).

Each release follows the 3.5.0 recipe (§7). `bl_info` description unchanged.
