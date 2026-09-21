# Next experiment: contextual sparse pose completion

Status: semantic data, contextual training, pinned length projection and callable research backend implemented. See CONTEXTUAL-POSE-RESULTS-v1.md for passing and failing evidence. Actual-rig integration and the full acceptance sequence below remain incomplete.

## Hypothesis

Other limb targets, torso/head context and the animator's starting pose reduce bend ambiguity that a single endpoint and length ratio cannot resolve. A model should propose plausible coordinated body poses and preserve explicit pins through constraint projection. Reconstructing one ground-truth elbow is only one evaluation dimension.

## Implementable sequence

1. Extend the verified BVH decoder to produce synchronized semantic joint samples for pelvis, spine, chest, neck/head, shoulders, elbows, wrists, hips, knees and ankles. Keep source frame/clip/side identifiers. Validate transforms and new landmarks against actual host imports.
2. Define rig-independent coordinates using immutable body/rest references and explicit pelvis pose. Include skeleton proportions and masks for available target positions/orientations. Separate observations from desired outputs; never leak a hidden elbow into its input. Account for BoneForge/Rigify rest-axis differences before using hand orientation.
3. Establish equally conditioned baselines: fixed/current pose, linear regression, and a compact nonlinear model. Include the other endpoints, head/body context and optional animator pole hints. Compare an endpoint-only ablation to show whether context helps. Do not adopt restricted research code or label an untrained network as working ML.
4. Train with independent subject-number splits, varied proportions, random input masks and realistic target perturbations. Preserve the original motion sequence boundaries. Record training-only normalization and reproducible seeds. The current V1-V4 confirmation clips are now diagnostic and cannot become a new blind test by renaming them.
5. Predict a full semantic pose or normalized bone directions, then project the selected result onto rig lengths, joint limits and explicit pins. Retain editable controls, source actions, rollback, save/reload and user influence. No writes to mechanism constraints or hidden destructive retargeting.
6. Test the full end-to-end workflow on actual default BoneForge and Rigify rigs and bound meshes. Learned arm participation must be asserted; geometric fallback must not count as learned support. Also assert pinned endpoints, lengths, orientation continuity and preservation of opted-out controls.

## Acceptance and evidence

Freeze the model and protocol before fresh confirmation. Report paired reconstruction and pin errors, per-clip/per-rig failures, domain coverage, cold/warm latency and memory. Separate synthetic proportion stress from real character evidence. Compare generated alternatives visually and collect animator accept/correct decisions; a plausible alternative may differ from a single recorded pose.

This is the route toward the existing whole-body objective, not a replacement for temporal contacts, learned inbetweening, physics, secondary motion, quadrupeds, production interactions or the optional connector. Keep those requirements active in REQUIREMENTS.md.
