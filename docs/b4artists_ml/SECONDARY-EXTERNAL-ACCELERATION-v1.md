# Secondary Motion External Acceleration v1

## Status

This is a verified development feature in B4Artists Machine Learning 0.37.0. It is not included in the frozen 0.36.0 archive and does not change that frozen package.

The feature adds one animator-authored, uniform world-space acceleration vector to selected-control Secondary Motion. It is deterministic procedural physics. It is not a learned motion model, a general force or torque solver, or evidence of Cascadeur parity.

## Workflow

1. Generate or reopen an animation candidate and select one or more controls with complete editable location curves.
2. In Secondary Motion, choose **World** and enable **Location**.
3. Set **External Acceleration** in scene units per second squared. `(0, 0, 0)` disables it. Each axis is bounded to `-100..100`.
4. Optionally combine it with Gravity Influence and Planar Collision, then preview the secondary result.
5. Use Restore Input to change the settings without stacking results. Keep, Discard, Restore Source, native Undo and native Redo retain their existing meanings.

The external vector is applied uniformly to every selected location control:

`effective acceleration = scene gravity * Gravity Influence + External Acceleration`

The existing stable implicit spring integrates that acceleration before the existing planar point-collision response. Boundary and priority-pose envelopes return every captured priority pose exactly to its authored value. Output remains ordinary editable linear action curves.

## Compatibility and failure behavior

- Verified on the BoneForge fixture and a generated default Rigify humanoid.
- World space and Location are required for a nonzero external vector.
- Local mode, rotation-only mode, nonfinite values, malformed vectors and values outside the per-axis bound fail before candidate mutation.
- Changing the vector while a cooperative solve is running invalidates the request and restores the input.
- A zero vector keeps the existing schema-3 `implicit_selected_control_secondary_v2` behavior. A nonzero vector reports schema 4 and `implicit_selected_control_secondary_v3`.
- The feature uses one scene-space acceleration for all selected controls. It does not infer mass, aerodynamic area, control purpose, joint torque, or connected soft-body behavior.

## Verification

- Focused Bforartists: 13/13 tests, including additive gravity equivalence, exact priority samples, planar collision, hostile settings, request invalidation, BoneForge, generated Rigify, restoration, zero-vector compatibility, complete-location admission and ten-owner admission/publication/restore exclusion. Evidence SHA-256: `5e3bb882aac7123070b1753630feb2dd8ed38204e362c921bcc0e57b031fd6d7`.
- Affected Bforartists regression: 91/91 tests across 6 suites on one frozen 44-file runtime set. Evidence SHA-256: `4020ddb4bd0c4a585116b35ef731dfc6d54209bdbc3055a03494fb0dd00b7f30`.
- Foreground Bforartists journey: panel visibility, generation, native Undo/Redo, Restore Input, Keep and Restore Source pass. The qualified 86 cooperative steps measured 10.67 ms p95 and 19.40 ms maximum. Evaluated world-location reconstruction error was below `2.7e-7` scene units. Evidence SHA-256: `10110f816499ee2b14bdcec3bbaa6fe2c575df6414667a774de46d254bf4371c`.
- Foreground screenshot SHA-256: `9ddea0b0d793cabdd31669af379f4533904e11f6f42771b375be12fb5b654a1e`.

The installed Bforartists 5.1 / Blender 5.2 Alpha host still exits through the previously isolated `ucrtbase.dll` access violation after writing passing reports. Assertions completed before shutdown; clean host shutdown remains unqualified.

## Remaining boundary

Per-control force and mass settings, torque, wind fields, drag derived from geometry, moving/deforming surfaces, arbitrary mesh and self-collision, deformable chains, learned secondary behavior, production-character review, independent animator evaluation and the matched Cascadeur protocol remain open.
