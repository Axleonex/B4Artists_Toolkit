# Equalize Later Pose Spacing v1

Status: verified development source in 0.37.0; newer than the frozen 0.36.0 package.

Click the `=` button beside any saved priority pose except the last. The dialog keeps that pose fixed and places every later saved pose at one constant interval from 0.25 through 240 frames. This gives an irregular blockout a regular beat without recapturing poses one at a time. Pose data, easing, Breakdown Bias, Departure Hold, Arrival Hold, descriptive name suffixes, collection storage order, source Action, and rig state remain exact.

The dialog starts with the pivot-to-next-pose interval and binds execution to the complete saved-pose collection. The backend validates the edited interval, independently rounds each destination to Blender float storage, and rejects no-op, colliding, out-of-order, non-finite, out-of-range, or over-240-frame results before mutation. Stored intervals must remain within one percent of the requested value. Expansion writes last-to-first and compression first-to-last. The shared transaction reconstructs exact semantic rows after topology-changing write callbacks.

`training/b4artists_ml/results/pose-spacing-equalize-focused-v1.json` passes 8/8 focused tests. SHA-256: `bd30baf467be519694b2e49d892ad8155703313e68bd1c3aff6eb060bd99a9e1`.

`training/b4artists_ml/results/pose-spacing-equalize-affected-v1-regression.json` passes 113/113 tests across eleven affected suites on one 44-file runtime set. SHA-256: `4e06ba9cf04efc00ee3db21d39f45aaedec8cf8a64a8a2c12dfa781b99523063`.

`pose-spacing-equalize-ui-v1.json` records the foreground dialog, an irregular `[1, 6, 14, 25]` blockout changed to `[1, 6, 10, 14]`, one native Undo and Redo, preview at moved frame 10, and source recovery. Report SHA-256: `6c8bba2322712f674f5a8b2b568580af9517afb7cd93909ebd3c48878b0209fc`. Screenshot SHA-256: `7573f745d08ec2606f2d1c0f95e57a66b2d75a85f653b8da6d5e04c1a41c733a`.

The host completed every assertion before its known shutdown access violation; shutdown is not labelled clean. This is deterministic timeline authoring. It does not infer timing or intent, learn motion style, improve physical plausibility, or qualify Cascadeur parity.
