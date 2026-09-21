# Architecture audit v2

## Verdict

The strongest practical architecture for this add-on is a hybrid constraint system, not a single end-to-end neural network. The current direction is suitable for a standalone Bforartists product: learned models propose poses and motion; exact animator controls, rig-space projection, kinematic limits, contact, balance, collision and source-safe publication remain deterministic. This is the selected architecture, but it is not called superior to Cascadeur until frozen unseen-character tests, target-host latency, animator use and a direct product comparison pass.

## Product pipeline

1. **Rig adapters.** BoneForge, default Rigify and supported imported humanoids map to a canonical semantic control vocabulary and a complete ancestor-local hierarchy. Rig-specific controls and deformation remain outside the learned representation.
2. **Canonical motion state.** Each frame contains root translation and continuous 6D local rotations for 23 hierarchy joints. Fixed offsets preserve proportions. World-space joint prediction is prohibited because it can break bone lengths and transfer poorly between rigs.
3. **Animator constraint layer.** Seventeen semantic joints expose sparse position/orientation controls, priority poses, contacts, direction, timing, gravity, action and style. Authored values carry explicit masks, confidence and provenance. A separate boundary-motion block encodes the immediate observed motion before and after the generated interval without reading hidden inbetween frames.
4. **Procedural floor.** Root interpolation plus local-rotation SLERP always produces a valid editable result. It is the quality and failure fallback, and is never presented as machine learning.
5. **Fast learned proposal.** A 711,053-parameter bidirectional dilated residual TCN predicts full-hierarchy corrections around the procedural floor. Its 253-frame receptive field covers the 97-frame maximum input. Zero initialization reproduces the floor, and exact control projection prevents the model from moving authored keys.
6. **Diverse learned proposal.** A conditional temporal diffusion model is the second distinct candidate for ambiguous or long sparse transitions. It must obey the same representation, masks and evaluation cohorts. It is justified only if its motion quality exceeds the TCN enough to offset multi-step latency.
7. **Deterministic refinement.** Forward kinematics, joint limits, contact locking, support/center-of-mass correction, gravity/momentum tools and collision cleanup enforce measurable constraints after generation. A learned model cannot waive these checks.
8. **Bforartists workflow.** Generation creates an isolated candidate with preview, strength, cancellation, keep/discard, undo, source recovery and editable curves. Runtime inference must be local CPU ONNX or an equivalent bundled backend; PyTorch and online services remain training-only.

## Why this split is appropriate

Cascadeur's documented workflow treats moved controllers as active pose constraints and combines assisted posing with separate physics tools. Its AutoPosing system can overwrite existing poses, which makes source-safe candidate actions and reversible preview a useful Bforartists improvement. The architecture follows that interaction model without depending on Cascadeur code or services.

[Conditional Motion Diffusion In-betweening](https://arxiv.org/abs/2405.11126) supports arbitrary sparse and partial keyframes and shows why a conditional diffusion candidate belongs in the comparison. [Factorized Motion Diffusion](https://assets.studios.disneyresearch.com/app/uploads/2024/10/Factorized-Motion-Diffusion-for-Precise-and-Character-Agnostic-Motion-Inbetweening-Paper.pdf) identifies exact sparse spatial constraints as a practical weakness of unconstrained motion diffusion; exact post-projection addresses that risk. [Scalable Motion In-betweening via Diffusion and Physics-Based Character Adaptation](https://arxiv.org/abs/2504.09413) supports separating character-agnostic generation from physical adaptation. For this local add-on, deterministic rig-aware refinement is the first adaptation layer because it is inspectable, reversible and deployable without a reinforcement-learning runtime.

## Evidence already passed

- Frozen memory-mapped corpus: 1,840 clips, 85 subjects, 773,836 frames and 7.158742 hours.
- Subject-disjoint split: 68 training subjects and 17 development subjects.
- Frozen windows: 6,531 training and 1,125 development across 8, 16, 32, 64 and 96-frame gaps.
- Conditioning: 483 constraint features plus 142 leak-resistant boundary-motion features, for 766 total model inputs with the 141-feature procedural state; weak target-derived contact is rejected for development.
- Kinematics: maximum synthetic bone-edge error 1.4901161193847656e-08, zero identity loss and finite nonzero gradients through root, pose, velocity, acceleration and contact losses. A 100-window training-only scale audit fixed balanced weights before model outcomes were observed.
- Fast candidate: exact procedural output at initialization, exact authored projection, finite gradients and a 3.989165 ms repeat measurement for 97 frames on the CUDA training host. This is not a Bforartists latency qualification.
- Integration microfit: the corrected 766-input path reduced one actual 33-frame training-window loss to 7.36% of its starting value in 160 steps. This proves optimization integration only.

## Remaining proof and stop rules

The largest risks are data scale and label quality, not network size. Contact labels are heuristic and capped at low confidence; scene and hand contacts, force, intent and naturalness remain unknown. Humanoid transfer still needs BoneForge, Rigify and imported-rig evaluation; quadrupeds require a later dedicated representation and corpus.

Train the fixed TCN once under the prospective plan and compare it with the procedural floor on every frozen development task/gap cohort. If it fails, do not sweep nearby TCN, Transformer, selector or loss-weight variants. Advance to the fixed diffusion family or improve evidence/data according to the failed cohort. Confirmation stays sealed until one exported candidate passes all development, lifecycle and target-host checks.

No parity or superiority claim is allowed before all of the following pass: unseen-character motion quality, exact controls, physical regressions, Bforartists warm/cold latency and memory, original-rig keep/discard/undo/reload, independent animator acceptance and a documented side-by-side Cascadeur workflow comparison.
