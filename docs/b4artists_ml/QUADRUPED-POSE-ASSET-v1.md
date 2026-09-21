# Quadruped Pose Request Asset v1

Development 0.35 adds scene-local **Save Solved Pose** and **Apply Pose** actions to generated Rigify cat, horse, and wolf Quadruped Pose previews. An animator can solve one sparse target request on one supported profile, save it, then reconstruct that request on another supported generated quadruped before solving and inspecting the destination pose.

## Workflow

1. Start **Quadruped Pose** on a generated Rigify cat, horse, or wolf.
2. Arrange Body, Head, fore/hind paw targets, and optional Pole Targets. Set Spine Follow and Neck Share.
3. Solve and inspect the request, then click **Save Solved Pose**.
4. Start a matching Pole Target mode preview on another supported quadruped in the same scene.
5. Click **Apply Pose**, solve the reconstructed request, inspect it, then Keep or Cancel.

The saved asset records semantic target deltas in the source preview's verified Body frame and normalizes translation by the preview body scale. Paw, Body, and Head rotation deltas use proper quaternions. Head remains rotation-only. Pole Targets remain position-only. Spine Follow and Neck Share transfer with the request. This representation lets the same request adapt across the different proportions and orientations of generated Rigify cat, horse, and wolf rigs.

Saving requires a current verified solve and schemas 3 or 4. Applying requires the destination preview to use the same Pole Target mode. Apply changes only preview helpers and request settings; it preserves the armature pose, source action and slot, object transform, IK/FK state, Pole Vector state, and scene-local asset. Apply clears the previous solve signature and metrics, so Keep remains blocked until the destination request solves successfully.

## Safety and compatibility

The scene asset has a strict schema, exact semantic target order, 64 KiB size limit, finite numbers, normalized rotations, zero Head translation, and an eight-body-scale translation limit. Preview scale must be a finite positive numeric value; booleans, NaN, infinity, zero, negative values, and derived world-transform overflow fail before mutation. Capture applies the same range checks, so it cannot save an asset that its own apply path rejects.

Before writing, Apply validates every owned helper, target-row topology, action/slot binding, rig mapping, saved frame, request settings, transform rule, and the exact raw scene asset. After Blender's dependency update it repeats strict helper validation and verifies the raw asset is unchanged along with pointer identity, ownership metadata, locks, deltas, constraints, AnimationData, matrices, options, topology, Spine Follow, Neck Share, action/slot, modes, and the complete rig pose. Any failure restores the original scene asset, target collection, helper transforms and settings, rig/action state, request settings, payload, and status.

This is deterministic semantic request reuse. It does not learn a motion style, synthesize a gait, expand imported/custom quadruped support, or establish Cascadeur parity.

## Evidence

- Focused Bforartists tests: 7/7. Coverage includes schema 3 and 4, generated Rigify cat/horse/wolf cross-profile transfer, an independent known body-local translation/rotation oracle, optional poles, Save/Apply operators, solve/reload/Keep, strict malformed input and overflow handling, excessive capture rejection, stale-solve invalidation, exact scene-asset replacement/deletion rejection, and forced dependency-handler rollback. Report SHA-256: `964197f0ad44fb8a10f49f384c751d95a61499fc05c524e657f67bde222b73be`.
- Affected regression: 122/122 across 16 suites and one frozen 44-file runtime set. Report SHA-256: `c130959aa29ae2ed86509e3f3c05f5681f953ad380666571eb84709b5f6c78da`.
- Foreground Bforartists journey: passed Cat Save, Horse Apply, native Undo, native Redo, source pose/action preservation, and live panel display. The report binds the exact 44-file runtime and journey-script hashes. Report SHA-256: `ecf3c355f278d9680822b43ea00d99c7bb1cb39987164c5f99ce4eb1012b2ad4`; screenshot SHA-256: `a8e5b124e3fe323befd77c88fba539bbb1a30a10456c52755098a2057824b5cf`.
- Final evidence manifest: `training/b4artists_ml/results/quadruped-pose-asset-v1-final.json`, SHA-256 `b8694a3b08ae2c06208ebd6af9d186bd2bb32682509fa7513b3a4356c891bc92`.
- Final serial read-only reviewer: PASS after hostile-scale, post-update interference, capture-range, independent-oracle, and legacy-suite stability corrections; no remaining actionable finding.

Every Bforartists subprocess completed assertions and wrote a source-bound report before the known non-clean shutdown path. Clean host shutdown is not claimed.

The coding router failed before emitting a T0-T4 lane because its `uv` trampoline could not spawn the Python child. The owner verifier could not import `rfc8785`. Work followed the recorded `DEGRADED_NATIVE_CONTINUE` path with one writer and serial read-only review. No activation, authorization, commit, merge, push, package, or production state changed. See `quadruped-pose-asset-routing-v1.json`.
