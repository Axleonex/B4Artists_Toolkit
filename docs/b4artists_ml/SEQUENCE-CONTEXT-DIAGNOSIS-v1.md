# Motion-context diagnosis and research conditioning

The frozen sequence models underuse neighboring authored motion. This conclusion is supported by paired inputs and outputs; it is not proof that explicit tangent features will solve learned-motion generalization.

## Evidence

All 1,926 boundary-mask training requests reproduced inference conditions, baselines, targets and masks exactly. The subsequent paired diagnostic used 365 training clip/gap pairs and all 384 development pairs. Each pair retained the same target and authored endpoints while testing absent context, genuine neighboring poses, and stationary exterior poses. Both frozen direct seeds were tested; no fitting, new assets or confirmation access occurred.

| Method | Development position error without context | With genuine context | Prediction displacement when genuine context becomes stationary |
|---|---:|---:|---:|
| Linear control | 0.160654 | 0.160654 | 0 |
| Shape control | 0.160654 | 0.118847 | 0.087043 |
| Direct seed 20260909 | 0.162229 | 0.162322 | 0.000135 |
| Direct seed 20260910 | 0.163388 | 0.163454 | 0.000128 |

These are canonical-space interior Euclidean position errors, averaged by window. They are diagnostic and do not replace protected acceptance metrics. The procedural shape control reduces position error by about 26% with context. The direct models respond weakly to actual exterior motion, including on the sampled training pairs. Adding context does not materially improve their development error.

The earlier apparent context deficit largely reflects the stronger procedural control benefiting from context, rather than a large increase in model absolute error. Both seeds still fail the original development requirements. Familiar proportions also do not remove the deficit. Projection and request serialization are not supported as the sole explanations.

The first paired diagnostic stopped because its assertion required bitwise equality to separately converted supervised rotations. The verified initial difference was 1.11e-16. Its source, plan and failure receipt remain preserved. Version 2 requires exact authored-boundary preservation and a separate 1e-12 label-conversion tolerance. No model or original acceptance gate changed.

## Bounded next hypothesis

`sequence_tangent_context_v1.py` exposes incoming/outgoing authored secants explicitly for each joint's position and orientation mask. It subtracts the current interval secant and scales by interval duration, producing canonical position deviations and angular deviations in radians. Missing neighbors have zero vectors with separate availability flags. Angular vectors use shortest world-relative rotations; hidden payloads are erased before construction.

The 272 added channels extend the existing 394-channel condition to 666. The module supports multiple observations and independent position/orientation masks. It requires newly trained weights; existing weights are incompatible. It is research code and is not bundled, registered or described as trained intelligence.

Thirteen analytic contracts passed, covering nonuniform timing, angular motion, partial masks, hidden payload independence, translation/rotation transformations, missing versus stationary context, boundary preservation and immutable arrays. Corpus verification also passed all 5,778 packets across 78 clips, including 1,926 examples of each mask pattern. The original condition prefix and known observations stayed exact; all added features were finite (maximum absolute value 99.1691). Evidence is in `training/b4artists_ml/results/sequence-tangent-corpus-v1/report.json`. These checks establish input correctness, not motion quality.

The next prospective fit should compare two fixed direct seeds with the existing direct-model reference, adding only these features while holding corpus, target representation, objective, baseline, optimizer budget and acceptance fixed. Freeze the plan and both outputs before development evaluation; no favorable-seed selection or repeated adjacent tuning. A failed result would reject this tested conditioning configuration, not justify claiming quality from the feature tests.

This is one motion-learning investigation. The full goal still requires contact/style intent, physical refinement, rig coverage, responsive animator workflows, human assessment and equivalent Cascadeur comparison. No parity claim or endpoint change follows from this milestone.

Evidence: `results/sequence-context-audit-v2/report.json`, `results/sequence-context-audit-v1/failed-attempt.json`, `results/sequence-tangent-contracts-v1/report.json` under `training/b4artists_ml/`. Routing and review services failed at their Python trampoline; native author verification is recorded and is not independent approval.
