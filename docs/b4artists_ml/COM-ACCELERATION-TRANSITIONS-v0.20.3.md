# COM acceleration transitions — experimental 0.20.3

Native Motion Layer now offers **Match COM Acceleration** for each authored airborne interval. When enabled, the takeoff and landing transition curves match both linear center-of-mass velocity and acceleration at the flight boundary. The option is off by default, so existing files and velocity-only results retain their established behavior.

The correction is a deterministic, source-safe three-span C2 cubic spline. It preserves zero displacement, velocity and acceleration at the untouched outer edge; preserves the authored takeoff and landing poses; and writes editable custom-property F-curves on the native motion-layer instance. The published flight F-curve and analytic gravity driver define the boundary target. This avoids matching an ideal curve that differs from the editable result an animator receives.

## Workflow

1. Generate an interpolation candidate and initialize the humanoid mass model.
2. Under **Airborne Motion**, choose **Native Motion Layer**.
3. Add an airborne interval between two authored priority poses.
4. Set transition frames before takeoff and/or after landing.
5. Enable **Match COM Acceleration**, then choose **Preview COM Flight**.
6. Inspect the reported boundary speed and acceleration jumps. Keep, restore, discard or edit the generated native curves as usual.

Acceleration matching is rejected when the transition crosses another priority, flight or held/blended contact. Cancellation, input changes, object/rig changes and playhead changes retain the existing fail-closed recovery behavior.

## Evidence

The source runtime passes 432 tests across the exact current 45-suite manifest. All suites use one runtime hash set. Each Bforartists process wrote its complete assertion result before the known post-result `ucrtbase.dll` shutdown crash; clean host shutdown remains unqualified.

The BoneForge source fixture reports:

| Boundary | Acceleration jump before | Acceleration jump after | Velocity jump after | Maximum COM fit error |
| --- | ---: | ---: | ---: | ---: |
| Takeoff | 9.8250 | 0.0688 | 0.000258 body units/s | `1.48e-7` |
| Landing | 9.8126 | 0.0129 | 0.001682 body units/s | `1.08e-7` |

The exact 0.20.3 archive passes all 10 momentum/math/host tests with outbound Python networking and process launch denied inside the add-on process. Every imported `b4artists_ml` module resolves to the extracted archive.

The exact-package real-window Rigify-default journey passes Escape cancellation, completed generation, Undo/Redo, Keep, Restore Source, saved-result reopen and Discard. Its takeoff/landing acceleration jumps fall from 9.6505/9.9064 to 0.0143/0.0202 body units/s²; velocity jumps are 0.000197/0.001490 body units/s; maximum COM fit error is below `7.5e-8`. The journey completes in 3.24 seconds across 47 cooperative steps. Step p95 is 54.4 ms and maximum is 70.6 ms, so the broader sub-50 ms responsiveness gate remains open.

Archive: `releases/b4artists_ml_v0.20.3.zip`  
SHA-256: `b648111fb38e5e37f8dfa12dd6e2d0006af4ca15f6ef984a0405e14ed9b1f193`

Evidence:

- `training/b4artists_ml/results/momentum-c2-full-v2-regression.json`
- `training/b4artists_ml/results/momentum-c2-v12-acceleration-host.json`
- `training/b4artists_ml/results/momentum-c2-package-v1.json`
- `docs/b4artists_ml/native-ui-momentum-c2-package-v1.json`
- `docs/b4artists_ml/package-test-v0.20.3.json`

## Claim boundary

This is translational COM boundary refinement. It does not estimate forces, conserve full-body angular momentum, solve collisions, add secondary motion or qualify learned temporal generation. Independent animator review, quadrupeds and the matched Cascadeur comparison remain open. The full goal remains active and incomplete.
