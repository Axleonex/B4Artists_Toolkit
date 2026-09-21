# Next required milestone: learned temporal motion

Status: first backend experiment implemented and rejected by quality gates; see TEMPORAL-MOTION-v1.md. Runtime workflow remains unimplemented. This records code-based findings from the contact milestone so the next step advances the original learned-motion requirement rather than adding more pose-only features.

## Existing evidence to reuse

- training/b4artists_ml/bvh_data.py Motion retains declared channel rotations, parent hierarchy, frame_time, frame values and evaluated world transforms. The bounded local cache and manifests already provide reproducible motion inputs; do not redownload or expand them by default.
- context_data.py defines the 17-joint semantic skeleton and positive reference scale. semantic_motion defaults to stride=8 and normalizes each frame in its own ground-truth pelvis frame. Those defaults were suitable for the prior pose experiment, not an end-to-end temporal root-motion predictor.
- The current pose network predicts one pose residual from sparse spatial observations. Its prior-pose validation regression and linear-baseline advantage remain recorded in its model card. Renaming it or interpolating its outputs does not satisfy learned inbetweening.
- contacts.py now provides editable, non-stacking contact correction and original-rig target checks. Its correction retains source animation and priority poses. These checks can evaluate a future temporal backend; its geometric output is not training evidence for a learned model by itself.

## Leakage and representation requirements

Use contiguous frames with recorded frame_time. Express each temporal window in a known anchor/reference frame, preserving unknown pelvis translation and orientation as prediction targets. Do not feed hidden frames' ground-truth pelvis bases/origins to the model through the existing per-frame normalization. Exclude artificial T-pose initialization from motion labels.

Inputs must distinguish animator-provided poses, context frames, timing, partial-body masks and explicit contact hints from hidden target motion. Separate oracle-contact evaluation from contacts available or inferred from the same observations at inference time. Hard priority poses must remain exact at candidate application.

Keep clip/window identities in every split. Overlapping windows from one clip must not cross train/validation/test boundaries. Existing confirmation clips were already inspected for pose research; they cannot be represented as a newly blind motion study. Recheck data/code/weight distribution suitability before training or packaging new models, using the recorded publisher and conversion provenance.

## Next implementation and evaluation

Research a compact local temporal architecture and compare it with deterministic interpolation and a simpler statistical baseline using identical observations. Preserve complete root trajectories, quaternion/rotation continuity, timing and editable rig control output. Pre-register acceptance metrics before inspecting held-out motion outcomes: endpoint and priority errors, contact drift, segment lengths, velocity/acceleration discontinuities, reconstruction, runtime and memory. Retain failed candidates and do not replace shipped weights merely because training loss decreases.

Build an actual short-gap animation workflow with preview, strength/selectivity, cancellation, source recovery and save/reload. Validate on known BoneForge/Rigify rigs and bound meshes, then broaden proportions/imports. Motion quality, style preservation, production coverage and an equivalent Cascadeur/animator comparison remain separate acceptance requirements.

Support/COM, gravity, momentum, secondary motion, quadrupeds and the optional entitlement-aware connector remain mandatory parts of the full goal. They must not be silently dropped while the temporal backend is developed.


V2 update: complete source ancestry, differentiable FK and whole-window temporal losses are implemented and tested; see TEMPORAL-MOTION-v2.md. Structural stretching is fixed, but generalization remains inadequate. The next experiment must address data/conditioning coverage and untouched evaluation while retaining actual-rig integration as required work.


V3 update: the curve representation fits the hidden-answer diagnostic well, and a nonzero kernel predictor improves average validation position by 1.86% but fails full quality gates. See TEMPORAL-MOTION-v3.md for the controlled comparisons, observed-input coverage and next data/root-context/cross-rig work. Oracle diagnostics are never deployable predictions.

The V3 gravity-alias diagnostic verifies that physical motion tilt relative to fixed gravity is erased by current anchor normalization. Prioritize explicit gravity/support conditioning and coordinate-versus-physical-transform tests alongside bounded coverage and actual-rig work.


V4 update: explicit gravity/support context and physical-versus-coordinate tests are implemented; direction-only learning remains below quality gates. See GRAVITY-CONTEXT-v4.md. Next physical work is actual-rig COM/support analysis with an explicit mass model, not automatic ballistic pelvis correction. Retain all learned-motion, data, cross-rig and full-product requirements.

