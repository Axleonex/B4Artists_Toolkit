# B4Artists ML UI experience contract v1

Status: authoritative contract for Phase 1–4 implementation.
Companion to `UI-ARCHITECTURE-PLAN-v1.md` and `B4ARTISTS_ML_UI_UX_HANDOFF.md`.
Date: 2026-09-21. Method: fable-design (treatment=UI/tool, depth=operated/multi-state).

---

## EXPERIENCE CONTRACT

```
EXPERIENCE DEPTH: operated / multi-state
USER + JOB: Production animator using Bforartists 5.1.2 with a Rigify humanoid;
  needs to capture key poses at two or more frames, generate interpolated motion
  between them, review the result side-by-side with the original, and commit or
  discard without risk of losing their source animation.
```

### Step 0 — Honor what exists

Blender/Bforartists owns type scale, widget sizing, spacing tokens, and the
native property widget library. This contract designs **structure, copy, state
presentation, gpu/blf overlays, and behavior** — not widget chrome. Rules:

- Reuse `contact_visualization._COLORS` (`contact_visualization.py:23`) as the
  house semantic palette: `ACCEPTED=(0.18,0.92,0.45)`, `PROPOSED=(1.0,0.58,0.12)`,
  `REJECTED=(0.95,0.18,0.18)`. These are already visible in the production overlay
  and are recognizable to any animator who has used the contacts workflow.
- Both Bforartists themes (default dark + light) are targets. Role colors in the
  DESIGN PLAN are validated against both surfaces.
- Ghost Tool label idiom (`ghost_tool/viewport_draw.py:1917`) is house style for
  blf labels: draw shadow one pixel offset, clip to region, use `blf.size` in
  multiples of `bpy.context.preferences.view.ui_scale`.
- Existing `B4ML_OT_*` idnames and `B4ML_PG_settings` property paths do not move.

### EVIDENCE

```
known:
  - Animator quote (handoff): "Clicking through the buttons feels like nothing
    is happening. The features are unclear, and nothing useful appears in the
    animation windows."
  - Single panel B4ML_PT_main at ui.py:2014: VIEW_3D / UI only; no Timeline,
    Dope Sheet, or Graph Editor registration.
  - state.status feedback written at body_preview.py:229 ("Move pelvis, chest,
    neck, head, hand or foot targets...") and workflow.py:1644 ("Candidate kept
    as a separate action" / "Original animation restored") — a trailing label
    that scrolls out of view in the current long panel layout.
  - body_preview.begin (body_preview.py:179) sets all main targets to
    empty_display_type='ARROWS' (body_preview.py:208); poles to
    empty_display_type='CIRCLE' (body_preview.py:223). No colour or label
    differentiation between roles.
  - workflow.preview (workflow.py:1406) raises ValueError if body_payload,
    posing_payload, or quadruped_payload is active, or if a candidate_action
    already exists. Blocking conditions are not visible in the current UI.
  - workflow.finish_preview (workflow.py:1594): keep=True renames the candidate
    to '<name> - B4ML' and sets kept_action; keep=False restores source_action
    and original pose. Both paths clear candidate_action (workflow.py:1629).
  - workflow.restore_kept_source (workflow.py:1649) requires
    obj.animation_data.action == state.kept_action (workflow.py:1654); raises
    if secondary_running or cleanup_running active (workflow.py:1652). No
    indication in the current UI of which action to select first.
  - Spike verified (UI-SPIKE-v1.md): markers render in Dope Sheet; ASCII names
    ≤12 chars; new markers are selected by default; timers fire at 18µs/tick
    but not in --background; TIME_HT_editor_buttons absent (use
    DOPESHEET_HT_header); factory Main workspace hides the marker lane.

inferred:
  - The "nothing happens" report maps to state.status being outside the
    visible scroll area and to the absent animation-editor integration. A
    persistent feedback card at the top of the panel and timeline markers
    together address both causes.
  - The Object-Mode requirement for target manipulation (body_preview.py:179
    places empties in scene; workflow demands Object Mode for free movement) is
    the largest single task-completion blocker. A mode guard with a one-click
    switch is sufficient mitigation without gizmos (Phase 5 stretch).
  - All ARROWS display type (body_preview.py:208) means every target looks the
    same; adding role colour rings via the viewport overlay is sufficient for
    identity without changing backend display types.

assumed:
  - Animator has one Rigify humanoid already set up (not a brand-new user
    configuring a rig from scratch); onboarding for rig setup is out of scope.
  - "Two key poses minimum" (workflow.preview raises with < 2 anchors) is
    known to the animator once the Motion panel shows anchor count and the
    lock reason.
  - The source action is not empty; discard path in finish_preview restores
    correctly (workflow.py:1623-1626).
  - [ASSUMED] Animator uses the default dark Bforartists theme; light theme
    coverage is required but is a secondary target.

open:
  - Does the animator prefer inline controls on each target row, or a
    shared Solve / Keep / Cancel cluster below the list?
  - What is the minimum acceptable feedback latency before a "Running..."
    indicator is needed (temporal solve takes several seconds)?
  - Does A/B toggling (swapping animation_data.action) feel natural, or does
    the animator expect a non-destructive overlay diff instead?
  - Should the Dope Sheet panel be visible by default, or collapsed behind a
    disclosure? (Factory Main hides the marker lane — the panel must help
    reveal it.)
  - Are foot-L and foot-R roles distinct enough for the animator's workflow,
    or do they always operate both feet together?
```

