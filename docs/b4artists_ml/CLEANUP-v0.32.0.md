# B4Artists Machine Learning 0.32.0 — Contact Review and Animation Cleanup

Experimental 0.32.0 adds family-filtered contact-review controls and deterministic, contact-aware animation cleanup. The cleanup workflow smooths handles and removes redundant keys from a copied candidate while preserving fractional priority poses, accepted-contact controls and their pose ancestors, and the original animation.

The feature remains explicitly procedural with `learned=false`. It does not satisfy learned inbetweening, independent animator acceptance, or Cascadeur parity.

## Workflow coverage

- Review contact proposals by compatible rig family, navigate fractional proposal frames, and bulk accept or reject them.
- Clean selected or all captured animator controls with separate smoothing, reduction, strength, and tolerance controls.
- Inspect removed keys, cleaned controls/curves, protected contacts, position and rotation drift, reduction error, derivative continuity, and skipped unsafe curves.
- Cancel with Escape, inspect before Keep or Discard, restore the cleanup input, and later restore the original source animation.
- Preserve Undo/Redo, save/reload, and editable action data.

## Native evidence

The frozen Bforartists source passes 495 tests across 55 clean factory-startup suites with no failures, errors, or skips and one runtime hash set. The aggregate SHA-256 is `8d12b115f6b338e94401fee14c5b46bff113bdad5757bdfc6291da0ecbbd0f`.

Focused cleanup results removed 807 of 2,942 keys in the BoneForge humanoid fixture and 1,485 of 4,301 keys in the generated Rigify cat fixture. Both retained authored priorities and accepted contacts. Maximum measured contact drift was zero position and `2.98e-8` radians rotation for the humanoid, and zero for both measures on the cat.

The exact 50-file archive passes 18 offline tests from its extracted modules. Archive members match the frozen source byte-for-byte, forbidden author identities are absent, and SHA-256 is `9fe0c71b1e5aa54bca37d57cab2ba07db4e989f08818976ac741e5cb8da24f0e`.

Evidence:

- `training/b4artists_ml/results/full-regression-032-v1.json`
- `training/b4artists_ml/results/cleanup-v1-integrated.json`
- `training/b4artists_ml/results/contact-review-ui-v4-integrated.json`
- `training/b4artists_ml/results/cleanup-package-v1.json`
- `docs/b4artists_ml/package-test-v0.32.0.json`

The installed Bforartists 5.1.0 / Blender 5.2 Alpha host still raises the independently isolated `ucrtbase.dll` exception during shutdown after writing passing reports. Clean shutdown is not claimed. Human visual assessment remains unverified.
