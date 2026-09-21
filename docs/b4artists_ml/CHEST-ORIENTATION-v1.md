# Semantic Chest orientation v1

Status: implemented and verified in development 0.33 source. It is not included in the experimental 0.32.0 archive, and no 0.33 package has been created.

## Animator workflow

Start **Humanoid Whole-Body Pose**, expand **Pose Targets**, and enable **Rotation** on the Chest row. Rotate the Chest helper, then solve or enable Live Solve. The position and rotation toggles remain independent, so an animator can request either constraint or both.

Chest orientation is measured on semantic joint 2 of the existing 17-joint body representation. The solver evaluates the mapped skeletal Chest bone, then distributes its rotation through the adapter's existing writable spine controls. This is necessary because the semantic Chest bone is not always a direct animator control. Existing direct pelvis, head, hand and foot orientation constraints keep their established mapping and acceptance behavior.

The request remains constrained by all enabled pins, limits and poles. A large Chest turn can be incompatible with several fixed hand, foot and head positions. The solver rejects that result and restores the prior pose. Release conflicting pins or make a smaller adjustment rather than expecting an arbitrary simultaneous constraint set to succeed. The foreground test retains all default position pins and verifies a 0.02-radian Chest adjustment; focused adapter tests verify a larger reachable turn with only the Pelvis pin retained.

## Compatibility and lifecycle

- BoneForge, generated Rigify Basic, generated Rigify Default, Rigify Basic metarig, Rigify Default metarig and independently authored Unity Humanoid FBX adapters are covered.
- New previews store `controls_version=4`. Version 4 exposes the Chest Rotation checkbox.
- Saved version 2 and 3 previews must be restarted before authoring Chest rotation. Existing Keep and Cancel recovery remains available when their saved ownership metadata validates. Reset is supported only for legacy rows reconstructible from saved target matrices; this slice does not claim broad Chest Reset compatibility for older records. Version 1 previews retain their original six target rows.
- Reflected or otherwise invalid helper axes are rejected before pose mutation.
- Body strength, target strength, native motion transforms, cancellation, Undo/Redo, save/reload, Keep and source-action recovery use the existing whole-body preview lifecycle.
- The solver accepts only results below the existing normalized position, length, orientation and pole gates. It does not loosen legacy tolerances.

## Evidence

Fifty-eight affected Bforartists tests pass across eight suites under the final source, plus the 33/33 base suite:

| Evidence | Coverage | Result | SHA-256 |
|---|---|---:|---|
| `training/b4artists_ml/results/chest-orientation-v1.json` | Focused orientation, save/reload/Keep and atomic old-preview/axis rejection; six humanoid adapter records | 3/3 pass | `f215cfa2b8ebe886d9bfffaeda08a5940a1db8d270a409dfa1def44efb4d081c` |
| `training/b4artists_ml/results/chest-target-v1.json` | Existing semantic Chest position behavior across six adapters | 3/3 pass | `8bf223f853b1d821d84b9df722235fc6abb71b560e4d7d7f6075c4fbfcf3079f` |
| `training/b4artists_ml/results/body-controls-v1.json` | Existing direct rotations, poles, save/reload, cancellation, stale edits and authentic 0.5.1 preview | 8/8 pass | `5a7289cf74ce74fd848bf18eb22f8c1dea1c8fb97341734d6a16dabbfbb01766` |
| `training/b4artists_ml/results/target-reset-chest-orientation-v2.json` | Per-target Reset and serialized-preview ownership/recovery | 8/8 pass | `ece65e77606fdc5482cf7aa9531962d43e18dcb308f0517d27adba7dbd22190d` |
| `training/b4artists_ml/results/target-mirror-chest-orientation-v1.json` | Semantic mirroring and version-1 recovery under preview controls version 4 | 7/7 pass | `1a9431e91e2a4f54c8375e7fa9e49f2d96c7d4bea15230c2adf59ec08087980d` |
| `training/b4artists_ml/results/joint-limits-v1.json` | Control and skeletal joint-limit regressions | 9/9 pass | `fd6602517cbdaba19b0e4c542c00bf3094ecb90de0b68c325a84e0ee73412ad8` |
| `training/b4artists_ml/results/bend-limits-chest-orientation-v1.json` | Directional bounds with combined pins, rotations and poles | 10/10 pass | `b28943aa478a63a47daef2be3f854ae915541330272ce0c694462d49941b3553` |
| `docs/b4artists_ml/body-preview-test-v0.32.0.json` | Existing preview lifecycle; historical filename retained | 10/10 pass | `9e1ae97e8e36cce04743f54b4359a50add46b30977fa482b7d3c6eea0c22bcc4` |

