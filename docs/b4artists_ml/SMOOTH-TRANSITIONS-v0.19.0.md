# Smooth Transitions — experimental 0.19.0

Whole-body Motion now offers an optional Smooth Transitions setting. It reduces abrupt speed changes between authored poses while keeping editable key values and priority poses. This is procedural curve interpolation; it does not satisfy the learned-motion requirement.

## Using it

Capture full-body humanoid poses, choose Whole-body Motion, enable Smooth Transitions, and Generate Whole-body Preview. Scrub the candidate and capture any required hand/foot contacts. Preview Contact Correction checks the smoothed limb curves before accepting its copied result. Keep/Discard and Restore Source Animation retain the normal recovery workflow. Smooth Transitions starts off and persists with the rig; active jobs do not resume after saving or loading.

Changing the smoothing setting while generation is paused cancels that job and preserves the new setting. Smoothing/publication failures restore source animation, rig modes and temporary-action inventory. Contact correction smooths only its captured limb controls, preserving unrelated curve edits. Unsupported axis-angle or ambiguous quaternion-sign sequences are rejected without rewriting authored keys.

## Evidence

- 398 current-source native cases across 40 suites pass, including 29 new smoothing, boundary, contact and publication/recovery checks.
- Six reach/hold and mechanical root-yaw references across BoneForge, basic Rigify and default Rigify reproduce the accepted research contact, priority and local derivative numbers exactly.
- The three original crouch/recover workflows also pass through the integrated controller and contact solver.
- The exact 41-file archive passes 13 offline workflows: 4 learned-live posing/Keep/Discard cases, 3 smoothed crouch/contact/Keep/Restore cases, and 6 smoothed reach/turn/contact/Discard cases. Those six cases repeat 9,813 dense contact checks and reproduce reference contact maxima exactly.
- The original 0.0002 limb-unit position tolerance, 0.001-radian orientation tolerance and four-refinement cap remain unchanged. Smoothed contacts use quarter-interval validation and refine the actual cubic output before publishing.

One initial Keep test incorrectly expected no additional action after Keep; its preserved failure was corrected to require the retained editable action. All final checks pass. Existing default interpolation paths remain covered by the full regression.

## Qualification limits

These are controlled skeleton references, including a mechanical root-yaw transition rather than a natural turning gait. Local angular-velocity jumps improve approximately 95–97% in those references; this does not establish complete motion plausibility, style, joint-limit safety or full-sequence continuity. Source-visible generation is cooperative, but current viewport responsiveness and human usability remain unverified. Some native jobs overlapped, so their elapsed timings are not controlled performance comparisons. Recorded generation slices reached about 0.74 seconds during those overlapping runs; isolated publication/smoothing profiling remains necessary before responsiveness can pass.

The host completes assertions before its previously isolated shutdown access violation; clean process termination remains unqualified. Independent review could not start because its Python entry point failed. Author source inspection, automated validation and independent human assessment are kept distinct.

No trained temporal model, additional assets, paid API, installation, Git commit or push is included. Learned motion, broader characters and meshes, physics/refinement, deferred quadrupeds/connector and equivalent Cascadeur comparison remain open. The full original goal is ACTIVE and incomplete.

See package-test-v0.19.0.json, BROADER-SHAPE-RESEARCH-v1.md, the shape-runtime-full-v1 regression, exact package report and runtime reference directories.
