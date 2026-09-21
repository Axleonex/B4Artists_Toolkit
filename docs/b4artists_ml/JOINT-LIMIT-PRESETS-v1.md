# Joint-limit presets — 0.33 source slice

Status: integrated and source-tested after experimental 0.32.0. This is a 0.33 development slice, not a new package release.

## Animator workflow

Whole-Body Pose now offers an opt-in **Conservative Humanoid v1** joint-limit preset. It applies broad animation-safe swing/twist ranges only to controls whose semantic roles are supplied by the active verified rig adapter. Verified skeletal-joint space is used where available; otherwise the existing rest-local control space is used. Unmapped controls remain unchanged.

The panel displays `Source: B4ML preset v1` for applied values. Editing enablement, measurement space, swing, twist, or bend settings changes the source to `Custom override`, and the override survives preview cancellation and restart. These values are artist-editable starting estimates. They are neither clinical anatomy nor learned output.

## Compatibility and preservation

The focused suite covers BoneForge, generated Rigify Basic and Default, Rigify Basic and Default metarigs, and an independently authored FBX Unity humanoid. Each adapter maps 20 semantic controls. Generated Rigify leaves two unmapped spine controls unchanged; the metarigs leave one unmapped control unchanged. BoneForge and generated Rigify Default also complete sparse whole-body solves with 20 active limits and zero measured joint-limit error.

Applying a preset changes settings only and preserves the current pose. A running solve rejects preset application without changing settings or pose. Custom overrides persist between previews through the existing saved settings path.

## Evidence

- Focused v7: five tests passed, zero failures/errors, SHA-256 `114eaf491ccd746f7d7608616de01e5a6cd4a68f31415ab6b77693bc73fcd79b`.
- Affected v3: 42 tests across five suites passed, zero failures/errors/skips, one runtime hash set, SHA-256 `a9ad91de37bc24a0b27f323c178ec1957857d0266ad21664d6c2efce31093a58`.
- Real-window v5: modal solve, Escape recovery, Undo/Redo, Keep, and source-mode restoration passed in 7.23 seconds. JSON SHA-256 `db304eccc467132d534a6620b977db1aea546430d40efd7870adf0693beea8c5`; screenshot SHA-256 `f9b161914015f29a422bd93010c8e352ab26d9907127932c36451ab61e72f4f0`.

Evidence files:

- `training/b4artists_ml/results/joint-limit-presets-v7.json`
- `training/b4artists_ml/results/joint-limit-presets-affected-v3-regression.json`
- `docs/b4artists_ml/body-preview-ui-vjoint-limit-presets-v5.json`
- `training/b4artists_ml/cache/body-preview-ui-vjoint-limit-presets-v5.png`

Failed exploratory evidence is preserved separately. v1 exposed incorrect fixture/teardown oracles. v3/v4 exposed a transformed BoneForge all-target convergence edge, and the ineffective constrained-retry experiment was reverted. Foreground v1 omitted the required event-simulation host flag; foreground v2 sampled a sparse Rigify retry before its private proxy existed. None is relabelled as passing evidence.

The installed Bforartists 5.1.0 / Blender 5.2 Alpha host still raises the independently isolated `ucrtbase.dll` exception during shutdown after writing passing reports. Clean shutdown and independent animator usability are not claimed.

## Remaining 0.33 work

Head/spine/pole usability, pose mirroring/reuse, rig-mapping diagnostics and bounded manual corrections, unsupported-space error improvements, complete release regression, and exact package validation remain open.
