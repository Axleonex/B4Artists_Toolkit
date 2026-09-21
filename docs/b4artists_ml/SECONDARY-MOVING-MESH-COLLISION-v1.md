# Secondary moving mesh collision v1

Development 0.37.14 adds opt-in direct object-transform animation to the triangle-mesh collision path. An unparented mesh with a direct Action on Location, Rotation, or Scale can be sampled at every secondary solve frame. Optional direct shape-key deformation can be combined with that object motion; modifiers, parents, constraints, drivers, NLA, rigid-body state, and unrelated Action data fail closed.

When Continuous-Time Sweep is enabled, the existing bounded eight-substep interpolation checks both selected-control motion and the evaluated mesh trajectory between adjacent samples. Closed meshes remain required for continuous mode. The solver keeps the existing priority-pose conflict policy and final evaluated clearance verification, then publishes normal editable rig curves. Moving mesh trajectories use schema 20 and the backend `implicit_selected_control_secondary_continuous_moving_mesh_v1` (with corresponding moving/deforming and moving-volume variants). A Closed Volume trajectory now has a separate schema-22 bounded finite-volume path; it evaluates the exact static swept-sphere kernel at each bounded interpolated mesh state and reports that bounded contract explicitly.

## Evidence

- Focused host math: 32 tests, 0 failures/errors/skips.
- Exact archive: `releases/b4artists_ml_v0.37.16-dev.zip`, SHA-256 `dc1811697f736ed9e87af4a949bb1fe985acfb296e71dcd587b85a86d53b1325`.
- Exact-package Bforartists binding: 3/3 in 4.663 seconds, including combined direct object motion plus direct shape-key deformation and an unrelated-Action-data rejection.
- Exact-package affected secondary regression: 158/158 in 228.078 seconds, 0 failures/errors/skips.
- Foreground archive journey: schema 20, 11 evaluated mesh samples, zero final penetration, Escape cancellation, native Undo/Redo, save/reload, and Restore Source all passed.
- The Bforartists 5.2 Alpha process still reports the known post-result `ucrtbase.dll` shutdown access violation; assertions and durable reports complete before that fault.

This is deterministic evaluated procedural geometry. It is not exact
moving/deforming swept-sphere distance, a coupled rigid/deformable-body solver,
learned temporal motion, independent animator usability evidence, or a
Cascadeur comparison. Static Closed Volume exact distance is a separate
schema-21 slice.

## Bounded moving/deforming finite-volume extension

Development 0.37.18 adds schema 22 for Continuous-Time Sweep plus Closed
Volume when the mesh is directly moving, shape-key deforming, or both. The
selected control keeps its authored radius plus clearance. Each of the bounded
interpolation intervals calls the exact static segment-to-filled-triangle
volume kernel against the interpolated interval-end mesh. This catches finite
volume contacts that a centerline-only moving/deforming sweep would miss, while
remaining explicit that it is not a globally exact moving-surface distance.

Backends are `implicit_selected_control_secondary_continuous_moving_swept_volume_v1`,
`implicit_selected_control_secondary_continuous_deforming_swept_volume_v1`, and
the combined moving/deforming variant. The report adds
`collision_mesh_bounded_swept_volume: true`; static exact volume remains schema
21 and `collision_mesh_exact_swept_volume: true`.

## Evidence

- Focused host-independent math: 34 tests, 0 failures/errors/skips.
- Exact-package moving-mesh binding: 4/4 in 10.134 seconds, including schema
  22 moving Closed Volume report binding.
- Exact-package affected secondary regression: 160/160 in 235.763 seconds,
  0 failures/errors/skips.
- Foreground exact-package journey: schema 22, bounded moving swept-volume
  backend, 11 evaluated mesh samples, zero final penetration, cancellation,
  native Undo/Redo, save/reload, and Restore Source all passed.
- Reproducible archive: `releases/b4artists_ml_v0.37.18-dev.zip`, 54 members,
  425956 bytes, SHA-256
  `ed3bfe1cb532ba831855163642a92415eb82746e5fa8c9df18cb285df11bd868`.
- The Bforartists 5.2 Alpha process still reports the known post-result
  `ucrtbase.dll` shutdown access violation; assertions and reports complete
  before that fault.