---

## STATE MAP

For each state: entry → presentation (most important fact) → available actions → exit → preserved data.

| # | State | Entry | Presentation | Primary action(s) | Exit | Preserved |
|---|---|---|---|---|---|---|
| 1 | **NO_RIG** | No armature or bound mesh active | Stage strip: Setup lit, all others dim. Card: "Select an armature or a mesh bound to one." | (none — selection only) | User selects a rig → UNSUPPORTED_RIG or MAPPED | — |
| 2 | **UNSUPPORTED_RIG** | Armature active; `family` not humanoid or quadruped | Setup lit. Character card: name + "Not supported — Check Rig" in ERROR card. | **Check Rig** (`b4ml.action operation=INSPECT`) | Mapping succeeds → MAPPED; fails → stays here with error detail | Previous mapping data |
| 3 | **MAPPED** | Rig active and mapped; no posing or preview active | Setup stage completed (checkmark). Pose stage lit. Character card: name + family badge + mapping summary one line. Next: "Start posing" | **Start posing** (`b4ml.body operation=BEGIN`); Advanced expand | Posing begins → POSING_OBJECT | Mapping, anchor list |
| 4 | **POSING / Object Mode** | `body_payload` set, `context.mode == 'OBJECT'` | Pose stage lit. Panel reduces to: target list, Solve/Live/Keep Pose/Cancel. HUD: "Move targets in Object Mode." Mode guard absent. | **Solve** (`b4ml.body_solve`), **Keep Pose** (`b4ml.body operation=KEEP`), **Cancel** (`b4ml.body operation=CANCEL`) | Keep Pose → ANCHORS_CAPTURED (if ≥2) or POSING_OBJECT again; Cancel → MAPPED | body_payload JSON, target empties, anchor list so far |
| 5 | **POSING / Pose Mode** | `body_payload` set, `context.mode == 'POSE'` | Pose stage lit. Mode guard row (ALERT colour): "Move targets in Object Mode — switch now" with one-click `object.mode_set(OBJECT)`. Solve disabled. | **Switch to Object Mode** (one click) | Switch → POSING_OBJECT | Same as state 4 |
| 6 | **ANCHORS_CAPTURED** | `anchors ≥ 2`, `posing=''`, `candidate=False` | Motion stage lit (Pose completed). Anchor list rows with frame + role + Go button. Range line: first frame – last frame. Next: "Generate preview (frames A–B)" | **Generate preview** (`b4ml.action operation=PREVIEW`); retime / ripple controls (`b4ml.temporal_preview` is the learned-motion path; stays in Advanced) | Generate → SOLVE_RUNNING | Anchor list, source action untouched |
| 7 | **PREVIEW_ACTIVE** | `candidate_action` set; source swappable | Review stage lit. State badge: "Previewing: \<name>". Range line active. A/B toggle shows which is visible. Keep and Discard prominent. Source bytes unchanged (`workflow.py:1447` snapshotted before candidate created). | **Keep** (`b4ml.action operation=KEEP`), **Discard** (`b4ml.action operation=DISCARD`), **A/B toggle** (swap `animation_data.action` temporarily) | Keep → KEPT; Discard → MAPPED (anchors remain) | source_action ref, before_pose, before_modes (all in state props) |
| 8 | **KEPT** | `kept_action` set, `candidate_action` cleared | Review stage. Badge: "Kept: \<name>". "Original animation available — Restore" button with copy "the kept result stays available as a separate action". | **Restore original** (`b4ml.action operation=RESTORE_SOURCE`) — only available when `animation_data.action == kept_action` | Restore → back to MAPPED / ANCHORS_CAPTURED | kept_action (fake_user=True, `workflow.py:1616`); kept_source |
| 9 | **RESTORED** | `restore_kept_source` completed; `kept_action` cleared | Transient: SUCCESS card "Original action and input rig modes restored; kept result remains in Actions." Stage returns to MOTION or POSE depending on anchor count. | Continue posing or re-generate | Organic → ANCHORS_CAPTURED or MAPPED | Source action restored; kept candidate action persists with fake_user in bpy.data.actions |
| 10 | **SOLVE_RUNNING** | `temporal_running=True` (or other `_running` flag) | Current stage preserved. Feedback card: "Generating — \<state.temporal_progress>". Panel reduces to one control: **Cancel**. Stage strip dims all other stages with "Wait for current task". | **Cancel** (`b4ml.temporal_cancel`) | Cancel or completion → previous stage | Source action, anchor list; partial output discarded on cancel |

