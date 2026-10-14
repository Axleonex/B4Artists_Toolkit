# Plan 02-01 summary

2026-10-14. Baseline verification and scoped repairs complete. Stock Bforartists
5.2.0 build 0a1ca45552db; task-owned profile, generated fixtures and native events.

Original exact 12.6.1: all 80 immediate catalogue effects and nine interactive
tools' preview/commit/cancel (18 cases) pass. Stronger native bar/recovery tests
found three failures: bilateral Mirror Selected read-after-write; fast object
motion trails add current position twice; immediate nested toolbar dispatch
does not retain committed redo state. Original failures are preserved under
evidence/baseline/ and evidence/undo-diagnostic/.

Repairs: snapshot mirror sources before destination writes (local and visual);
sample object location through parent basis rather than animated object matrix;
explicit completed immediate-dispatch undo checkpoint, leaving asynchronous
modal ownership intact. No toolbar redesign in this plan.

Repaired interim package: evidence/repaired-baseline/package-identity.json.
All 80 immediate effects, 11 immediate default native-row clicks, 18 native
interactive commit/cancel cases and 20 native undo/redo assertions pass. The
two other default controls, Breakdown and Smooth, are exercised through native
row input in interactive cases. Bake sampled error 0; object trail world sample
error 0. Every saved curve/handle/selection snapshot matches on cancellation.
Evidence: effect-summary.json, bar-actions.json, modal-actions.json, recovery.json
and coverage.json in evidence/repaired-baseline/.

Harness corrections: dismiss first-start welcome popup before native events;
use an unkeyed pose fixture for an unkeyed Mirror Selected action so asynchronous
animation evaluation does not replace deliberately edited pose; use native
ed.undo/redo instead of assuming the host's keyboard shortcut mapping. A
diagnostic-only extra undo push proved the missing commit checkpoint; it is NOT
used in the passing qualification run. Unsafe profile paths are rejected before
launch. Direct Python launch stalled; PowerShell launch wrapper works.

Limits: representative fixtures, not every production rig. Extended range/mask,
new slider modes and named-layout tests are owned by later plans. Prior public
archive remains unchanged; interim repaired ZIP lives only in task cache. User
profile and scene untouched; no video/audio capture. Router preflight unavailable
(Unix sockets); scoped native continuation under Static Native Execution Policy.

Next: 02-02 configuration/capabilities. No publication.
