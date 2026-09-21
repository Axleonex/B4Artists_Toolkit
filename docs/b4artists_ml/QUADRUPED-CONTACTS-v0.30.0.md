# Quadruped four-paw contacts — experimental 0.30.0

This release adds animator-authored paw-contact intervals to generated Rigify cat, horse and wolf rigs. It operates on an active Pose Blending candidate and copies that action before writing correction curves. The existing Ghost Tool and Anim Assist remain separate and unchanged.

## Qualified workflow

1. Capture at least two priority poses and generate a Pose Blending candidate.
2. Keep all four generated Rigify limbs in IK.
3. In Four-Paw Contacts, select a paw and capture its evaluated tip point at the current frame.
4. Author the contact start, end, boundary blend, strength and optional orientation lock.
5. Preview the correction, inspect the reported paw drift and edit the resulting ordinary linear curves.
6. Restore Before Paw Contacts, Discard, Keep Candidate or Restore Source through the retained-action workflow.

The solver samples each authored interval at no more than 0.25-frame spacing and validates at no more than 0.125-frame spacing. It preserves captured priority-pose frames and rejects conflicts instead of changing them. Cancellation, incompatible locks, constraints, drivers, changed contact requests and unsupported rigs restore the input.

## Native evidence

The direct Bforartists test generated real Rigify cat, horse and wolf rigs and introduced separate mid-interval slips on all four native paw IK controls. All three profiles passed:

| Profile | Drift before | Drift after | Solver time | Validation checks |
|---|---:|---:|---:|---:|
| Cat | 0.124854 | 0.00000101 | 21.39 s | 324 |
| Horse | 0.0234546 | 0.000000610 | 12.56 s | 324 |
| Wolf | 0.0378182 | 0.000000508 | 23.87 s | 324 |

Drift is measured as a fraction of the evaluated body-to-paw reference distance. The acceptance bound is 0.0002; locked paw-orientation error remained 0 radians in these fixtures against a 0.001-radian bound. The earlier 0.125-frame fit used 81 samples and took 25.10–52.18 seconds. Quarter-frame fitting used 41 samples, cut measured solver time by roughly half, and retained a margin of about 198 times against the worst accepted position bound.

The frozen source passed 481 tests across 52 separate factory-startup Bforartists suites with one runtime hash set. The exact 49-file archive passed 41 focused tests from an extracted directory while Python outbound calls were denied. Package SHA-256: `2b47a30657c9dc4f6b2f711db399bcf5e9821044241d37780f48a04286bdda13`.

## Boundaries

The contact point and interval come from the animator. No contact classifier, gait generator, balance solver, flight solver, arbitrary-surface collision or learned quadruped motion is claimed. Direct metarig, imported and custom quadrupeds are not qualified. Human reviewed cases and matched Cascadeur comparisons remain zero. The installed Bforartists 5.2.0 Alpha build still returns its independently reproduced `ucrtbase.dll` shutdown failure after writing passing evidence, so clean host shutdown is not qualified.
