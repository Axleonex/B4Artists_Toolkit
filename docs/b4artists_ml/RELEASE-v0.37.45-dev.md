# B4Artists Machine Learning v0.37.45-dev checkpoint

Date: 2026-09-16

This is a controlled development checkpoint, not a qualified release. The
source-bound archive is
`releases/b4artists_ml_v0.37.45-dev.zip` with SHA-256
`239abcb52bfb21eb661e741f9f5c7d42205e27b8d44ac9487ea90fd06180c791`.

## Verified surface

- Exact-package pole/posing regression: 85/85 tests across 8 suites.
- Exact-package secondary-motion regression: 32/32 tests on Bforartists 5.2.0
  Alpha, including the new explicit `LOCAL_ROTATION` force-at-offset chain.
- The local angular-chain slice requires a contiguous direct parent-to-child
  selection, a nonzero offset assignment on every chain control, and Rotation
  without Location. It converts world torque to each control's local frame,
  transfers bounded equal-and-opposite angular impulses, preserves priority
  samples, and reports weighted control-local angular-momentum residuals.
- Exact-package combined static capsule-plus-mesh compound fixture: 1/1.
- Direct-ZIP imported-humanoid regression: 12/12.
- Bounded production-character generalization probe: 3/3 test methods across
  nine cases: three frozen Unity proportion fixtures, three generated native
  BoneForge/Rigify fixtures, and three project-authored imported
  Mocap/Unity/Unreal FBX roundtrips. Native and authored-import cases remain
  qualified only for the bounded six-endpoint target slice; the authored FBX
  roundtrips are not external production assets.
- Exact ZIP math contract: 50/50 tests (38 secondary math and 12 capsule math).

The angular-chain extension is procedural (`learned: false`) and deliberately
does not claim a general rigid-body, joint-inertia, collision-impulse, or
deformable-body solver. The linear force component remains the World+Location
path. The archive is not installed, promoted, or published.

## Gates that remain open

Foreground usability and independent animator acceptance remain unqualified.
Temporal training and promotion remain fail-closed pending human review,
identity receipts, and a qualified disjoint corpus. Broader collision behavior,
general rigid-body dynamics, finer torso orientation/limits, and production
asset validation remain open. Cascadeur conversion/comparison and the
entitlement-aware connector remain intentionally last and untouched.

The known Bforartists alpha-host shutdown fault occurs after successful
assertions and is recorded separately; the current exact runs also observed
the host's successful-receipt exit-code variant 11. Neither is treated as
clean host shutdown evidence.

Evidence is bound in
`training/b4artists_ml/results/exact-package-pole-v0.37.45.json`,
`training/b4artists_ml/results/exact-package-v0.37.45-secondary-motion-all.json`,
`training/b4artists_ml/results/exact-package-v0.37.45-compound-capsule-mesh.json`,
`training/b4artists_ml/results/current-package-direct-zip-import-v0.37.45.json`,
`training/b4artists_ml/results/exact-package-v0.37.45-production-character-generalization.json`,
and `docs/b4artists_ml/package-test-v0.37.45-dev.json`.