V5 update: a frozen subject-disjoint holdout evaluator now tests the selected V4 gravity learner on cached subjects 16 and 35, excluding subject 13 because it appears in earlier training/confirmation material. Across 192 windows and 3,776 query frames, the learner is 7.25% worse than the frozen V3 control on position, also fails velocity, acceleration and cohort gates, and remains research-only. See `TEMPORAL-HOLDOUT-v1.md` and `training/b4artists_ml/results/temporal-holdout-v1.json`. The holdout is now locked evidence; the next experiment must address data/support and root-context coverage without reusing it for selection.

V6 update: the validation-selected `motion_relative_gravity_2.0` candidate combines the existing root-context representation with explicit gravity direction. On the locked holdout it improves position by only 0.16% versus the V3 control but fails velocity, acceleration and cohort gates. See `TEMPORAL-ROOT-CONTEXT-v1.md` and `training/b4artists_ml/results/root-context-holdout-v1.json`. Root-path/derivative quality, actual-rig integration and all human/Cascadeur gates remain open.

V7 update: the authored-motion preview now exposes bounded procedural strength/selectivity, with exact endpoint semantics, shortest-path rotation blending, live-setting stability, source recovery and explicit `learned=False` candidate provenance. Bforartists assertions pass (9/9), with the known unclean `ucrtbase.dll` shutdown exit recorded separately. This advances the procedural workflow only; learned temporal quality, independent animator review and Cascadeur comparison remain open. See `TEMPORAL-PROCEDURAL-STRENGTH-v1.md` and `training/b4artists_ml/results/temporal-procedural-strength-v1.json`.

V8 update: a read-only audit of the frozen 20-clip corpus finds action identities `01`, `04` and `17` crossing train/validation/test, and no rig or skeleton identity field in the manifest. Action- and rig-disjoint learned evaluation is therefore unqualified; no new model was trained or promoted. The next data checkpoint must freeze action groups, add source-rig identity, and obtain reviewed contact/intent provenance before another temporal family is selected. See `ACTION-RIG-DISJOINT-AUDIT-v1.md` and `training/b4artists_ml/results/action-rig-disjoint-audit-v1.json`.

V9 update: an outcome-independent action-only partition proposal now assigns complete action groups without leakage using a stable hash rule. It remains explicitly unqualified for temporal promotion because rig identity and reviewed contact/intent provenance are missing. No frozen manifest was rewritten and no model was trained. See `training/b4artists_ml/results/action-disjoint-protocol-v1.json`.

V10 update: a fail-closed temporal-training boundary check now blocks future learned training until action-disjointness, rig/skeleton identity, and reviewed contact/intent provenance all pass together. This is a guard, not a learned-quality result; current status is blocked by missing evidence and no model is promoted. See `training/b4artists_ml/results/temporal-training-boundary-v1.json`.

V11 update: a read-only audit of the pinned BVH cache verifies all 20 manifest checksums and derives six distinct 38-joint skeleton-topology fingerprints, one per cached subject. This strengthens provenance but does not establish source-rig/retargeting identity. Action `01` links all six skeleton groups, making the current action+skeleton partition one connected component and therefore infeasible without a new qualified corpus/protocol. Training and promotion remain blocked. See `training/b4artists_ml/results/cached-skeleton-provenance-v1.json` and `ACTION-RIG-DISJOINT-AUDIT-v1.md`.

V12 update: a deterministic, outcome-independent search finds the least-destructive reduced joint action/skeleton proposal by excluding action `01`, retaining 14/20 rows across three structural components with no proposed action or topology leakage. The proposal is deliberately not treated as a qualified evaluation: its proposed cohorts are only 2/1/11 rows, it drops an action group, derived topology is not rig identity, and reviewed contact/intent provenance is still absent. The fail-closed gate remains blocked and no model was trained or promoted. See `training/b4artists_ml/results/joint-action-skeleton-protocol-v1.json` and `training/b4artists_ml/results/temporal-training-boundary-v1.json`.

V13 update: a fail-closed temporal-corpus intake validator now defines the exact future manifest and receipt contract. The current 20-row corpus is rejected because explicit action/source-rig/skeleton fields, a manifest-bound reviewed contact/intent receipt, and a separate manifest-bound identity/authorization receipt are missing. This preflight does not authorize training; it makes the next data handoff deterministic. See `TEMPORAL-CORPUS-INTAKE-v1.md` and `training/b4artists_ml/results/temporal-corpus-intake-v1.json`.

V14 update: the temporal training boundary now consumes the intake receipt as a required gate. The current boundary remains `BLOCKED_DATA_BOUNDARY_UNQUALIFIED`; no model was trained or promoted. This prevents a future qualified-looking action audit from bypassing the explicit corpus-intake and human-provenance contract.
