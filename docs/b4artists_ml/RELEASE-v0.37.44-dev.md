# B4Artists Machine Learning v0.37.44-dev checkpoint

Date: 2026-09-16

This is a controlled development checkpoint, not a qualified release. The
source-bound archive is
`releases/b4artists_ml_v0.37.44-dev.zip` with SHA-256
`54a51e76bb3974c2c17c4cccf9463dc33cf397fd41e2d5d6a6165db2987cf4b6`.

## Verified surface

- The 54-file ZIP imports directly in Bforartists 5.2.0 Alpha.
- Exact-package pole/posing regression: 85/85 tests across 8 suites.
- Exact-package secondary-motion regression: 30/30 tests, including the new
  support-plane + static sphere-set + static closed-mesh compound.
- Exact-package compound-mesh fixture: 1/1; schema 32, four colliders, two
  static spheres plus the support plane and closed mesh, zero final penetration,
  momentum residual `2.220446049250313e-16`, and maximum world-location error
  below `2e-7`.
- Exact-package combined compound fixture: 1/1; schema 32, five colliders,
  two static spheres plus the support plane, static capsule, and closed mesh,
  zero final penetration, momentum residual `2.220446049250313e-16`, and
  maximum world-location error below `2e-7`.
- Direct-ZIP imported-humanoid regression: 12/12.
- Bounded production-character generalization probe: 3/3 test methods across nine
  cases—three project-owned Unity Humanoid proportion fixtures, generated
  BoneForge/Rigify Basic/Default fixtures, and project-authored imported Mocap,
  Unity, and Unreal FBX roundtrips—with source recovery. Native and authored-import
  cases are qualified only for the bounded six-endpoint target slice; authored FBX
  roundtrips are not external production assets.
- Exact ZIP math contract: 48/48 tests (36 secondary math and 12 capsule math).

The new compound remains intentionally narrow: one static authored support plane,
the existing bounded static sphere set, one optional static endpoint capsule, and
one optional static closed triangle mesh. Moving, deforming, open, continuous,
and finite-volume mesh forms are rejected in this mixed compound path. The
feature is procedural (`learned: false`) and does not claim general rigid-body
dynamics or broad collision behavior.

## Gates that remain open

The archive is not installed, promoted, or published. Foreground usability and
independent animator review remain unqualified. Temporal training and promotion
remain fail-closed pending reviewed identity receipts and a qualified disjoint
corpus. Cascadeur conversion, matched comparison, and the entitlement-aware
connector remain unqualified and intentionally last. The known Bforartists alpha
host shutdown access violation still occurs after passing assertions and is
recorded separately from test results. The latest fully foreground-bound
checkpoint remains v0.37.42 until a human-facing rerun is performed for this
archive.

Evidence is bound in
`training/b4artists_ml/results/exact-package-v0.37.44-compound-mesh.json`,
`training/b4artists_ml/results/exact-package-v0.37.44-compound-capsule-mesh.json`,
`training/b4artists_ml/results/exact-package-v0.37.44-secondary-motion-all.json`,
`training/b4artists_ml/results/exact-package-pole-v0.37.44.json`,
`training/b4artists_ml/results/current-package-direct-zip-import-v0.37.44.json`,
`training/b4artists_ml/results/exact-package-v0.37.44-production-character-generalization.json`,
and `docs/b4artists_ml/package-test-v0.37.44-dev.json`.
