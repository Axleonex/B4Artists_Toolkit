# B4Artists Machine Learning v0.37.43-dev checkpoint

Date: 2026-09-16

This is a controlled development checkpoint, not a qualified release. The
source-bound archive is
`releases/b4artists_ml_v0.37.43-dev.zip` with SHA-256
`0a012b08562519ae6bb9187f8378b8d5fad5dbb81f7fdfda0c56af07d1e1c3a3`.

## Verified surface

- The 54-file ZIP imports directly in Bforartists 5.2.0 Alpha.
- Exact-package pole regression: 85/85 tests across 8 suites.
- Exact-package secondary-motion regression: 29/29 tests, including the new
  support-plane + static sphere-set + static capsule compound.
- Exact-package compound fixture: 1/1; schema 31, four colliders, two collision
  samples, raw penetration `0.030880139527631356`, resolved penetration `0.0`,
  momentum residual `2.220446049250313e-16`, and maximum world-location error
  below `2e-7`.
- Direct-ZIP imported-humanoid regression: 12/12.
- Frozen production-character generalization probe: 1/1 across three
  project-owned Unity Humanoid proportion fixtures, with source recovery.
- Exact ZIP math contract: 47/47 tests (35 secondary math and 12 capsule math).

The new compound is intentionally narrow: one static authored support plane,
the existing bounded static sphere set, and one static endpoint capsule. Moving,
scaling, and continuous capsule endpoint animation are rejected in this form.
It is procedural (`learned: false`) and does not claim general rigid-body
dynamics or broad multi-collider momentum behavior.

## Gates that remain open

The archive is not installed, promoted, or published. Foreground usability and
independent animator review remain unqualified. Temporal training and promotion
remain fail-closed pending reviewed identity receipts and a qualified disjoint
corpus. Cascadeur conversion, matched comparison, and the entitlement-aware
connector remain unqualified and intentionally last. The known Bforartists alpha
host shutdown access violation still occurs after passing assertions and is
recorded separately from test results.

Evidence is bound in
`training/b4artists_ml/results/exact-package-v0.37.43-compound-capsule.json`,
`training/b4artists_ml/results/exact-package-v0.37.43-secondary-motion-all.json`,
`training/b4artists_ml/results/exact-package-pole-v0.37.43.json`,
`training/b4artists_ml/results/current-package-direct-zip-import-v0.37.43.json`,
and `docs/b4artists_ml/package-test-v0.37.43-dev.json`.
