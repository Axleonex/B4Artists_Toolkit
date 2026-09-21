# Secondary deforming continuous mesh collision v1

Status: Complete as a bounded procedural development slice on 2026-09-13. The
exact-package binding, affected regression, and foreground recovery evidence
are recorded below. This does not establish exact moving/deforming swept
distance, learned temporal quality, independent animator usability, or
Cascadeur parity.

Development 0.37 adds a bounded continuous-time path for a closed triangle mesh
that follows a direct shape-key Action. The solver linearly interpolates the
evaluated triangle positions between adjacent solve samples and checks a fixed
eight-substep budget for selected-control and mesh crossings. A finite
**Closed Volume** uses the same path with its authored control-volume radius.

## Supported contract

- Enable **Follow Shape-Key Deformation** and **Continuous-Time Sweep** on a
  closed, unparented mesh with stable topology.
- Direct object transforms, modifiers, drivers, NLA, constraints, rigid-body
  state, topology changes, open meshes, and nonfinite or degenerate samples
  remain rejected.
- The sweep is deliberately bounded and deterministic. It is not an exact
  moving/deforming swept-sphere solver, a coupled deformable-body solver, or a
  learned motion model. Static Closed Volume exact distance is a separate
  schema-21 slice.
- Point-path results report schema 18/backend
  `implicit_selected_control_secondary_continuous_deforming_mesh_v1`.
  Finite-volume results report the corresponding
  `...continuous_deforming_volume_v1` backend.

## Validation boundary

The host-independent math tests cover mesh-motion crossings, stationary-control
contacts, topology validation, and the existing static/deforming compatibility
paths. Static continuous-time remains schema 17; the moving/deforming path is
schema 18. The exact `releases/b4artists_ml_v0.37.12-dev.zip` package passes
30 focused math tests, a 5/5 Bforartists binding suite, and a 153/153 affected
regression with zero failures, errors, or skips. The foreground journey passes
visible controls, cancellation, editable generation, native Undo/Redo, Restore
Input, Keep, save/reload, and Restore Source; its report records 11 evaluated
mesh samples, 1,482.184 ms solver time, and a 102.141 ms maximum step. The
known alpha-host `ucrtbase.dll` shutdown access violation occurs after the
passing assertions and is recorded separately.

Machine-readable evidence: `DEFORMING-CONTINUOUS-BFORARTISTS-REGRESSION-v1.json`
and `deforming-continuous-ui-rerun-v1.json`.

This feature remains separate from self-collision, coupled force transfer,
learned temporal quality, independent animator usability, and Cascadeur parity.