---

## FAILURE + RECOVERY

| Failure | User-side description | Preserved | Recovery action |
|---|---|---|---|
| **Mapping failure** | "This rig is not supported — \<mapping_error text>." Caused by missing bones or an unrecognised rig family. | Previous anchor list, source action | **Check Rig** button in the ERROR card (`b4ml.action operation=INSPECT`). On success, transitions to MAPPED. |
| **Begin posing while playing** | "Stop playback before posing." Raised at `body_preview.py:182` when `screen.is_animation_playing`. | Nothing lost — posing did not start | **Stop Playback** button in the ERROR card (`screen.animation_play`). |
| **Solve failure** (body or temporal) | "Solve failed — \<exc message>." Pose targets remain in the viewport; previous anchors are intact. | All targets, existing anchors, source action | **Retry Solve** (`b4ml.body_solve`) after the animator repositions targets. ERROR card persists until a solve succeeds or the session is cancelled. |
| **Keep / Discard with active posing session** | "Finish or cancel the posing session first." Raised by `workflow.finish_preview` (`workflow.py:1597`) when `body_payload` is set. | Posing session and all its targets | No fix button — the panel shows the Pose stage controls. Animator must Keep Pose or Cancel the session before returning to Review. INFO card explains the block. |
| **Restore with wrong active action** | "Select the kept result before restoring its source." Raised by `restore_kept_source` (`workflow.py:1654`) when `animation_data.action != state.kept_action`. | Source action, kept action (both still in bpy.data.actions) | ERROR card names the kept action. **Select Kept** button sets `animation_data.action = kept_action` (`b4ml.action operation=SELECT_KEPT`) so the animator can then click Restore. |

---

## ONBOARDING

```
ONBOARDING: none — the stage strip + Next line carry it.
```

Justification: the target user already operates Blender/Bforartists at a production
level (assumed). The workflow is a sequence of five named stages (Setup → Pose →
Motion → Polish → Review) that appear as a persistent strip. Every stage shows one
**Next:** line with a filled verb-labeled button and a reason if it is locked.
No concept in the 10-step journey requires explanation that a visible stage name and
a one-line lock reason cannot supply. Adding a tour would duplicate the strip and
increase the time-to-first-action beyond the 30-second target.

If usability testing (handoff §Human usability acceptance) reveals that the
"Start posing" → Object Mode → targets step fails anyway, a one-time contextual
callout can be added to POSING_OBJECT state without a full onboarding flow.

---

## BEHAVIORAL SUCCESS

Observable criteria restating the eight handoff animator observations
(B4ARTISTS_ML_UI_UX_HANDOFF.md §Human usability acceptance):

