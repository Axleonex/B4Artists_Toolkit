# Full-hierarchy subject and task cohorts v1

Status: split and materialization contracts pass. These are future-model development cohorts, not untouched confirmation or human-quality labels.

## Subject split

Before another model fit, the 85 CMU subjects were divided into 68 training subjects and 17 development subjects. The selection used only weak motion tags and a frozen deterministic coverage algorithm; it did not read pose arrays or model outcomes. SHA-256 tie-breaking makes the result reproducible.

Development subjects: `14, 15, 31, 49, 70, 75, 79, 82, 86, 88, 94, 108, 111, 113, 120, 140, 144`.

There is no subject overlap. Any next model must exclude all 17 development subjects from fitting and training-derived normalization.

These source clips appeared in earlier research models. This is therefore a clean holdout for the next model only, not an independently untouched corpus. The separate confirmation material remains sealed.

## Task windows

The split contains 1,125 deterministic development windows covering gaps of 8, 16, 32, 64, and 96 frames. Each task/gap has at least six windows, with a maximum of four windows from one subject. The represented weak-metadata tasks are walking, running, jumping, turning, crouching, reaching, recovery, aerial motion, interaction, combat, dance, gesture, and difficult sparse transitions.

All 1,125 windows were materialized after the split froze. They produce finite 23-joint hierarchy state and 483-feature conditioning, use only development subjects, and preserve the selected sparse-control pattern.

## Missing qualification cohorts

Four requirements remain explicitly unfilled:

- Static motion needs a frozen low-motion detector followed by representative review.
- Landing needs event-level descending-to-support proposals and representative review because source metadata has no landing labels.
- Contact quality needs reviewed single/double support, takeoff, landing, hand contact, moving support, uneven ground, and penetration-risk cases.
- Naturalness, intent preservation, and correction effort require independent animator evidence.

Weak task metadata can organize development sampling. It cannot establish naturalness, intent, or contact correctness.

Evidence: `training/b4artists_ml/results/hierarchy-cohorts-v1/` and `training/b4artists_ml/results/hierarchy-cohorts-contract-v1/report.json`.
