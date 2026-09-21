# Multiple static spherical colliders v1

Status: verified development 0.37 source and exact v0.37.38 archive; deterministic sampled control-pivot exclusion, not learned motion or a general rigid-body solver.

## Animator workflow

In **Secondary Motion**, choose **World**, enable **Location** and **Collision**, then set **Shape** to **Sphere**. The existing **New Sphere Center** and **New Radius** fields stage one collider. Click **Add Sphere to Set** to copy it into the persistent list. Repeat for up to eight different unparented, unanimated, non-rigid-body scene objects. Each list row keeps its own explicit radius and can be edited or removed; **Clear Sphere Set** returns to the legacy staged single-sphere behavior.

Clearance expands every excluded radius. Bounce reflects inward radial speed and Friction removes tangential speed at a sampled contact. The center object's geometry, display size, rotation and scale do not set its radius.

The solver retains the input Action, publishes ordinary editable location curves, preserves every captured priority pose, and reports the complete collider list, contact count, raw penetration, desired-array penetration and evaluated published-pivot penetration. Adding or removing a list item supports native Undo/Redo, the list survives save/reload, and the existing Preview, Escape, Restore Input, Keep Candidate and Restore Source lifecycle remains intact.

## Algorithm and safety boundary

The implicit selected-control follower validates and canonically sorts one to eight center/radius pairs for deterministic math. At every participating sample, it repeatedly projects the deepest remaining penetration to radius plus clearance, with a bounded iteration count. The final influence pass repeats exclusion after blending. If the bounded projection cannot produce a point outside every sphere, the solve rejects instead of publishing a partial result.

Every center must belong to the active scene, be distinct, and remain free of parenting, constraints, Actions, drivers, NLA tracks and rigid-body simulation. Every list radius must be finite, bounded, unkeyed and undriven. A complete center/radius token is checked while sampling and publishing, so moving any listed center or editing the set during cooperative work cancels and restores the input. A priority pose inside any excluded volume rejects before publication. The single staged sphere retains report schema 9/backend v8; two or more listed spheres use schema 10/backend v9. Planar collision retains its earlier path.

## Verification

- Focused Bforartists 5.2 Alpha qualification: 8/8, zero failures, errors or skips. Coverage includes overlapping-sphere order independence, bounded hostile input and empty-mask handling, add/duplicate/remove/clear operations, one-step native Add Undo/Redo, save/reload persistence, keyed and driven list-radius rejection, second-center mutation cancellation, second-sphere priority conflict rollback, and complete BoneForge/generated Rigify Default workflows. The receipt binds the complete transitive fixture chain. Evidence: `training/b4artists_ml/results/secondary-multi-sphere-focused-v1.json`, SHA-256 `c21a10a9b9ccea4fa98ac5ef548cec402c6bc349d9bbcd88efc1b81eef7269b7`.
- Affected regression: 172/172 across 13 suites on one frozen 44-file runtime set. It includes the unchanged 13-test one-sphere suite and every affected secondary-motion, force/load, chain, visible-state and registration/recovery suite. The multi-sphere child and aggregate both bind its four transitive fixture sources. Evidence: `training/b4artists_ml/results/secondary-multi-sphere-affected-v1-regression.json`, SHA-256 `9de03dd7a4241a4c29da41db5cde2fb61a8fb9ca5c93774e0b8c4ebdcbae48e5`.
- Foreground BoneForge journey: two visible editable sphere rows, modal solve, three contacts, 0.035118090334440966 maximum raw penetration, 9.71445146547012e-17 desired-array penetration and 4.548495677325626e-08 evaluated published-pivot penetration under the 1e-6 tolerance. Native Undo/Redo, Restore Input, synchronous regeneration, Keep and Restore Source pass. Across 86 cooperative callbacks, p95 was 10.76 ms and maximum was 18.26 ms. The UI receipt binds the complete transitive fixture chain. Evidence: `docs/b4artists_ml/secondary-multi-sphere-collision-ui-v1.json`, SHA-256 `286aed36ec7192b992cdcf18e5e95a96db1bcbbf51c23a32e3b6a67808e02455`.
- Foreground screenshot: `training/b4artists_ml/cache/secondary-multi-sphere-collision-ui-v1.png`, SHA-256 `bb3b00de6e4f3809f2ddbfda877c2bc21d06bf369c8f6c214206c62bf67a2762`.
- Exact v0.37.38 archive binding: 8/8, zero failures, errors or skips, including BoneForge and generated Rigify Default, persistence, rollback, order independence and bounded hostile-input checks. Evidence: `training/b4artists_ml/results/exact-package-v0.37.38-test_b4artists_ml_secondary_multi_sphere_collision_v1.json`; the receipt binds the archive SHA-256 `9858e537f722d9ec8f0ef9fc45d2a1f3d52a2153f5020e3f7568c9361757321e`.

All Bforartists processes completed assertions and wrote fresh source-bound reports. The known host shutdown access violation remained afterward, so clean shutdown is not claimed.

## Limits

Collision applies to selected control pivots at sampled frames. This slice does not derive bone or mesh volume, use arbitrary or deforming mesh geometry, support moving, parented, constrained or animated spheres, guarantee continuous-time collision, transfer collision impulses or torque through joints, detect self-collision, infer physical properties, learn motion, establish independent animator quality, or demonstrate Cascadeur parity.
