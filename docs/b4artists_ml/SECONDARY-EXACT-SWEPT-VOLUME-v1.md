# Secondary exact swept-volume collision v1

Development 0.37.17 adds an exact static finite-volume path to the existing
closed triangle-mesh Continuous-Time Sweep. The selected control is treated as
a sphere with the authored volume radius plus collision clearance. For each
solver segment, the implementation computes the exact closest distance between
the center segment and every filled triangle, then bisects the first boundary
crossing of that radius. This catches near-face and rounded-edge contacts even
when the centerline never intersects a triangle.

## Supported contract

- Closed static triangle mesh, **Closed Volume**, and **Continuous-Time Sweep**
  use schema 21/backend
  `implicit_selected_control_secondary_exact_swept_volume_v1`.
- Static point-mesh Continuous-Time Sweep remains schema 17. Direct shape-key
  and direct object-transform mesh trajectories retain their bounded schema 18
  and schema 20 interpolation paths; Closed Volume trajectories use the
  separately bounded schema 22 path documented in
  `SECONDARY-BOUNDED-MOVING-VOLUME-v1.md`; none are silently presented as
  globally exact moving/deforming distance.
- The exact path preserves the existing priority-pose conflict policy,
  editable output, final evaluated clearance verification, native lifecycle,
  and fail-closed closed-mesh requirement.

This is deterministic static sphere-vs-triangle swept distance. It is not a
coupled rigid/deformable-body solver, exact moving/deforming swept distance,
learned temporal motion, independent animator usability evidence, or a
Cascadeur comparison.

## Evidence

- Focused host-independent math: 33 tests pass with zero failures/errors/skips.
- Exact-package Bforartists binding: 6/6 tests pass in 9.795 seconds, including
  schema 21 report binding and the existing static/deforming/open-mesh guards.
- Exact-package affected secondary regression: 159/159 tests pass in 226.150
  seconds with zero failures/errors/skips. The run uses the scoped writable
  temp directory recorded in the regression receipt.
- Foreground exact-package evidence: `exact-swept-volume-ui-v1.json` passes
  visible controls, Escape cancellation, generation, native Undo/Redo, Restore
  Input, Keep, save/reload, Restore Source, and final evaluated clearance. The
  solver elapsed time is 1,485.0146 ms, maximum step time is 67.2075 ms, and
  final measured penetration is 0.
- Reproducible archive: `releases/b4artists_ml_v0.37.17-dev.zip`, 54 members,
  425655 bytes, SHA-256
  `1ae634fcb233e04cca038a2d2e005c741b5c93e9420febac762e5b8b9c630a43`.
- The Bforartists 5.2 Alpha process still reports the known post-result
  `ucrtbase.dll` shutdown access violation; assertions and reports complete
  before that fault.
