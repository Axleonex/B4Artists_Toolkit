# Ghost Tool — Motion Paths (design)

Date: 2026-10-05. Target release: Ghost Tool 3.5.0 (Bforartists only).
Status: approved by the owner section by section; implementation plan pending.

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
