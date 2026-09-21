# Research rig observation interface

This research-only adapter samples actual BoneForge and Rigify humanoids in their
existing IK/FK mode. It is outside the v0.14.2 installable package. It does not
load or apply a temporal model, generate inbetweens, or claim Cascadeur parity.

`training/b4artists_ml/rig_observations.py` reads exactly start/end and, when
requested, start-minus-one/end-plus-one. Hidden frames are not sampled. It restores
the prior frame/subframe, raw bone/object channels, and rig modes on success,
cancellation, and frame-evaluation failure. It creates no actions or helpers.
Active solver/pose/animation previews are refused. Unsupported reflection, collapsed
or sheared joint frames fail explicitly. Bone roll is removed using each semantic
bone's rest frame; global rotation, translation and uniform scale are normalized.

The schema is `b4ml-semantic-observations-v1`: four sets of 17 world semantic
positions and rest-calibrated orientations, static normalized rest positions,
context flags and timing (667 features). World positions and rotations have explicit
inverse transforms. This is not the existing V6/V8 637-feature, 23-joint,
fixed-offset representation. A corresponding trained model or independently
validated retargeter is required before connecting those weights. Collapsed rig
segments must not be asserted to have constant physical bone lengths.

## Verification

Thirteen focused test methods pass inside the actual Bforartists host with no
skips, covering five supported humanoid rig profiles, transformed objects,
context-free reads, exact source preservation, interrupted sampling and canonical
math. The first host test attempt exposed an unsupported class-method interception
in the test harness, which was corrected. A later test exposed a real restoration
precision problem: reassigning matrix_basis decomposed its Euler/scale channels.
The sampler now restores the original authored channels directly. Prior failed
reports are retained.

A separate final experiment samples a small nontrivial authored FK pose and fits
all 17 semantic joints through body_solver.Session, then cancels it. Every profile
passes the existing pin, bone-length and pelvis-orientation gates and restores
its original source action/pose. These are single measurements, not distributions
or end-to-end animation latency.

| Rig | Two-pose sampling ms* | One-pose fitting ms | Max world position error | Source restored |
|---|---:|---:|---:|---|
| boneforge | 10.15 | 385.24 | 0.000013270 | True |
| basic | 24.25 | 796.60 | 0.000000382 | True |
| default | 48.82 | 871.60 | 0.000000382 | True |
| basic_meta | 15.81 | 581.05 | 0.000000712 | True |
| default_meta | 17.03 | 208.42 | 0.000000712 | True |

*The projection experiment uses two anchors with context disabled; its sampling
column measures those two poses. Four-pose sampling is exercised by the focused
test suite and has no separate performance claim.

Final evidence:
- training/b4artists_ml/results/rig-observations-v4-regression.json
- training/b4artists_ml/results/rig-observation-projection-v2.json
- training/b4artists_ml/results/rig-observation-projection-v2-process.json

The host again exits with code 3221225477 after writing passing assertions. The
previously reproduced host shutdown failure remains a failed lifecycle check.
These cases do not prove mesh quality, imported rigs, quadrupeds, temporal quality,
interactive performance, or independent human usability. Runtime source/package
bytes are unchanged; the existing 230-case and 68-case offline evidence is carried
forward only after checking all prior artifact and runtime hashes.

## Next bounded learning experiment

The existing learned controller was trained against predictions from a base model
fitted to those same training clips. Validation and confirmation remain separate,
so this is not evidence of holdout leakage. However, in-sample base predictions
may make the controller optimistic about that base model's generalization.
A useful next experiment is clip-grouped cross-fitting: train each temporary base
on other training clips, construct controller targets only from held-out training
clip predictions, then evaluate against the already frozen validation gates.
Do not relabel V8 confirmation as fresh, add training clips from any holdout,
relax cohort thresholds, or ship a failed model.
