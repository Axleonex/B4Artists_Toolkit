# Static balance assistance ? experimental 0.12.0

The whole-body pose workflow now fits the authored COM projection toward an explicit support region, preserving positional/orientation pins and enabled joint limits. It uses the mass and patch approximation introduced in 0.11.0. This is geometric static assistance, not learned dynamics or a completed physics system. The full goal remains active and incomplete.

## Use the workflow

1. On the original pose, initialize and tune **Center of Mass / Support > Mass Model**. In **Animation Contacts**, capture the intended load-bearing hand/foot centers with local offsets, enable **Use as Support Patch**, and set each patch's hold interval, dimensions and heading. Configure the support plane and tolerances. See [SUPPORT.md](SUPPORT.md) for the model assumptions and internal/display units.
2. Click **Start Whole-Body Pose**. Enable **Assist Static Balance**. Support contacts must match this preview's starting pose, be inside their hold interval at full strength, and lie on the authored plane. Correction currently requires gravity perpendicular into that plane; zero gravity and inclined/friction-dependent cases are rejected.
3. Set **Support Inset** to the desired distance inside the support boundary. Oversized insets that erase the usable area are rejected. **Balance Strength** blends from the original preview COM projection toward the closest point in that inset region. Partial strength can deliberately leave COM outside support; it is not described as full balance. Zero strength uses the ordinary whole-body solver without balance correction.
4. Keep the controls you intend to pin. **Allow Pelvis Translation** explicitly releases only the pelvis position pin; its orientation remains constrained. Leave this unchecked to retain the pelvis position. Supporting hands/feet remain pinned to their captured points and orientations, even when their ordinary position checkbox is off. Conflicting authored pins fail with a diagnostic. Unpin head/hands or other ordinary targets only if their movement is part of your intended correction.
5. **Solve Whole Body** runs a cancellable preview. Inspect the pose, last COM error and signed support margin. Escape restores the preceding preview. Change mass, support or pose settings and solve again before keeping. Repeated strength previews use the original reference and do not accumulate correction.
6. **Keep as Pose Anchor** stores editable FK control values and restores the source rig/action. The saved pose can enter the existing multi-anchor interpolation workflow. **Cancel Preview**, Undo/Redo and save/reload retain their prior recovery semantics. This release does not enforce balance between those anchors.

Learned Influence is independent of Balance Strength. The existing trained contextual pose network can propose a pose before geometric balance/pin projection. Its weights and known quality limitations are unchanged. The network does not learn from segment masses or predict balance forces. A zero learned influence remains useful for inspecting the geometric correction alone.

## Geometry and acceptance

The mass model's normalized segment weights and center fractions produce evaluated whole-character COM. Positive uniform object transforms and the verified humanoid adapters retain their existing support. The pelvis is not substituted for COM.

Accepted rectangular patches form a convex planar support hull. Each inward-shifted edge clips the hull to form the requested inset. The closest point in that convex region defines the full-strength target; interpolating from the immutable starting COM projection defines partial strength. An already-inside COM retains its projection. Only the two in-plane coordinates are targeted; height can change through the allowed rig controls.

The whole-body least-squares fit includes the COM projection alongside pins, rotations, poles, enabled limits and a small pose-change preference. Supporting effector orientations are evaluated during fitting so head/hand/foot segment centers match the final pose. The dependency-closed proxy can accelerate fitting, but acceptance always evaluates the original rig.

Final COM target and support point errors must each be at most 2e-4 of the session's torso reference length. Support and other constrained orientation errors must be at most 0.001 radians. Existing positional, joint-limit, pole and segment-length checks remain active. The fitter may trade errors internally, but a preview that violates acceptance is rolled back rather than silently relaxing pins. A positive margin indicates geometric interior distance; the support report may still label a small positive margin as Boundary when it is within the user-authored contact tolerance.

Requests copy mass, plane, gravity, contact, timing and strength settings. Changes during a solve reject and restore that result, while changes after solving invalidate Keep. Each new session stores 17 reference transforms alongside its existing source/preview recovery data. Starting-reference validation catches incompatible saved transforms. This also preserves the intended reference across repeated solves and save/reload.

