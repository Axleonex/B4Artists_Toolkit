# Secondary Motion Wind Velocity v1

Status: verified development feature; full product goal remains active.

This development 0.37.0 feature adds a uniform world-space air velocity to selected-control Secondary Motion. Air Friction now damps selected-control velocity relative to the authored wind velocity. The result is deterministic procedural physics with ordinary editable keys. It is not a learned motion model, geometric aerodynamics, a force/torque solver, or evidence of Cascadeur parity.

## Animator workflow

1. Generate or reopen an animation candidate and select pose controls with complete editable location curves.
2. In Secondary Motion, choose **World** and enable **Location**.
3. Set **Air Friction** above zero and set **Wind Velocity** in scene units per second. `(0, 0, 0)` disables wind. Each axis is bounded to `-100..100`.
4. Optionally combine it with Gravity Influence, External Acceleration, and Planar Collision.
5. Click **Preview Secondary**, inspect or edit the linear keys, then Keep, Restore Input, Discard, or Restore Source through the existing candidate lifecycle.

The implicit velocity step uses the existing spring and damping terms plus:

`air drag acceleration = Air Friction * (Wind Velocity - control velocity)`

The existing denominator retains the implicit `Air Friction * control velocity` term. The numerator adds the constant `Air Friction * Wind Velocity` forcing term, whose magnitude is reported separately from the varying relative-drag acceleration. A zero wind vector therefore preserves the earlier solver result exactly; nonzero wind uses report schema 5 and backend `implicit_selected_control_secondary_v4`. Zero wind retains schema/backend v2 or v3 according to whether External Acceleration is active.

## Admission and recovery

- Nonzero wind requires World space, Location, positive Air Friction, and complete editable location curves on every selected control.
- Malformed, nonfinite, out-of-range, stale, local-space, rotation-only, and zero-friction wind requests reject before committed mutation.
- Priority poses remain exact. Existing planar point collision runs after the wind-relative velocity update.
- Admission, cooperative publication, Restore Input, Escape, Undo/Redo, Keep, Discard, and Restore Source retain the existing exclusive workflow ownership and source-action recovery contracts.

## Verification

- `test_b4artists_ml_secondary_wind_velocity_v1.py`: 11/11 focused cases pass. Coverage includes the relative-drag equation, exact zero-wind compatibility, validation, gravity/external-acceleration/collision composition, BoneForge, generated default Rigify, admission, all-rotation-only and mixed-selection location-curve rejection, stale requests, editable result recovery, and report versions.
- `secondary-wind-affected-v1-regression.json`: 102/102 cases pass across seven suites on one frozen 44-file runtime. SHA-256: `b0a6a79d194f8708e3c42c9db099ec22d31211eccc0f0612852d9abad499ca69`.
- `secondary-wind-velocity-ui-v1.json`: the foreground BoneForge journey displays Wind Velocity, generates the candidate, and completes native Undo/Redo, Restore Input, Keep, and Restore Source. Its 86 cooperative callbacks measure 10.35 ms p95 and 21.69 ms maximum; maximum evaluated world-location error is `2.67e-7`. SHA-256: `4ca2bdff7a4d0179b5a5519bffa53766e388e2808050f6ca4e23c00647b2f703`.
- `secondary-wind-velocity-ui-v1.png`: visually inspected Bforartists screenshot showing World + Location, Air Friction `0.80`, zero External Acceleration, and Wind Velocity `(3, -1, 0.5)`. SHA-256: `7d7dcdaa0ff0880d1680fbd002849a30d9e9b1de794d5e1a57a4f263adf704e6`.

Each Bforartists child process can exit with the documented `ucrtbase.dll` shutdown fault after its report and assertions finish. The evidence records that ordering and does not claim clean host shutdown.

## Remaining boundary

The wind is uniform for every selected control. The solver does not infer surface area, drag coefficient, mass, local gusts, turbulence, joint torque, deformable-body coupling, or arbitrary/self collision. Per-control forces and masses, torque, broader collision, learned secondary behavior, production-character review, independent animator evaluation, and the matched Cascadeur protocol remain open.
