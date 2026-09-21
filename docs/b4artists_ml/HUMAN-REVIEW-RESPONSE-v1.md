# Human review response v1

Status: review ingested; focused corrective candidates pass deterministic native gates; the exact BoneForge v54 and Rigify Basic v58 run cases have qualified non-blind visual acceptance.

The completed blinded review contains 32/32 locked cases from reviewer `Axlbot` with `10+ years` animation experience. Its validated summary is `training/b4artists_ml/results/procedural-vertical-slice-reviewer-v2/human-review-summary-v2.json`. The canonical export and the post-lock `rigify_basic/land` note remain preserved under `training/b4artists_ml/results/human-review-exports/`.

The review is not a pass for the current procedural packet. Each compared method was accepted in 9 of 32 cases. The largest recurring defects were anatomically wrong or inconsistent elbow/knee bend directions, inward rather than forward reaching, missing or weak jump elevation, hips lagging behind locomotion, uniform timing, foot slide, and landings that did not clearly separate impact from absorption.

## Review-directed candidates

v14 is a separately versioned bend-only experiment. It enables the already bundled local elbow/knee bend-direction prior at full influence while leaving deterministic reach projection, interpolation, contacts, flight, and lifecycle behavior unchanged. Seven focused Bforartists cases passed their existing deterministic gates. Every tested leg request used the learned direction; the out-of-range reach-arm requests correctly failed closed to the authored pole. v14 is not temporal learned motion and is not a promoted model.

v15 preserves v14 and changes two task definitions that the review showed were invalid independently of the solver:

- Reach moves primarily forward instead of mostly inward.
- Landing establishes foot contact at impact, then lowers into a deeper post-impact absorption crouch. It does not introduce midair knee bending.

All eight v15 reach/landing cases pass on BoneForge, generated Rigify Basic, generated Rigify Default, and imported Unity Humanoid. Source restoration and save/reload recovery pass in every case. The fixed receipt is `training/b4artists_ml/results/procedural-vertical-slice-v15-focused.json`.

The focused runs wrote passing case receipts before the known Bforartists Alpha shutdown fault. These direct runs did not persist parent process exit capture, so the focused receipt explicitly leaves clean shutdown unqualified.

v16 attempted to add separate transition-timing overrides while the projected
samples already carried timing. The workflow correctly rejected that case with
`Projected samples already define timing; remove per-transition overrides`.
Its failed BoneForge walk report is preserved as negative evidence rather than
being overwritten or counted as a pass.

v17 removes the second timing authority and keeps projected samples as the sole
timing source. It adds authored forward/vertical hip variation to walk, aligns
run landing hips more closely with landing feet, and extends jump flight from
12 to 16 frames at 30 fps. All 12 walk/run/jump cases pass their deterministic
gates across BoneForge, generated Rigify Basic/Default, and imported Unity
Humanoid. Every case preserves anchor payloads, restores the source, and passes
save/reload. The bound receipt is
`training/b4artists_ml/results/procedural-vertical-slice-v17-focused.json`.
Each jump report independently records the intended frame 7-to-23 flight
interval (`0.5333333333333333` seconds).

## Completed follow-up chain

The later review-directed chain preserves every export and negative candidate rather than replacing them. The v9 review accepted the exact BoneForge v54 run and rejected the Rigify v54 run for excessive jitter and poor flow. The v55 release-blending experiment failed contact reachability, and the v56 label-addressed experiment failed closed because repeated stride labels were ambiguous. V57 introduced exact frame-addressed support-foot damping and reduced lower-limb jerk p95, but left the largest swing-leg spike essentially unchanged.

V58 retains the v57 support-foot targets and interpolates the opposite swing leg through all four toe-off frames. Its exact Bforartists report passes every existing mechanics, contact, source-recovery and save/reload gate. Against v54 native-display samples, lower-limb jerk p95 decreases by about 40 percent, p99 by about 51 percent, and the maximum spike by about 60 percent.

The one-case v11 Axlbot review selected v58 (Candidate B), scored it 4/4/4/5 for naturalness/contact/continuity/intent, marked it production-acceptable, recorded zero estimated corrections and interactions, and applied no visible-failure tags. The exact export and strict import are:

- `training/b4artists_ml/results/human-review-exports/b4ml-review-directed-followup-human-review-v11-axlbot.json`
- `training/b4artists_ml/results/review-directed-followup-reviewer-v11/human-review-summary-v11-native-display.json`

This acceptance is limited to `boneforge/run@v54` and `rigify_basic/run@v58`. It is non-blind and does not establish reviewer identity, training authorization, general animation quality, or a Cascadeur comparison.

## Claim boundary and next work

The exact accepted run cases are now preserved, but no temporal model was trained or promoted, no Cascadeur comparison was run, and the full goal is not complete. The fail-closed temporal pipeline still requires a qualified action- and skeleton-disjoint corpus, manifest-bound contact/intent provenance, and a separate identity and training-authorization receipt. The optional Cascadeur connector remains staged and inactive pending entitlement, verified conversion settings, matched outputs, and independent comparison results. The checksum-bound aggregate is `training/b4artists_ml/results/current-goal-gate-status-v2.json`.