## Compatibility and correctness fix

Authentic 0.11.0 previews remain solvable and keepable with balance disabled. They lack balance reference transforms, so enabling balance asks for a new whole-body preview. It does not guess the missing data or discard the existing preview.

During implementation, immediate script-driven solves exposed stale helper `matrix_world` values before the first viewport redraw. Request capture now updates the view layer before reading helper transforms. This fixes valid pins being incorrectly read at the origin; it does not change the intended targets or relax tolerances.

## Evidence and limitations

Ten balance integration tests cover all five real builders, retained pelvis pins, free-pelvis corrections, pinned support, weighted mesh samples, enabled skeletal limits/orientations, learned proposal integration, partial/zero strength, repeatability, cancellation, stale settings, conflicting targets, invalid physical inputs, transformed coordinates and save/reload. They also recover an authentic preview created with the released 0.11.0 ZIP. Four new pure numerical tests cover inset construction, closest points, coordinate/length transformations and invalid/degenerate support; the eight earlier support math tests remain in the package validation.

The main correction fixture deliberately leans a torso and uses a stylized head-heavy distribution to put COM outside two small authored foot patches. It proves that the tested solver corrects a measurable constraint on real rigs; it is not a representative animator study or calibrated human dynamics benchmark. Bound mesh checks use controlled weighted samples, not a production character collision or deformation-quality review.

The real-window test invokes the normal modal operator, verifies the original-rig result, sends Escape during a repeat solve, checks Undo/Redo, and keeps the pose anchor while verifying source restoration. Its screenshot was visually inspected. No synthetic post-solve undo push is used.

All host processes still show the pre-existing `ucrtbase.dll` shutdown access violation after their assertions. Passing assertions do not imply a clean host exit. Full regression and final package identities are recorded in `checkpoint-balance-v1.json` and `package-test-v0.12.0.json`.

This release does not supply contact forces, friction, torque limits, moving surfaces, impacts, dynamic stability, angular momentum, inertia, COM trajectory generation, temporal balance enforcement, secondary motion, quadrupeds or a Cascadeur connector. It does not promote the failed temporal research models or establish Cascadeur parity. The mass distribution and support rectangles remain explicitly authored approximations.

## Measured fixture results

Margins are internal world length units. COM and contact errors are normalized by the session torso reference. These are one controlled solve per fixture, not cross-hardware guarantees.

| Fixture | Margin before | Margin after | COM target error | Contact error | Solve seconds | Step p95 ms | Step max ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| boneforge | -0.026466 | 0.004983 | 3.3e-05 | 1.02e-06 | 1.001 | 17.07 | 19.78 |
| rigify_basic | -0.048744 | 0.004971 | 5.68e-05 | 4.91e-06 | 2.027 | 29.67 | 78.34 |
| rigify_default | -0.048744 | 0.004971 | 5.68e-05 | 4.91e-06 | 3.078 | 47.01 | 150.51 |
| metarig_basic | -0.048362 | 0.004970 | 5.94e-05 | 2.39e-06 | 0.690 | 11.63 | 13.85 |
| metarig_default | -0.048362 | 0.004970 | 5.94e-05 | 2.39e-06 | 0.777 | 12.62 | 24.96 |

The default-Rigify window test measured 82 solver checkpoints: p95 44.58 ms, maximum 183.27 ms. This is cooperative click-to-solve interaction, not continuous real-time posing. The long initialization checkpoint and complex-rig cost remain optimization work. Test and UI processes overlapped with other regressions, so these are observed host timings rather than isolated latency bounds.

## Final package validation

`releases\b4artists_ml_v0.12.0.zip` contains 30 files and 222,184 bytes. SHA256: `8f1231927cb0f725b85446df538c3ac38de02d8e40deed5ae6f62586312b60b8`. All members match the final source. The exact package passed 168 regression tests across 14 host suites (158 package-entry tests, 10 tests using identical source), 12 pure numerical tests, and the real-window modal workflow. There were no skipped tests. Host shutdown remained abnormal as recorded above. No files were committed or pushed; trained models, Ghost Tool and Anim Assist remain unchanged.
