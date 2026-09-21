# Selected-Control Force-at-Offset Torque v1

Status: verified development 0.37 source and exact v0.37.38 archive.

## Animator workflow

In Pose Mode, select one or more recognized controls on the active animation candidate. In Secondary Motion, choose World space and enable both Rotation and Location. Set Selected Force, Selected Mass, Application Offset (Local), and Rotational Inertia, then use Assign Load. Preview Secondary creates a copied animation candidate with ordinary editable location and rotation keys. Clear Load removes assignments from the selection; Clear Invalid Assignments recovers malformed stored data. Native Undo/Redo, Restore Input, Keep, and Restore Source retain their existing behavior.

Force is constant in world space and is expressed in kilograms times scene units per second squared. Mass is in kilograms. The application offset is expressed in scene units in each selected control's authored local orientation. Rotational inertia is a scalar in kilograms times scene units squared. A zero offset applies the existing force-over-mass translation without torque.

## Deterministic model

For every selected loaded control and sample, the solver rotates the local application offset by the authored target world orientation and evaluates:

```text
linear acceleration = force / mass
world torque = rotated local offset x world force
world angular acceleration = world torque / rotational inertia
```

The bounded angular acceleration enters the same implicit damped rotational follower used by world-space secondary motion. Linear force continues through the existing implicit location follower and composes with gravity, external acceleration, wind, velocity impulse, priority envelopes, and planar point collision. Every captured priority pose is written back exactly. The result is converted through the native rig spaces and independently checked against its requested evaluated world transforms before publication.

The host-independent validation limits are 1,000 scene units per offset component, rotational inertia from 0.001 through 1,000,000, and a conservative maximum possible angular acceleration of 100 radians per second squared. Boolean, malformed, nonfinite, out-of-range, wrong-rig, stale, partially editable, driven, locked, or unsupported requests fail before committed animation mutation.

## Compatibility and persistence

Existing schema-1 force/mass records load with an exact zero local offset and inertia 1. Assignments with only those defaults continue to write schema 1 and retain the schema-7 `implicit_selected_control_secondary_v6` solve path. A nonzero offset or nondefault inertia writes the rig-bound deterministic schema-2 record. A configured nonzero force and offset uses solve report schema 8 and backend `implicit_selected_control_secondary_v7`.

Zero angular forcing delegates directly to the original quaternion follower using the original inputs. Focused tests confirm exact array equality. A zero offset with a nondefault stored inertia also produces the same force-only location curves, correction metric, schema, and backend as inertia 1.

## Verification evidence

The 14 focused Bforartists tests cover independent cross-product direction and magnitude, inertia scaling, local-offset rotation, hostile input rejection, exact zero-forcing compatibility, bounded forced rotation, schema-1 compatibility, deterministic schema-2 persistence, clear, save/reload, BoneForge, generated default Rigify, simultaneous translation and rotation, World/Location/Rotation admission, missing-curve rejection, ten foreign workflow owners, stale-request rollback, source preservation, and full candidate recovery.

- `training/b4artists_ml/results/secondary-force-offset-torque-focused-v1.json`: 14/14, SHA-256 `2c465e659e883d3bb512817282f113644f368fbdb2fda9f9beb81cd03107c909`.
- `training/b4artists_ml/results/exact-package-v0.37.38-test_b4artists_ml_secondary_force_offset_torque_v1.json`: exact archive 14/14 receipt; force/mass translation, local-offset torque, inertia scaling, BoneForge/Rigify workflow, persistence, and rollback all pass.
- `training/b4artists_ml/results/secondary-force-offset-torque-affected-v1-regression.json`: 143/143 across ten suites on one frozen 44-file runtime, SHA-256 `ed5400bef2f9d3775b328b1b4a7845295a5ea93e1ea940e80083d72a659137d5`.
- `docs/b4artists_ml/secondary-force-offset-torque-ui-v1.json`: passing foreground assignment, native Undo/Redo, cooperative solve, Restore Input, synchronous solve, Keep, and Restore Source; SHA-256 `d8b113c769a5a3431f15f3f7313ee26e7baa2c9f616b8ac75866aac1320e3a69`.
- `training/b4artists_ml/cache/secondary-force-offset-torque-ui-v1.png`: visible force, mass, local offset, inertia, full assignment actions, and assignment count; SHA-256 `fbdc49047cf7ae3688855ce285469952f782945c9365556b587572a8069b494f`.

The foreground journey completed 96 cooperative steps with 11.7706 ms p95 and 21.7982 ms maximum. Its BoneForge result reports one torque control, 1.9534001 maximum torque, 1.9534001 maximum angular acceleration, `2.6657e-7` maximum world-location error, and zero measured world-rotation error.

Every Bforartists child process may exit with the established `ucrtbase.dll` shutdown fault after the assertions and evidence report complete. The records preserve that ordering and do not claim clean shutdown.

## Claim boundary

This is deterministic force-at-offset refinement on explicitly selected control pivots with animator-authored scalar inertia. It does not infer mass, geometry, anatomy, force points, or inertia. It does not transfer force or momentum through joints, derive impact impulses from collision, solve connected rigid bodies, deformable volume, arbitrary/self/deforming collision, or learned secondary behavior. Production-character review, independent animator judgment, learned motion, matched Cascadeur evaluation, and overall parity remain open.
