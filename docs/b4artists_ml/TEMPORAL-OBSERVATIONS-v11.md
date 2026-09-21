# Shared temporal observations v11

Status: verified research integration component. The complete learned inbetweening
workflow remains unfinished. Package 0.16.0, both shipped pose models and all
existing V9/V10 weights are unchanged. No new model is trained or promoted here.

## Fixed animator-input gap

Whole-body Keep stores a new pose in anchors and restores the source action.
The previous research sample function only observed the source action, so using
it for temporal input would discard the saved animator pose. sample_anchors now
applies the stored controls and canonical rig modes for each observed endpoint,
then restores original state. It resets unkeyed channels between samples so an
applied pose cannot contaminate the next sample. A stored anchor at an exact
outside-context frame is preferred to the action pose. Context remains exactly
one frame before/after; arbitrary nearest-key time spacing is not encoded.
Intervals spanning another authored priority are rejected: callers must process
adjacent intervals and preserve every priority. Subframe anchors are accepted
with at least one frame of separation. No hidden interior frame is sampled as
input. Restoring the user's original playhead is recovery, not a model observation.

Ordinary sample still explicitly samples the source action. Both paths reject
an unresolved whole-body payload even when no live session exists after a runtime
reset. They create no actions, keys or helpers and restore channels/modes/frame
on success, cancellation and frame-evaluation failure.

## One training/rig representation

semantic_motion_data uses the exact rig_observations.encode function. Its 667
features contain four 17-joint position/orientation observations, rest geometry,
context flags and timing. Targets use the same per-bone rest calibration and
have explicit world decoding. Labels are constructed separately; changing hidden
motion cannot alter known inputs or procedural baselines. Linear/SLERP and
Cartesian/quaternion Hermite remain explicitly procedural, and may distort
collapsed semantic edge lengths. Neither is a learned-motion result.

The existing 23-joint targets agree after an explicit orientation calibration
transform, but that does not make 637-feature V9 weights compatible with 667
actual-rig inputs. Missing intermediate joints cannot be reconstructed by padding
or renaming. A matched model and a verified projection to the actual rig are still
required. No constant-length claim is made for collapsed semantic edges.

## Evidence

- Nine semantic-data tests pass in desktop Python and actual Bforartists: hidden-
  label/context isolation, endpoint preservation, similarity/bone-roll invariance,
  world decoding, explicit legacy target conversion and manifest/split checks.
- Nine actual-anchor tests pass, including eight profiles: BoneForge, basic/default
  generated Rigify, basic/default metarigs, and the three independently authored
  imported FK conventions. Saved endpoint world poses and optional context match
  the actual values recorded while authoring; original animation/data are restored.
- All 13 earlier observation tests pass after the change. There are 31 unique
  focused native cases; the semantic tests precede the final selection-only
  correction, whose AST leaves shared encoding unchanged.
- Two separate processes reproduce all feature, target and window-identity hashes:
  2912 windows from 31 training clips and 480 from 10 validation clips. Maximum
  target-conversion error is 9.992007221626409e-16. Source hashes, split ownership,
  sample identities and original quality thresholds are retained. Development
  and confirmation data are not read by this audit. No data is downloaded.

Reports: anchor-observations-v1/v2-regression.json,
semantic-observations-v11a/v11b.json, semantic-observations-reproduction-v11.json,
and semantic-anchor-selection-structure-v1.json under training/b4artists_ml/results.
Host assertions pass before the existing shutdown crash; host lifecycle still fails.
These results do not prove prediction quality, temporal projection, contacts,
visual plausibility, animator usability or Cascadeur superiority.

## Next implementation boundary

Implement a bounded external semantic-proposal projection and editable-action
path, then fit/evaluate a matched predictor through that path. Initialize fitting
from known-anchor interpolation; do not allow hidden source keys on modeled
controls to improve test reconstruction. Preserve unselected channels as source
context, explicitly distinguish them from prediction labels, and test that
poisoning hidden modeled keys leaves generated inbetweens unchanged.

Projection must retain real bone lengths, control/rig-space restrictions, explicit
pins/rotations/limits, exact priority raw controls and complete source recovery.
Build results in an isolated candidate and publish it to the viewport only after
validation. Avoid temporarily bypassing preview ownership or disguising procedural
proposals as learned output. The same geometric projection must be used when
comparing baselines and learned predictions. All original model/cohort gates,
production-rig/quadruped requirements, physics/refinement, optional connector and
independent human/comparative requirements remain open.
