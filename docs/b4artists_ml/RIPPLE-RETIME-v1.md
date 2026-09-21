# Ripple Pose Retime v1

Status: verified development source in 0.37.0. This feature is newer than the frozen 0.36.0 package.

## Animator workflow

Move the playhead to a new time, then click the right-arrow button beside a saved priority pose. The **Ripple Pose Retime** dialog shows the exact source and destination frames and how many poses will move. Confirming moves the clicked pose and every later pose by the same delta.

The source Action is not edited. Every moved anchor keeps its serialized pose, destination-owned incoming timing, and descriptive name suffix byte-for-byte. Only its float32 frame and round-trippable frame-name prefix change. The stored collection order remains exact. Intervals among the moved poses remain within one percent of their original duration after Blender float storage; only the interval from the prior unmoved pose to the clicked pose changes.

Use the clock button when only one pose should move within its neighbors. Use the right-arrow ripple button when a beat and the complete later sequence should move together. Native Undo restores the entire ripple and prior status in one operation; Native Redo reapplies it in one operation.

## Bounds and failure behavior

- The playhead destination is rounded to Blender's float32 RNA frame representation before the delta is calculated. Every shifted frame is then rounded independently.
- Proposed frames must remain finite, strictly ordered, more than the anchor ambiguity tolerance apart, inside Blender's absolute timeline range, and within the existing 240-frame experimental span.
- Float32 rounding may change each internal shifted interval by at most one percent, with an ULP allowance for numeric comparison. A larger distortion or frame collapse is rejected before mutation.
- Dialog execution is bound to the full saved-pose collection identity/order/content digest and the displayed destination. A changed playhead, frame, name, payload, order, or replacement makes the dialog stale and rejects it before writing.
- Every active animation workflow, retained Native Motion Layer, active NLA strip, and NLA Tweak Mode rejects the request. Muted NLA tracks remain allowed.
- Positive ripples write last-to-first and negative ripples first-to-last. The complete collection is postvalidated.
- The transaction snapshots every frame, name, payload, collection slot, and prior status. Ordinary write failures restore those values in place. If a callback clears, removes, adds, or reorders anchors during the write, rollback reconstructs the exact semantic rows in their original storage order and verifies the reconstruction before returning the error.

## Verification

`training/b4artists_ml/results/ripple-retime-v1.json` records 8/8 focused tests on Bforartists 5.2.0 Alpha. Coverage includes first/interior/last ripples in both directions, collection storage differing from sorted order, exact payload/timing/suffix preservation, float32 destinations, accepted and rejected one-percent spacing cases, exact and over-limit spans, absolute timeline bounds, collisions, malformed and hostile data, stale dialog frame/name/payload/order changes, every active workflow owner, retained motion, muted and active NLA, forced partial multi-item failures, forced mid-write clear/remove/add/move callbacks, exact semantic rollback, source Action/slot/digest and complete rig-state preservation, operator execution, and save/reload. SHA-256: `1806af821d23cd0593e9d958e2b112b52e1bab638834c6603c4c8c9e94575eb9`.

`training/b4artists_ml/results/ripple-retime-affected-v1-regression.json` binds 97/97 passing tests across nine affected suites to one 44-file runtime source set. SHA-256: `fb871af7aa1275b0d3d5fac6a5de45d5eb6060ce4e97896fa73dabff5139c99a`.

`ripple-retime-ui-v1.json` records a foreground dialog/operator journey that moves frames 6, 11, and 16 to 8, 13, and 18. One native Undo restores every frame, name, payload, timing, status, source Action digest, and rig value. One native Redo restores the complete ripple. Preview evaluates the moved pose at frame 8 and Discard restores the source. Report SHA-256: `862dfc6670ec31eae796cb3cfebc8b9cc0cc8ae5d5c4b7583a9cf4ee2c20278b`. Screenshot SHA-256: `aeed7d012c2fc9c684e65b3d70a83ba40819eec0ddd034c658dedb005aa761b2`.

The host completed every assertion before its known shutdown access violation. This evidence does not label shutdown as clean.

## Claim boundary

Ripple Pose Retime is deterministic timeline authoring. It reduces repetitive multi-pose retiming while preserving authored data, but it does not infer timing or intent, learn motion style, improve physical plausibility, or qualify Cascadeur parity.
