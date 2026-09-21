# B4Artists ML UI architecture plan v1

Status: plan. Companion to `B4ARTISTS_ML_UI_UX_HANDOFF.md`. Baseline `0.37.51`, target `0.38.x`.
Date: 2026-09-21.

## 1. What Cascadeur actually does that we don't

The animator's complaint ("nothing happens, nothing appears in the animation windows") maps to five Cascadeur habits. Each becomes a design rule here; each rule has a code owner.

| Cascadeur habit | Rule for B4ML | Owner |
|---|---|---|
| You touch the character, not a panel. Controllers are the interface. | Targets are framed, colour-coded, labelled in the viewport; Solve/Keep/Cancel live next to them. | `viewport_overlay.py`, `body_preview.py` |
| One mode per task. Starting AutoPosing changes what the screen offers. | A posing session collapses the panel to the task; other stages dim with a reason. | `stage.py`, `panels/pose.py` |
| The timeline is the hub: keys, intervals, tracks are visible and draggable. | Anchors are timeline markers, candidate range is the preview range, intervals are coloured bands. | `markers.py`, `editor_dopesheet.py` |
| Result is live and non-destructive; apply is one obvious click. | Source / Preview / Kept / Restored are four visibly different states with one primary button each. | `feedback.py`, `panels/review.py` |
| The tool tells you why not. | Every locked control has a one-line reason in the panel *and* in its tooltip. | `stage.py` |

Nothing in this plan changes solver, contact, cleanup, flight, or secondary math. `ui.py` operators keep their `bl_idname`s and semantics; only presentation and state feedback move.

## 2. Architecture

### 2.1 New package layout

```
b4artists_ml/
  ui.py                    # shrinks: property groups + operators only (no Panel)
  ui_workflow/
    __init__.py            # register()/unregister() for everything below
    stage.py               # pure stage engine (no bpy at import; takes a snapshot)
    feedback.py            # persistent success/error model + operator wrapper
    copy.py                # animator-facing strings in one place
    panels/
      header.py            # stage strip + feedback card (drawn at top of every panel)
      setup.py             # B4ML_PT_setup
      pose.py              # B4ML_PT_pose
      motion.py            # B4ML_PT_motion
      review.py            # B4ML_PT_review
      advanced.py          # B4ML_PT_advanced + subpanels wrapping today's boxes
    viewport_overlay.py    # target labels/colours, HUD, legend, mode hint
    markers.py             # anchor/contact/flight <-> timeline marker sync
    editor_dopesheet.py    # Dope Sheet / Timeline panel, header buttons, band overlay
```

`ui.py` stays the owner of `B4ML_PG_settings` and all `B4ML_OT_*` so existing tests and `bl_idname`s do not move. `B4ML_PT_main` is deleted in Phase 1 and replaced by the panel set. `ui.register()` calls `ui_workflow.register()` last and unregisters it first.

### 2.2 Stage engine (`stage.py`)

One pure function replaces the ~30 scattered `row.enabled = a and not b and not c` expressions:

```python
@dataclass(frozen=True)
class Snapshot:            # built from obj.b4ml + context by stage.snapshot(context)
    has_rig: bool; family: str; mapped: bool; mapping_error: str
    posing: str            # '', 'BODY', 'ASSISTED', 'QUADRUPED'
    anchors: int; candidate: bool; kept: bool
    running: str           # '', 'BODY', 'TEMPORAL', 'CONTACT', ...
    mode: str              # context.mode
    playing: bool

@dataclass(frozen=True)
class StageState:
    current: str                       # SETUP | POSE | MOTION | POLISH | REVIEW
    completed: frozenset[str]
    next_action: tuple[str, str, dict] # (label, operator idname, props)
    locks: dict[str, str]              # action key -> one-line reason
    required_mode: str | None          # 'OBJECT' while posing, else None

def evaluate(snapshot: Snapshot) -> StageState: ...
```

Action keys are stable strings (`'pose.begin'`, `'pose.solve'`, `'pose.keep'`, `'motion.preview'`, `'review.keep'`, `'review.discard'`, `'review.restore'`, `'polish.contacts'`, …). Panels ask `stage.locked(key)` and draw both the reason label and a tooltip. Tooltips use the dynamic `description(cls, context, properties)` classmethod on the operators so hovering a greyed button explains it.

