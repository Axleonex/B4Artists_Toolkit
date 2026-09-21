# Quadruped Per-Target Reset v1

Development 0.35 adds a visible **Reset** action beside every active Quadruped Whole-Body Pose helper on generated Rigify cat, horse, and wolf rigs. Body, four paws, semantic Head, and the optional four Pole Targets can each return independently to the exact world transform saved when the preview began.

## Workflow

1. Start **Quadruped Pose** on a generated Rigify cat, horse, or wolf.
2. Move or rotate one or more helpers.
3. Click **Reset** beside the helper whose request should be discarded.
4. Solve again before Keep when a previously solved request was reset.

Reset preserves every other helper, each helper's enabled and Rotation options, the source action and slot, the complete rig pose, Rigify IK/FK modes, and schema-4 Pole Vector modes. A reset after Solve clears the solved signature and metrics, so stale results disappear and Keep remains blocked until the current target set is solved again.

## Safety and compatibility

The operation supports active preview schemas 1 and 2 as well as current schemas 3 and 4. It validates the saved preview metadata, helper ownership, source action/slot, rig/rest/world/frame binding, IK/FK and Pole Vector modes, and target-kind rules before mutation. Playback, replaced or foreign helpers, parenting, constraints, any helper animation data, drivers, NLA, delta transforms, changed scale or rotation mode, malformed metadata, and unknown labels fail closed.

After the depsgraph update, the operation revalidates helper identity, ownership, payload, options, all five helper lock families, target-kind invariants, source action/slot, IK/FK and Pole Vector modes, and the full rig pose. Failure restores the helper pointer, ownership, transform, deltas, lock state, animation-data emptiness, source action/slot, rig transforms, pose-bone modes and locks, preview payload, and status.

This is deterministic preview editing. It does not use a learned model, generate motion, extend rig compatibility, or establish Cascadeur parity.

## Evidence

- Focused Bforartists tests: 9/9. They cover all helper kinds on cat/horse/wolf, solved-state invalidation, schemas 1/2, save/reload, operator wiring, dormant constraints/NLA rejection, malformed and foreign state, concurrent depsgraph mutation, and atomic rollback. Report: `training/b4artists_ml/results/quadruped-target-reset-focused-v1.json`, SHA-256 `a7c8e296c08c54798044a341fa9b991996d7421a43020c2bbaedb47c9829f88b`.
- Affected regression: 107/107 across 14 suites and one frozen 44-file runtime set. Each suite used a freshly created report bound to the same frozen runtime and test hashes. Report: `training/b4artists_ml/results/quadruped-target-reset-affected-v1-regression.json`, SHA-256 `91669bca4f629255e5aadf4e31bcf42176885e59176150247c36c46125f55068`.
- Foreground Bforartists journey: passed Reset, native Undo, native Redo, pose/action/toggle preservation, and live panel display. Report: `docs/b4artists_ml/quadruped-target-reset-ui-v1.json`, SHA-256 `7760f5d0548b6ca7a68c5648c37a81d1bcde63897b43364ed12c3cbf233d707c`.
- Screenshot: `training/b4artists_ml/cache/quadruped-target-reset-ui-v1.png`, SHA-256 `55c9f53bc205e09c9d7c5b752390fa8c293a126272df84a57337f41d85080f6f`.
- Final evidence manifest: `training/b4artists_ml/results/quadruped-target-reset-v1-final.json`, SHA-256 `9274e62a2f8e19e72daa3f84fbf139bc853bab9880c74ca03fa55dfaa5680abc`.
- Final serial read-only reviewer: PASS after three correction rounds; no remaining blocker.

Every background Bforartists subprocess completed assertions and wrote a source-bound report, then returned exit code `11` through the known non-clean shutdown path. The foreground process also returned `1` after its successful report. Clean host shutdown is not claimed.

The coding router failed before emitting a T0-T4 lane because its `uv` trampoline could not spawn the Python child. The owner verifier could not import `rfc8785`. Work followed the recorded `DEGRADED_NATIVE_CONTINUE` path with one writer and serial read-only review. No activation, authorization, commit, merge, push, package, or production state changed. See `quadruped-target-reset-routing-v1.json`.
