# B4Artists Machine Learning v0.37.49-dev checkpoint

Date: 2026-09-16

This is a controlled development checkpoint, not a qualified release. The
source-bound archive is
`releases/b4artists_ml_v0.37.49-dev.zip` with SHA-256
`2355e5b591f88cbbc5b40faae599aa4ef2bd2c8a72568cb725a26dcb26542e2f`.
It contains 54 files and is 454622 bytes. It is not installed, promoted, or
published.

## Verified surface

- Exact-package pole/posing regression: 85/85 tests across 8 suites.
- Exact-package secondary-motion regression: 36/36 tests on Bforartists 5.2.0
  Alpha, including the bounded local rotational-chain path, static compound
  paths, moving-sphere compound paths, and moving-capsule compound paths.
- Exact-package two-moving-sphere compound fixture: 1/1. It uses one authored
  static support plane and exactly two directly animated, optionally uniformly
  scaled spheres. Each sphere is evaluated from its direct Action; the bounded
  relative-motion sweep, deterministic support/sphere projection, priority
  preservation, and bounded chain momentum path are exercised.
- Exact-package focused math contract: 54/54 tests, consisting of 42
  secondary math tests and 12 capsule math tests.
- Direct-ZIP imported-humanoid regression: 12/12.
- Bounded production-character generalization probe: 3/3 test methods across
  nine project-owned or generated cases. Native and authored-import cases are
  qualified only for the bounded six-endpoint target slice; authored FBX
  roundtrips are not external production assets.
- Smallest temporal pipeline recheck: 2/2 tests; the corpus remains
  `BLOCKED_BEFORE_TRAINING`, no learner module is imported, no candidate
  artifact is created, and promotion remains disabled.

The new compound is procedural (`learned: false`). Its qualified scope is one
authored support plane plus exactly two directly animated, optionally
uniformly scaled spheres. It reports schema 37 and backend
`implicit_selected_control_chain_location_moving_sphere_set_compound_support_v1`.
The implementation uses bounded analytic relative-motion crossing detection,
deterministic projection, and relative surface-velocity response. It is not a
general rigid-body solver.

## Explicit limitations and open gates

This checkpoint does not claim general rigid-body dynamics, broad
collision-coupled momentum, more than two moving spheres, two moving spheres
mixed with static spheres, moving capsule or mesh mixtures, general
moving/deforming mesh or volume behavior, learned temporal quality, independent
animator usability, production-asset acceptance, or Cascadeur
parity/superiority. The torso orientation and finer spine-shaping dependency
remains open. Temporal training and promotion remain fail-closed pending human
review, identity receipts, and a qualified disjoint corpus. The
entitlement-aware Cascadeur connector remains intentionally last and
untouched.

The Bforartists alpha host emits the passing test marker before its known
`ucrtbase.dll` shutdown access violation (`3221225477`). The assertion suites
and exact receipts pass; the process exit is recorded as a host teardown
limitation, not as clean-shutdown evidence. Foreground lifecycle and
independent animator acceptance were not rerun for this archive.

Evidence is bound in:

- `training/b4artists_ml/results/exact-package-pole-v0.37.49.json`
- `training/b4artists_ml/results/exact-package-v0.37.49-secondary-motion-all.json`
- `training/b4artists_ml/results/exact-package-v0.37.49-compound-moving-sphere-set.json`
- `training/b4artists_ml/results/exact-package-v0.37.49-focused-secondary-math.json`
- `training/b4artists_ml/results/current-package-direct-zip-import-v0.37.49.json`
- `training/b4artists_ml/results/exact-package-v0.37.49-production-character-generalization.json`
- `docs/b4artists_ml/package-test-v0.37.49-dev.json`
