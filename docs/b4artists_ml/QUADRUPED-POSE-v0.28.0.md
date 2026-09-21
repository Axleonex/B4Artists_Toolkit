# Quadruped Body + Four Paws posing — 0.28.0

Version 0.28.0 adds a separate deterministic posing workflow for generated Rigify cat, horse and wolf rigs. It translates the native Rigify torso control while holding four animator-defined paw IK targets. It does not reuse the 17-joint humanoid model and it does not claim learned quadruped motion.

## Qualified workflow

- Start from a generated Rigify cat, horse or wolf with every limb already in IK.
- Create one body helper and four paw helpers without editing the source action.
- Move the helpers, solve in at most eight bounded residual passes, and inspect the live pose.
- Keep one editable full-control pose anchor or cancel and restore the source.
- Reject changed targets at Keep until they are solved again.
- Recover the pending session after save/reload, then Solve, Keep or Cancel.
- Reject metarigs, mixed/FK limb modes and locked, constrained or driven writable controls before mutation.

The tool preserves the rig's native constraints and writes no generated mechanism or deform controls. Humanoid posing, contact, flight and temporal workflows also reject active quadruped sessions so that two preview owners cannot mutate the rig together.

## Evidence

The source regression aggregate is `training/b4artists_ml/results/quadruped-pose-source-v1.json`: 478 assertions pass across 51 suites using one runtime hash set. The direct quadruped suite generated cat, horse and wolf rigs in Bforartists and measured these maximum paw residuals:

| Rigify profile | Maximum paw error | Body error |
|---|---:|---:|
| Cat | 1.885e-7 | 6.007e-8 |
| Horse | 6.889e-7 | 2.413e-7 |
| Wolf | 3.313e-7 | 3.725e-8 |

The exact archive check is `training/b4artists_ml/results/quadruped-pose-package-v1.json`: 38 checks pass from the unpacked archive with the offline guard active and zero outbound runtime calls. The package is `releases/b4artists_ml_v0.28.0.zip`, contains 48 files, and has SHA-256 `1aaf7ca1a84d54aab3ca786c6aedb5dcceb1e0dab5d84063e5b0799745ac278e`.

Bforartists wrote the passing result files and then exited with Windows status `3221225477` in each automated process. Clean host shutdown is therefore unqualified.

## Remaining scope

This release does not qualify paw or body orientation, pole control, detailed spine/head shaping, direct metarig use, imported/custom quadrupeds, contact detection/correction, balance, gait, flight, learned posing or learned temporal motion. It has no human usability reviews and no equivalent Cascadeur comparison, so parity or superiority remains unverified.
