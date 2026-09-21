# B4Artists Machine Learning v0.37.42-dev checkpoint

Date: 2026-09-16

This is a controlled development checkpoint, not a qualified release. The
source-bound archive is
releases/b4artists_ml_v0.37.42-dev.zip with SHA-256
e4099811be506e8a64e3585819d2d5d3af54259ece40974ec36d62b0498fc410.

## Verified surface

- The archive contains the current 54-member b4artists_ml runtime package.
- Exact-package checks imported the package directly from the ZIP in
  Bforartists 5.2.0 Alpha (dd23ab17120d), including Body Controls 11/11,
  pole-control regression 85/85, and direct-package import 12/12.
- Focused secondary math from the exact ZIP passes 46/46 tests: 34 secondary
  math tests and 12 secondary capsule tests.
- The new continuous sphere-set path selects the earliest bounded analytic
  sphere sweep hit deterministically, with final bounded sphere-set
  reprojection. It is covered by host-independent math and the exact archive
  pole; it does not claim general rigid-body dynamics.
- Additional exact-package collision and generalization checks pass for the
  bounded multi-sphere, force-offset torque, selected-control self-collision,
  production-character fixture, moving/deforming mesh, moving capsule, and
  moving sphere slices.
- The production-character check now enables the current nine-row torso target
  layout, including the coupled Spine row, across all three frozen proportion
  profiles; source-pose and source-action recovery remain verified.
- The exact moving-capsule foreground receipt records 22 independent finite
  clearance samples and the expected recovery journey. The known
  Bforartists alpha-host shutdown access violation occurs after the passing
  receipts and is recorded separately.
- Host-independent regression is source-hash bound and passes 379 collected
  tests, 416 passing call reports, and 37 unittest subtests with no failures,
  collection errors, or skips. The selected/excluded source counts are 56/114.

The coupled Pelvis/Spine/Chest implementation remains a bounded procedural
position solver. It does not claim torso orientation, anatomical joint-limit
shaping, dynamic balance, learned temporal quality, animator usability, or
Cascadeur parity.

## Temporal boundary

training/b4artists_ml/train_temporal_minimal_v1.py was exercised and stopped
before training. It created no candidate artifact and permitted no promotion.
The preflight correctly blocks on qualified action/skeleton-disjoint corpus
identity, reviewed contact/intent provenance, and separate human identity and
authorization receipts. No learned model was trained, promoted, or installed.

## Remaining gates

The aggregate gate remains ACTIVE_INCOMPLETE. The remaining work requiring
external evidence is independent animator review, a qualified disjoint corpus
with valid identity and review receipts, matched Cascadeur conversion and
comparison, and finally the entitlement-aware Cascadeur connector. The
standalone Bforartists workflow remains available for controlled testing while
those gates are pending.
