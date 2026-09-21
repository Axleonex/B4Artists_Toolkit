# Quadruped optional orientation targets — 0.29.0

Version 0.29.0 extends the generated Rigify cat, horse and wolf Body + Four Paws workflow with optional world-space orientation targets. Each helper has a Rotation option. When enabled, the corresponding native Rigify torso or paw IK control follows the helper axes while the existing bounded position solver preserves the requested body and paw points.

This is a separate deterministic quadruped path. It does not reuse the humanoid 17-joint model, download a model, infer natural motion or change native Rigify constraints.

## Qualified workflow

- Start from a generated Rigify cat, horse or wolf with all four limbs already in IK.
- Move the body and four paw helpers; independently enable Rotation on any helper.
- Solve positions in at most eight residual passes and apply enabled control orientations through Blender pose-space conversion.
- Keep one editable full-control pose anchor or cancel and restore the source.
- Reject a changed helper or Rotation option at Keep until it is solved again.
- Recover a solved position/orientation session after save/reload.
- Reject metarigs, mixed/FK limb modes and locked, constrained or driven writable channels before mutation.

## Evidence

`training/b4artists_ml/results/quadruped-orientation-source-v1.json` records 478 passing assertions across 51 suites using one runtime hash set. The direct suite generated cat, horse and wolf rigs in Bforartists, enabled all five orientation targets, and measured zero control-orientation residual in each fixture. Maximum paw-position residuals remained below `7e-7` world units, with scale-aware tolerances between `7.84e-5` and `3.94e-4`.

`training/b4artists_ml/results/quadruped-orientation-package-v1.json` records 38 passing checks from the unpacked archive with the offline guard active and zero outbound runtime calls. The exact package is `releases/b4artists_ml_v0.29.0.zip`, contains 48 files, and has SHA-256 `105f5c32dc4dc1c178b25744cc47ca5b21ad193b7b5d7b48121cc1d17beee530`.

Bforartists wrote passing reports and then exited with Windows status `3221225477` in the automated processes. Clean host shutdown remains unqualified.

## Remaining scope

This release does not qualify pole direction, automatic paw planting, detailed spine/head shaping, direct metarig use, imported/custom quadrupeds, contact detection/correction, balance, gait, flight, learned posing or learned temporal motion. Human usability reviews and equivalent Cascadeur comparisons remain at zero, so parity or superiority is unverified.
