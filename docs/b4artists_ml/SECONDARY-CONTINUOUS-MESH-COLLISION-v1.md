# Secondary continuous-time mesh collision v1

Development 0.37.10 adds a bounded continuous-time guard to selected-control
Secondary Motion. It catches a control segment crossing a static closed
triangle mesh between solver samples, while keeping the existing sampled
surface and finite-volume paths available separately.

## Supported contract

- Enable **Continuous-Time Sweep** with a static closed triangle mesh.
- Each solver step tests the segment from the previous simulated position to
  the current simulated position for the earliest triangle hit. The result is
  projected back to the closed mesh boundary with authored clearance and, for
  **Closed Volume**, the finite control-volume radius.
- Open meshes fail closed. Direct shape-key trajectories, moving collision
  objects, modifiers, drivers, NLA, rigid-body state, and self-collision are
  outside this slice and are rejected or remain unavailable.
- Schema 17 reports backend
  `implicit_selected_control_secondary_continuous_mesh_v1` for the point path
  or `implicit_selected_control_secondary_continuous_volume_v1` for the finite
  volume path.

This point path is a conservative segment/triangle sweep for static closed
geometry. Closed Volume uses the separately documented exact static
swept-volume path in `SECONDARY-EXACT-SWEPT-VOLUME-v1.md`. Neither path is a
general continuous rigid-body solver or a claim of exact moving/deforming
swept distance, coupled force transfer, learned motion, or Cascadeur parity.

## Evidence

- Focused secondary math floor: 29 passing tests, including earliest
  segment/triangle hit selection, solver tunneling prevention, finite-radius
  compatibility, and fail-closed open/deforming inputs.
- Exact-package Bforartists binding: 5/5 tests passed, retaining the static,
  deforming, closed-volume, open-volume and dependency-guard checks.
- Exact-package affected regression: 153/153 tests passed across the affected
  suites in 178.034 seconds, with zero failures, errors, or skips. The alpha
  host emitted its known `ucrtbase.dll` access violation only after the `OK`
  result during shutdown.
- Foreground evidence: `continuous-ui-v1.json` passes visible controls, Escape
  cancellation, generation, native Undo/Redo, Restore Input, Keep, save/reload,
  and Restore Source. The report records schema 17 and target space
  `continuous-time closed evaluated triangle mesh`.
- Reproducible archive: `releases/b4artists_ml_v0.37.11-dev.zip`, 54 members,
  SHA-256 `9f1b88f21e39035cd595db55e42500fa0bfebfb837c1e15cee6c6af3da7d800c`.

## Remaining limits

Deforming/moving collision-mesh sweep, exact moving/deforming finite-sphere
distance, self-collision, coupled collision forces, learned temporal qualification,
independent animator review, and Cascadeur parity remain open.
