# B4Artists ML UI Phase 5 goal (b4ml-ui-slice-2)

## Status

Goal contract. Successor to b4ml-ui-slice-1 (complete, tag `b4ml-ui-slice-1-complete`, main 727f40b). NOT YET ACTIVATED — activation waits on the animator usability session. Date: 2026-09-22.

## Why this exists

Slice 1 proved a pattern — stage strip, persistent feedback card with one fix action, lock reasons, viewport overlay, Timeline/Dope Sheet integration — on one journey: humanoid posing → preview → keep/discard/restore. Contacts, cleanup, flight, secondary motion and quadruped still sit under Advanced as their original boxes, reachable but not redesigned. Phase 5 extends the proven pattern to the rest of the addon.

## Contract

| Field | Value |
|---|---|
| `objective` | Extend the slice-1 stage/feedback/overlay pattern to the Polish features and quadruped posing, resolve the Object-Mode friction, and close the known copy and layout gaps, so every workflow in the addon — not only the humanoid journey — is discoverable and gives visible feedback. |
| `scope` | `b4artists_ml/ui_workflow/**` including a new `panels/polish.py` and edits to `panels/advanced.py`, `panels/pose.py`, `copy.py`, `stage.py`, `feedback.py`; new tests under `tests/test_b4artists_ml_ui_*/test_b4artists_ml_native_*`; `docs/b4artists_ml/**`; NO changes to solver, contact, cleanup, flight, secondary or temporal math, and no changes to operator `bl_idname`s or operation semantics. |
| `role` | UI/UX implementer working through the governed code router, one declared path per packet. |
| `autonomy_profile` | Interactive — each goalpost reports to the user; merges to main need the commit confirmation. |
| `execution_lane` | Per-packet from the router's `actual_lane`; expect T0/T1 for single-file packets. |
| `yellow_allowances` | Choosing icons, row grouping, foldout placement, test structure, and copy wording that passes the copy gate. |
| `red_exclusions` | Solver/math edits; operator `bl_idname` or semantics changes; evidence-store edits; commit/merge/push without confirmation; Graph Editor/NLA work while it remains deferred. |
| `completion_criteria` | See §Endpoint. |
| `validation_evidence` | Routed receipts per packet, pure + native test runs on Bforartists 5.1.2, screenshots in both themes, the second animator session record. |

## Endpoint (finite)

The goal is complete when ALL of:

(a) Contacts, cleanup, flight and secondary motion are Polish-stage cards with visible prerequisites and lock reasons, not Advanced boxes.

(b) Quadruped posing runs the same guided Pose-stage flow as humanoid.

(c) The gizmo question has a documented decision backed by a spike — ship it or defer it with named reasons.

(d) The five EVIDENCE.open questions from the experience contract are answered from the animator session and the answers are reflected in the UI.

(e) The six known rough edges (listed in §Known gaps) are closed.

(f) Every slice-1 test still passes and new tests cover the Polish action keys, the quadruped stage path and any gizmo surface.

(g) A usability protocol exists for the extended surface and its session is scheduled. The human session itself is outside the endpoint — the goal stops at "scheduled with protocol written", exactly as slice 1 did.

## Workstreams

