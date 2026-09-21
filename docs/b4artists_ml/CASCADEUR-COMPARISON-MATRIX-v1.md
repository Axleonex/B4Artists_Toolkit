# Cascadeur comparison matrix v1

Status: evidence baseline only. This matrix records documented Cascadeur workflows and the current B4Artists Machine Learning state. It does not claim parity or superiority.

Research date: 2026-09-13. Cascadeur behavior is taken from the first-party help pages listed in the source column. B4Artists claims are limited to development-source evidence already recorded in this repository.

| Workflow area | Cascadeur documented behavior | B4Artists Machine Learning current state | Evidence needed before a parity claim |
|---|---|---|---|
| Drafting | Animation is authored as key poses, then transitions are added between crucial poses. | Pose anchors and editable procedural preview generation exist for supported BoneForge, Rigify and tested imported FK conventions. | Equivalent reach, crouch, walk, run, jump, landing and turn tasks on the same characters, with interaction counts and correction time. |
| Multi-pose inbetweening | The 2025.1 Inbetweening tool generates animation from at least two keyframes in a selected interval, with a documented 88-frame nearest-key limit. | Procedural Inbetween Series and deterministic timing/spacing tools exist. A qualified learned temporal model is not enabled; SLERP and geometric interpolation remain procedural. | Unseen multi-anchor sequences, contact preservation, style retention, discontinuity and foot-drift measurements against the procedural floor and Cascadeur. |
| AutoPosing | AutoPosing predicts a desired full-body pose from controller manipulation, supports humanoid and quadruped characters, and uses fixed/active controllers. It requires Cascadeur's standard rig. | Whole-body geometric posing supports sparse Body, hands, feet, head and pole requests on BoneForge/Rigify adapters, with pins, limits, contacts and rollback. Quadruped controls are deterministic. | Same sparse-control tasks across the frozen three-character set, with pinned-control accuracy, joint-limit violations, stretching, correction count and independent animator review. |
| Physics refinement | AutoPhysics analyzes authored animation, proposes a physically accurate version, and can snap the animation to the physics result while honoring fixed controls and global rotation/translation settings. | Gravity, center-of-mass/support analysis, contacts, momentum and bounded secondary-motion physics are implemented as separate procedural workflows. Static planar, spherical and development capsule collision are available. | Matched physics scenes with measured COM/support error, penetration, momentum continuity, animator intent preservation, latency and keep/discard recovery. |
| Trajectory and spacing editing | Trajectories expose traveled paths, interpolation frames and spacing; trajectory points can be edited with manipulators. | Ghost Tool remains the visual trajectory/onion-skin surface. B4ML provides deterministic timing/spacing authoring and editable curves, with the tools kept separate by product boundary. | Combined workflow study measuring whether the separated visual and interpolation surfaces reduce or increase animator corrections. |
| Interpolation controls | Cascadeur exposes interpolation types, kinematics choices, tangent reset and interval/current-frame application. Timeline docs also describe easing and AI interpolation entries. | B4ML exposes bounded procedural easing, bias, holds, breakdown insertion, retiming and spacing. These controls are explicitly labelled procedural. | Compare motion smoothness, velocity/acceleration continuity, style preservation and interaction count; do not count procedural easing as learned motion. |
| Rig and Blender interchange | Cascadeur imports Blender FBX/DAE/GLB/GLTF/USD workflows, warns about unit scale and DCC-vs-game rigs, and recommends deform-bone export for control-rig creation. | Standalone core runs inside Bforartists and preserves native control/deform/mechanism distinctions for supported adapters. A one-way optional bridge remains separate from the core. | Exact frozen FBX import/conversion in the installed Cascadeur entitlement, round-trip hashes, mapping correctness and animator recovery evidence. |
| Timeline organization | Cascadeur provides animation tracks, interval editing, playback, cycles and keyframe/interpolation controls in the Timeline. | B4ML uses Bforartists actions, copied candidates, editable curves, native Undo/Redo and reversible previews. Track-level parity is not established. | Equivalent track and interval workflows with measured steps, source preservation and save/reload behavior. |
| Distribution and entitlement | Cascadeur features vary by edition; the AutoPosing documentation explicitly marks quadrupeds as Pro-and-higher. | Standalone B4ML must not require Cascadeur, an account or paid API. The connector may expose only capabilities verified for the installed entitlement. | Entitlement-aware connector tests and a documented free-tier capability matrix; standalone tests must pass with the connector absent. |

## Source references

- [Workflow Basics](https://cascadeur.com/help/getting_started/workflow_basics)
- [Inbetweening / 2025.1](https://cascadeur.com/help/category/279)
- [AutoPosing](https://cascadeur.com/help/tools/animation_tools/autoposing)
- [AutoPhysics](https://cascadeur.com/help/tools/physics_tools/autophysics)
- [Spline](https://cascadeur.com/help/animation/spline)
- [Trajectories](https://cascadeur.com/help/tools/animation_tools/trajectories)
- [Timeline](https://cascadeur.com/help/interface/timeline)
- [Timeline Tools](https://cascadeur.com/help/tools/timeline_tools)
- [Import from Blender](https://cascadeur.com/help/getting_started/import_fbxdae/import_from_blender)
- [Export to Blender](https://cascadeur.com/help/category/300)

The matrix is a comparison protocol input. It is not a benchmark result, and no row can be marked “surpasses Cascadeur” until matched scenes, independent animator review and current entitlement evidence exist.