Because `evaluate()` takes a plain dataclass it runs in the host-independent suite with no `bpy`.

### 2.3 Feedback model (`feedback.py`)

Replace the single trailing `state.status` label with four properties on `B4ML_PG_settings`:

```
feedback_level: Enum INFO | SUCCESS | WARNING | ERROR   (SKIP_SAVE)
feedback_text:  String
feedback_fix:   String   # operator idname that resolves it, or ''
feedback_fix_label: String
```

`feedback.success(obj, text)`, `feedback.error(obj, text, fix='b4ml.action', fix_label='Refresh Mapping', **props)`. The card is drawn at the **top** of every B4ML panel (`panels/header.py`), uses `layout.alert = True` for ERROR, and shows the fix button. Every `B4ML_OT_*.execute` is wrapped by `feedback.guarded(fn)`: `ValueError` → ERROR card + `self.report`, success path keeps whatever the operator set. Existing `state.status = ...` assignments are mechanically routed through `feedback.info()` in Phase 1 and re-worded in Phase 4.

### 2.4 Copy (`copy.py`)

All animator-facing strings live in one module so the "no `candidate_action` / `payload` / `backend` / internal units" rule is greppable and testable. Vocabulary:

| Internal | Animator-facing |
|---|---|
| source action | **Original animation** |
| candidate action | **Preview** |
| kept action | **Kept result** |
| anchor | **Key pose** |
| body_payload session | **Posing session** |
| backend (ROOT/NATIVE) | **Method** |
| "Machine Learning" on procedural features | **Procedural** (learned features keep the label only where qualified) |

## 3. The five panels

All are `VIEW_3D / UI / 'B4Artists ML'`. Each draws `header.draw(layout, stage_state, state)` first: a one-row stage strip (`Setup ▸ Pose ▸ Motion ▸ Polish ▸ Review`, current stage `depress=True`, completed stages `CHECKMARK`, locked stages `LOCKED` + reason on hover), then the feedback card, then a single **Next:** line with the `next_action` button. The user never scrolls to learn what happened.

### Setup (`B4ML_PT_setup`)
- Character card: name, family badge (Humanoid / Quadruped / Unsupported), mapping result in one line.
- Primary button: **Check Rig** (existing `b4ml.action INSPECT`). On failure the feedback card offers **Open Mapping Repair** which expands the existing correction editor (moved under Advanced but reachable from here).
- Nothing else. Diagnostics, role table, manual corrections → Advanced ▸ Rig.

### Pose (`B4ML_PT_pose`)
- Idle: one primary button **Start Posing** (whole-body). Assisted Pose (geometric) and Quadruped move under Advanced until the humanoid journey passes.
- Active session (`body_payload`): the panel *reduces* to
  - Mode guard: if `context.mode != 'OBJECT'` show an alert row **Switch to Object Mode** (`object.mode_set`).
  - Compact target list: name + Pin + Rot; pole and reset controls collapse behind a per-target `▸`.
  - **Solve** / **Live** toggle / **Keep Pose** / **Cancel** — the same four controls the viewport HUD shows.
  - Balance, limits, mirror, pose asset → "More" foldout.
- Stage strip dims Motion/Polish/Review with reason "Finish or cancel the posing session".

### Motion (`B4ML_PT_motion`)
- Key-pose list (existing anchor rows, but each row shows frame + role + a **Go** button that sets `scene.frame_current`). Retime/ripple/spacing/timing icons stay.
- Method (`interpolation_method`) + timing controls as today.
- Primary: **Generate Preview (frames A–B)** — the label carries the range so the animator can say what will happen before clicking.
- Locked when `< 2` key poses: "Capture a second key pose to generate motion".

### Review (`B4ML_PT_review`)
- State badge, one of: `Original animation` / `Previewing: <name>` / `Kept: <name>` / `Original restored`.
- Range line: frames A–B, `use_preview_range` on.
- While previewing: **A/B** toggle (temporarily swaps `animation_data.action` between original and preview, no data change), **Keep**, **Discard**. Buttons say what they are: "Keep (saves preview as a new action; original is kept too)".
- After keep: **Restore Original** (existing `RESTORE_SOURCE`) with copy "the kept result stays available".

### Advanced (`B4ML_PT_advanced`, `DEFAULT_CLOSED`)
Subpanels via `bl_parent_id`: Rig Mapping, Assisted Pose, Quadruped, Center of Mass, Contacts, Airborne, Cleanup, Secondary Motion, Saved Results. These are the existing `box` blocks moved verbatim, each with a header line stating its prerequisite (e.g. "Needs a preview or kept result").

