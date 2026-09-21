# Explicit physical context and gravity-direction learning v4

Status: the gravity input alias is fixed in the research interface. Learned quality remains below acceptance gates. Release 0.10.0 is unchanged and the overall goal remains active and incomplete.

## Physical context contract

`environment_context.py` introduces immutable `Environment` and `SupportPlane` values. Gravity is either an explicit acceleration vector, a direction-only hint, or unknown. Known zero acceleration is distinct from unknown acceleration. Support is an explicitly supplied static plane; no plane or contact is inferred from hidden foot positions.

`encode_environment(environment, origin, basis, length_scale, duration)` reads only the known anchor frame and explicit world context. It validates finite inputs, positive length/time and a proper orthonormal basis. Its 11 values are:

| Index | Meaning |
|---|---|
| 0-2 | Gravity direction in anchor coordinates, or zero if unavailable |
| 3 | Dimensionless acceleration magnitude: norm(g) * duration squared / length_scale |
| 4 | Gravity direction is known |
| 5 | Acceleration magnitude is known, including explicit zero |
| 6-8 | Explicit support-plane normal in anchor coordinates |
| 9 | Signed anchor height above the plane, divided by length_scale |
| 10 | Support plane is known |

A coordinate change rotates gravity, support and character together and preserves the encoding. Physically tilting a motion while gravity stays fixed changes its encoding. This addresses the V3 alias directly. Rescaling coordinate length and time units transforms acceleration accordingly, preserving dimensionless features. Physically resizing a character while keeping real gravity/time fixed is a different operation and appropriately changes normalized acceleration strength.

`from_scene(scene, support=None)` reads Bforartists' current raw scene gravity, respecting `use_gravity`. It does not rewrite scene properties or multiply by display unit scale. The [official scene-unit documentation](https://docs.blender.org/manual/it/latest/scene_layout/scene/properties.html) distinguishes internal quantities from UI unit conversion; current English manual/API direct fetches failed, but the official indexed manual and actual host property checks were available. `timeline_seconds` handles fractional frame intervals and fps_base explicitly. These are context snapshots, not a simulator or support for animated forces/time-remapping.

`free_flight_points` implements the constant-acceleration path between two supplied point positions. It preserves endpoint values and has the supplied acceleration. It requires a known acceleration magnitude; a direction hint cannot silently supply an Earth-gravity value. A pelvis is not automatically a center of mass. This helper does not infer mass distribution, apply a trajectory to a rig, preserve arbitrary incoming momentum, detect collisions, solve contact transitions, or claim completed character physics.

## Learned conditioning and data limits

`environment_data.py` attaches environment context to existing temporal windows using their original known anchor frames. Static source rest orientation is checked against the declared Y-up convention. This is an explicit conversion-axis assumption, not a measured gravity vector, ground plane or contact label. Acceleration magnitude and support remain unknown for training.

The learned variant consumes only gravity direction and its known mask, adding four values to the existing 637 pose/rest/time features. It does not learn gravity-strength or support-plane effects. Unknown/zero direction is rejected by this direction-conditioned model instead of inventing a default direction; the physical-context API itself supports known zero acceleration.

V3's selected nonlinear kernel settings remain fixed: width 0.25 and regularization 10. Four preregistered gravity-feature weights (0.5, 1, 2, 4) are compared. Width is adjusted by sqrt(637/641) so the original feature-distance denominator is unchanged. A unit test verifies the zero-added-information control mathematically. The frozen V3 learner is both the initial incumbent and an added strong baseline. Training uses the same 23 clips, validation the same 6 clips, and old development the same 3 clips. No new raw assets, packages or paid compute are used.

The selected gravity weight is 4.0. The saved model is genuinely nonzero and consumes the supplied direction. It still uses supervised kernel regression of articulated temporal coefficients, not a neural network. The shared report's legacy `mlp` slot denotes this selected candidate, not its architecture.

## Quality outcome

| Validation method | Position error | Rotation error (rad) | Velocity error |
|---|---:|---:|---:|
| linear | 0.099178 | 0.132492 | 0.619511 |
| fk_linear | 0.100869 | 0.133288 | 0.624428 |
| v3_control | 0.097331 | 0.129574 | 0.601110 |
| V4 selected gravity learner | 0.097044 | 0.129109 | 0.599977 |

