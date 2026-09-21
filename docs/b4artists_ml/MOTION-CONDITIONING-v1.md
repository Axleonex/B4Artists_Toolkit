# Motion conditioning contract v1

Status: schema contracts pass. Contact labels, trained use, runtime integration, and animation quality remain unqualified.

## Purpose

The learned motion prior now has an explicit interface for facts that the previous world-pose models either omitted or inferred implicitly. The interface distinguishes animator commands, measured scene geometry, reviewed labels, weak metadata, heuristics, and model predictions.

Unknown values must be zero and carry an explicit false mask. This prevents hidden target motion or missing labels from leaking into training inputs.

## Per-frame conditioning

The 483-feature packed representation contains:

- Contact probability, known mask, confidence, and provenance for left/right feet and hands.
- Support point, normal, velocity, and known mask for each contact effector.
- Signed distance, surface normal, known mask, confidence, and provenance at the root and four effectors.
- A probability distribution over 14 motion intents: walk, run, jump, landing, turn, crouch, reach/object interaction, recovery, interaction, aerial, combat, dance, gesture, and other.
- A probability distribution over nine broad style tags.
- Desired root velocity, facing, known mask, confidence, and provenance.
- Exact authored root values/masks and local 6D rotations/masks over the full hierarchy.
- One-hot provenance for authored, reviewed, measured, metadata, heuristic, and model-derived values. Unknown provenance is represented by zeros.

Only the 17 semantic rig controls can be marked authored. Six retained hierarchy helper joints remain latent. Each authored rotation exposes all six rotation coordinates or none.

## Trust policy

Heuristic evidence cannot carry confidence above 0.35. Description/style metadata cannot exceed 0.5. Measured scene queries, reviewed labels, and animator-authored intent retain distinct provenance instead of sharing a generic `known` bit.

The confidence value informs the learned prior; it does not weaken deterministic authored-control projection. Authored pins, explicit contacts, joint limits, collision checks, and priority poses remain hard post-generation constraints.

## Contract evidence

The schema passes exact authored-value transport, hidden-value isolation, semantic-only masking, unit-normal, probability-distribution, confidence/provenance, dimension, and invalid-input checks. Nine invalid cases are rejected, including hidden action leakage, heuristic overconfidence, partial rotation masks, and values outside authored masks.

Evidence: `training/b4artists_ml/results/motion-conditioning-contract-v1/report.json`.

## Remaining evidence

The current CMU corpus has no reviewed contact or scene labels. Height/speed estimates remain heuristic proposals and cannot train hard contact behavior at high confidence. Before model fitting resumes, a deterministic subject-held-out cohort split and a representative contact-review queue must be frozen. Landing, takeoff, support transitions, moving contacts, hand contacts, uneven ground, and collision/penetration examples need explicit coverage.
