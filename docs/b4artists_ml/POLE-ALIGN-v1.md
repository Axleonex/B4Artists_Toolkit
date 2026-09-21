# Align Pole to Current Bend v1

Status: implemented and verified in development 0.33 source. It is not included in the experimental 0.32.0 archive, and no 0.33 package has been created.

## Animator workflow

Start **Humanoid Whole-Body Pose** and expand **Pose Targets**. Each supported Hand and Foot row shows its existing **Elbow Direction** or **Knee Direction** toggle and a new **Align to Bend** button. Use the button to place that limb's owned pole helper on the current evaluated elbow or knee bend plane, then enable the direction toggle if the next solve should preserve that direction.

The action preserves the helper's current radial distance from the middle joint when it is already stable. A helper closer than 0.4 body scales is moved to that minimum distance so its direction remains numerically useful. The direction toggle is never changed. If an enabled pole was moved after the last solve, solve again before Keep.

Stop Live Solve and finish or cancel an active single solve before using Align to Bend. A straight or nearly straight limb has no stable bend plane, so the operation reports an error and leaves the helper, rig pose, status and source animation unchanged. Bend the limb slightly or position the pole manually in that case.

## Architecture and compatibility

The implementation reads the current evaluated 17-joint semantic limb from the existing rig session, projects the middle joint away from the root-to-end axis, and moves only the owned pole helper along that normalized direction. It uses the saved display-motion transform, so transformed native rigs keep the established helper space. The solve itself continues to use the existing geometric pole residual and unchanged acceptance gates.

Focused behavior is covered on:

- BoneForge Control Rig.
- Generated Rigify Basic and Default humanoids.
- Rigify Basic and Default metarigs.
- An independently authored Unity-style humanoid passed through FBX.

All four Hand/Foot helpers and their toggles are covered. Parented, constrained, animated, driven, replaced, non-finite or foreign helpers are rejected before mutation. Save/reload/Keep is exercised with an enabled Foot R pole on generated Rigify Basic. The existing preview lifecycle restores the source pose and action.

## Evidence

| Artifact | Scope | Result | SHA-256 |
|---|---|---:|---|
| `training/b4artists_ml/results/pole-align-v1.json` | Six adapters, all four helpers, UI operator wiring, atomic rejection, read-only status, solve/reload/Keep | 6/6 pass | `33b126222438c35ce513139b2715b4786af9c9b633ee1b3f1d5cca41b7f86957` |
| `docs/b4artists_ml/body-preview-ui-vpole-align-v1.json` | Generated-Rigify-Default foreground operator, modal solve, Escape, Undo/Redo and Keep | PASS | `772f537a5c25d143b1250c9969556a10e2bc4a8308d371a7d361f95190d87e23` |
| `training/b4artists_ml/cache/body-preview-ui-vpole-align-v1.png` | Screenshot from the passing foreground journey | Captured | `1ad2e9259169fb5cdbbfc3d9cac4470ee60e72a9322460e5ed0a63bd76363701` |
| `training/b4artists_ml/results/target-reset-v1.json` | Shared helper validation and Reset regression | 8/8 pass | `ece65e77606fdc5482cf7aa9531962d43e18dcb308f0517d27adba7dbd22190d` |
| `training/b4artists_ml/results/target-mirror-v1.json` | Shared helper validation and Mirror regression | 7/7 pass | `1a9431e91e2a4f54c8375e7fa9e49f2d96c7d4bea15230c2adf59ec08087980d` |
| `training/b4artists_ml/results/pole-status-affected-v1-regression.json` | Current status-enabled Align, Flip, Distance, Body Controls, Context Preview and Base regression | 67/67 pass | `405c5b086f171d5ddef62ee24921f58a8919a4df05ac25eeb6034061eae2cf48` |
| `training/b4artists_ml/results/pole-status-shared-v1-regression.json` | Current status-enabled Reset and Mirror regression | 15/15 pass | `f16d5db1008fb353139c7d419070146bed83b2e3ba1e6eab656ae53a19a6992e` |
| `training/b4artists_ml/results/body-controls-v1.json` | Existing direct orientations and four-pole solve lifecycle | 8/8 pass | `5a7289cf74ce74fd848bf18eb22f8c1dea1c8fb97341734d6a16dabbfbb01766` |
| `docs/b4artists_ml/body-preview-test-v0.32.0.json` | Existing preview lifecycle; historical filename retained | 10/10 pass | `9e1ae97e8e36cce04743f54b4359a50add46b30977fa482b7d3c6eea0c22bcc4` |

The focused six-adapter records begin 1.2617 to 1.3728 radians away from the evaluated bend and finish between `3.37e-7` and `6.13e-7` radians. The foreground Rigify Default journey begins at 1.3260 radians, aligns to `8.17e-8`, and finishes the modal solve at `1.99e-6` radians after 1,608 evaluations and 9.72 seconds of solver work. Distance and enabled state remain unchanged in that journey.

The current affected regression set passes 82/82 test methods across the focused Align, Flip, Distance, Reset, Mirror, Body Controls, Context Preview and Base suites. The installed Bforartists 5.1.0 host uses Blender 5.2 Alpha build `dd23ab17120d`; assertions and result files complete before its previously isolated `ucrtbase.dll` shutdown crash. These process exits are not described as clean.

## Execution and review record

- Harness/profile: Codex workspace.
- Authorization risk tier: `workflow_scaffolding`; the implementation stayed inside the declared preview, UI, test and 0.33 documentation paths.
- Code Router: both native routing-only invocations stopped in the configured `uv` trampoline before execution-value classification. Neither `recommended_lane` nor `actual_lane` was emitted, so no lane is inferred. Escalation count is zero and no remote patch was applied.
- Policy hashes: active adaptive policy `c0dce1c33ee9d164c51df0ceab2e8022e9e8a35ae98a0bb1f7c33c5e731502a2`; execution-value policy `74041cc3740f3165b7a3280583628c2fbe21b60b626d08045eb0560771492466`.
- The active policy is configured as owner-authorized production through 2026-10-11 with execution initial 2/ceiling 8 and reviewer ceilings S0=0, S1=1, S2=2, S3=4, S4=4. Current Windows verification stopped before identity/source validation because Python 3.14 lacks `rfc8785` and managed Python 3.11 lacks `jsonschema`; the WSL retry produced path-translation failures and no PASS report. This session therefore failed closed to serial execution and serial review. No activation was renewed or modified.
- Deterministic validation: focused 6/6, Flip 4/4, Distance 5/5, Reset 8/8, Mirror 7/7, Body Controls 8/8, Context Preview 10/10, Base 34/34 and the generated-Rigify-Default real-window journey PASS. AST parsing passes 141 Python files; whitespace, conflict-marker, JSON and evidence-reference checks pass on the declared scope.
- The independent serial reviewer found one user-facing error message that still named Reset during Align-specific delta-transform rejection. The message now uses the requested action, a focused regression covers it, and the final re-review returned PASS with no remaining finding.

## Claim boundary

Align to Bend and the read-only pole status are procedural posing ergonomics. They read a pose the animator already has, place a helper on that pose's geometric bend plane, and report whether the current helper is aligned, opposite or off-plane. They do not infer a new pose, use learned weights, validate natural motion, or establish Cascadeur parity. Further manual tuning remains within 0.33; quadruped pole controls remain scheduled for 0.35.
