# Architecture decision v3: product-first hybrid

## Decision

The product keeps the hybrid architecture, but model fitting is no longer the main development loop. Learned motion remains a replaceable proposal provider inside a deterministic, rig-aware and source-safe animation system. A larger model is useful only after reviewed data and real-rig workflow evidence show that it improves the same frozen tasks that an animator will use.

The existing diffusion v1 comparison remains valid as the final prospectively frozen capacity-first experiment. It is evidence about the present corpus and conditioning contract, not a commitment to ship diffusion. If both seeds fail, the hard stop applies: do not tune a nearby model. Move to data, rig, physics and animator-evaluation work before another temporal fit.

## Product pipeline

```text
Bforartists controls, timeline and selected interval
                         |
                 immutable task packet
                         |
  rig adapter -> canonical family graph -> authored constraint masks
                         |
       procedural candidate / learned proposal provider
                         |
 exact projection -> kinematic/contact/physics refinement
                         |
 isolated editable action -> preview -> keep/discard/undo/reload
```

1. **Rig adapters own rig complexity.** BoneForge, Rigify and imported rigs map animator controls, deform bones, mechanism bones, rest transforms, scale, axes and IK/FK spaces into a canonical family graph. Humanoid and quadruped models remain separate.
2. **The task packet is the stable boundary.** It contains normalized hierarchy state, authored masks, priority frames, pins, contacts, timing, surrounding observed motion, intent and provenance. No inference worker receives `bpy` or RNA objects.
3. **The procedural candidate is always available.** It provides a fast editable floor and a safe fallback. Its UI and reports identify it as procedural.
4. **Learned models propose; they do not own constraints.** A provider may supply pose completion or an inbetween, but exact priority controls, bone lengths and explicitly pinned contacts are projected deterministically.
5. **Refinement is an explicit optimization stage.** Joint limits, support, center of mass, contacts, gravity, momentum and collision objectives report residuals and infeasible intervals. The animator controls correction strength and can preserve selected channels.
6. **Publication is isolated and reversible.** Preview writes a candidate action. Keep, discard, cancel, undo, redo and reload preserve the original rig and animation.

## Learned-motion strategy

Pose completion and temporal inbetweening remain separate tasks. The temporal path uses two deployment roles only after evidence supports them:

- A quality teacher may use conditional diffusion or flow matching for ambiguous sparse transitions. It is an offline/local candidate generator and is not presumed interactive.
- A compact single-pass student is distilled or trained against reviewed motion only if the teacher or reference data beats the procedural floor. The student must export reproducibly, match its training implementation and meet target-host latency before it enters the add-on.

The product-facing humanoid contract is a 17-joint semantic local hierarchy because it maps directly to animator controls across the eight qualified BoneForge, Rigify and imported fixtures. A richer 23-joint source hierarchy remains useful for training losses and motion-reference reconstruction, but its six helper joints are adapter detail rather than portable controls. `REAL-RIG-TASK-PACKET-v1.md` records the measured roundtrip evidence. Finger articulation, props and quadrupeds need explicit later schemas rather than silently expanding the humanoid contract. Twist and helper controls remain adapter/refinement responsibilities and must reproduce complete priority poses exactly.

## Revised order of work

1. Finish and report the frozen diffusion comparison without changing seeds, thresholds, schedule or architecture.
2. Qualify real BoneForge, default/generated Rigify and imported-rig task packets, roundtrip behavior and control-space projection on the reference scenes.
3. Replace weak inferred contacts with a reviewed reference subset. Record contact intervals, takeoff/landing, action intent and unusable clips. Add action-disjoint and rig-disjoint evaluation alongside subject-disjoint evaluation.
4. Complete the animator-facing contact, trajectory, center-of-mass and infeasibility diagnostics using the procedural floor. Measure interaction count and corrections, not just numerical reconstruction.
5. Train another learned temporal family only after the reviewed data/evidence checkpoint identifies a model-addressable failure. Freeze its plan before development outcomes.
6. Export only a candidate that passes unseen motion gates. Verify ONNX or equivalent parity, CPU latency, memory, cancellation and exact-package Bforartists lifecycle.
7. Run blinded animator comparisons against both the procedural tool and Cascadeur on matched tasks. Claim parity or an advantage only for categories that pass.

## Why this is stronger

The existing TCN results show that exact constraints and bone lengths can pass while motion metrics regress. All four diffusion fits show the same generalization ceiling: training loss continues to fall after development loss stops improving, and every 4/8/12-step aggregate motion comparison regresses against the procedural floor. That evidence points to data coverage and supervision before model capacity.

The revised sequence prevents a long architecture search from substituting for a usable animation workflow. It also preserves the main opportunity to outperform Cascadeur in named areas: native Bforartists rig handling, editable F-curves, source-safe candidate actions, transparent constraint residuals and a workflow that does not require export to another application. Broad animation-quality superiority remains unverified until direct evaluation exists.

## Release gates

A learned provider is not bundled unless all of these pass:

- both fixed seeds pass aggregate and worst-cohort motion gates;
- complete priority poses, pinned controls and bone lengths remain exact;
- reviewed contact and physical metrics pass;
- BoneForge, Rigify and imported-rig lifecycle tests pass on original rigs;
- target Bforartists warm/cold latency, memory and cancellation pass;
- independent animators prefer or require fewer corrections than the procedural floor;
- any Cascadeur comparison uses matched tasks and documented versions/settings.

Until then the add-on may ship deterministic assistance, but the UI and documentation must not describe an unqualified model as intelligent interpolation or claim Cascadeur parity.
