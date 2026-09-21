# Secondary closed-volume collision v1

Development 0.37.9 adds a separately bounded finite-volume path to the
selected-control Secondary Motion workflow. It is deterministic and remains
separate from learned temporal motion, general rigid-body dynamics,
continuous collision, self-collision, and Cascadeur comparison.

## Supported contract

- Choose **Closed Volume** with one unparented triangle-mesh collision object.
- The mesh must be finite, nondegenerate, and topologically closed. Open meshes
  fail closed; the existing `MESH` shape remains the sampled surface path.
- **Control Volume Radius** treats each selected control as a finite spherical
  volume. The solver maintains `radius + clearance` from the nearest evaluated
  triangle and supports static geometry or the existing direct shape-key
  trajectory path.
- Static mesh transforms must remain unanimated and free of parents,
  constraints, modifiers, drivers, NLA and rigid-body state. Deforming mode
  retains the stable-topology/direct-shape-key guards from the deforming-mesh
  milestone.
- Report schema 16 uses backend
  `implicit_selected_control_secondary_volume_v1`, records the finite radius,
  and identifies target space as `closed evaluated triangle volume`.

This is a sampled spherical-volume approximation around selected controls. It
does not claim swept continuous-time contact, self-collision, coupled force
transfer, deformable volume inference, learned motion, or Cascadeur parity.

## Evidence

- Focused secondary math floor: 27 passing tests, including the legacy plane
  and capsule paths, static/deforming mesh paths, finite-radius projection,
  invalid-radius rejection, and volume follow-through.
- Exact-package Bforartists binding: 5/5 tests passed, covering static mesh,
  deforming shape-key mesh, closed-volume radius binding, open-volume rejection
  evidence, and animation/dependency guards.
- Exact-package affected regression: 153/153 tests passed across the affected
  suites in 179.340 seconds, with zero failures, errors, or skips. The alpha
  host emitted its known `ucrtbase.dll` access violation only after the `OK`
  result during shutdown.
- Foreground evidence: `volume-ui-v1.json` passes visible controls, Escape
  cancellation, generation, native Undo/Redo, Restore Input, Keep, save/reload,
  and Restore Source. The report records schema 16, 12 closed-mesh triangles,
  radius `0.12`, zero measured penetration, and editable linear output keys.
- Reproducible archive: `releases/b4artists_ml_v0.37.9-dev.zip`, 54 members,
  SHA-256 `e2c966f78595706950c68ab7c8ebc1389ee8acb298b15631a9de334c7a2c96a1`.

## Remaining limits

Continuous-time swept collision, self-collision, moving collision-mesh
transforms, coupled collision forces, learned temporal qualification,
independent animator review, and Cascadeur parity remain open.