1. **30-second start**: an animator unfamiliar with the addon selects a Rigify
   humanoid, looks at the N-panel, and clicks the correct first action within 30
   seconds. Measured: time from N-panel opening to first **Check Rig** or
   **Start posing** click.

2. **Explains preview before generating**: before clicking **Generate preview**,
   the animator can verbally state the frame range and what will be created.
   Verified by: the Motion panel shows "frames A–B" in the button label and the
   anchor list shows count and positions.

3. **Every click noticed**: every primary action produces a visible change —
   either a SUCCESS/ERROR feedback card at the top of the panel, a stage
   transition, a marker appearing in the Dope Sheet, or a viewport change.
   No click may leave the UI in a state visually identical to before it.

4. **Source vs candidate distinguishable**: while in PREVIEW_ACTIVE state, the
   animator can identify which of "original animation" and "preview" is currently
   playing without reading the action name in the header. Verified by: state badge
   and A/B toggle label are both readable at a glance.

5. **Anchors visible in Dope Sheet**: after capturing two key poses, the animator
   finds markers named `B4ML Pose 1` and `B4ML Pose 2` in the Timeline or Dope
   Sheet without being coached to look there. Verified by: `markers.sync` ran
   and the factory Animation workspace is available.

6. **Keep / discard / restore without fear**: the animator executes Keep, then
   Restore original, without asking whether data will be lost. Verified by: Keep
   button copy includes "(original is kept too)"; Restore button copy includes
   "the kept result stays available".

7. **Locked feature explained**: the animator reads the reason for a disabled
   stage or control without hovering a tooltip. Verified by: every locked stage
   in the strip has a visible one-line reason in the panel; `stage.locked(key)`
   returns a non-empty string for every locked action key.

8. **No bottom-of-panel dependence**: no step in the primary journey requires
   scrolling to the bottom of any panel to learn the outcome of the previous
   action. Verified by: the feedback card is always drawn at the top of every
   B4ML panel via `header.draw` before the stage-specific body.

---

## DESIGN PLAN

```
SUBJECT: B4Artists ML — Bforartists addon UI for a 10-step humanoid posing and
  preview workflow; audience = production animators; single job = guide the
  animator from rig selection through pose capture to motion preview and commit.
TREATMENT: UI / tool
```

### PALETTE

Role colors for viewport overlay (gpu lines + blf labels on target empties).
These are `gpu` floating-point tuples; hex listed for readability and
palette-validation input.

```
pelvis:   #C97E00  →  (0.788, 0.494, 0.000)   amber — center of gravity, warm
torso:    #28905E  →  (0.157, 0.565, 0.369)   malachite — upright mid-body
head:     #9B7D00  →  (0.608, 0.490, 0.000)   antique gold — topmost, prominent
hand-L:   #E74C3C  →  (0.906, 0.298, 0.235)   Rigify red   (left-side convention)
hand-R:   #3498DB  →  (0.204, 0.596, 0.859)   Rigify blue  (right-side convention)
pole:     #9B59B6  →  (0.608, 0.349, 0.714)   violet — IK chain arc hint
```

Feet borrow the hand hue family at −20 % luminance:
```
foot-L:   #C0392B  →  (0.753, 0.224, 0.169)   deep red
foot-R:   #2E86C1  →  (0.180, 0.525, 0.757)   deep blue
```

Semantic (reused from `contact_visualization._COLORS`, `contact_visualization.py:23`):
```
good:  #2EEB72  →  (0.180, 0.922, 0.451)   = ACCEPTED
warn:  #FF941F  →  (1.000, 0.580, 0.122)   = PROPOSED
bad:   #F22E2E  →  (0.949, 0.180, 0.180)   = REJECTED
```

Semantic colors are separate from role colors and never used decoratively.
The feedback card uses `layout.alert = True` for ERROR (Bforartists native red
tint) rather than a raw bad-color draw, staying within the native theme system.

#### Palette validator output (role colors only — 6 categorical slots)

Input: `#C97E00,#28905E,#9B7D00,#E74C3C,#3498DB,#9B59B6`

