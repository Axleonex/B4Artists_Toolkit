# B4Artists Machine Learning v0.37.40-dev checkpoint

Date: 2026-09-16

This is a controlled development checkpoint, not a qualified release. The
source-bound archive is
`releases/b4artists_ml_v0.37.40-dev.zip` with SHA-256
`950ac89e2df372da944d2ec37851a261562791b8ef2f5149c64900424618924f`.

## Verified surface

- The archive contains the current 54-member `b4artists_ml` runtime package.
- Exact-package checks imported the package directly from the ZIP in
  Bforartists 5.2.0 Alpha (`dd23ab17120d`), including Body Controls 11/11,
  pole-control regression 85/85, and direct-package import 12/12.
- Focused secondary math from the exact ZIP passes 44/44 tests: 32 secondary
  math tests and 12 secondary capsule tests.
- Additional exact-package collision and generalization checks pass for the
  bounded multi-sphere, force-offset torque, selected-control self-collision,
  production-character fixture, moving/deforming mesh, moving capsule, and
  moving sphere slices.
- The exact moving-capsule foreground receipt records 22 independent finite
  clearance samples and the expected recovery journey. The known
  Bforartists alpha-host shutdown access violation occurs after the passing
  receipts and is recorded separately; it is not treated as a clean-exit
  claim.
- Host-independent regression is source-hash bound and passes 377 collected
  tests, 414 passing call reports, and 37 unittest subtests with no failures,
  collection errors, or skips. The selected/excluded source counts are 56/114.

The coupled Pelvis/Spine/Chest implementation remains a bounded procedural
position solver. It does not claim torso orientation, anatomical joint-limit
shaping, dynamic balance, learned temporal quality, animator usability, or
Cascadeur parity.

## Temporal boundary

`training/b4artists_ml/train_temporal_minimal_v1.py` was exercised and stopped
before training. It created no candidate artifact and permitted no promotion.
The preflight correctly blocks on qualified action/skeleton-disjoint corpus
identity, reviewed contact/intent provenance, and separate human identity and
authorization receipts. No learned model was trained, promoted, or installed.

## Remaining gates

The aggregate gate remains `ACTIVE_INCOMPLETE`. The remaining work requiring
external evidence is independent animator review, a qualified disjoint corpus
with valid identity and review receipts, matched Cascadeur conversion and
comparison, and finally the entitlement-aware Cascadeur connector. The
standalone Bforartists workflow remains available for controlled testing while
those gates are pending.
