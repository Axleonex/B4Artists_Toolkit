# B4Artists Machine Learning v0.37.46-dev checkpoint

Date: 2026-09-16

This is a controlled development checkpoint, not a qualified release. The
source-bound archive is
`releases/b4artists_ml_v0.37.46-dev.zip` with SHA-256
`4c6f07ebb32bb2c89d3a1a61107704f67a47d05079bd6377eb241da7ebd13eef`.

## Verified surface

- Exact-package pole/posing regression: 85/85 tests across 8 suites.
- Exact-package secondary-motion regression: 33/33 tests on Bforartists 5.2.0
  Alpha, including the bounded local rotational-chain path and the new static
  support-plane plus one moving-sphere compound path.
- Exact-package moving-sphere compound fixture: 1/1. It uses one authored
  static support plane and exactly one directly animated sphere with optional
  uniform scale; mixed moving/static sets, multiple moving spheres, capsules,
  and meshes remain rejected.
- Direct-ZIP imported-humanoid regression: 12/12.
- Bounded production-character generalization probe: 3/3 test methods across
  nine cases: three frozen Unity proportion fixtures, three generated native
  BoneForge/Rigify fixtures, and three project-authored imported
  Mocap/Unity/Unreal FBX roundtrips. Native and authored-import cases remain
  qualified only for the bounded six-endpoint target slice; the authored FBX
  roundtrips are not external production assets.
- Exact ZIP math contract: 51/51 tests (39 secondary math and 12 capsule math).
- Smallest temporal pipeline recheck: 2/2 tests; the current corpus remains
  `BLOCKED_BEFORE_TRAINING`, no learner module is imported, no candidate artifact
  is created, and promotion remains disabled.

The moving-sphere compound extension is procedural (`learned: false`) and
deliberately does not claim a general rigid-body, joint-inertia,
collision-impulse, or deformable-body solver. The archive is not installed,
promoted, or published.

## Gates that remain open

Foreground usability and independent animator acceptance remain unqualified.
Temporal training and promotion remain fail-closed pending human review,
identity receipts, and a qualified disjoint corpus. Broader collision behavior,
general rigid-body dynamics, finer torso orientation/limits, and production
asset validation remain open. Cascadeur conversion/comparison and the
entitlement-aware connector remain intentionally last and untouched.

The known Bforartists alpha-host shutdown fault occurs after successful
assertions and is recorded separately; it is not treated as clean host shutdown
evidence.

Evidence is bound in
`training/b4artists_ml/results/exact-package-pole-v0.37.46.json`,
`training/b4artists_ml/results/exact-package-v0.37.46-secondary-motion-all.json`,
`training/b4artists_ml/results/exact-package-v0.37.46-compound-moving-sphere.json`,
`training/b4artists_ml/results/current-package-direct-zip-import-v0.37.46.json`,
`training/b4artists_ml/results/exact-package-v0.37.46-production-character-generalization.json`,
and `docs/b4artists_ml/package-test-v0.37.46-dev.json`.
