# B4Artists Machine Learning v0.37.50-dev checkpoint

Date: 2026-09-16  
Status: controlled development checkpoint, not a qualified release

## Package identity

- Archive: `releases/b4artists_ml_v0.37.50-dev.zip`
- SHA-256: `13aa37181f5f341d696beaca53983b50b0d8215ad4e88c802294bc5b30274745`
- Archive members: 54
- Archive bytes: 454727

## Verified bounded evidence

- Pole and posing regression: 85/85.
- Exact secondary-motion regression: 37/37.
- Dedicated two-moving-sphere plus static-sphere-set collision fixture: 1/1.
- Focused secondary/capsule math contract: 55/55.
- Direct ZIP humanoid import regression: 12/12.
- Production-character generalization probe: 3/3.
- Temporal pipeline contract: 2/2 fail-closed checks; training and promotion remain blocked before training.

The new procedural collision slice reports schema 38 and backend
`implicit_selected_control_chain_location_mixed_moving_sphere_set_compound_support_spheres_v1`.
It supports exactly two directly animated, optionally uniformly scaled moving
spheres, one authored support plane, and a bounded static sphere set with
continuous relative-motion sweep, deterministic projection, priority
preservation, and bounded momentum response.

## Explicit limits

This checkpoint does not qualify general rigid-body dynamics, broad collision
behavior, more than two moving spheres, arbitrary moving/static mixtures,
moving capsules or meshes in the same moving-sphere compound,
general moving/deforming colliders, learned temporal training or promotion,
human review, production acceptance, torso orientation/spine shaping, or
Cascadeur parity. The entitlement-aware Cascadeur connector remains last.
The installed Bforartists alpha host still emits its known shutdown-only
access-violation code after passing receipts; that code is not counted as a
test failure.