| ID | Workstream | What changes | Exit test | Depends on |
|---|---|---|---|---|
| W1 | Polish stage migration | Contacts, cleanup, flight, secondary motion move from Advanced subpanels into a new `panels/polish.py` as stage cards; each carries its prerequisite line, `stage.locked()` reason and feedback-card routing; `stage.py` gains real Polish state transitions instead of the always-locked placeholder. | Stage matrix covers every `polish.*` key with a non-empty reason in each state; native fake-layout draw of the Polish panel in all states; existing contact/cleanup/flight/secondary regression suites unchanged. | W5 (design answers), slice 1 |
| W2 | Quadruped into the Pose stage | Quadruped posing gets Start Posing → framed targets → Solve → Keep parity with humanoid; `stage.Snapshot.posing == 'QUADRUPED'` becomes a first-class path rather than a label pointing at Advanced. | Stage matrix for the QUADRUPED posing states; native test starting a quadruped session and asserting the same state/feedback contract the humanoid path satisfies. | W1 (shared card pattern) |
| W3 | Gizmo evaluation and decision | Spike a `GizmoGroup` with `move_3d`/`arrow_3d` handles bound to the body targets so posing works in Pose Mode, keeping empties as the persisted truth; measure against the Object-Mode guard on a real rig; document ship-or-defer. | A spike doc with a runnable script per finding (same format as `UI-SPIKE-v1.md`) and an explicit decision; if shipped, a native test asserting gizmos appear only during a session and that empties remain authoritative. | Slice 1 Phase 2, W5 (does the animator actually hit this friction?) |
| W4 | Graph Editor / NLA (conditional) | The same marker/range/band treatment extended to those editors. | Deferred: do not start until the animator session confirms the Timeline/Dope Sheet integration landed; carries its own spike first. | Animator session outcome |
| W5 | Answer the open design questions | The five EVIDENCE.open items become decisions recorded in the experience contract, then applied: inline vs clustered Solve/Keep/Cancel; the latency threshold before a "Running…" indicator; A/B action-swap vs a non-destructive overlay diff for review; Dope Sheet panel default visibility; whether L/R feet operate independently. | The contract's EVIDENCE.open list is empty or each remaining item states why it stayed open; each applied answer has a test or a screenshot. | The animator session |
| W6 | Close the known gaps | The six items in §Known gaps. | Each item's own check, listed there. | None |

W5 gates the design of W1/W2/W3, so the session runs first; W6 is independent and can run at any time.

## Known gaps carried from slice 1

1. Feedback-card wrap width estimate (~7 px/char in `header.wrap_label`) still clips a few characters at default sidebar width — verified by a screenshot at default width with no clipped line.

2. `'Stage %d of 5 — %s'` in `header.py` and the Advanced subpanel prerequisite lines are literals, not `copy.py` entries — verified by the copy gate extended to cover them.

3. Bforartists 5.1.2's bundled Rigify cannot generate a rig (`make_custom_pivot` AttributeError — upstream bug), so mapped-rig screenshots used fallbacks; verified by capturing the mapped-rig journey with the repo's `rigify_default` fixture instead.

4. One malformed auto-advance commit message (`": auto-advance (receipt 38fc6f10 …)"`, empty path prefix) — cosmetic; verified by the commit-message helper deriving a non-empty subject or the message being corrected in a future rewrite window (do NOT rewrite published history for this).

5. The overlay's `hud_lines()` logic is embedded in the `POST_PIXEL` draw handler, so `test_b4artists_ml_native_overlay_v1::test_hud_lines_only_in_session` self-skips — verified by extracting a pure `hud_lines(snapshot)` helper and that test running for real.

6. BoneForge-gated native tests remain skipped on this host (9 across the new suites, consistent with the project's pre-existing 37) — verified only by naming it a host-configuration limitation, not by pretending it is closed.

## Out of scope (unchanged from the handoff)

Reproducing every Cascadeur feature; replacing Bforartists' full animation workspace; claiming learned-motion quality before its separate qualification gate passes; rewriting verified collision/contact/motion math for layout reasons.

## Activation

This goal activates only after the slice-1 animator session runs and its record exists. On activation, derive the per-packet declared paths, keep the goal ID `b4ml-ui-slice-2` across harnesses, and reuse the lane/wave execution model from slice 1 (`G:/LapArt/.planning/b4ml-ui-slice-1/` scripts: `lane.sh`, `run-wave.sh`, `drive-lane.sh`, `auto-advance.sh`). Note that the parallel-lane model exists because the change-evidence collector snapshots the whole worktree, so concurrent packets need separate git worktrees.
