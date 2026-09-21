# Secondary deforming mesh collision v1

Development 0.37.8 adds one separately bounded deforming-surface path to the
selected-control Secondary Motion workflow. It is deterministic and remains
separate from learned temporal motion, general rigid-body dynamics, continuous
collision, self-collision, and Cascadeur comparison.

## Supported contract

- One unparented collision object with a stable raw loop-triangle topology.
- The object has at least `Basis` plus one additional shape key.
- The shape-key deformation is driven by a direct editable shape-key Action with
  finite `.value` curves. Drivers, NLA tracks, muted/locked curves, modifiers,
  parent/constraint state, rigid-body state, and animated object transforms are
  rejected.
- The solver evaluates the shape-key surface at every authored solve sample,
  converts the evaluated vertices and loop triangles to world space, and uses
  only that per-frame trajectory as the mesh collision input.
- Topology changes, nonfinite coordinates, degenerate triangles, or failure to
  produce the evaluated mesh reject before a committed candidate is published.

Static mesh binding remains available when **Follow Shape-Key Deformation** is
disabled. The UI labels the two modes separately; the report uses schema 15,
backend `implicit_selected_control_secondary_deforming_mesh_v1`, target space
`evaluated shape-key triangle mesh`, and records the sampled trajectory count.

## Evidence

- Focused pure math coverage: 24 passing tests plus 10 subtests, including
  current-sample trajectory selection, topology/sample-count rejection, and
  degenerate-sample rejection. The local pytest process printed all 24 passing
  cases but did not exit cleanly during interpreter teardown; the exact
  Bforartists suites below are the authoritative host evidence.
- Bforartists binding: 3/3 passing (`test_request_and_static_mesh_binding`,
  `test_parent_animation_modifier_and_rigid_body_guards`, and
  `test_shape_key_deforming_mesh_binding_and_samples`). The alpha host then
  emitted its known post-test `ucrtbase.dll` access violation while quitting.
- Exact-package affected regression: 151/151 tests passed across the affected
  suites in 182.084 seconds, with zero failures, errors, or skips. The host
  shutdown access violation occurred only after the `OK` result.
- Foreground evidence: `deforming-mesh-ui-v1.json` passes visible controls,
  Escape cancellation, generation, native Undo/Redo, Restore Input, Keep,
  save/reload, and Restore Source. The report records 12 triangles, 11
  evaluated shape-key samples, zero measured post-solve penetration, and
  editable linear output keys.
- Reproducible archive: `releases/b4artists_ml_v0.37.8-dev.zip`, 54 members,
  SHA-256 `a14b39de40878f8f9029f41b93afd39cb86d3d19b052f34c881d02ec5659f7fc`.

## Remaining limits

This milestone does not support moving collision-object transforms, modifiers,
drivers, NLA-driven deformation, topology-changing deformation, volume
colliders, continuous-time swept collision, self-collision, coupled force
transfer, learned motion, independent animator review, or Cascadeur parity.