**Light mode:**
```
Palette (light, surface #fcfcfb, categorical): 6 slots
  [PASS] Lightness band         all 6 inside L 0.43–0.77
  [PASS] Chroma floor           all 6 >= 0.1
  [WARN] CVD separation         worst adjacent #E74C3C↔ #9B7D00 ΔE 10.2 (deutan) · tritan 58.3 · normal 50.5
  [PASS] Contrast vs surface    all 6 >= 3.0:1

  → ALL CHECKS PASS  (CVD in the 8–12 floor band is legal ONLY with secondary encoding: direct labels, gaps, or texture)
  scope: categorical palettes only. For a lone status/text color check WCAG text contrast; for a sequential ramp, lightness monotonicity.
```

**Dark mode:**
```
Palette (dark, surface #1a1a19, categorical): 6 slots
  [PASS] Lightness band         all 6 inside L 0.48–0.67
  [PASS] Chroma floor           all 6 >= 0.1
  [WARN] CVD separation         worst adjacent #E74C3C↔ #9B7D00 ΔE 10.2 (deutan) · tritan 58.3 · normal 50.5
  [PASS] Contrast vs surface    all 6 >= 3.0:1

  → ALL CHECKS PASS  (CVD in the 8–12 floor band is legal ONLY with secondary encoding: direct labels, gaps, or texture)
  scope: categorical palettes only. For a lone status/text color check WCAG text contrast; for a sequential ramp, lightness monotonicity.
```

