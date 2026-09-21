# Humanoid workflow review and exact contact keys

The user authorized75total evaluations, preserving the existing2026-09-09T19:24:05Zdeadline, full endpoint and all50prior evaluations. The focused humanoid workflow is not yet complete. Quadrupeds, connector, advanced angular momentum, secondary motion and broad rig coverage remain deferred. Repeated selector fitting is paused.

## Concrete correction

The first three-anchor crouch/recover scene exposed merged adaptive contact keys. Native insertion of7.625and7.62890625produced one key; FCurve.update() also merged independently allocated close keys. Allocating exact samples, sorting them and recalculating handles separately retains both times and evaluates their midpoint correctly. The worktree contact correction now uses those operations. Its drift/orientation thresholds, four-refinement cap, original-pose checks and recovery rules are unchanged.

All14existing contact tests and6native motion/contact integration tests pass. The original implementation, unsuccessful first patch, native API probes and failing scene reports are preserved. This is a tested worktree fix, not a new packaged release; the existing0.17.5ZIP remains unchanged and differs from current contacts.py. Full current-source package regression and packaging remain pending. The host still exits with3221225477after passing assertions.

## Actual-rig review artifacts

Each scene uses authored frames1,11and21for a planted-foot crouch/recovery on a real fixture rig. It preserves original source, authored interpolation, contextual procedural candidate and any accepted correction as editable native actions. The contact failure rolls back; a rejected correction is never applied. Keep and Restore Source pass, and the saved file retains an inspectable candidate.

| Rig | Authored pelvis range | Contextual pelvis range | Max contextual tick | Contact result |
|---|---:|---:|---:|---|
| boneforge | 0.150000 | 0.338094 | 40.5ms | Rejected: rotation discontinuity |
| rigify_basic | 0.150000 | 0.338132 | 55.3ms | Rejected: rotation discontinuity |
| rigify_default | 0.150000 | 0.338132 | 108.2ms | Rejected: rotation discontinuity |

Files are under training/b4artists_ml/results/humanoid-workflow-review-v4/{boneforge,rigify_basic,rigify_default}/. Open the corresponding *-crouch-recover.blend file and scrub1to21. The internal READ ME explains the candidate, original action and known errors. These are controlled skeleton/rig fixtures, not finished production-character animations or a rendered animator assessment.

The original source-action neighbor poses can differ substantially from newly authored poses. In all three cases, contextual pelvis excursion more than doubles the authored range. This is an observed mismatch and a hypothesis about the limb-branch failure, not proof of its sole cause. Next compare context/tangents derived from authored neighbors against the same scene, thresholds and source-preservation requirements. Do not clamp away errors or promote an unqualified model.

No trained temporal model was used; this is an explicitly procedural workflow baseline. Independent animator assessment, broad motion coverage, current GUI usability, full responsiveness and Cascadeur comparison remain unverified. Existing source snapshots and prior evidence are retained. The code reviewer is unavailable (uv child-spawn failure); author inspection and tests are not independent review.
