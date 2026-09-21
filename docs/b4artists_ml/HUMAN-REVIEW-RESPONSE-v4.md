# Human review response v4

## Outcome before visual review

The corrected-display Axlbot v3 review was imported without authorizing model
training or promotion. Its eight actionable jump, landing, and run findings drove
the v19 repair-2 candidate. BoneForge and Rigify Basic landings that the reviewer
accepted remain preserved.

The deterministic successor matrix passes all 16 declared cases across
BoneForge, Rigify Basic, Rigify Default, and the authored Unity import. The
focused evidence receipt is:

`training/b4artists_ml/results/procedural-vertical-slice-v19-repair2-focused.json`

## Review-directed changes

- Added reachable coupled pelvis/Spine/Chest orientation shaping with explicit
  projection evidence and contact re-pinning.
- Added jump anticipation, whole-body takeoff, an authored flight-end pose,
  pre-impact extension, impact, post-impact absorption, follow-through, and
  recovery.
- Increased jump clearance while preserving native ballistic refinement.
- Made run arms travel with the advancing pelvis and swing opposite the legs;
  lengthened stride and retained short flight phases.
- Reversed the imported arm bend hint and kept imported landing torso tilt under
  the declared two-degree limit.
- Smoothed landing contact onset on Rigify/imported rigs. BoneForge alone uses
  exact impact locking without pre-contact blending because both one- and
  two-frame pre-contact blends were proven unreachable and failed closed.

## Production and learning boundaries

- Nine bounded production-character/rig probes pass.
- Three frozen body-proportion variants pass the new paired torso-orientation
  projection with source-action recovery and visible mesh deformation.
- The minimal temporal pipeline recomputes source receipts, remains blocked
  before importing or training a learner, creates no candidate artifact, and
  keeps model promotion disabled. The present corpus is not action/rig/skeleton
  disjoint and lacks the required manifest-bound review/identity receipts.
- Cascadeur remains disabled pending entitlement and its existing prerequisites.

## Required human review

Open `review-directed-followup-reviewer-v4/reviewer.html` and rate all eight
comparisons. This is deliberately non-blind because the baseline was reviewed
previously. For each case, verify:

- jump: anticipation, height, whole-body motion, knee direction, impact,
  absorption, follow-through, and popping;
- landing: descent before impact, knees bending after impact, foot stability,
  and torso balance;
- run: recognizable running rather than skipping, consistent center of gravity,
  longer stride, opposite arm swing, and stable contacts.

The review is evidence for the next deterministic engineering decision only. It
does not authorize training, model promotion, or Cascadeur activation.
