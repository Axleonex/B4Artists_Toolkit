# Quadruped Target Mirroring v1

Development 0.35 adds visible **Mirror L to R** and **Mirror R to L** actions to the generated Rigify cat, horse, and wolf Quadruped Pose preview. Each action transfers the edited fore- and hind-paw request to the opposite side. Schema-4 previews mirror the matching fore and hind Pole Target positions as well.

## Workflow

1. Start **Quadruped Pose** on a generated Rigify cat, horse, or wolf.
2. Move or rotate one side's paw helpers. Move that side's optional Pole Targets when they are active.
3. Click **Mirror L to R** or **Mirror R to L**.
4. Solve again, inspect the pose, then Keep or Cancel.

The operation mirrors each source edit relative to its own preview-start transform and applies that reflected delta to the opposite helper's preview-start transform. Paw orientation deltas are mirrored as proper rotations. Pole Targets remain position-only and retain their saved orientation. Body, Head, source helpers, destination Pin/Rotation options, the source action and slot, the complete rig pose, IK/FK modes, and Pole Vector modes remain unchanged.

## Safety and compatibility

Saved schemas 1 and 2 remain supported, along with current schemas 3 and 4. The mirror plane is derived from the verified saved quadruped body frame and both left/right paw spans. Ambiguous, non-finite, scaled, sheared, reflected, parented, constrained, animated, driven, foreign, or replaced helpers fail before mutation.

After the dependency-graph update, the operation independently revalidates the stored source pointer, active action and slot; exact target collection topology; every row pointer and option; helper ownership, transform rules and lock state; Rigify modes; preview metadata; and the full rig pose. Failure restores the source binding, action/slot, rig pose and modes, complete collection row topology, helper transforms and settings, payload, and status. Mirroring after Solve clears the solved signature and metrics, so Keep remains blocked until the mirrored request is solved.

This is deterministic preview editing. It does not recognize or generate gait, use a learned quadruped model, extend rig compatibility, or establish Cascadeur parity.

## Evidence

- Focused Bforartists tests: 8/8. Coverage includes generated Rigify cat/horse/wolf, schemas 1-4, optional poles, independent left/right reflection and rotation checks, both directions, save/reload, stale-solve invalidation, invalid helper state, source-pointer and action substitution, collection clearing, concurrent mutation, and atomic rollback. Report SHA-256: `b05112f825b9b82531c86033c4513a62a437b71ec1c7c540192c9d2ddfaee572`.
- Affected regression: 115/115 across 15 suites and one frozen 44-file runtime set. Report SHA-256: `ab67df1740dbc34674b185196e724927c9a59eb777d9fae6535e4f3688894021`.
- Foreground Bforartists journey: passed Mirror L to R, native Undo, native Redo, source/destination invariants, pose/action/toggle preservation, and live panel display. Report SHA-256: `42843027005f381f7430b2b875c3f18d6e3c23a5245f4549db35daa023b2cbe6`; screenshot SHA-256: `18d9f87d7e82546116c6507b1dcf908fb1651fa3a64a2a59a5d7caa4cd41f2f6`.
- Final evidence manifest: `training/b4artists_ml/results/quadruped-target-mirror-v1-final.json`, SHA-256 `eb21e0a9a50987c2fbde086cf99e81e3f920e3cbc99fdf79d0902c1e11b6e3a7`.
- Final serial read-only reviewer: PASS after the source-binding, collection-topology, and independent-oracle corrections; no remaining blocker.

Every background Bforartists subprocess completed assertions and wrote a source-bound report before the known non-clean shutdown path. The foreground host also crashed after writing its successful report. Clean host shutdown is not claimed.

The coding router failed before emitting a T0-T4 lane because its `uv` trampoline could not spawn the Python child. The owner verifier could not import `rfc8785`. Work followed the recorded `DEGRADED_NATIVE_CONTINUE` path with one writer and serial read-only review. No activation, authorization, commit, merge, push, package, or production state changed. See `quadruped-target-mirror-routing-v1.json`.