CVD WARN on red (#E74C3C) ↔ gold (#9B7D00) adjacent pair: **legal** because every
target carries a direct label ("Hand L", "Foot R", etc.) drawn by the viewport
overlay — primary encoding is the label, color is secondary reinforcement.

### TYPE

Two blf sizes, both scaled by `bpy.context.preferences.view.ui_scale`:

```
stage_label:   blf size 11  — stage strip glyphs, lock-reason line, feedback copy
next_label:    blf size 13  — Next: line action text, HUD task description
```

Blender's native panel widgets (prop, operator, label) use their own sizing;
these two sizes apply only to custom `gpu`/`blf` draw passes.

### LAYOUT

Stage strip (one horizontal row across the panel top, five stages, current
`depress=True`, completed = `CHECKMARK` icon, locked = `LOCKED` icon + inline
reason) → feedback card (single `layout.alert` row, only when non-empty, always
above panel body) → **Next:** line (one filled operator button with a verb label
and the active frame range where relevant) → task-reduced panel body (only the
controls needed to finish or cancel the current task; remaining stages dim with
a one-line reason).

---

## GENERICNESS TEST

Re-reading the palette and copy against the anti-patterns catalog:

- The pelvis / torso / head / hand-L / hand-R / foot-L / foot-R / pole taxonomy
  is specific to a **humanoid IK-rig posing tool**. No generic dashboard, form, or
  report would name colors after body segments.
- Left-side red / right-side blue is borrowed from Rigify — it is the vernacular
  of the Blender character-animation world, not a generic UI convention.
- The violet pole color encodes "IK chain arc hint", a concept that exists only
  in inverse-kinematics posing workflows.
- Copy vocabulary ("Key pose", "Posing session", "Original animation", "Preview",
  "Kept result") belongs exclusively to animation review workflows.
- The A/B toggle (swapping `animation_data.action` between source and candidate)
  is an animation-review-specific interaction with no analogue in general UI kits.
- Stage names Setup / Pose / Motion / Polish / Review map the animator's own
  mental model of the character-animation pipeline, not a generic wizard pattern.

**PASS** — both palette and copy are subject-specific. Nothing here would survive
transplantation to a file manager, analytics dashboard, or settings panel.

Anti-pattern check:
- No cream + serif + terracotta. No purple→blue gradient. No Inter/Space Grotesk.
- No emoji markers, no everything-centered, no glassmorphism.
- No `rounded-lg` on every card; Bforartists native panel chrome handles all
  surface separation.

---

## MAPPING TABLES

### STATE MAP state → `stage.py` identifiers

Phase 1 `stage.evaluate()` must return the correct `StageState.current` and
`StageState.locks` for each combination. Tests in
`test_b4artists_ml_ui_stage_v1.py` assert this matrix one-to-one.

| State | `Snapshot` field condition | `StageState.current` | Key locks added |
|---|---|---|---|
| NO_RIG | `has_rig=False` | `'SETUP'` | all keys: "Select an armature or bound mesh" |
| UNSUPPORTED_RIG | `has_rig=True, mapped=False, mapping_error != ''` | `'SETUP'` | `'pose.begin'`: "Check Rig first" |
| MAPPED | `has_rig=True, mapped=True, posing='', anchors<2, candidate=False` | `'POSE'` | `'motion.preview'`: "Capture a second key pose to generate motion" |
| POSING_OBJECT | `posing='BODY', mode='OBJECT'` | `'POSE'` | `'motion.preview'`: "Finish or cancel the posing session"; `'review.keep'`: same; `'review.restore'`: same |
| POSING_POSE_MODE | `posing='BODY', mode='POSE'` | `'POSE'` | same as POSING_OBJECT + `'pose.solve'`: "Switch to Object Mode to move targets" |
| ANCHORS_CAPTURED | `mapped=True, posing='', anchors>=2, candidate=False, kept=False` | `'MOTION'` | — (preview unlocked) |
| PREVIEW_ACTIVE | `candidate=True` | `'REVIEW'` | `'pose.begin'`: "Discard or keep the preview first"; `'motion.preview'`: same |
| KEPT | `kept=True, candidate=False` | `'REVIEW'` | `'review.keep'`: "Already kept — restore or start a new posing session" |
| RESTORED | `kept=False, candidate=False, posing=''` (post-restore) | `'MOTION'` (if anchors≥2) or `'POSE'` | — |
| SOLVE_RUNNING | `running != ''` | (current preserved) | all keys: "Wait for the current task to finish" |

`Snapshot.posing` maps directly to `obj.b4ml.body_payload` (non-empty string →
`'BODY'`), `posing_payload` → `'ASSISTED'`, `quadruped_payload` → `'QUADRUPED'`.
`Snapshot.candidate` = `bool(obj.b4ml.candidate_action)`.
`Snapshot.kept` = `bool(obj.b4ml.kept_action)`.

### FAILURE list → `feedback.py` levels and fix operators

Phase 1 `feedback.guarded(fn)` wraps every `B4ML_OT_*.execute`; the table below
is the authoritative mapping from caught exception text to feedback payload.
Tests in `test_b4artists_ml_ui_stage_v1.py` assert `feedback_level` and
`feedback_fix` after each simulated failure.

| Failure | `feedback_level` | `feedback_text` (animator-facing) | `feedback_fix` operator | `feedback_fix_label` |
|---|---|---|---|---|
| Mapping failure | `'ERROR'` | "Rig not recognised — \<mapping_error>" | `'b4ml.action'` (`operation='INSPECT'`) | "Check Rig" |
| Begin while playing | `'ERROR'` | "Stop playback before starting a posing session." | `'screen.animation_play'` | "Stop Playback" |
| Solve failure | `'ERROR'` | "Solve failed — \<exc>. Reposition targets and retry." | `'b4ml.body_solve'` | "Retry Solve" |
| Session blocks keep/discard | `'INFO'` | "Finish or cancel the posing session to review the preview." | `''` (no fix button; panel shows Pose controls) | `''` |
| Restore with wrong action | `'ERROR'` | "Select the kept result before restoring its source." | `'b4ml.action'` (`operation='SELECT_KEPT'`) | "Select Kept Result" |
| Preview exists, new preview blocked | `'WARNING'` | "Keep or discard the current preview before generating another." | `''` | `''` |
| Motion layer blocking | `'WARNING'` | "Restore the kept motion source before generating another preview." | `''` | `''` |

`feedback_level` values are the string literals used in `B4ML_PG_settings`:
`'INFO'`, `'SUCCESS'`, `'WARNING'`, `'ERROR'` (EnumProperty, SKIP_SAVE).

The `'SELECT_KEPT'` operation is a new `b4ml.action` operation added in Phase 1
(additive; no existing operation changes). It sets
`obj.animation_data.action = obj.b4ml.kept_action` in one click, resolving the
`restore_kept_source` guard at `workflow.py:1654`.

Operator names above were verified against `b4artists_ml/ui.py` on 2026-09-22 (D1).
