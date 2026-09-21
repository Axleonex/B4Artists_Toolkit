# B4Artists Machine Learning v0.37.47-dev checkpoint

Date: 2026-09-16

This is a controlled development checkpoint, not a qualified release. The
source-bound archive is
`releases/b4artists_ml_v0.37.47-dev.zip` with SHA-256
`d11aedef5d818ed06465de9d60bc45a812784b6e5af7eedccf823d4c46d18339`.
It contains 54 files and is 454140 bytes. It is not installed, promoted, or
published.

## Verified surface

- Exact-package pole/posing regression: 85/85 tests across 8 suites.
- Exact-package secondary-motion regression: 34/34 tests on Bforartists 5.2.0
  Alpha, including the bounded local rotational-chain path, static compound
  paths, moving-sphere compound path, and moving-capsule compound path.
- Exact-package moving-capsule compound fixture: 1/1. It uses one authored
  static support plane, a static sphere set, and exactly one directly animated
  capsule with optional uniform endpoint scale. The capsule trajectory is
  sampled from endpoint Actions, receives bounded relative-motion sweep and
  support/sphere/capsule projection, and preserves priority poses and bounded
  chain momentum.
- Exact-package focused math contract: 52/52 tests, consisting of 40 secondary
  math tests and 12 capsule math tests.
- Direct-ZIP imported-humanoid regression: 12/12.
- Bounded production-character generalization probe: 3/3 test methods across
  nine project-owned or generated cases. Native and authored-import cases are
  qualified only for the bounded six-endpoint target slice; authored FBX
  roundtrips are not external production assets.
- Smallest temporal pipeline recheck: 2/2 tests; the corpus remains
  `BLOCKED_BEFORE_TRAINING`, no learner module is imported, no candidate
  artifact is created, and promotion remains disabled.

The new compound is procedural (`learned: false`). Its qualified scope is one
directly animated, optionally uniformly scaled capsule after one authored
support plane and a static sphere set. The host report recorded a desired
post-projection residual of approximately `1.11e-16`; the host-evaluated
penetration was `4.284391255660047e-08` against the declared compound
evaluation tolerance of `1e-6`. The underlying math contract remains strict
and fail-closed at `1e-8`.

## Explicit limitations and open gates

This checkpoint does not claim general rigid-body dynamics, broad
collision-coupled momentum, mixed moving/static sphere sets, multiple moving
colliders, moving capsule plus mesh compounds, general moving/deforming mesh
or volume behavior, learned temporal quality, independent animator usability,
production-asset acceptance, or Cascadeur parity/superiority. The torso
orientation and finer spine-shaping dependency remains open. Temporal training
and promotion remain fail-closed pending human review, identity receipts, and
a qualified disjoint corpus. The entitlement-aware Cascadeur connector remains
intentionally last and untouched.

The Bforartists alpha host emits the passing test marker before its known
`ucrtbase.dll` shutdown access violation (`3221225477`). The assertion suites
and exact receipts pass; the process exit is recorded as a host teardown
limitation, not as clean-shutdown evidence. Foreground lifecycle and
independent animator acceptance were not rerun for this archive.

Evidence is bound in:

- `training/b4artists_ml/results/exact-package-pole-v0.37.47.json`
- `training/b4artists_ml/results/exact-package-v0.37.47-secondary-motion-all.json`
- `training/b4artists_ml/results/exact-package-v0.37.47-compound-moving-capsule.json`
- `training/b4artists_ml/results/exact-package-v0.37.47-focused-secondary-math.json`
- `training/b4artists_ml/results/current-package-direct-zip-import-v0.37.47.json`
- `training/b4artists_ml/results/exact-package-v0.37.47-production-character-generalization.json`
- `docs/b4artists_ml/package-test-v0.37.47-dev.json`
