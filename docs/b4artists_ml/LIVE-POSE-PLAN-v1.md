# Optional live whole-body preview: implementation plan

Scope: connect the existing accepted pose-preview lifecycle and cooperative
solver to an opt-in continuous target-update workflow. This is the current-frame
posing feature in the original goal, not learned temporal inbetweening.

## Intended animator behavior

After starting a whole-body preview, the animator can enable Live Solve. Moving
position/pole helpers or changing supported target/strength/limit/balance settings
queues the newest complete request. A short quiet interval avoids repeated work
while dragging. If a request changes during fitting, cancel the stale fit back
to its preceding preview and schedule only the latest request. A settled request
uses the existing solver and existing accuracy gates. Unchanged targets do not
trigger repeated solving. Live solving is optional and off by default.

Stop Live Solve or Escape ends automatic scheduling and cancels an unfinished
fit. The solved preview remains available for the existing Keep as Pose Anchor
or Cancel Preview operations. Changes to scene/frame/ownership, save, load,
undo/redo, preview finish, disable or unregister stop scheduling safely. No
unsolved request can be kept, no source action is rewritten, and live scheduling
must never resume automatically from a saved file.

## Files and architecture

- New b4artists_ml/body_live.py owns the small live request scheduler. Explicit
  clock injection permits deterministic debounce/queue tests. It delegates all
  fitting, numerical gates, recovery and persistence to body_preview.
- b4artists_ml/ui.py adds a live modal operator, opt-in controls, a transient
  SKIP_SAVE live flag and clear status. Timer callbacks perform at most one
  cooperative fit step. Target edits pass through while live scheduling runs;
  manual-solve ownership cannot overlap.
- b4artists_ml/body_preview.py closes live scheduling from its existing lifecycle
  boundaries. Prefer local imports to avoid import cycles. Existing manual
  solve/Keep/Cancel behavior remains protected by regression tests.
- b4artists_ml/__init__.py changes version only after a qualified experimental
  build is packaged. Existing model weights and other add-ons remain unchanged.

## Required evidence before the feature milestone passes

1. Deterministic scheduler tests: quiet interval, no redundant work, changing
   requests abort/restart only the newest intent, cancellation and invalid input.
2. Actual BoneForge plus basic/default generated Rigify and metarig fixtures:
   two nontrivial target edits, existing pin/length/orientation gates, source
   action/keys/modes restoration, no leaked helpers/jobs/evaluation copies.
3. Cooperative timing measured separately for scheduling and solve steps;
   report actual cold/warm distributions and limits without claiming instant
   posing when a fit still takes seconds.
4. Existing preview, directed control, joint-limit, balance and lifecycle
   regressions appropriate to changed integration paths.
5. Actual UI events exercise start, edit, stale cancellation, stop, Keep/Cancel,
   undo/redo, save/reload and disabling. No simulated pass replaces an untested
   native event path. Source identity/keys and unsolved-request guards verified.
6. Updated guide, requirements mapping and experimental installable package;
   package-source parity and offline lifecycle check. No temporal weights added.

The goal's quality thresholds, identity/publication rules and expanded 50-total /
15-hour limits remain authoritative. This is a prospective implementation
milestone; passing it cannot establish full usability, rig coverage, temporal
quality, or Cascadeur parity. Do not weaken requirements to force it to pass.
