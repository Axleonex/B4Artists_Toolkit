# Bounded Moving/Deforming Mesh Chain Coupling v1

Development 0.37.36 adds the next bounded coupled world-location collision slice. A selected direct parent-child chain can now exchange equal-and-opposite momentum while its point controls are resolved against one sampled world-space mesh trajectory. The trajectory may combine direct object-transform motion and direct shape-key deformation when topology remains stable.

The chain accepts either one static mesh or one per-sample mesh trajectory. With continuous mode enabled, each interval uses the existing bounded interpolation sweep; a positive finite-volume radius uses the bounded interpolated exact-static-volume helper. The result is projected again after envelope blending, so the published interior samples retain mesh clearance. Authored priority samples and endpoints remain exact, and the normal momentum residual remains within the existing numerical tolerance.

Evidence:

- `tests/test_b4artists_ml_secondary_math.py`: 29 focused tests pass, including moving/deforming trajectory collision, continuous sweep, post-blend clearance, and mutually exclusive input validation.
- `training/b4artists_ml/results/exact-package-v0.37.36-moving-deforming-mesh.json`: one exact-ZIP Bforartists host test passes with schema 28 / `implicit_selected_control_chain_location_moving_deforming_mesh_v1`, three continuous collision samples, zero final penetration, and world-location error below `2e-7`.
- `docs/b4artists_ml/package-test-v0.37.36-dev.json`: the 54-member archive is bound to SHA-256 `b00dc667b549f311772def7b5e1f23cd7ac9b736a8e3e2616885df01d300256a`; its exact package regression, direct-ZIP import, and foreground lifecycle receipts pass.

This remains deliberately bounded. It does not claim a globally exact moving-surface distance, arbitrary broad-phase collision, multiple independently moving mesh colliders, rigid-body impulse exchange with collider mass, general deformable-body dynamics, learned temporal quality, production-character generalization, independent animator usability, or Cascadeur parity. Training and promotion remain fail-closed pending the separate human-review, identity/authorization, and disjoint-corpus gates.