Position error improves by approximately 0.30% over V3 and 2.15% over world-position linear interpolation. This is a marginal validation gain, not evidence of substantially improved animator quality. The 5% position-improvement and per-cohort gates still fail. The worst validation cohort remains 3.16 times its strongest baseline's position error. Observed-development position error remains approximately 17.45% worse than its strongest baseline, with a failed velocity gate too. Those clips are not fresh confirmation.

Recorded endpoint position errors stay below 2.7e-15 normalized distance; true source-edge length errors stay below 8.4e-16. Fixing missing gravity orientation is necessary for gravity-aware conditioning, but it does not alone establish gravity-aware character motion, plausible transitions, style preservation or generalization.

## Verification and measured scope

14 new tests cover the physical-tilt distinction, coordinate/length/time-unit invariance, known zero versus unknown gravity, direction-only limitations, explicit support height/normal, hidden-label isolation, free-point acceleration/endpoints, read-only scene semantics, fractional frame timing, invalid frames/vectors/bases, kernel denominator control and actual model consumption of gravity direction. Together with 38 prior temporal tests, 52 standalone tests pass with exit 0 and no skips.

Bforartists core 5.2.0 Alpha / NumPy 2.3.4 passes all 14 new tests and these real scene checks:

- Raw acceleration and disabled-gravity semantics.
- Unchanged internal acceleration when display unit scale changes.
- fps_base and fractional frame conversion.
- Y-up source coordinates converted to Z-up scene coordinates, including consistent gravity-conditioned inputs.
- Nonzero learned inference with preserved endpoints and edge lengths.
- Constant-acceleration free-point sampling using the actual scene acceleration.
- Complete restoration of changed factory-scene test settings.

The host then reports its previously observed ucrtbase.dll shutdown access violation, exit 3221225477. Assertions passed; the process did not exit cleanly. These checks do not apply learned motion to actual BoneForge/Rigify animator controls or a bound mesh, and do not establish a user-facing COM/physics workflow.

Four candidate fits and recorded evaluations took 28.24 seconds, using four OpenBLAS threads, Python 3.14.3, NumPy 2.4.4. Selected model size is 16,619,471 bytes. In a fresh standalone process, loading took 82.48 ms; a 33-frame prediction plus FK took 5.54 ms on its first call and warm p50/p95 4.68/5.85 ms. Peak process working set was 66,351,104 bytes. This excludes Bforartists, actual control-rig fitting and viewport rendering.

## Reproduction and evidence

```powershell
# [PowerShell]
$env:OPENBLAS_NUM_THREADS='4'
python -B tests/test_b4artists_ml_environment.py
python -B tests/test_b4artists_ml_motion_coverage.py
python -B tests/test_b4artists_ml_sequence.py
python -B tests/test_b4artists_ml_temporal.py
python -B -u training/b4artists_ml/train_gravity_motion.py --output gravity_motion_reproduction
```

This reproducer requires the existing pinned motion cache and frozen V3 control model/report; use a new output name. `results/gravity_motion_v4/` contains the protocol, source/model hashes, per-candidate and per-cohort reports, scene/host records, inference benchmark and reproducibility record. A fresh repeat exited 0 with identical selected/best-gravity weight files and identical validation/development results. Repetition is replication, not fresh blind evidence.

Earlier CMU/conversion provenance, dataset limitations and acknowledgment requirements remain as documented in TEMPORAL-MOTION-v1.md through TEMPORAL-MOTION-v3.md. Source-frame initialization is excluded from motion targets. There are no newly bundled weights, no new installed add-on, and no publication in this pass.

## Next coherent work

Actual-rig center-of-mass and support analysis is now the useful next physical step. It must use an explicit, inspectable mass model and authored contacts, distinguish a character's pelvis from its COM, preserve the source rig/animation, and be tested on real BoneForge/Rigify rigs and meshes. The context and free-flight helpers are prerequisites, not substitutes for that workflow.

Learned-motion data coverage, a genuinely untouched evaluation split, canonical cross-rig encoding, multi-anchor/partial-body/style conditioning, contact-aware previews, cancellation/recovery and measured animator quality remain required. Gravity/momentum/secondary motion, quadrupeds, the optional separate Cascadeur connector and equivalent Cascadeur comparisons remain in the full goal. No parity or superiority claim is supported.