## 4. Viewport (`viewport_overlay.py`)

Extends the `contact_visualization.py` pattern (POST_VIEW gpu lines) with a POST_PIXEL layer for text, and reuses Ghost Tool's `blf` label idiom (`ghost_tool/viewport_draw.py:1917`).

1. **Target identity** — `body_preview.begin` sets distinct empties: pelvis `CIRCLE`, chest/neck/head `CONE`, hands `SPHERE`, feet `CUBE`, poles stay `PLAIN_AXES`. Overlay draws a role colour ring + label (`Hand L`, `Foot R`, …) at each target; pinned = solid, unpinned = hollow; a thin line from each target to its solved joint.
2. **Focus** — after `begin`, select all targets, make the pelvis active, `object.mode_set(OBJECT)`, `view3d.view_selected` under `context.temp_override(area, region)`. Exposed as **Frame Controls** so it is repeatable.
3. **HUD** (top-left of the viewport, only while a B4ML task or preview is active): stage, task, legend, mode hint ("Move targets in Object Mode" / "Switch to Object Mode" in alert colour), source-vs-preview badge, frame range bar with key-pose ticks.
4. **Task controls** — a `VIEW3D_HT_header`/tool-settings append or a small floating panel (`bl_region_type='HEADER'`, poll on session) with Solve / Live / Keep / Cancel so the animator does not leave the viewport.
5. COM, support, contacts, flight bounds draw only when their Advanced subpanel is open or their solve is running.

Deferred option (Phase 5): a `GizmoGroup` with `move_3d`/`arrow_3d` gizmos bound to the targets so posing works in Pose Mode too, removing the Object-Mode requirement. Keep empties as the persisted truth either way.

## 5. Timeline / Dope Sheet (`markers.py`, `editor_dopesheet.py`)

Use native, already-visible mechanisms first; custom drawing second.

1. **Key poses → timeline markers.** `markers.sync(scene, obj)` reconciles `scene.timeline_markers` with `state.anchors`: name `B4ML ◆ <Rig>: Pose 1`, frame = anchor. Markers appear in Timeline, Dope Sheet, Graph, NLA with zero extra drawing. Called after capture/remove/retime/ripple/reuse/undo (`undo_post` handler) and on load (`load_post`).
2. **Marker → anchor.** A `bpy.app.timers` poll (0.25 s, registered only while a rig has anchors) detects a moved or selected `B4ML` marker: moved → `workflow.retime_anchor`; selected → `state.active_anchor` so the Motion panel highlights that row. Contacts (`contacts`) and flights get the same treatment with `●` / `↗` glyphs.
3. **Active range** — while a preview exists, set `scene.use_preview_range` and `frame_preview_start/end` to the key-pose span; restore the previous values on keep/discard. Action names already carry ` - B4ML Preview`, which the Action Editor header shows.
4. **Dope Sheet panel** — `B4ML_PT_dopesheet` (`DOPESHEET_EDITOR / UI / 'B4ML'`, poll: rig with anchors or preview). Contents: key-pose list with Go/Retime, preview state, Capture Here / Generate / Keep / Discard. Header append (`DOPESHEET_HT_header`) adds the same four buttons as icons.
5. **Band overlay** — `SpaceDopeSheetEditor.draw_handler_add(POST_PIXEL)` draws translucent bands over the region using `region.view2d.view_to_region(frame, 0)`: candidate range, accepted contacts (green), proposed (orange), flight intervals (blue), protected priority frames (hatched). Same colours as `contact_visualization._COLORS`.

Graph Editor / NLA get nothing until the humanoid journey passes usability.

## 6. Phases

