# Secondary bounded moving/deforming finite-volume collision v1

Development 0.37.18 adds the next separately bounded collision slice after
static exact swept volume. It applies the existing exact static
segment-to-filled-triangle swept-sphere kernel at each bounded interpolated
mesh state when **Closed Volume** and **Continuous-Time Sweep** are combined
with a directly moving mesh, a shape-key-deforming mesh, or both.

This catches finite-volume contacts that a centerline-only moving/deforming
sweep can miss. It is deliberately not presented as globally exact
moving-surface distance: the mesh is held at the bounded interval-end state
for each static kernel evaluation. Static Closed Volume remains the separate
schema-21 exact path.

## Supported contract

- Closed meshes remain required for Continuous-Time Sweep.
- Stable triangle topology, direct transform/shape-key dependency guards,
  priority-pose conflict handling, mutation guards, editable output and final
  evaluated clearance checks are retained.
- Schema 22 reports
  `implicit_selected_control_secondary_continuous_moving_swept_volume_v1`,
  `implicit_selected_control_secondary_continuous_deforming_swept_volume_v1`,
  or the corresponding combined moving/deforming backend.
- Reports set `collision_mesh_bounded_swept_volume: true` and expose target
  spaces beginning with `bounded continuous-time closed ... swept triangle
  volume`. Static exact reports continue to set
  `collision_mesh_exact_swept_volume: true` and schema 21.

This remains deterministic procedural geometry. It is not a globally exact
moving/deforming swept-sphere solver, a coupled rigid/deformable-body solver,
learned temporal motion, independent animator usability evidence, or a
Cascadeur comparison.

## Evidence

- Focused host-independent math: 35 tests pass with zero
  failures/errors/skips, including bounded moving/deforming finite-volume
  interpolation.
- Exact-package moving-mesh binding: 5/5 in 15.267 seconds.
- Exact-package affected secondary regression: 161/161 in 256.530 seconds,
  zero failures/errors/skips.
- Foreground exact-package journey: schema 22, bounded moving swept-volume
  backend, 11 evaluated mesh samples, zero final penetration, Escape
  cancellation, native Undo/Redo, save/reload and Restore Source all pass.
- Reproducible archive: `releases/b4artists_ml_v0.37.18-dev.zip`, 54 members,
  425956 bytes, SHA-256
  `ed3bfe1cb532ba831855163642a92415eb82746e5fa8c9df18cb285df11bd868`.
- Bforartists 5.2 Alpha still reports the known post-result
  `ucrtbase.dll` shutdown access violation after the assertions and reports
  have completed.
