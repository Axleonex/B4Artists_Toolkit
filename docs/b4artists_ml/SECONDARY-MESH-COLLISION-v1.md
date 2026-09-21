# Secondary Motion — Static Arbitrary Triangle-Mesh Collision v1

Development 0.37.5 adds an opt-in `Mesh` collider to the B4Artists Secondary Motion world-space location path. The collider is one explicit, unparented, static mesh object with no modifiers, constraints, animation, drivers, NLA tracks, or rigid-body simulation. Its evaluated world-space loop triangles are frozen before the solve and rebound through a mutation token on every cooperative step.

The deterministic math path supports both open two-sided sampled surfaces and closed triangle meshes. It finds the nearest point on a validated nondegenerate triangle, applies a finite clearance, uses deterministic fallback normals for exact-surface degeneracy, and uses ray parity only for closed-mesh interior exclusion. It reports collision count, raw and final penetration, triangle count, closed-mesh status, editable curves, exact priority-pose preservation, and the static evaluated-mesh target space.

The feature intentionally does not claim deforming or moving geometry, modifiers, continuous-time swept collision, self-collision, coupled rigid-body forces, mesh thickness inference for open surfaces, learned temporal motion, independent animator usability, or Cascadeur parity. A closed mesh provides sampled volume exclusion; an open mesh is a sampled two-sided surface. Continuous-time and self-collision remain separate milestones.

## Evidence

- Focused math: `test_b4artists_ml_secondary_math.py`, `test_b4artists_ml_secondary_capsule_math_v1.py`, and `test_b4artists_ml_secondary_mesh_math_v1.py` pass 22 tests plus 10 subtests.
- Exact archive: `releases/b4artists_ml_v0.37.5-dev.zip`, 54 members, 418,879 bytes, SHA-256 `5feea714c77c1bd99f3ce652854b34f5d0556f120c3c7fa946a5687f68e5a92b`; independent archive check passes.
- Bforartists 5.1.0 / Blender 5.2.0 Alpha / build `dd23ab17120d`: mesh binding and static-geometry guard suite passes 2/2.
- Exact-archive affected Bforartists regression passes 150/150 across 15 suites, with zero failures, errors, or skips, in 182.620 seconds.
- Foreground report: `mesh-ui-v1.json`. The modal journey visibly exposes the Mesh shape and binding, cancels without replacing the input, generates an editable schema-14 candidate, passes native Undo/Redo, Restore Input, Keep, save/reload, and Restore Source. Controls and completion screenshots are `training/b4artists_ml/cache/mesh-ui-v1-controls.png` and `training/b4artists_ml/cache/mesh-ui-v1-completed.png`.

The Bforartists process still exits with the known `ucrtbase.dll` access violation after assertions and report writing. That host shutdown defect is recorded as an execution note, not a test failure.

No independent S3 reviewer or full-goal completion authority is claimed here. The governed review gate remains fail-closed separately from this feature evidence; learned temporal quality, human usability, and matched Cascadeur comparison are still open.
