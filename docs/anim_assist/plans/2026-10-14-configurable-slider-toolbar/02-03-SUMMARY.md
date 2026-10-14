# Plan 02-03 summary

Eight scalar adapters implemented through the existing Breakdown, curve and
retime math, with full key/handle/type/interpolation/selection snapshots.
Absolute previews restore the starting state first. New operator provides
hold/release commit, Esc/right-click cancel, numeric entry, Shift precision,
snapping and explicit configured range. Anim Offset remains a session tool.

Six pure transaction tests pass. Stock Bforartists native events pass 32 cases
(eight tools × inline/popout × cancel/commit), with independent numeric effect
expectations and 32 undo/redo assertions. Evidence: adapters/slider-actions.json,
slider-coverage.json and recovery.json. Intermediate package is separate from
published archives and contains the current source; no UI drawing parity claim
yet, because the new row will be connected in 02-04.

Caught and fixed an actual bpy collection-membership TypeError in the area-loss
guard; iteration compares objects rather than Python `in` on RNA collections.
A transient request-file lock stopped an early test-bridge timer; the bridge now
retries atomic responses and transient file errors. The full rerun passes.
Failure paths restore the transaction rather than leaving preview edits.
Curve tool sensitivity now resolves the actual installed preference package.
Further settings/extended range/lifecycle/actual-row paths are final-suite gates.

Next: row rendering and native settings dialogs, then named-layout UI.
