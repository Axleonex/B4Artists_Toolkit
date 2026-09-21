# B4Artists Machine Learning architecture decision v2

Status: active research direction. This decision does not claim Cascadeur parity and does not promote a learned backend.

## Decision

Build the product as a constrained hybrid animation system. Keep one canonical humanoid motion representation between rig adapters, learned models, deterministic solvers and Bforartists actions. Treat the current compact temporal convolution as a reproducible feasibility baseline. Use a data-centered keyframe-conditioned Transformer as the primary candidate for fast, deterministic inbetweening. Evaluate a conditional diffusion backend later as an optional way to propose several plausible transitions. Apply contact, joint, balance and authored-priority corrections after learned inference through explicit solvers.

This gives the interactive workflow one repeatable default result while preserving a path to alternate motion ideas. It also keeps physical correction inspectable and testable instead of asking a learned model to imply physics.

## Product pipeline

1. BoneForge, default Rigify and compatible humanoid rigs map into a versioned canonical skeleton with proportions, root trajectory, local rotations and explicit authored-control masks.
2. The request builder captures sparse full or partial key poses, timing, incoming and outgoing context, priority, contact intent and optional style controls.
3. A deterministic shape-preserving reference supplies a safe editable result and the baseline over which a learned model predicts bounded residual motion.
4. The fast learned backend predicts motion plus contact likelihood and confidence in one pass. Authored channels remain exact by construction.
5. Kinematic projection restores bone lengths and legal joint behavior. Contact fitting locks selected hands and feet. Balance and dynamic refinement operate as a separate explicit stage.
6. A nonblocking Bforartists preview creates a temporary editable action. Keep, Discard and Restore remain transaction boundaries.
7. Publication writes ordinary F-curves and metadata so the output remains usable without the model loaded.

## Learned backend sequence

The next model comparison must hold data, masks, losses and evaluation windows constant:

- Current six-block temporal convolution: small offline baseline and regression oracle.
- Compact Transformer encoder: primary interactive candidate. Include velocities, normalized time, keyframe masks and proportion features; predict residual pose and contact channels.
- Conditional diffusion: later research candidate for multiple plausible transitions, partial constraints and style diversity. It must meet a separate latency and reproducibility contract and cannot replace the interactive default merely by scoring well on average.

The Transformer is evaluated before diffusion. SILK reports that representation, velocity inputs and data volume can matter as much as model complexity for motion inbetweening. CondMDI demonstrates the value of diffusion for arbitrary sparse and partial keyframe constraints, but its suitability for an offline Bforartists interaction loop still requires direct latency and usability evidence.

## Data strategy

The expanded train-only CMU split provides 1,840 clips, 85 subjects and 7.16 hours of unique motion with subject-disjoint development and confirmation partitions. It is a substantial feasibility corpus, not evidence of product parity. Cascadeur describes using dozens of hours of proprietary animation plus supplementary data. Before a parity claim, add legally redistributable motion with better authored timing, contacts, aerial motion, acting and varied proportions. Record dataset rights, clip identity and subject separation in every model manifest. Do not redistribute source motion or third-party weights unless their terms expressly allow it.

## Required evidence before promotion

- Both fixed seeds beat the strongest deterministic reference on old, new and combined development partitions without regressing the original gates.
- Authored full and partial channels remain exact; generated bones, rotations and contacts remain valid after rig mapping.
- Long gaps, turns, crouches, jumps, reaches, locomotion transitions and contact changes pass cohort limits rather than only aggregate means.
- Bforartists preview and publication remain responsive on default Rigify and BoneForge rigs, and failures return the safe deterministic reference.
- Independent animators need less correction time than the deterministic workflow and rate the result at least as usable as the agreed Cascadeur comparison.
- Confirmation clips remain sealed until the prospective confirmation plan permits one final read.

## Current limits

The current corpus is smaller and less curated than the training scope Cascadeur describes. The temporal convolution has not passed held-out quality gates. Strict continuous derivative behavior is not established merely by applying a smooth residual envelope to frame samples. Full force and torque physics, scene-aware collision, quadrupeds, animator usability and direct Cascadeur comparison remain open requirements.

## Primary evidence

- Cascadeur AI tools and training scope: https://cascadeur.com/help/category/285
- Cascadeur inbetweening behavior and limits: https://cascadeur.com/help/category/278
- SILK, a data-centered Transformer study for motion inbetweening: https://openaccess.thecvf.com/content/CVPR2025W/HuMoGen/html/Akhoundi_SILK_Smooth_InterpoLation_frameworK_for_motion_in-betweening_CVPRW_2025_paper.html
- Flexible Motion In-betweening with Diffusion Models: https://arxiv.org/abs/2405.11126
- SceneMI, scene-aware diffusion inbetweening: https://openaccess.thecvf.com/content/ICCV2025/html/Hwang_SceneMI_Motion_In-betweening_for_Modeling_Human-Scene_Interaction_ICCV_2025_paper.html
- CMU Graphics Lab Motion Capture Database and usage FAQ: https://mocap.cs.cmu.edu/ and https://mocap.cs.cmu.edu/faqs.php
