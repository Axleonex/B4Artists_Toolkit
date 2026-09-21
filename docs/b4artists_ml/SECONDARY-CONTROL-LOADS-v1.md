# Secondary Motion Per-Control Force and Mass v1

Status: verified development feature; full product goal remains active.

Development 0.37 now lets an animator assign a persistent world-space force and mass to specific pose controls. During World + Location secondary motion, each selected control receives its own `force / mass` acceleration in addition to the existing uniform External Acceleration and scene gravity. Wind-relative drag, a frame-authored velocity impulse, priority preservation, and planar collision keep their established order. The result is deterministic procedural physics with editable keys. It is not a learned model, a torque or general rigid-body solver, or evidence of Cascadeur parity.

## Animator workflow

1. Generate or reopen an animation candidate, enter Pose Mode, and select one or more recognized animator controls.
2. In Secondary Motion, choose **World** and enable **Location**.
3. Set **Selected Force** in `kg * scene units / second squared` and **Selected Mass** in kilograms, then click **Assign Load**. Select other controls and repeat to give them different loads. **Clear Load** removes assignments from the current selection.
4. Click **Preview Secondary**, inspect or edit the resulting linear keys, then use Restore Input, Keep, Discard, or Restore Source through the existing candidate lifecycle.

Assignments are stored on the armature in a strict rig-bound record and survive save/reload. Force axes are bounded to `-1,000,000..1,000,000`, mass to `0.001..10,000`, and the resulting acceleration to `-100..100` per axis. Assignment and clearing are single-step native Undo/Redo operations. A stored zero force may retain its mass assignment but contributes exactly zero acceleration.

A nonzero selected-control load uses report schema 7 and backend `implicit_selected_control_secondary_v6`. Zero or unassigned loads retain the exact earlier schema/backend branch: schema 3/v2, external-acceleration schema 4/v3, wind schema 5/v4, or impulse schema 6/v5.

## Admission and recovery

- Active loads require World space, Location, and complete editable location curves on every selected control. Local space, rotation-only use, unrecognized deform bones, structural bones, missing controls, partial curve groups, locks, drivers, malformed records, nonfinite values, out-of-range values, and wrong-rig records fail before committed mutation.
- The request contains only assignments for the explicit current selection. Changing a participating load while a cooperative solve is running invalidates the request and restores the original candidate.
- The persistent record is deterministically sorted, duplicate-free, bounded to the armature bone count and one MiB, and tied to the exact rig bone signature.
- Existing job exclusion, source fingerprints, Escape cancellation, Restore Input, Undo/Redo, Keep, Discard, and Restore Source remain active.

## Verification

- `test_b4artists_ml_secondary_control_loads_v1.py`: 14/14 focused cases pass. Coverage includes the host-independent `F/m` equation, mass scaling, force/mass/acceleration bounds, deterministic assignment and clearing, corrupt/wrong-rig recovery, BoneForge, generated default Rigify, distinct loads on two independent controls, an independent `External 80 + Load 30 == External 80 + Gravity 30` workflow oracle, exact zero-load versus unassigned output, Pose Mode admission, World/Location admission, missing curves, cooperative stale-request rollback, all ten foreign workflow owners, and save/reload persistence.
- `secondary-control-loads-affected-v1-regression.json`: 129/129 cases pass across nine suites on one frozen 44-file runtime. SHA-256: `45004c618ebb8a21e1845b0ae7e5ae0b35165e2bb52640b7c03715d152019ad0`.
- `secondary-control-loads-ui-v1.json`: a foreground BoneForge journey displays and assigns force/mass, proves one-step assignment Undo/Redo, generates the candidate, and completes solve Undo/Redo, Restore Input, Keep, and Restore Source. Its 86 cooperative callbacks measure 11.14 ms p95 and 20.29 ms maximum; maximum evaluated world-location error is `2.67e-7`. SHA-256: `5593137875bfe87f065e9b9e53f7730d43d5233cc3f77a1f7204d7a754ed16b2`.
- `secondary-control-loads-ui-v1.png`: visually inspected Bforartists screenshot showing World + Location, Selected Force `(6, -2, 1)`, Selected Mass `2`, full-width Assign Load/Clear Load actions, and one assigned load. SHA-256: `d894b2a43a2df91d0cba027ca601cb68fc88cf952e9f4dbe7fc7dbd467fb1d3c`.

Each Bforartists child process can exit with the documented `ucrtbase.dll` shutdown fault after its report and assertions finish. The evidence records that ordering and does not claim clean host shutdown.

## Remaining boundary

This milestone applies constant animator-authored forces to selected control pivots. The later development-source extension in `SECONDARY-FORCE-OFFSET-TORQUE-v1.md` adds explicit local application offsets and scalar-inertia angular acceleration. Neither milestone infers mass or inertia from anatomy or geometry, transfers momentum between controls, derives impact forces from collision, solves arbitrary/self/deforming collision, or provides a coupled deformable-body simulation. Learned secondary behavior, production-character review, independent animator evaluation, and the matched Cascadeur protocol remain open.