The six focused adapter errors range from `2.8322e-7` to `1.6495e-6` radians, below the unchanged `0.001` orientation gate. The result records 886 to 1,560 nonlinear evaluations and approximately 1.5 to 7.7 seconds of solver time on this machine.

The generated-Rigify-Default real-window journey is `docs/b4artists_ml/body-preview-ui-vchest-orientation-v5.json` (SHA-256 `7739064c7a35d4b5db52dd154a148658b6e65ec281718f52b4778701646d3b39`). It verifies visible Chest Rotation authoring, modal solve, evaluated Chest orientation, Escape restoration, native Undo/Redo, Keep and source-mode recovery. Its measured Chest error is `6.6386e-7` radians after 1,599 evaluations and 11.78 seconds of solver work. The inspected screenshot is `training/b4artists_ml/cache/body-preview-ui-vchest-orientation-v5.png` (SHA-256 `5da200627330d5263c78b3f7b3db516516466c87654d1ef6f4a2cf5e4e85f735`).

Four preceding real-window experiments are retained as failed evidence. A 0.08-radian request with every default position pin exceeded the position gate at the normal solve budget; increasing the iteration budget or pin weights did not make that conflicting request acceptable. The shipped source retains the prior weight and solve budget.

All assertions finish before the installed Blender 5.2 Alpha host's known `ucrtbase.dll` shutdown crash. The process exit is not described as clean.

## Execution and review record

- Harness/profile: Codex workspace.
- Authorization risk tier: `workflow_scaffolding`; scope stayed within the declared solver, preview, UI, focused tests and 0.33 documentation paths.
- Code Router: the configured WSL invocation returned `REMOTE_EXECUTOR_REQUIRED` for the allowlisted `desktop-prime-ssh` route before execution-value classification. Neither `recommended_lane` nor `actual_lane` was emitted, so no lane is inferred. Escalation count is zero and no remote patch was applied.
- Policy hashes: active adaptive policy `c0dce1c33ee9d164c51df0ceab2e8022e9e8a35ae98a0bb1f7c33c5e731502a2`; execution-value policy file `74041cc3740f3165b7a3280583628c2fbe21b60b626d08045eb0560771492466`.
- Native production verification stopped before identity/source validation because the default Python lacks `rfc8785` and the managed Python 3.11 lacks `jsonschema`. Execution therefore failed closed to one serial parent and one serial reviewer; no activation was renewed or modified.
- The requested S3 evaluator command was rejected by automatic approval review while identity/source binding remained unverified. The serial reviewer found two documentation warnings, both corrected, and then returned PASS with all updated artifact hashes verified.
- Deterministic validation: focused 3/3, body controls 8/8, Chest position 3/3, target Reset 8/8, target mirror 7/7, joint limits 9/9, bend limits 10/10, preview lifecycle 10/10, base 33/33, real-window journey PASS, AST parsing 140 files, and whitespace/conflict/reference checks on the 18-file declared scope.

## Claim boundary

This feature is a procedural evaluated-rig orientation constraint around the existing contextual pose proposal. It changes no model, weight, training data or inference claim. It improves direct torso posing on the tested adapters, but it does not establish learned orientation conditioning, natural-motion quality, human usability, or Cascadeur parity.

The subsequent per-limb current-bend pole action is recorded separately in `POLE-ALIGN-v1.md`; it does not change the Chest evidence or claim boundary above.
