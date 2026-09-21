# Priority Pose Retime v1

Status: verified development source in 0.37.0. This feature is newer than the frozen 0.36.0 package.

## Animator workflow

Move the playhead to the desired time, then click the clock beside the saved priority pose to move. The **Priority Pose Retime** dialog shows the exact source and destination frames before applying the move.

Retiming moves the saved pose anchor without recapturing the rig or editing its source Action. The anchor's serialized pose and destination-owned incoming timing remain byte-identical. Its display name receives the new round-trippable frame prefix while the existing descriptive suffix remains exact. The following pose keeps its own incoming timing unchanged.

The saved-pose order cannot change. A middle pose must remain strictly between its immediate sorted neighbors. The first pose must stay before the second, and the last must stay after the penultimate. This keeps timing ownership and interpolation topology explicit.

Native Undo restores the complete frame, name, payload, timing, and status in one step. Native Redo reapplies the same move in one step.

## Bounds and failure behavior

- The destination is rounded to Blender's float32 RNA frame representation before collision, neighbor, and range checks.
- Same, ambiguous, colliding, and order-changing destinations are rejected before mutation.
- The final sorted anchor span may not exceed the existing 240-frame experimental limit. The exact boundary is accepted; the next representable value beyond it is rejected.
- The source is resolved uniquely from the fully validated sorted anchor set during dialog invocation and again during execution. A moved anchor, changed playhead, malformed payload, or changed display binding makes a stale dialog fail.
- Active preview/generation work, a retained Native Motion Layer, active NLA strips, or NLA Tweak Mode reject the request. Muted NLA tracks remain allowed.
- Frame, name, payload, and prior status are snapshotted before writing. A failure after the frame or name write restores all four values.

## Verification

`training/b4artists_ml/results/pose-retime-v1.json` records 8/8 focused tests on Bforartists 5.2.0 Alpha. Coverage includes interior/first/last moves, collection order differing from sorted order, exact payload/timing/suffix preservation, float32 storage, exact and over-limit spans, same/collision/reorder/ambiguous frames, stale dialogs, hostile sources and saved data, every active workflow owner, retained motion, muted and active NLA, forced failures after frame and name writes, source Action/slot/digest and complete rig-state preservation, operator execution, and save/reload. SHA-256: `90814cc77767414b0134618b4e1cac30eed1c1d3a14c7995096abbd6660836d2`.

`training/b4artists_ml/results/pose-retime-affected-v1-regression.json` binds 89/89 passing tests across eight affected suites to one 44-file runtime source set. SHA-256: `708aa4d109320b6d696f929dfad2f347812f8ae0fe3937d2d88fa81b5084d1bd`.

`pose-retime-ui-v1.json` records a foreground dialog/operator journey. One native Undo restores the exact frame, name, payload, timing, status, source Action digest, and rig state. One native Redo restores the exact retime. The retimed pose is then used by preview and the original source is recovered through Discard. Report SHA-256: `6ac43836a618f37f1546bf1fe94e3c956f83ed6061ce4b810455765866594d74`. Screenshot SHA-256: `0a8578ea5bf16276c0b2468569db28ffd17722d2e6dc02a185f1596e6a13fe58`.

The host completed every assertion before its known shutdown access violation. This evidence does not label shutdown as clean.

## Claim boundary

Priority Pose Retime is deterministic timeline authoring. It reduces recapture and repair work but does not infer timing or intent, learn motion style, improve physical plausibility, or qualify Cascadeur parity.
