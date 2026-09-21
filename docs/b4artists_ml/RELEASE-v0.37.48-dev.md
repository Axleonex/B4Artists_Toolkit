# B4Artists Machine Learning v0.37.48-dev checkpoint

Date: 2026-09-16

This is a controlled development checkpoint, not a qualified release. The
source-bound archive is
`releases/b4artists_ml_v0.37.48-dev.zip` with SHA-256
`be29e89499be85c4322075a0945ec9dfad3df522ddd20334a985fb9c669dfcdc`.
It contains 54 files and is 454425 bytes. It is not installed, promoted, or
published.

## Verified surface

- Exact-package pole/posing regression: 85/85 tests across 8 suites.
- Exact-package secondary-motion regression: 35/35 tests on Bforartists 5.2.0
  Alpha, including the bounded local rotational-chain path, static compound
  paths, moving-sphere compound path, moving-capsule compound path, and the
  new mixed-sphere compound path.
- Exact-package mixed-sphere compound fixture: 1/1. It uses one authored
  static support plane, a static sphere set, and exactly one directly animated
  sphere with optional uniform scale. The moving sphere is evaluated from its
  direct Action, receives bounded relative-motion sweep and support/sphere
  projection, and preserves priority poses and bounded chain momentum.
- Exact-package focused math contract: 53/53 tests, consisting of 41
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
directly animated, optionally uniformly scaled sphere after one authored
support plane and a static sphere set. The exact fixture reports schema 36 and
backend
`implicit_selected_control_chain_location_mixed_moving_sphere_compound_support_spheres_v1`.
It records two sweep samples, zero final penetration, and bounded momentum
residual about `2.22e-16`.

## Explicit limitations and open gates

This checkpoint does not claim general rigid-body dynamics, broad
collision-coupled momentum, multiple moving spheres, moving capsule plus mesh
compounds, general moving/deforming mesh or volume behavior, learned temporal
quality, independent animator usability, production-asset acceptance, or
Cascadeur parity/superiority. The torso orientation and finer spine-shaping
dependency remains open. Temporal training and promotion remain fail-closed
pending human review, identity receipts, and a qualified disjoint corpus. The
entitlement-aware Cascadeur connector remains intentionally last and
untouched.

The Bforartists alpha host emits the passing test marker before its known
`ucrtbase.dll` shutdown access violation (`3221225477`). The assertion suites
and exact receipts pass; the process exit is recorded as a host teardown
limitation, not as clean-shutdown evidence. Foreground lifecycle and
independent animator acceptance were not rerun for this archive.

Evidence is bound in:

- `training/b4artists_ml/results/exact-package-pole-v0.37.48.json`
- `training/b4artists_ml/results/exact-package-v0.37.48-secondary-motion-all.json`
- `training/b4artists_ml/results/exact-package-v0.37.48-compound-mixed-spheres.json`
- `training/b4artists_ml/results/exact-package-v0.37.48-focused-secondary-math.json`
- `training/b4artists_ml/results/current-package-direct-zip-import-v0.37.48.json`
- `training/b4artists_ml/results/exact-package-v0.37.48-production-character-generalization.json`
- `docs/b4artists_ml/package-test-v0.37.48-dev.json`
