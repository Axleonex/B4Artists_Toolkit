# Rigid-segment angular inertia in 0.22.1

Experimental 0.22.1 replaces the airborne point-mass-only measurement with a finite rigid-segment approximation. Each of the existing 17 artist-mass segments is represented as a solid ellipsoid whose local Y axis follows its evaluated endpoints. The evaluated bone X axis supplies the roll reference, so axial twist contributes to measured angular momentum. The mass panel now exposes **Inertia Radius**, an artist-editable ellipsoid radius divided by evaluated segment length.

The solver measures both COM-relative orbital momentum and intrinsic segment spin. It adds each rotated segment tensor to the whole-body inertia tensor, solves a constant world-angular-momentum target, and applies the same source-safe rigid motion-layer correction used in 0.21. Takeoff and landing orientation remain exact, the correction remains capped at 35 degrees, and a correction that worsens total measured variation falls back to identity. The native result remains editable quaternion, COM-pivot and translation curves.

This is a finite-volume rigid-segment estimate. Default masses, center fractions and radii are artist-facing starting values rather than scanned anatomy. The model does not infer density from a mesh and does not solve joint torque, external forces, collision impulse, drag, soft tissue or secondary motion. Rotation increments above 180 degrees between quarter-frame samples are outside the measurement contract. Animator inspection remains required.

## Measured result

The final same-hash source manifest is `training/b4artists_ml/results/rigid-segment-full-v3-regression.json`: 46 Bforartists suites and 441 tests pass with one runtime hash. New checks prove axial spin when segment centers are stationary, proper segment frames, quadratic inertia scaling, invalid-input rejection, artist-radius persistence across save/reload, mid-solve invalidation, and real BoneForge/Rigify behavior.

On the qualified airborne fixtures, total rigid-segment angular variation falls by 88.59% for BoneForge and 87.05% for generated Rigify default. Spin variation falls from `0.0006798` to `0.0003343` on BoneForge and from `0.0051516` to `0.0022305` on Rigify. Maximum displayed COM error is `1.07e-6` body units, relative basis error is `2.14e-7`, and rigid-position error is `1.40e-6`. The combined Rigify C2 case retains normalized acceleration jumps of `0.0234` and `0.0198`.

The deterministic archive is `releases/b4artists_ml_v0.22.1.zip`, SHA-256 `6fa8951ed175251e490aaba38cea81b76905f9e0b52d4d90d56febbbd0be5085`. Its extracted bytes pass 18 offline-guarded tests with no outbound calls. The visible exact-package workflow passes Escape cancellation, generation, Undo/Redo, Keep, Restore Source, reopen and Discard in 119 cooperative steps. Callback p95 is `41.29 ms`; the maximum is `54.42 ms`, so p95 responsiveness passes on this machine while an absolute all-callbacks-under-50-ms claim does not. The host still exits through the known `ucrtbase.dll` shutdown crash after writing passing evidence.

Independent animator review, anatomical calibration, long/high-spin production motion, forces, collision, dynamic contact balance, secondary motion, accepted learned temporal motion, quadrupeds and matched Cascadeur evaluation remain open.
