# Static planar collision response in experimental 0.23.0

## Animator workflow

Choose **Native Motion Layer** for an airborne interval. Under **Static planar collision**, raise **Collision Response** above zero and set **Collision Clearance**. The response uses the same explicit support plane or optional static planar mesh selected for contact tools. The authored plane normal defines the allowed side; a mesh normal is oriented against scene gravity. Zero remains the default and reproduces the existing flight workflow.

**Preview COM Flight** publishes a separate set of editable linear translation curves on the native motion instance. Escape, Restore Before Flight, Undo/Redo, Keep, Restore Source, saved-result reopen and Discard retain their existing behavior. Root Curves rejects a nonzero collision setting rather than silently ignoring it.

## Model and composition

The solver represents each of the 17 editable mass segments as a finite solid ellipsoid. Evaluated segment length, orientation and **Inertia Radius** determine its plane support extent. At quarter-frame-or-finer samples, the solver predicts the gravity-corrected COM and any angular-momentum rotation, measures the deepest segment penetration, and translates the complete displayed character along the plane normal. A reported interpolation margin of 0.0005 evaluated trunk lengths covers between-key linear interpolation; verification repeats at a 0.137-frame phase offset.

The response composes with gravity influence, finite-segment angular momentum, velocity transitions and C2 acceleration matching. Its endpoint correction is exactly zero. A required endpoint correction above 0.0002 trunk lengths is rejected because authored priority poses own those frames.

## Current evidence

- `test_b4artists_ml_collision_math.py` covers plane normalization, ellipsoid orientation/radius effects, full and partial strengths, bounded-surface masks, invalid inputs, BoneForge and Rigify-default host workflows, source-safe cancellation, Root Curves rejection, combined angular/C2 execution, editable curves, and Keep/save/reload/reopen/Discard.
- The adjacent real-host regression ran 61 flight, native-layer, contact, momentum and collision tests with zero assertion failures.
- `native-ui-collision-package-v1.json` records an exact-package real-window Rigify-default journey with Escape, generation, Undo/Redo, Keep/Restore Source, reopen and Discard. Combined angular/C2/collision callbacks measured 40.65 ms p95 and 54.56 ms maximum across 169 steps on the recorded Ryzen 7 5800XT host. The authored test obstruction measured 0.007516 world units of penetration before response and zero at the shifted verification samples afterward.
- The installed Bforartists build still exits in `ucrtbase.dll` after writing passing reports, as it does in the established empty-host control. This is not a clean process exit.

The final same-hash regression passes 448 tests across 47 suites. The deterministic 45-file archive has SHA-256 `ce19e2316357a4f28c970785be5c507f5f0bf856c92a05955a5be2cf9f6fd83c`; 25 exact-package tests pass with the outbound-call guard active and every add-on module loaded from the extracted archive. Package metadata is recorded in `package-test-v0.23.0.json`. Callback p95 is below 50 ms, but the 54.56 ms maximum leaves the every-callback target open.

## Limits

This is a deterministic sampled refinement stage, not learned collision intelligence. It handles one static infinite plane or bounded planar mesh and tests bounded participation using each segment center's plane projection. It does not solve arbitrary mesh or self-collision, moving platforms, collision impulses, restitution, friction, joint torques, deformation-volume contact, aerodynamic drag or secondary motion. Partial strength intentionally permits a measured residual penetration. The ellipsoid radii and mass distribution are animator estimates rather than anatomical measurements.

The implementation closes only the first bounded environment-collision slice. Human motion review, production assets, continuous-time collision guarantees, learned temporal motion and matched Cascadeur comparison remain open. The overall project goal is still active.