| # | Phase | Deliverable | Exit test | Est. |
|---|---|---|---|---|
| 0 | **API spike** (Bforartists 5.1) | `docs/b4artists_ml/UI-SPIKE-v1.md` recording: subpanel `bl_parent_id` in the N-panel; Dope Sheet `UI` region availability in Timeline mode; `DOPESHEET_HT_header` / Bforartists header class names; `SpaceDopeSheetEditor` draw handler + `view2d` mapping; marker rendering; `temp_override` for `view_selected`; timer cost. | Each item has a 20-line script that ran in `X:/5.1.0/bforartists.exe --background` or a screenshot. | 1–2 d |
| 1 | **Stage engine + feedback + panel split** | `stage.py`, `feedback.py`, `copy.py`, five panels, Advanced subpanels, `B4ML_PT_main` removed. Operator semantics untouched. | Host-independent: `evaluate()` matrix for the 7 handoff situations; every locked key has a non-empty reason. Native: registration/unregistration in a fresh profile; fake-layout draw of each panel with no exceptions; feedback card present after `INSPECT` on a mesh with no armature. Existing 83 + 47 suites green. | 3–4 d |
| 2 | **Viewport** | Target shapes/colours/labels, focus, HUD, mode guard, task controls. | Native: after `body_preview.begin` all targets selected, active = pelvis, mode = OBJECT; `viewport_overlay.build_payload` returns 8 labelled targets with finite positions; no draw registered in background. Existing `test_b4artists_ml_body_controls` green (check for display-type assertions before changing shapes). | 3 d |
| 3 | **Timeline / Dope Sheet** | `markers.py`, preview range, Dope Sheet panel + header, band overlay. | Native: marker set equals anchor set after add/remove/retime/ripple/undo/save/reload; moving a marker retimes the anchor; preview range set/restored around keep and discard; source action bytes unchanged while previewing (reuse `_action_signature`). | 3–4 d |
| 4 | **Copy audit, docs, package, animator session** | `copy.py` complete; PUBLIC-BETA doc + README + `bl_info` describe the delivered flow; zip via `build_public_beta_package_v1.py`; clean-profile smoke. Run the handoff's usability protocol with the original reviewer. | Grep test: no `candidate`, `payload`, `backend`, `internal units` in `copy.py` or panel strings. Session record: time-to-first-action ≤ 30 s, all eight handoff observations logged. | 2 d + session |
| 5 | **Migrate Polish** (after 4 passes) | Contacts / cleanup / flight / secondary become Polish stage cards with prerequisites; quadruped enters Pose stage; gizmo evaluation. | Same lock-reason and feedback tests extended to Polish keys. | later |

Phases 2 and 3 are independent after Phase 1 and can run in parallel.

## 7. Tests to add

```
tests/test_b4artists_ml_ui_stage_v1.py          # pure: evaluate() matrix, lock reasons, next_action
tests/test_b4artists_ml_ui_copy_v1.py           # pure: forbidden-term grep over copy.py + panel modules
tests/test_b4artists_ml_native_ui_register_v1.py# register/unregister per editor, fake-layout draws
tests/test_b4artists_ml_native_ui_journey_v1.py # the 10-step slice via operators; feedback after each
tests/test_b4artists_ml_native_markers_v1.py    # marker sync incl. undo/save/reload, source integrity
tests/test_b4artists_ml_native_overlay_v1.py    # overlay payload + focus/mode after begin
```

Fake-layout pattern: a recorder class with `row/column/box/prop/operator/label/separator` (see `tests/smoke_bforartists.py` `HelpLayout`) so panel `draw()` runs in `--background`. Screenshots (`screen.screenshot`) are an optional non-background job, not a gate.

## 8. Risks and decisions

- **Object-Mode requirement** is the largest remaining friction; Phase 2 mitigates with auto-switch + guard, Phase 5 evaluates gizmos. Do not attempt gizmos before the journey passes with empties.
- **Bforartists header classes** may differ from Blender's; the spike decides between header append, a `HEADER`-region panel, or Dope Sheet sidebar only.
- **Markers are scene-scoped, anchors are object-scoped.** Names carry the rig name; `sync` only touches markers with the `B4ML ` prefix; two rigs with anchors are covered by a test.
- **Timer polling** must be cheap: compare a frozen tuple of `(name, frame, select)`; unregister when no rig has anchors.
- **Display-type changes** in `body_preview.begin` are a backend edit; allowed by the handoff only if a UI integration test needs it — the label overlay works without it, so shapes are a Phase 2 stretch, not a dependency.
- **Version and claims**: bump to `0.38.0`, keep "public beta", and keep learned-motion language unqualified.

## 9. Definition of done for this plan

Same as the handoff's Definition of done, plus: `stage.evaluate()` is the *only* place lock logic lives (a grep for `.enabled =` in `ui_workflow/panels/` returns nothing but `stage.locked(...)` lookups).
