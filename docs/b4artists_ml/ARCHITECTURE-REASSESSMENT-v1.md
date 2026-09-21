# Architecture reassessment

User steering: assess whether the method, plan and architecture are the best route to the original B4Artists Machine Learning goal. This is an engineering assessment, not an independent quality evaluation or a new endpoint.

## Judgment

The modular host integration is worth preserving. The learned-motion strategy has not demonstrated sufficient generalization and should change before additional selector fitting. No evidence establishes that the current architecture is best, or that Cascadeur parity is near. Repeated correctness tests and small interpolation improvements cannot substitute for learned motion and animator assessment.

The expanded training audit contains 78 distinct clips totaling 1,026.296 seconds (17.1 minutes), with 7,358 overlapping/context-conditioned windows. Recent selectors choose among procedural and learned proposal curves rather than generate complete motion sequences. v26-v28 fail unchanged development gates. No trained temporal model is bundled. These observations support revisiting representation, model class and data coverage together; they do not isolate which factor caused every failure.

## Keep and develop

Preserve BoneForge/Rigify adapters, canonical semantic skeleton mapping, immutable solve inputs, priority/contact constraints, editable candidate actions, Keep/Discard, source recovery and protected regression evidence. Keep Ghost Tools and Anim Assist separate. The optional Cascadeur connector remains optional and deferred.

Use distinct latency budgets and interchangeable backends for interactive pose completion and whole-sequence generation. A shared canonical representation must include joint rotations, root motion, timing, observed-control masks, contact intent and character proportions. Pose completion should respond to pinned position/orientation controls; sequence generation should condition on sparse authored poses and intended movement. Constrained refinement must preserve priority poses and contacts and validate the final mapped rig animation. Dynamic balance and physics remain separate explicit work, not implied by smooth curves.

## Revised next research stage

1. Complete the pending exact-package validation and preserve its result. Profile the current default-Rigify generation/publication bottleneck in isolation before changing implementation technology.
2. Prepare one bounded sequence-model comparison before fitting: a compact temporal sequence baseline and a keyframe-conditioned diffusion candidate, alongside the unchanged projected procedural controls. Specify representation, compute and local inference budgets, reproducibility, data rights, training coverage and failure/stop criteria prospectively. Neither research popularity nor a paper abstract selects the winner.
3. Audit usable training data and any proposed code/weights separately for permitted training and redistribution. Expand coverage based on missing motions and proportions, within existing authorization; paid services and paid data require explicit approval. Do not silently replace providers, download large assets or assume a paper's license covers weights/data.
4. Retain original development and confirmation safeguards. Repeatedly exposed development data must stay labeled as such; the six sealed confirmation clips remain sealed. Broader natural locomotion and airborne tasks supplement existing gates and cannot dilute old regressions.
5. Compare end-to-end output on BoneForge and Rigify: priority preservation, foot/hand drift, joint behavior, full-sequence motion, sensitivity to edits, local latency and animator correction effort. Human usability and an equivalent Cascadeur comparison remain required and currently unknown.
6. Promote a learned backend only after its fixed acceptance checks pass. If both candidates fail, report a model/data feasibility gap and revise that evidence-backed hypothesis; do not spend the remaining budget on unbounded nearby variants.

The existing 100-total-evaluation ceiling, extended deadline, original goal ID, acceptance floors, history and sequencing deferrals remain unchanged. This review neither consumes a formal evaluation nor certifies the product.

## Sources and evidence

- Local ROADMAP.md and EXPANDED-TRAJECTORY-PLAN-v19.md describe the integration architecture and corpus. PROJECTED-SELECTOR-PLAN-v26.md and retained v26-v28 reports describe failed selector experiments.
- Cascadeur distinguishes learned posing/inbetweening from non-ML AutoPhysics and describes dozens of hours of proprietary training animation plus supplementary data: https://cascadeur.com/help/category/285 . This supports a hybrid design and highlights a coverage gap; it does not establish a minimum required dataset size for our tool.
- Flexible Motion In-betweening with Diffusion Models (SIGGRAPH 2024) is a relevant candidate for arbitrary sparse/partial constraints: https://arxiv.org/abs/2405.11126 . Its published results do not establish our target host's latency, licensing suitability or best architecture.
