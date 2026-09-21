# Secondary Motion Velocity Impulse v1

Status: verified development feature; full product goal remains active.

This development 0.37.0 feature adds one animator-authored world-space velocity change at a chosen frame. It gives selected location controls a directional kick and lets the existing stable secondary follower, damping, gravity, wind, external acceleration, and planar collision evolve the following samples. The result is deterministic procedural physics with ordinary editable keys. It is not a learned model, a collision-derived impact, a general force/torque solver, or evidence of Cascadeur parity.

## Animator workflow

1. Generate or reopen an animation candidate and select pose controls with complete editable location curves.
2. In Secondary Motion, choose **World** and enable **Location**.
3. Set **Velocity Impulse** in scene units per second and set **Impulse Frame**. `(0, 0, 0)` disables the impulse. Each velocity axis is bounded to `-100..100`.
4. Click **Preview Secondary**, inspect or edit the linear keys, then use Restore Input, Keep, Discard, or Restore Source through the existing candidate lifecycle.

The impulse changes solver velocity at its exact sampled frame. Its position at that frame remains unchanged; the new velocity affects the following step. A fractional frame inside the candidate is inserted into the solver samples exactly. Existing priority-envelope rules keep every captured priority pose exact, including an impulse placed on a priority pose.

A zero impulse preserves the previous solver result and report version exactly. A nonzero impulse uses report schema 6 and backend `implicit_selected_control_secondary_v5`. Earlier zero/wind/external-acceleration combinations retain schemas 3/4/5 and backends v2/v3/v4.

## Admission and recovery

- Nonzero impulse requires World space, Location, complete editable location curves on every selected control, and a finite frame at or after the first priority pose and before the last.
- With a nonzero impulse, malformed, nonfinite, out-of-range, stale, local-space, rotation-only, and out-of-interval requests reject before committed mutation. With a zero impulse, the dormant frame is normalized to `null` and cannot block or contaminate the earlier solver/report path.
- Existing job exclusion, cooperative guards, source fingerprints, Escape cancellation, Restore Input, Undo/Redo, Keep, Discard, and Restore Source remain active.
- Gravity, External Acceleration, Wind Velocity, and Planar Collision retain their existing ordering and can combine with the impulse.

## Verification

- `test_b4artists_ml_secondary_velocity_impulse_v1.py`: 13/13 focused cases pass. Coverage includes temporal placement, exact zero compatibility, dormant hostile-frame normalization, hostile values and indices, priority/collision composition, BoneForge, generated default Rigify, fractional impulse frames, a distinct fractional priority key/world-pose oracle, admission, missing location curves, stale requests, recovery, and report versions.
- `secondary-impulse-affected-v1-regression.json`: 115/115 cases pass across eight suites on one frozen 44-file runtime. SHA-256: `85137691227ff7be66128f8f88e3662b6f5afc22669952c6f788bbb944b8b82e`.
- `secondary-velocity-impulse-ui-v1.json`: a foreground BoneForge journey displays the impulse controls, generates the candidate, and completes native Undo/Redo, Restore Input, Keep, and Restore Source. Its 86 cooperative callbacks measure 9.93 ms p95 and 18.79 ms maximum; maximum evaluated world-location error is `3.58e-7`. SHA-256: `2db74c8869e19a3db888f01d15fbdb4d2b58871de37e6fb3dd7033bb0e839fe4`.
- `secondary-velocity-impulse-ui-v1.png`: visually inspected Bforartists screenshot showing World + Location, zero External Acceleration and Wind Velocity, Velocity Impulse `(3, -1, 0.5)`, and Impulse Frame `6`. SHA-256: `8f62a9723dbf982d623c212495912d8ac83c73d18e412b6c8c47744dc4b74167`.

Each Bforartists child process can exit with the documented `ucrtbase.dll` shutdown fault after its report and assertions finish. The evidence records that ordering and does not claim clean host shutdown.

## Remaining boundary

The impulse is uniform across selected controls and is authored directly rather than derived from collision geometry, momentum transfer, mass, or contact forces. Multiple impulses, per-control mass/force, joint torque, arbitrary/self collision, deformable coupling, learned secondary behavior, production-character review, independent animator evaluation, and the matched Cascadeur protocol remain open.
