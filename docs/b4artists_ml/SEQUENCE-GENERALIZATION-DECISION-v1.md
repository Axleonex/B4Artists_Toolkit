# Generalization audit and next architecture decision

The current host architecture remains useful; the learned-motion architecture has not earned promotion. This audit changes no acceptance threshold, model, split, goal endpoint, evaluation ceiling or deadline. It is diagnostic evidence, not a formal goal evaluation or an independent review.

## Frozen evidence

The complete audit is training/b4artists_ml/results/sequence-generalization-audit-v1/report.json. Its plan records input and script hashes. It reuses all 768 development windows (96 cohorts) and four frozen models. No training, downloads or confirmation access occurred.

Six development clips match training rest proportions and ten do not, using the existing normalized pairwise-distance tolerance of 1e-4. Matching shape is not equivalent to matching performer, motion or deployment rig.

Projected position error relative to the fixed strongest combined procedural control:

| Group | Direct seed 1 | Direct seed 2 | Diffusion seed 1 | Diffusion seed 2 |
|---|---:|---:|---:|---:|
| Seen proportions | 1.066 | 1.078 | 1.183 | 1.172 |
| Novel proportions | 1.178 | 1.180 | 1.248 | 1.223 |
| Without surrounding context | 0.999 | 1.003 | 1.073 | 1.058 |
| With surrounding context | 1.354 | 1.359 | 1.446 | 1.416 |

Lower is better. These are equally weighted cohort summaries for diagnosis, not replacements for the original acceptance aggregation. Context groups use different requests and control behavior: the ratios do not prove that adding context increases a model's absolute error. They show a larger deficit relative to the control in that condition. No subgroup establishes overall acceptance.

Both families already fail before physical projection. The encoder already removes initial-root orientation. Do not weaken physical validation or add duplicate heading normalization on the basis of these failures.

## Decision

Keep further nearby fits paused. The next bounded investigation should audit how observed neighboring poses and their implied velocity are represented, weighted and used by the model versus the stronger context-aware procedural control. Compare paired requests on existing training/development clips, with the same targets, and report absolute errors alongside baseline-relative errors. Check conditioning correctness before attributing failure to capacity or corpus size. Preserve the sealed confirmation set.

Only after that diagnosis should a prospective experiment choose a specific representation or objective change, with fixed compute, data rights, split and stop criteria. A kinematically structured sequence representation is a candidate to investigate, not a selected solution. More data is also a hypothesis, not an established cure.

The target architecture remains layered: rig adapters and source-preserving transactions; separate interactive posing and sequence-generation backends; explicit timing, observed controls, contact and intent conditioning; geometric constraint enforcement; distinct dynamics/refinement; editable preview and publication. Explicit gravity/support context must be transformed consistently with canonical coordinates. Contact, style, physics and human usability requirements remain open even if positional error later improves.

The next quality milestones must be complete animator tasks, with motion quality, corrections, interactions and latency reported separately from regression counts. Existing exact-package and performance evidence should not be rerun absent a relevant change. No temporal model is bundled and no Cascadeur parity claim is justified.
