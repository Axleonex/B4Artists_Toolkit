# Native motion layer investigation and standalone validation

The user authorized six additional goalpost evaluations and up to four additional hours. The same goal ID, original endpoint, history, regression floors and acceptance thresholds remain. The extension state retains six evaluated rounds and permits up to twelve total. The existing no-progress limit is unchanged.

## Native trajectory evaluation

The existing release remains experimental 0.13.1. All work below is confined to diagnostic scripts, saved test scenes and evidence. No production motion-layer adapter, installation, commit or push was added.

An isolated 240-frame parabola comparison reproduced native Bezier acceleration error p95 0.52875 and polynomial-generator error 0.315 world units/s?. Formula drivers and a dense-linear diagnostic control reached 0.0365625. Dense linear sampling is not a smooth interpolation solution and was not promoted.

Splitting a small pose-COM residual curve from an analytic gravity driver on a character collection instance preserved the evaluated Rigify bone basis and mesh. Default driver remapping keys snapped positive residuals below approximately 0.0001 to zero in this fixture. Removing those generated driver keys corrected that prototype error. This is not evidence of a released-product driver bug: the release does not use this approach.

| Case | Residual spacing | COM error / trunk | Acceleration error p95 | Existing gates |
|---|---:|---:|---:|---|
| Transformed default Rigify, 240 frames | 4 frames | 6.70e-6 | 0.101289 | Acceleration fails |
| Transformed default Rigify, 60 frames | 4 frames | 4.48e-5 | 0.480118 | Acceleration fails |
| Transformed default Rigify, 60 frames | 0.5 frames | 1.10e-6 | 0.017102 | Sampled geometry and acceleration pass |

The passing 60-frame fit took 0.868 seconds for the fit phase only. It uses 121 residual keys per axis, with maximum relative bone-basis error 8.99e-8 and normalized mesh error 9.08e-7. These are fixture measurements, not production UI latency claims.

A separate saved-scene validation with add-on absent and script auto-execution disabled passed both ordinary quarter-frame samples and quarter-frame samples shifted by 0.137 frames. The shifted acceleration error p95 was 0.027668, below the unchanged 0.1 limit. COM error stayed below 1.46e-6 of trunk length. Out-of-order seeking and saved playback had zero sampled geometry differences.

Driver RNA simple-expression flags remained false even after evaluation. The initial verifier incorrectly required that introspection flag and stopped before playback; its failure is preserved. The corrected verifier measures actual native playback with explicit auto-execution settings and reports the flags separately. This result does not certify arbitrary driver expressions or resolve the flag semantics.

The 240-frame case still fails. No threshold, sample spacing in the acceptance gate, or rig-preservation requirement was relaxed. Reports whose `passed` field covers setup/geometry must not be interpreted as a physics pass; consult `acceleration_budget_pass`.

## Standalone core evidence

54 existing tests across seven workflow groups passed against an extracted, byte-verified copy of the final v0.13.1 release while Python networking and subprocess launches were denied. Coverage includes the host guard, source-preserving interpolation, learned limb inference, whole-body preview/keep/cancel/reload, contact correction, COM/support, learned balance and flight on actual fixture rigs.

The dependency inventory contains only standard-library modules, host bpy/mathutils and NumPy; no dynamic exec/import calls were found. The only direct bpy operator call in runtime code is object.mode_set. The unsupported-host preferences panel has an explicit Get Bforartists browser link. Test fixture builders are source-scene preparation dependencies, not imports of the distributed core. This verifies current core independence, not implementation of missing product features or an OS firewall boundary.

The support test selector initially named a nonexistent class. That harness failure is retained; the corrected six-test SupportRigTests group passed. The other groups did not need to be rerun. STANDALONE-OFFLINE-v0.13.1.json records exact artifacts and hashes.

All host processes still exit with 3221225477 after assertions, matching the existing alpha-host shutdown issue. Supported-host lifecycle acceptance remains failed.

## Next coherent implementation

Before exposing a native motion layer, validate ownership and visibility of the original rig, associated meshes and generated collection instance. The original and instanced meshes are currently both visible. Verify selection and world-space posing against the moved result, source collection/view-layer membership, contact/support coordinates, external drivers and constraint targets, and multi-character isolation. Then integrate cancellable regeneration, Keep/Discard, Undo/Redo, save/reload, source restoration and editable export. These are required parts of one user workflow, not optional cleanup after enabling a preview button.

Use adaptive residual fitting against unchanged geometry and acceleration gates. Keep the long-flight failure visible until resolved. The source rig must continue evaluating near its original coordinates; merely translating the armature object or changing its constraint spaces did not solve the measured precision problem.

Actual learned temporal motion, broader humanoid/imported coverage, quadrupeds, momentum transitions, secondary motion, production performance, independent animator usability, the optional entitlement-aware connector and equivalent Cascadeur comparison remain part of the original goal. No parity or superiority claim is supported by this milestone.
