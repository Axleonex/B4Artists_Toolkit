# Path to standalone animation-assistance parity

Experimental 0.32.0 adds family-filtered contact review and contact-aware animation cleanup for copied humanoid and quadruped candidates. The frozen source passes 495 tests across 55 suites; the exact archive passes 18 offline tests and matches source byte-for-byte. See CLEANUP-v0.32.0.md. Cleanup remains procedural; learned temporal motion, human usability and Cascadeur parity remain unqualified.

Current delivery authority: `DELIVERY-ORDER-v1.md`. With the frozen 0.36.0 procedural package complete, it continues achievable animator-facing work in development 0.37 before the longer learned-inbetweening and comparison work. `ARCHITECTURE-REVIEW-v4.md` continues to govern the retained hybrid architecture, evidence boundaries and model ladder. The chronological notes below preserve evidence from earlier checkpoints; their expired 50/75-evaluation and deadline statements are historical and do not override the current active goal or its latest user-authorized limits.

This is a staged engineering and evaluation plan. A phase is complete only when its user workflow and acceptance evidence pass. There is no estimate here implying that one prototype equals Cascadeur.

## Active build sequence after 0.32.0

1. Complete: the frozen 0.32.0 source passes 495 tests across all 55 current suites; focused cleanup/contact-review and 18-package-test evidence remains separately labelled.
2. Complete: 0.32 contact review and cleanup pass focused, affected, real-window, full-regression, and exact-package gates.
3. Open release gates: 0.33 Posing and Rig Usability has thirteen verified development slices covering the semantic joint-limit preset, Chest and Neck position/orientation, per-target Reset, target mirroring, Rig Mapping Diagnostics, bounded per-armature humanoid mapping corrections, same-armature Reusable Pose Anchors, Align Bend, Flip Side, body-scale Pole Distance and a scene-local Semantic Pose Asset. Mapping corrections are bound to adapter plus bone-name/hierarchy signature and pass BoneForge, generated Rigify Basic/Default, imported Unity Humanoid, save/reload, invalid-data, and real-window Undo/Redo coverage. A direct lower-Spine target was evaluated and removed after failing the six-adapter projection gate; its coupled pelvis/spine dependency is recorded in SPINE-TARGET-v1.md and remains deferred. Package and milestone-wide gates remain open. See JOINT-LIMIT-PRESETS-v1.md, CHEST-TARGET-v1.md, CHEST-ORIENTATION-v1.md, NECK-TARGET-v1.md, TARGET-RESET-v1.md, TARGET-MIRROR-v1.md, RIG-DIAGNOSTICS-v1.md, MAPPING-CORRECTIONS-v1.md, POSE-REUSE-v1.md, POLE-ALIGN-v1.md, POLE-FLIP-v1.md, POLE-DISTANCE-v1.md and POSE-ASSET-v1.md.
4. Open release gates: 0.34 Practical Contact Expansion has four verified development slices: Contact Interval Editing, Explicit Humanoid Hand-to-Prop Holds, Explicit Moving Rigid Planar Platforms, and Contact Visualization and Blend Review. Package and milestone-wide gates remain open. See `CONTACT-INTERVAL-EDIT-v1.md`, `PROP-HOLDS-v1.md`, `MOVING-PLATFORMS-v1.md`, and `CONTACT-VISUALIZATION-v1.md`.
5. Active: build 0.35 Quadruped Workflow Expansion. Ten slices now qualify on generated Rigify cat, horse, and wolf: the rotation-only semantic Head target, schema-3 Head-to-Spine Follow, opt-in schema-4 Fore/Hind Pole Targets, current-frame **Match + Enable All Poles**, procedural accepted-contact support-phase review, per-target preview-start Reset, bidirectional paw/pole target mirroring, a scene-local normalized quadruped pose-request asset, per-limb current-bend Pole Target alignment, and guarded per-pole **Flip Side** plus body-scale **Set Distance**. The newest slice passes 8/8 focused and 136/136 affected tests across 18 suites on one frozen 44-file runtime set, independent cat/horse/wolf limb oracles, strict helper, workflow and parent-space rollback, a foreground Flip/Distance/Undo/Redo journey, and final serial-review PASS. Imported/custom adapters, learned gait recognition/generation, packaging, and milestone-wide gates remain open. See QUADRUPED-HEAD-v1.md, QUADRUPED-SPINE-FOLLOW-v1.md, QUADRUPED-POLES-v1.md, QUADRUPED-POLE-MATCH-v1.md, QUADRUPED-GAIT-PHASES-v1.md, QUADRUPED-TARGET-RESET-v1.md, QUADRUPED-TARGET-MIRROR-v1.md, QUADRUPED-POSE-ASSET-v1.md, QUADRUPED-POLE-ALIGN-v1.md, and QUADRUPED-POLE-CONTROLS-v1.md.
6. Complete and frozen: 0.36.0 consolidates Interpolation Timing Controls, editable Breakdown Pose insertion, and rig-local timing Copy/Paste with its release and exact-package evidence. See `RELEASE-v0.36.0.md`.
7. Active: development 0.37 adds the six **Short-Cycle Workflow** features plus twelve selected-control physics-workflow slices: **External Acceleration**, **Wind Velocity**, **Velocity Impulse**, **Per-Control Force and Mass**, **Force-at-Offset Torque**, **Load From Active**, **Static Spherical Collision**, **Multiple Static Spheres**, **Moving Rigid Spheres**, **Animated Sphere Radius**, **Sphere Radius Fit**, and **Sphere Proxy from Bounds**. These use the stable followers, exact priority envelopes, editable curves, exclusive workflow ownership and full recovery; load recall changes only the visible authoring fields, while the sphere workflow excludes sampled selected-control pivots from one to eight persistent explicit radii. Static and directly animated sphere centers can be mixed, an opt-in radius follows complete direct uniform Scale XYZ animation, bounce/friction use relative center and radial surface velocity, and setup operators can snapshot a conservative radius or create and add an unparented Empty sphere at the current world-bounds center. Their focused/affected totals are 13/91, 11/102, 13/115, 14/129, 14/143, 8/151, 13/164, 8/172, 9/181, 15/187, 5/192, and 5/197. Each has a foreground operator/native Undo/Redo/source-recovery journey. See INBETWEEN-SERIES-v1.md, POSE-RETIME-v1.md, RIPPLE-RETIME-v1.md, POSE-SPACING-SCALE-v1.md, POSE-SPACING-EQUALIZE-v1.md, SECONDARY-CHAIN-SELECTION-v1.md, SECONDARY-EXTERNAL-ACCELERATION-v1.md, SECONDARY-WIND-VELOCITY-v1.md, SECONDARY-VELOCITY-IMPULSE-v1.md, SECONDARY-CONTROL-LOADS-v1.md, SECONDARY-FORCE-OFFSET-TORQUE-v1.md, SECONDARY-LOAD-FROM-ACTIVE-v1.md, SECONDARY-SPHERE-COLLISION-v1.md, SECONDARY-MULTI-SPHERE-COLLISION-v1.md, SECONDARY-MOVING-SPHERE-COLLISION-v1.md, SECONDARY-ANIMATED-RADIUS-v1.md, SECONDARY-SPHERE-FIT-v1.md, and SECONDARY-SPHERE-PROXY-v1.md.

The exact v0.37.51-dev package additionally qualifies the bounded schemas
39/40 world-location chain compound for one support plane plus exactly three
directly animated, optionally uniformly scaled spheres, with or without the
bounded static sphere set. More than three moving spheres, arbitrary
moving/static mixtures, broad collision-coupled momentum, and general
rigid-body dynamics remain open and fail-closed.
8. Complete as infrastructure: Motion-label Reviewer v2 adds a strict offline path from the frozen 130-item weak-label queue to a fully ordered, hash-bound, transactionally published review artifact. Its synthetic page-to-Python contract passes, but no human review or training authorization is claimed. See `MOTION-LABEL-REVIEWER-v2.md`.
9. Resume long-horizon learned temporal, broader physics/generalization and matched Cascadeur work in the order defined by `DELIVERY-ORDER-v1.md`.

Independent animator evidence remains the prerequisite for selecting or promoting another temporal model. It can be collected alongside the shorter milestones; its absence does not force unrelated procedural work to stop.

| Phase | Deliverable | Acceptance evidence | Current state |

|---|---|---|---|

| 1. Safe humanoid foundation | BoneForge/Rigify adapters, saved anchors, local interpolation, isolated candidate actions | Real Rigify generation and motion; source preservation; failure rollback; .blend roundtrip | Experimental 0.1 implemented |

| 2. Assisted posing | End-effector targets and poles, limb reach, rotation limits, pelvis/spine compensation, fixed hands/feet | Reach error relative to character height, fixed-point drift, zero limb stretching unless enabled, stable singularities; same tests on BoneForge and Rigify | 0.9: reversible FK fitting from known IK inputs, head/spine compensation, positions/orientations/poles and editable control swing/twist bounds implemented. Evaluated skeletal frames, directional bend bounds and forward-axis calibration added for supported joints; anatomical range presets and dynamic/temporal balance remain; static COM correction added in 0.12 |

| 3. Contacts and motion correction | Explicit contact intervals, foot locking, support polygon/center of mass, gravity-aware root arcs, editable corrections | Foot slip, penetration, endpoint error, acceleration/jerk; regression scenes for walk, crouch, jump, reach | 0.26.0 plus development 0.37: contacts, COM/support, static balance, constant-gravity COM flight, C2 transitions, finite rigid-segment angular refinement, sampled static planar response, selected-control local/world gravity/collision dynamics, explicit local rotation-chain propagation, uniform external acceleration, uniform wind-relative drag, one frame-authored velocity impulse, per-control force/mass, selected-control force-at-offset torque, active-control load recall and one-to-eight direct rigid spheres with optional center/uniform-radius animation and conservative bounds-to-radius fitting; anatomical calibration, coupled joint dynamics, arbitrary/deforming collision, continuous collision, self-collision, temporal balance and broad motion benchmarks remain |

| 4. Learned pose completion | Licensed local model conditioned on partial position/orientation controls, per-rig normalization and constraint projection | Better plausibility than IK-only baseline in blind animator comparisons; preserve fixed controls; CPU and optional GPU latency | 0.7: frozen limb and contextual whole-body priors integrated with reversible rig fitting. Prior-pose regression, orientation-conditioned learning, broader proportions and visual acceptance remain |

| 5. Learned inbetweening | Context and timing-conditioned motion between priority poses, style, local inference and contact correction | Endpoint/control error, contact slip, jerk, generation latency, animator accept/edit rates compared with deterministic baseline | Fixed full-sequence direct/diffusion comparison remains unqualified across both seeds and all original development gates. Training-only coverage and loss diagnostics are recorded; no further nearby fits are planned. No temporal model is bundled. Explicit contact/intent representation, generalization and independent comparison remain |

| 6. Production animation | Secondary motion, unbaking/key reduction, multi-character isolation, cancel/preview blend, rig-space switching, production rig coverage | Long clips, complex constraints, undo/redo/reload, cancellation, before/after profiling | Partial: cooperative previews, keep/discard, undo/redo, reload, one explicit local rotation-chain workflow, and bounded reversible direct-chain selection are tested; deformable or semantically inferred secondary motion and remaining production features remain open |

| 7. Quadrupeds | Four-limb rig adapters, contact patterns and suitable learned priors | Dedicated quadruped fixtures and gait/pose evaluation | Development 0.35 adds semantic Head-to-Spine shaping, opt-in pole targets, current-frame pose-preserving pole matching, schema-1-4 per-target reset, bidirectional paw/pole target mirroring, normalized cross-profile pose-request reuse, schema-4 current-bend pole alignment, pole-side flipping, normalized pole-distance control, and procedural support-phase review from animator-accepted contacts on generated Rigify cat/horse/wolf. Contact inference, gait recognition/generation, balance/flight/arbitrary surfaces, animated-range pole conversion, imported/custom rigs and learned priors remain |

| Optional connector | Explicit import/export or live exchange with an installed Cascadeur build | Version/capability checks and roundtrip tests under the supported entitlement | Not implemented; never a core dependency |

## Current-release review checkpoint v13

The unchanged four-rig/eight-task procedural protocol passes 32/32 cases on exact 0.25.0 source and again on exact 0.26.0 runtime. A refreshed reviewer bound to the v0.26 scenes has balanced A/B assignment, exact scene/report hashes, locked reveals, complete-export gating and a passing Edge interaction smoke. A separate correction-trial add-on copies the frozen candidate, measures active time and actual key changes, preserves priority poses and restores the source on cancel. Synthetic evidence cannot satisfy the human validator. No reviewer has completed the packet, so phases 5 and 6 retain their independent visual and hands-on acceptance gates.

## Architecture

```text

Bforartists UI / selection / timeline

              |

BoneForge-compatible rig adapter

  semantic skeleton + animator controls + spaces

              |

immutable solve request: anchors / masks / contacts / units / timing

              |

local deterministic solver ---- optional local trained-model backend

              |                         |

              +--- constraint projection and result validation

                                        |

                          separate candidate action

                             review / keep / discard

```

The pure mathematical core must remain independent of `bpy`. The adapter is responsible for translating semantic joints to writable controls, including FK/IK spaces. A learned model should operate on a normalized skeleton rather than Blender bone names. All Blender evaluation and mutation stay on the main thread; future worker inference receives arrays and returns arrays, never RNA references.

The source maps use BoneForge's existing target vocabulary to avoid incompatible rig conventions. Persistent state belongs to each armature object, not a process-global singleton. Bforartists exclusivity is checked before registering the actual toolset.

## ML implementation direction and open decisions

Pose completion and temporal motion generation are separate models/problems. [ProtoRes](https://arxiv.org/abs/2106.01981) is a relevant learned inverse-kinematics reference for sparse control inputs. [Robust Motion In-betweening](https://arxiv.org/abs/2102.04942) is a reference for temporal conditioning and endpoint constraints. Neither is bundled or claimed to be implemented here.

Before adopting weights, record the exact model, input/output skeleton, normalization, runtime, weight checksum, code license, weight terms, and training-data provenance. Evaluate models on the same saved rig fixtures and deterministic baseline. A model that looks plausible but drifts pinned feet or misses priority poses does not pass.

The [LAFAN1 publisher](https://github.com/ubisoft/ubisoft-laforge-animation-dataset) identifies its dataset as CC BY-NC-ND 4.0. It is not being silently bundled as unrestricted product training data. That earlier phase downloaded no data or weights. The subsequent 0.4 experiment uses a bounded CMU subset under its published product-use terms; see the model card and training manifests. Prefer a demonstrably suitable redistributable model/data source, or build a training corpus from motion the project has rights to use.

A future inference backend may use ONNX Runtime or an isolated local process, chosen after CPU/GPU compatibility and measured latency tests. The current add-on imports neither PyTorch nor ONNX and installs no packages automatically. No cloud service or pay-per-token API is required.

## Evaluation contract

- Persist a reference set of humanoid poses and motions covering different limb proportions, scales, handedness, parent transforms and rigs.

- Express position errors and penetration as a fraction of character height, plus world-space values.

- Measure all pinned joints, not just the root. Track quaternion angular error and continuity across 180-degree boundaries.

- Check source action contents, slots, custom rig properties, selection, playhead and registration before/after success, cancellation and injected failures.

- Compare learned outputs against the existing deterministic solver and a manual animator reference. State tested hardware, clip size, cold/warm latency and peak memory.

- Keep visual acceptance separate from mathematical correctness and speed. Current tests do not establish natural-motion quality or Cascadeur parity.

## Next work after the 0.3 checkpoint

1. Default IK input now uses verified FK matching and reversible mode-aware candidates. Extend evaluated conversion coverage to varied proportions, imported rigs and parent spaces. Native IK output and broader rig-state transitions remain future work; the original native constraints must continue to stay intact.

2. Add head/pelvis constraints and spine compensation, then continuous/cancellable preview with measured latency budgets. Add varied-proportion and imported-skeleton deformation fixtures.

3. Introduce temporal contact intervals and world-space planted-foot projection into generated candidates. Measure contact drift and retain authored priority poses.

4. Continue licensed local-model/data research alongside deterministic evaluation. Learned pose completion and learned motion remain mandatory, separate deliverables.

5. Build the complete benchmark scene set, hardware/runtime measurements and animator visual evaluation before any quality comparison. No direct Cascadeur comparison has been run.

These steps preserve the complete active goal. Completion of this checkpoint is not completion of phase 2 or product parity.

## Next work after the 0.4 learned-bend checkpoint

1. Close the learned arm-proportion gap on actual default BoneForge/Rigify rigs. Investigate pose-preserving length-ratio augmentation and validate on a new frozen confirmation protocol. Do not widen bounds merely to make tests pass. Preserve v1/v2 failures and results; existing confirmation is no longer blind for subsequent design decisions.

2. Extend from a local limb prior to real whole-body completion, including head/spine/pelvis compensation, joint/twist limits and animator pins. The bundled prior alone does not satisfy phase 4.

3. Continue the temporal contact, physics, learned inbetweening and production workflow milestones above. Current single-frame regression has no timing, style or motion context.

4. Add animator visual assessment, varied-proportion deformation fixtures and benchmark scenes for equivalent Cascadeur comparison. The model's numerical CMU reconstruction results are not product parity.

## Evidence after the 0.4 proportion experiments

V3/V4 training and fresh confirmation are complete as research, with failed release gates. No new model replaces 0.4. The contextual data/model/length-projection experiment is now implemented and measured; see CONTEXTUAL-POSE-RESULTS-v1.md. Next, build explicit actual-rig kinematic adapters and evaluate reversible full-body application. Orientation/pole conditioning and prior-pose quality remain gaps. The existing full product phases remain unchanged.

## Actual-rig contextual integration checkpoint

CONTEXTUAL-RIG-v1.md records five real-rig projection fixtures, learned elbow participation, weighted mesh checks and reversible source modes. Next reduce dense host derivative evaluation cost while preserving these accuracy gates, then integrate persistent/cancellable product previews and editable anchors. Contextual model quality, anatomical constraints and all later motion/physics phases remain open.

## Cooperative contextual solver checkpoint

CONTEXTUAL-RIG-OPTIMIZATION-v2.md records reduced derivative evaluation cost and cancellation-safe progress steps. Next integrate a persistent modal preview and editable anchors, and investigate cached forward kinematics to reduce remaining multi-second fits. All model-quality, physics/motion and product acceptance requirements remain active.

## 0.5 whole-body preview checkpoint

The contextual runtime now belongs to the independently installable add-on. Persistent target helpers, cooperative modal solving, Escape cancellation, strength and learned influence, editable anchors, source/action recovery, save/reload and actual UI undo/redo have lifecycle coverage. Unregister restores previews in their own scenes. Rigify capture includes the full relevant spine/neck controls.

This advances phases 2, 4 and 6; it does not complete them. Next reduce host evaluation cost for continuous interaction, add anatomical/pole/orientation and contact constraints, and improve learned preservation of an authored starting pose. The temporal learned-motion, physics, quadruped, connector and comparative visual-evaluation phases remain mandatory. See VALIDATION-0.5.md for exact package evidence and the model card for measured regressions.

## 0.5.1 evaluation checkpoint

A dependency-closed private rig copy reduces whole-body evaluation cost, with original-rig output verification and automatic full-rig fallback. Complete solves and cancellation/save cleanup are tested. PROXY-EVALUATION.md retains the intermediate failures and differential evidence. Next add explicit pole/orientation inputs and anatomical constraints, improve learned preservation of authored poses, and pursue the still-required motion/contact/physics milestones. Continuous live posing and comparative quality remain open.

## 0.6.0 directed posing checkpoint

Whole-body position, rotation and pole controls now share the persistent preview/anchor workflow. They are geometric constraints, with no new neural weights. BODY-CONTROLS.md records numerical and lifecycle evidence. Next implement rig-aware anatomical/twist limits and contact/balance control, then continue learned temporal motion and the full physics/production milestones. Learned prior-pose quality, production rigs and comparative animator evaluation remain unresolved.

## 0.7.0 joint-limit checkpoint

Artist-defined control swing/twist bounds now participate in the whole-body fitting and persistent preview workflow. Actual Rigify root-follow versus neck-follow behavior is tested explicitly; authored spaces remain intact. Next add anatomical joint frames and directional limits, calibrated character presets and contact/balance assistance. Temporal limit enforcement, learned inbetweening, physics, quadrupeds and equivalent Cascadeur/animator evaluation remain open. JOINT-LIMITS.md distinguishes the current control-space implementation from those unmet requirements.

## 0.8.0 evaluated skeletal frame checkpoint

Limits now support rest-corrected skeletal child/parent measurements alongside existing control-local bounds. Rigify follow-space differences and distributed neck dependencies are covered by actual-rig tests. Next add directional hinge/swing regions and character calibration, then contacts and balance. The longer-term learned motion, physics, responsiveness, production rig coverage, quadrupeds, optional connector and equivalent comparative evaluation goals remain unchanged.

## 0.9.0 directional bend checkpoint

Artist-defined forward/sideways regions now constrain whole-body fitting, with calibration of the forward axis from a posed control or supported skeletal joint. This supplies directional bounds without claiming anatomical range estimation. Central derivatives resolve tested coupled fitting failures at the existing accuracy gates, with additional runtime cost.

Next advance the contact/balance workflow: explicit animator-authored contact state, measured world-space support and contact drift, and editable correction while preserving priority poses. Retain the remaining anatomical range/neutral-reference calibration, distributed torso/neck adapters and performance work. Learned temporal motion and style, physics, production rigs/meshes, quadrupeds, the optional connector and equivalent Cascadeur/animator evaluation remain mandatory. Do not treat another pose-only milestone as completing those requirements.

## 0.10.0 explicit temporal contacts

Artist-authored static hand/foot contacts now correct FK candidate motion while preserving anchor poses and retaining the input animation. Held point/orientation, offset points, strength and blend intervals participate in evaluated-rig checks; midpoint failures drive local refinement. The workflow is cancellable, reversible and persistent. This is geometric temporal correction, not learned inbetweening or a completed physics system.

Next implement and evaluate the required local learned temporal backend using contact/priority checks as acceptance evidence; TEMPORAL-MOTION-NEXT.md records existing data code and a ground-truth pelvis-normalization leakage risk to avoid. Integrate support/COM and contact-informed motion evaluation into the same candidate workflow as the remaining physics work advances. Add walk/run/jump/landing/turning and proportion/mesh fixtures beyond the current crouch/reach cases. Continuous-time bounds, contact-aware anatomical limits, collision/moving surfaces, realistic root compensation, animator quality and equivalent Cascadeur comparisons remain open. Further pose-only polish must not displace learned motion and physics deliverables.

## Temporal research checkpoint

The first actual temporal query model and reproducible evaluation pipeline are implemented outside the add-on. Both validation and confirmation quality gates fail; no new motion model is promoted into release 0.10.0. TEMPORAL-MOTION-v1.md records 14 leakage/math tests, host inference checks, frozen results and the sequence/kinematic changes required next. Learned-motion product acceptance remains incomplete.

## Full-hierarchy sequence research checkpoint

TEMPORAL-MOTION-v2.md records a 23-joint differentiable FK decoder, smooth learned curve coefficients and velocity/acceleration training. Source-edge stretching is eliminated in tested research outputs; learned validation quality still regresses and the zero-residual baseline wins selection. No model or runtime release is promoted. 13 new tests, prior temporal regressions and nonzero-model host inference cover the research layer only. Learned-animation, real-rig workflow and full product acceptance remain open.

## Motion capacity and kernel research checkpoint

TEMPORAL-MOTION-v3.md records a hidden-answer capacity diagnostic and controlled observed-input/learner comparisons. A nonzero kernel model wins validation selection with 1.86% lower average position error than linear interpolation, but fails the 5% improvement, cohort and observed-development gates. It remains research-only. 38 standalone tests and selected-model host inference pass; the host still crashes at shutdown. Runtime 0.10.0 and the full remaining product scope are unchanged.

## Explicit physical-context checkpoint

GRAVITY-CONTEXT-v4.md records gravity/support encoding, a read-only scene adapter and an analytical free-point helper. Physical tilt is now distinguishable from coordinate changes. The direction-conditioned learner improves validation only marginally and still fails full quality gates. 52 standalone tests and actual scene-context checks pass, followed by the known host shutdown crash. No runtime release is promoted; actual-rig COM/support and full learned-motion/physics acceptance remain open.

## 0.13.1 flight maintenance

The measured quadratic key-search hotspot now uses exact lookup with a nearest-neighbor fallback for host frame rounding; curve invalidation uses bulk numeric/enum reads. Ownership checks limit cleanup to unused unchanged generated output. Regression work covers fractional equivalence with 0.13.0, retained alternatives, refinement boundary edits and the known long-Rigify rollback. FLIGHT-OPTIMIZATION.md holds measurements and remaining failures.

Next investigate long-Rigify facial precision without discarding deformation checks, bound remaining expensive stages, measure the complete posing/inference workflow, and obtain independent animator usability evidence. Accepted learned temporal motion, momentum/secondary motion, imported production rigs, quadrupeds, optional connector and equivalent Cascadeur comparisons remain mandatory.

## Internal native motion ownership validation

See [MOTION-LAYER-PERSISTENCE.md](MOTION-LAYER-PERSISTENCE.md): 14 recovery checks, five real rig builds with synthetic bound meshes, native render isolation and saved playback/source restoration now pass for an internal component. It is not connected to the released animator journey; no additional full-goal acceptance requirement is marked complete.

## 0.14.0 integrated native motion

Native trajectory generation now connects source ownership, complete editable result archives, preview/source recovery and displayed authoring coordinates. Long default Rigify native flight passes the unchanged precision gates in the documented 60-frame fixture. Actual UI events and fresh saved playback exercise the implementation; the two learned pose models are unchanged.

Next measure the complete long-clip native interaction and resource bounds, strengthen mixed contact/flight and production-mesh coverage, and obtain an independent animator assessment. Continue the accepted learned temporal motion, momentum/secondary motion, imported humanoid behavior, quadruped and optional connector work. Direct Cascadeur comparison remains unverified. The approved implementation-progress gate retains the same full endpoint, quality thresholds, three-evaluation allowance and original extension deadline; feature completion alone cannot complete the goal.

## Qualification after native integration

Measured 60-frame native flight meets current subset budgets, but both 240-frame fixtures reject at the unchanged acceleration tolerance. Preserve their failures and source-recovery evidence. The two shipped static pose models now have fresh byte-identical training/confirmation with documented BLAS conditions. Next qualify mixed-strength/native-interval behavior and retain the remaining learned temporal, momentum/secondary-motion, rig coverage, host lifecycle and independent animator/comparison requirements.

## 0.14.1 qualification checkpoint

The native driver length limit is resolved for the tested maximum of sixteen intervals; source-safe recovery and native saved playback are verified. The remaining highest-priority product work is accepted learned temporal motion and complete physics/refinement, with independent animator feedback, production/imported rig coverage, quadrupeds and an entitlement-aware optional connector still required. Preserve the current goal's evaluation/deadline limits and all recorded failures; the installable build is an experimental milestone, not Cascadeur parity.

## 0.14.2 native sampling maintenance

Reusing the guarded rig mapping and sampling only mass segments during fitting reduces measured 60-frame solve time by approximately 5% on BoneForge/default Rigify while preserving exact generated channel values. Five actual rig families have exact segment-sampling parity tests. Existing source recovery and 240-frame rejection remain unchanged. NATIVE-SAMPLING-0.14.2.md records the precision diagnostic and bounded regression evidence. Full learned temporal, physics, rig coverage, host lifecycle and independent comparative acceptance remain incomplete.

## Contextual temporal research v5

The observation-only full-hierarchy contextual baseline and nine learned residual fits pass isolation/kinematic tests but fail model-quality selection. No new temporal model is bundled. TEMPORAL-CONTEXT-v5.md records exact repeatability, stronger baselines, failed gates and next research; the original intelligent inbetweening and comparative goal remain incomplete.

## Learned temporal context and coverage research v6-v8

A learned context controller substantially improves aggregate validation but still fails cohort/development gates. More complex per-joint gating is rejected. A bounded, prospectively split 8.27 MB expansion and reproducible training pipeline now exercise untouched confirmation after frozen model selection; the selected expanded pair fails confirmation and remains research-only. TEMPORAL-CONTROLLER-v6-v8.md records complete evidence and limits. No temporal model is bundled or full-goal requirement declared complete.

## Rig observations and cross-fitted temporal research v9

The research rig adapter reads only known poses, calibrates rest axes and preserves

source state across five verified humanoid profiles; authored-pose reconstruction

passes existing control-fitting gates. RIG-OBSERVATIONS-v1.md states the limits.

A separately trained group-excluded convex controller improves validation position

error by 3.4% versus V8 and reproduces exactly, but still fails cohort and previously

observed confirmation acceptance. TEMPORAL-CROSSFIT-v9.md records the protocol,

models and failures. No temporal model is bundled; full learned motion, physics,

rig coverage and independent comparison requirements remain open.

## Context-prior rejection and next product work

All 36 v10 contextual-prior variants lose to the retained V9 research model;

zero-prior controls and group-excluded predictions match V9 exactly. See

TEMPORAL-CONTEXT-PRIOR-v10.md. The next bounded product milestone is optional

continuous whole-body target preview under LIVE-POSE-PLAN-v1.md. It retains the

existing solver, source recovery and quality gates; it does not substitute for

accepted learned temporal motion or the full comparison goal.

## Live posing implementation 0.15.0

The prospective live-preview feature now passes deterministic scheduling and actual-window recovery checks, including undo snapshots captured during fitting. All 238 current regression cases, 76 packaged offline cases and the complete packaged real-window journey pass. The next performance task is to profile idle request validation and the longest cooperative steps without weakening source guards or numerical acceptance. Real learned temporal motion, physics continuity, broader rigs, quadrupeds, optional connector and independent comparative/human assessment remain required.

## Scoped request decoding 0.15.1

The prospective optimization passes exact five-profile output parity, paired

idle timing improvement, source/invalidation guards, relevant regression and

packaged offline/UI recovery. Larger fitting steps remain too slow for full

responsiveness acceptance. The next coherent original-scope milestone is

actual imported-humanoid behavior: existing Mocap/Unity/Unreal recognition is

currently rejected by the whole-body adapter. Follow the prospective

IMPORTED-HUMANOIDS-PLAN-v1.md; no adapter change has been made yet.

## Imported workflow milestone 0.16.0

The prospective IMPORTED-HUMANOIDS-PLAN-v1.md now has behavioral evidence for Mocap, Unity and Unreal FK rigs, real FBX and .blend roundtrips, weighted meshes, source/root ancestry, whole-body/live and legacy posing, anchors, priority interpolation, limited learned completion, contacts, COM and native flight results. The exact ZIP passes offline and actual-window recovery checks. See IMPORTED-HUMANOIDS-v1.md and package-test-v0.16.0.json. Wider imports, Rigify deform-only variants, quadrupeds and production coverage remain required. Next, resolve the actual-rig versus research temporal representation gap using the existing V9/V10 and RIG-OBSERVATIONS evidence, while retaining all model-quality gates; no further unbounded context-prior sweep is warranted. Learned temporal motion, physics refinement, optional connector and independent usability/comparison remain incomplete.

## Temporal observation integration v11

The source-action/stored-anchor mismatch is fixed in the research sampler. A shared rest-calibrated 17-joint training and actual-rig encoder now has 31 focused host cases and exact two-process corpus reproduction over 2912 training / 480 validation windows. Known neighboring anchors and all interior priorities are respected. See TEMPORAL-OBSERVATIONS-v11.md and TEMPORAL-INTEGRATION-PLAN-v11.md. No new model or package is promoted; learned temporal integration remains incomplete. Next implement projection plus isolated editable action generation from known-anchor initialization, with explicit tests against hidden-key leakage, before fitting a corresponding predictor and applying unchanged quality gates.

## Temporal actual-rig projection v1

TEMPORAL-PROJECTION-v1.md records external position/orientation proposals, known-anchor initialization without hidden modeled-key leakage, explicit pins, and validated editable native actions. Fifteen actual-host cases pass. A matching qualified temporal model, interactive generation, general partial-body motion and all original quality/comparison requirements remain pending. Package qualification is recorded separately in package-test-v0.16.1.json.

## Shared-schema learned temporal experiment v12

TEMPORAL-SEMANTIC-MODEL-v12.md records eight reproducible learned candidates through the same physical projection as procedural controls. The procedural control wins; the best learned candidate fails position, rotation, continuity and worst-cohort gates. All eight actual-rig candidate/priority/source-recovery diagnostics and 32 focused native cases pass, but these do not establish learned motion quality. Runtime/package 0.16.1 is unchanged. Raw-output diagnostics locate the quality regression before rig fitting and motivate a frozen trajectory-aware training experiment with training-only design decisions. No temporal model, full milestone or comparative claim is promoted.

## Trajectory-space learned fitting v13

TRAJECTORY-TRAINING-v13.md records exact quadratic trajectory/continuity training and four catalog-group-excluded internal folds. The fixed candidate reduces the projected position deficit from v12's 10.69% to 2.39% and passes acceleration, but position, rotation, velocity and worst-cohort gates still fail. Both complete runs reproduce all 18 model artifacts and metrics. All eight actual-rig candidate/source-recovery diagnostics and 37 focused native cases pass. No model/runtime/package promotion or full milestone is credited. Conditioning and training-error evidence motivate a bounded learned-feature experiment, retaining training-only design selection and all original gates.

## Neural trajectory feature experiment v14

NEURAL-TRAJECTORY-v14.md records real local neural feature learning, gradient tests, four training-only excluded-group configurations and exact independent reproduction. The model fits training motion but fails transfer and the required comparative motion-quality acceptance; no weights or runtime changes are promoted. All 42 focused host cases and eight rig/action/source-recovery diagnostics pass. A controlled identical-anchor diagnostic exposes unintended movement in v12/v13/v14 proposals and motivates observation-conditioned residual magnitude with exact stationary preservation, prospectively retrained under the same gates. Full learned workflow, physics, performance and independent comparison remain incomplete.

## Stationary-preserving learned trajectories v15

CONDITIONED-TRAJECTORY-v15.md records observed-motion scaling in training and prediction. All 186 identical-observation cases now have exactly zero learned correction; sixteen stationary actual-rig cases and eight ordinary candidate/source-recovery cases pass across eight profiles. All 51 focused native cases and exact independent model reproduction pass. Position improves only 0.14% over the projected baseline, below the required 5%; rotation, continuity and worst-cohort acceptance still fail. Runtime/package remains 0.16.1 with no new temporal weights. Next test preservation of context-implied boundary velocities under a prospectively frozen representation and the same original gates.

## Context-reference and boundary experiment v16

BOUNDARY-TRAJECTORY-v16.md records four training-only reference/envelope ablations and an optimizer overshoot repair verified before fitting. Selection favored contextual Hermite with C0 correction; C1 boundary-velocity preservation did not win. The learned candidate wins the combined validation score but fails all required comparative motion-quality acceptance, with only 0.62% position improvement. All 63 focused native cases, 32 moving/stationary real-rig cases and exact independent reproduction pass. No model/runtime/package promotion occurs. The same full goal continues with the missing native takeoff/landing velocity-transition workflow; learned temporal acceptance remains unresolved and mandatory.

## Native velocity transitions 0.17.1

MOMENTUM-TRANSITIONS-v1.md records native takeoff/landing COM velocity matching, priority/contact guards, editable recovery and measured continuity. The 317-case regression coverage (71 refreshed patch cases and 246 audited unchanged-workflow cases), 124 offline package cases and actual-window package lifecycle checks pass. This completes the bounded momentum_refinement implementation milestone; full physics acceptance remains incomplete (angular momentum, dynamic forces/collision and secondary motion), and learned temporal qualification, broader rig coverage, independent human usability and Cascadeur comparisons remain required. Package and host limitations: package-test-v0.17.1.json.

## Presentation patch 0.17.2

The installable build is releases/b4artists_ml_v0.17.2.zip. Only transition labels and the version changed; exact source audit retains the 0.17.1 behavioral qualification without claiming a fresh full regression. All six actual-window recovery events pass on the exact package, and the transition captions/values fit the tested narrow sidebar. See package-test-v0.17.2.json. This adds no learned-motion, comparative, performance or independent usability acceptance; the full goal remains active.

## Learned readout diagnosis v17

READOUT-TRAJECTORY-v17.md records exact final-layer learning and byte-identical reproduction. Validation position improves2.6%, but the 5% target, acceleration and worst-cohort protection still fail. All32 moving/stationary actual-rig diagnostics preserve editable/source recovery. No temporal model is promoted; experimental 0.17.2 remains the installable build. TEMPORAL-COVERAGE-AUDIT-v1.md identifies7.8 minutes of source motion and a fitting/generalization gap; DISTRIBUTION-RECHECK-v17.md resolves the current CMU publisher retrieval gap. Next diagnose contextual-reference overshoot using training data before another frozen experiment or bounded data expansion. All original endpoint requirements and quality thresholds remain.

## Shape-reference learned experiment v18

SHAPE-TRAJECTORY-v18.md records a reproduced learned model and 32 passing actual-rig recovery cases. The added procedural reference improves position materially; the learned correction adds only0.75%, failing the 5% requirement. Acceleration and worst-cohort protection also fail, despite reducing the worst ratio to2.74. No temporal weights are promoted and the 0.17.2 package is unchanged. Next prioritize prospectively bounded distinct motion-data coverage while preserving every holdout, quality threshold and original endpoint requirement.

## Expanded learned trajectory experiment v19

EXPANDED-TRAJECTORY-v19.md records the fixed expansion to78 training clips (17.1minutes), exact six-artifact reproduction and 32 passing actual-rig recovery cases. Position improves3.89% on original validation and 3.21% on new validation relative to the strongest procedural control, short of 5%; acceleration now passes, but worst-cohort ratios2.26/2.91 fail. No temporal model is promoted. A duplicate candidate was excluded against protected validation, and all six new confirmation clips remain sealed. Original controls/windows and addon0.17.2 are unchanged. Next diagnose reference-choice/capacity/objective limitations using training-only evidence before a new frozen experiment. All original endpoint requirements and thresholds remain active.

## Observed kinematic conditioning v20

KINEMATIC-TRAJECTORY-v20.md records an information-preserving548-input representation, exact six-model reproduction and 32 passing actual-rig recovery checks. Combined positional error improves5.83% versus the strongest procedural control; the old set improves4.13% and the newer set6.78%. Worst-cohort ratios worsen to3.05/3.14, so qualification fails and no temporal weights are promoted. All controls, datasets, thresholds and addon0.17.2 remain unchanged; confirmation stays sealed. Next address difficult-cohort protection using training-only evidence and prioritize an inspectable motion-review artifact plus viewport responsiveness. The full original goal remains active.

## Experimental 0.17.3: cancellable preparation

The 0.17.3 ZIP adds staged preparation of temporary evaluation rigs. Default Rigify first active ticks averaged 146.6 ms before and 39.5 ms after in the final headless comparison; worst ticks averaged 95.6 ms after, and total active work increased 9.1%. Full responsiveness remains unqualified. 321 fresh regression cases and four exact-package offline live/Keep/Discard cases pass. Current-package UI interaction and independent animator usability remain unverified; the known host shutdown crash persists. See COOPERATIVE-PREPARATION-v1.md and package-test-v0.17.3.json.

For manual motion inspection, motion-review-v1/index.html contains 96 fixed examples with recorded motion, procedural control and two learned candidates. Data and JavaScript syntax pass static checks; browser policy blocked local-file interaction verification. No reviewer ratings were supplied, and no temporal candidate is qualified or included in the addon. See MOTION-REVIEW-v1.md. All original learned-motion, physics/refinement, rig coverage, optional connector and equivalent Cascadeur comparison requirements remain.

## Experimental 0.17.4: finalization and recovery

The 0.17.4 ZIP reduces finishing pauses, reads structural signatures more efficiently without caching them, and restores the verified preview if the public record is damaged during completion. The released/current fault comparison confirms the recovery fix on BoneForge and default Rigify. All 330 regression cases and four exact-package offline live/Keep/Discard cases pass. Default Rigify finishing ticks averaged 77.99 ms before and 48.03 ms after; worst-tick averages fell 28% and total active work fell 8%, with identical poses and solver metrics across five profiles. The first candidate missed its worst-tick gate and remains recorded as a failure.

Full responsiveness remains incomplete: worst ticks still exceed 50 ms and solves take seconds. Current-package UI interaction, independent animator assessment and equivalent Cascadeur comparison remain unverified; the known host shutdown crash persists. No temporal model is qualified or bundled. All original learned-motion, physics/refinement, rig/quadruped, connector and distribution requirements remain. See FINALIZATION-PERFORMANCE-v1.md and package-test-v0.17.4.json.

## Learned position mixture v21

MIXTURE-TRAJECTORY-v21.md records a fixed supervised blend of procedural and learned v20 positions. Average position improves 7.40%/7.75% on old/new development sets, but worst-cohort ratios remain 1.71/1.37 against a 1.10 ceiling. Failures fall from 25 to 11 of 96 cohorts, including two newly failing long-gap cases; no temporal weights are promoted. Fourteen math/data-boundary checks, exact independent reproduction and 32 actual-rig editable/recovery cases pass. Runtime and ZIP0.17.4 are byte-identical; prior330-case/four-offline-package coverage is retained, not rerun. Host shutdown still fails, confirmation remains sealed, and the full original endpoint and 50-evaluation/15-hour resumed limits remain unchanged. Next investigate learned confidence/loss balancing using training-only evidence, separating raw positional and rotational contributions.

## Relative cohort loss v22

RELATIVE-MIXTURE-v22.md records a fixed loss-only experiment, motivated by a training audit and three rotation/position ablations. Average positional gains remain above5%, and failed cohorts fall11to8of96, but the old worst case worsens1.71to2.45against the unchanged1.10ceiling. This is not an overall improvement or release qualification. Nine new weighting checks, exact inference/zero-strength compatibility, independent reproduction and 32actual-rig recovery checks pass. Package0.17.4, all prior runtime coverage, confirmation ownership and the full original goal/50-evaluation/15-hour limits remain unchanged. Next investigate observed curve-confidence descriptors with group-excluded parent features; do not retune existing candidates or open confirmation.

## Observed curve descriptors v23

CURVE-CONFIDENCE-v23.md records 48 additional observed-proposal features with the original v21 loss. Average position gains remain above 5%; failures fall from 11 to 7 of 96 cohorts versus v21, and worst ratios improve to 1.59/1.21. The unchanged 1.10 limits still fail, so no temporal model is bundled. Comparisons also retain one newly failed case relative to v22. Eighteen pre-fit checks, coordinate/zero-extension compatibility, exact reproduction and 32 actual-rig recovery cases pass. Runtime/package 0.17.4 and prior coverage remain unchanged. Next isolate rotation effects while holding v23 positions fixed. Confirmation, original endpoint, 50-evaluation and 15-hour limits remain unchanged.

## Per-joint position and rotation mixture v24

JOINT-MIXTURE-v24.md records a rejected research candidate: separate joint selections improve aggregate rotation accuracy but increase positional cohort failures from seven to eighteen of 96, including eleven new failures. The old worst ratio rises from 1.59 to 7.86; old and combined average-position gates also fail. Earlier models remain preserved and no temporal weights are bundled. Eighteen pre-fit checks, exact complete reproduction and 32 actual-rig recovery cases pass; host shutdown remains failed. Runtime/package 0.17.4 and prior coverage remain unchanged. Next separate frozen position/rotation contributions before another architecture. Confirmation, full original endpoint, 50 total evaluations and the unchanged 15-hour resumed deadline remain protected.

## Frozen component diagnosis v25

COMPONENT-DIAGNOSIS-v25.md isolates the rejected v24 candidate: using v23 positions with v24 rotations leaves seven failing cohorts, while v24 positions with v23 rotations leaves seventeen. The largest positional regression already exists before physical projection. No combination qualifies; earlier candidates stay frozen and confirmation stays sealed. A fresh current 0.17.4 instrumented profile identifies private-copy bone pruning as the largest default-Rigify preparation pause. Next test bounded pruning batches with restored context at every yield, exact source/pose preservation and measured before/after acceptance. Runtime/package and full original goal/50-evaluation/15-hour limits remain unchanged.

## Rejected pruning optimizations

PRUNING-EXPERIMENTS-v1.md records two rejected performance experiments.64-bone batches and native bulk deletion preserve exact five-profile pose/signature/metric results but worsen default Rigify worst ticks; original speed thresholds were retained. Runtime0.17.4 was restored byte-for-byte and no package was promoted. One fresh source-isolation unittest covers three rigs on the restored implementation; prior330-case coverage is retained, not rerun. Next measure repeated preview decoding before choosing a bounded cache. All original goal criteria and the fixed50-evaluation/15-hour limits remain unchanged.

## Bounded record-cache research

RECORD-CACHE-v1.md records a research-host-only cache with 15passing existing live/record guards and exact five-profile pose/signature/metric parity. Default Rigify idle p95improves32.6%, active work13.5% and worst ticks12.5%, but worst ticks remain above50 ms. Production integration, full regression, memory/lifecycle and package validation remain pending. Runtime and ZIP0.17.4are unchanged; this is not full responsiveness, human-usability or original-goal completion. Preserve the fixed50-evaluation/15-hour limits.

## Experimental 0.17.5: bounded record reconstruction

The local experimental 0.17.5 package integrates bounded record reconstruction. All 345 native regression cases and four exact-package offline live/Keep/Discard cases pass. Default Rigify idle p95 improves 44.4%, total active work 14.3%, and worst-tick averages 13.3%, with exact five-profile poses, signatures and solver metrics. Each read returns an independent mutable tree; source validation remains unchanged. Cache keys/blobs stay within 4 MiB plus bounded container overhead and are released at preview/lifecycle boundaries. Worst ticks still exceed 50 ms. Current UI interaction, independent animator assessment, full learned motion and Cascadeur parity remain unverified; the known host shutdown crash persists. See RECORD-CACHE-PRODUCTION-v1.md and package-test-v0.17.5.json. The original goal remains active and incomplete.

The user authorized 20 additional hours starting September 8 at 23:24:05 UTC, ending September 9 at 19:24:05 UTC. The same goal and 50-evaluation ceiling remain in force; no criteria or history were reset.

## Projected-risk selector preparation v26

The training-only proposal pool contains a hidden-label position oracle with 10.3% average improvement across the first window of each of 466 training cohorts. The existing position-plus-0.1-rotation oracle also passes the diagnostic gates. These are upper-bound coverage diagnostics, not deployable model quality or a release claim. Eighteen proposal/selector checks pass, including exact stationary preservation after a retained one-ULP pre-fit correction.

One configuration is frozen before corpus fitting: 596 observed inputs, 32 hidden units, 12 whole-interval choices, 60 epochs and the unchanged projection/gates. Projected costs and model fitting completed for all 7358 training windows. The fixed candidate passes average position improvement and the other aggregate checks, but fails the 1.10 worst-cohort limit in three of 96 development groups (worst 2.90). Sixteen moving-rig, sixteen stationary-rig, fifteen action/recovery and twenty-five cooperative/lifecycle methods pass. The independent run produced identical frozen weights; complete reproduction of development reports remains pending. A separate 1728-edit raw-proposal diagnostic finds discrete-selection jumps. See PROJECTED-SELECTOR-v26.md; the model remains unqualified. Procedural choices remain labelled procedural; selected v20 components use frozen learned residuals. Runtime/package 0.17.5 and its prior 345-case/four-offline-check evidence remain unchanged. Fresh confirmation stays absent. See PROJECTED-SELECTOR-PLAN-v26.md.

The complete original goal, 50-evaluation ceiling and September 9 at 19:24:05 UTC deadline remain unchanged.

## Cooperative temporal research v1

TEMPORAL-SCHEDULING-PERFORMANCE-v1.md records selective restoration and per-known-pose pauses, with 28 passing native methods and two 24-run counterbalanced comparisons. Exact source, reference samples and cleanup are preserved; total work increases modestly for finer cancellation. Worst steps still exceed the original 50 ms target. Trained-provider cooperative validation passes 25 methods; production UI/disable integration remains pending. No model or runtime package is promoted. Runtime and ZIP 0.17.5, and prior 345 native/four offline evidence remain unchanged. The original endpoint, 50-evaluation ceiling and September 9 at 19:24:05 UTC deadline remain unchanged.

## Evaluation-limit checkpoint

The original goal remains incomplete. Development has reached the authorized 50-evaluation ceiling; the extended time allowance does not raise that ceiling. All tracked jobs are terminal. Experimental 0.17.5 remains the local test build; no temporal research candidate is promoted. See EVALUATION-LIMIT-HANDOFF.md for the full endpoint audit, exact evidence and resumption boundaries.

## Authored-motion product integration, experimental 0.18.0

A bundled procedural trajectory now uses all authored pose positions, explicit interval timing and endpoint SLERP, then projects into the real rig and publishes through the existing editable preview workflow. Authored-only sampling exactly matches the research result on the same three crouch/recover rigs. The panel exposes a cancellable Whole-body Motion option alongside existing Pose Blending. All 369 native regression cases, including 24 new runtime math/lifecycle/operator checks, pass. Seven extracted-package offline workflows pass; the exact 0.18.0 archive is available for local testing.

The derivative diagnostic finds a remaining rotation-velocity discontinuity at the middle crouch priority. Contact correction reduces this jump on these fixtures, but neither C1 continuity nor broad animation quality is established. Next address trajectory timing/rotation continuity and multi-action humanoid references; avoid more selector fitting until the animator workflow is dependable. Preserve original learned temporal motion, physics, human usability, rig/quadruped, optional connector and comparative Cascadeur requirements. The budget is75 total evaluations with the existing September 9, 19:24:05 UTC deadline.

## Full-hierarchy conditioning data

The 23-joint memory-mapped store, 483-feature conditioning schema and frozen 68/17 future train/development subject split now have a train-only weak-label layer. The fixed scan yields 6,160 foot-contact intervals, 1,629 takeoffs, 1,828 landings and 398 static windows. Its deterministic 130-item queue spans 39 subjects, all three duration bands and 16 weak motion tags. Independent reconstruction passes. These are low-confidence review proposals, not physical or human truth. Motion-label Reviewer v2 now makes the complete queue reviewable and strictly validates a completed export, while human-reviewed items remain zero and training remains unauthorized. After actual review evidence exists, freeze an action- and rig-disjoint target before fitting the next full-hierarchy architecture. Do not resume nearby selector variants or promote weights before the unchanged development gates pass. The endpoint is unchanged.

## Full-hierarchy architecture audit

ARCHITECTURE-AUDIT-v2.md freezes the product split between rig adapters, a 23-joint ancestor-local state, exact 17-joint animator constraints, a procedural fallback, a fast bidirectional residual TCN, a distinct conditional-diffusion candidate and deterministic physical refinement. The 6,531 training and 1,125 development window identities are frozen with no subject overlap. A leak-resistant 142-feature block now exposes only immediate previous-to-start and end-to-next motion; hidden inbetween edits cannot change model input. Kinematics and gradient contracts pass. A 100-window training-only scale audit corrected an acceleration-dominated loss before model outcomes were read. The corrected actual-data microfit reaches 7.36% of its starting loss while preserving authored controls exactly. This proves optimization integration only; unseen-character quality, target-host latency, complete physics, human usability and Cascadeur comparison remain open.

## Product-first architecture decision

ARCHITECTURE-DECISION-v3.md retains the hybrid product pipeline while ending capacity-first model iteration after the fixed TCN and diffusion comparisons. Learned models remain replaceable proposal providers behind exact constraints and deterministic physical refinement. The four diffusion fits preserve exact priority poses and hierarchy edges, but all twelve 4/8/12-step comparisons regress against the procedural baseline in position, rotation, derivatives and foot velocity; no checkpoint is exported or promoted. FULL-HIERARCHY-DIFFUSION-v1.md preserves the exact results. REAL-RIG-TASK-PACKET-v1.md now qualifies a 17-joint semantic local hierarchy across eight BoneForge, Rigify and imported fixtures, with a maximum fixed-offset reconstruction error of `8.77e-7` body scales. ACTION-EVIDENCE-AUDIT-v1.md separates 1,824 seen-action development windows from 82 novel aerial/recovery windows and shows why the current heuristic tags are not a qualified action benchmark. MOTION-LABEL-REVIEWER-v1.md provides an offline, source-bound visual workflow for the 130 weak contact, takeoff, landing and static candidates; no item is counted as reviewed yet. Next obtain reviewed evidence, freeze deliberate action holdouts, and complete the animator-facing constraint and physics workflow. Do not train a nearby temporal variant before those independent evidence improvements identify a model-addressable failure.

## Complete-priority TCN comparison

The first four TCN fits exposed a priority-mask defect: six unpinned hierarchy joints caused up to 49.53 degrees of endpoint helper drift and 0.4416 body-scales of endpoint semantic error. Those v1 fits are rejected and preserved. A versioned repair makes all 23 captured hierarchy rotations exact derived constraints at complete priority frames while retaining 17 direct semantic controls elsewhere. A fresh 54/14 subject split excludes all 17 exposed v1 development subjects.

Four repaired fits pass exact priority and bone-length gates but fail learned-motion gates on all 1,906 fresh development windows. Aggregate position improves only 1.87–2.58%, rotation regresses 0.74–1.39%, worst task/gap position ratios are 1.13–1.21, and derivative/foot-velocity measures generally regress. No TCN weights are promoted. FULL-HIERARCHY-TCN-v1.md, FULL-HIERARCHY-TCN-v2.md and the evaluation report preserve the evidence. The fixed hard stop now advances to the distinct conditional-diffusion candidate; no nearby TCN/Transformer/selector or loss-weight variant is allowed.


## 0.20.0 scene-aware contact-suggestion checkpoint

Static authored planes and bounded planar mesh objects now produce provisional foot-contact intervals from evaluated motion and matching grounded priority poses. Suggestions include confidence, provenance and reasons, require explicit animator acceptance, and do not alter animation during scanning. Source, cancellation, acceptance/rejection, correction, Keep/Restore and reload pass on the qualified humanoid fixtures and exact archive. Next extend the vertical-slice benchmark to deliberate walking, running, jumping, landing and turning actions and obtain animator review before using any suggestion as label evidence. Moving surfaces, hands/props, collision and learned temporal motion remain open.

## 0.20.1 contact-performance checkpoint

The default-Rigify foot-contact workflow now passes the frozen source and exact-package latency gates. The final archive passes 429 native checks, 13 established offline workflows, 4 packaged contact-suggestion tests and 3 exact-package actual-window journeys. Suggestion sampling avoids redundant state restoration, complete-rig verification avoids a duplicate dependency-graph update, and final publication is split across cooperative callbacks. This evidence supplies the contact interaction baseline retained by the completed v12 procedural slice below.

## Procedural vertical slice v12

The fixed procedural humanoid slice passes 32/32 automated cases across BoneForge, generated Rigify basic/default and an FBX roundtrip Unity-style rig. It adds difficult transition to reach, crouch, walk, run, jump, land and turn, and records exact source/artifact hashes, scripted correction/interaction counts, lifecycle checks, contact/flight metrics and Windows working-set counters. The 0.20.2 repair keeps large shape-aware rigs on the dependency-closed evaluator and reduces Rigify-default median case time 39.5%. No learned runtime is promoted. Next obtain human motion labels and an independent animator pass on this frozen packet while continuing end-to-end latency work. Only failures demonstrated by that evidence may select the next learned experiment. Quadrupeds, complete physical refinement, the optional connector and matched Cascadeur evaluation remain later gates.

## Procedural vertical-slice human-review gate

The complete 32-case v12 scene set now feeds a balanced, blind, offline reviewer. It contains 3,136 evaluated skeleton frames across two saved variants, preserves displayed priority poses exactly and binds every input scene/report by SHA-256. Per-case method identity and automated measurements remain hidden until the reviewer locks naturalness, contact, continuity, intent, acceptability, correction, interaction and preference judgments. Full export requires every case plus reviewer identity and experience. Static checks and an isolated Edge 152 interaction smoke pass, including playback, filtering, lock/reveal order, incomplete-export rejection and reload persistence. The synthetic browser entry was destroyed and is not human evidence.

Next obtain one complete independent animator export and a separate timed hands-on Bforartists correction pass. Validate the export with `check_procedural_vertical_slice_human_review_v1.py`, then use the observed failures to freeze the next learned experiment. Reviewed cases remain zero; no visual-quality, usability, learned-motion or Cascadeur gate is marked complete. See PROCEDURAL-VERTICAL-SLICE-REVIEWER-v1.md.

## Prospective matched Cascadeur comparison gate

CASCADEUR-COMPARISON-PROTOCOL-v1.md freezes the comparison design before any result. It maps reach, crouch, walk, run, jump, land, turn and difficult transition across three portable proportion-varied humanoids. Each animator completes 24 matched cases; at least three independent animators are required. Exact input poses/timing, asset hashes, version/edition/entitlement/settings, failed runs, 11 automated metrics and 10 blind human metrics are retained. Parity and superiority thresholds are predeclared and validated against the exact v12 source hashes.

The three neutral Unity-style FBX assets are now frozen with project-owned block meshes, standard/tall-long-limbed/short-broad proportions, exact hashes, matching source `.blend` files and a six-open Bforartists source/import audit. `cascadeur_comparison_protocol_v2.json` binds them without changing the matched tasks or claim gates. The bounded disposable Cascadeur import audit now passes for all three assets. Next audit units, rest pose, standard-rig mapping and conversion in the installed Cascadeur entitlement, then run the matched animation protocol. A learned temporal comparison still waits for a separately accepted B4ML model, and human sessions remain external evidence gates; no comparison result or parity claim is present. See `PORTABLE-COMPARISON-CHARACTERS-v1.md`.

## COM acceleration refinement checkpoint

Experimental 0.20.3 adds an opt-in C2 transition that matches the editable native flight representation at takeoff and landing. Source and exact-package BoneForge/Rigify-default evidence show greater than 99% reductions in measured acceleration jumps while keeping velocity, priority, COM-fit and recovery gates. Continue physical refinement with angular momentum, forces, collision and secondary motion. The measured callback p95/max keep the complete responsiveness gate open.

## Rigid-segment angular refinement checkpoint

Experimental 0.22.1 replaces point-mass-only angular measurement with finite solid-ellipsoid tensors for all 17 artist-mass segments, including evaluated axial spin. BoneForge and Rigify-default total variation falls by more than 87%, while C2 composition, editable publication, exact priority endpoints and source recovery remain qualified. Vectorized rotation logs keep exact-package callback p95 at 41.29 ms; one 54.42 ms sample keeps the absolute sub-50 ms gate open. Continue with joint/external forces, collision and secondary motion, while human review remains the prerequisite for choosing another learned temporal experiment.

## 0.23.0 static planar collision checkpoint

Native free flight now offers an opt-in static plane or bounded planar-mesh response using the 17 editable finite ellipsoid segments. It publishes editable linear translation curves, preserves authored endpoints, rejects conflicting priority poses and Root Curves use, and composes with angular refinement and C2 transitions. The same-hash 448-test regression, 25 exact-package offline checks and exact-package five-event window journey pass. The combined window run measures 40.65 ms callback p95 and 54.56 ms maximum. Continue toward force/torque and secondary-motion stages; arbitrary/deforming collision and continuous-time guarantees remain open. Learned temporal work still waits on the existing human-review gate.

## 0.24.0 selected-control secondary-motion checkpoint

The active candidate can now be refined through a stable implicit damped follower on explicitly selected rotation and/or location controls. Every captured priority pose remains exact, channels publish as editable linear keys, and cancellation, regeneration, Restore, Keep/Discard, save/reload, Undo/Redo and flight composition retain the source. The 458-test/49-suite same-hash regression and 35 exact-package checks pass. The exact-package full Rigify journey measures 35.95 ms callback p95 and 38.95 ms maximum. Continue toward secondary gravity/global-space behavior and production-character review without treating this procedural stage as learned motion or parity evidence.

## 0.25.0 world-space secondary checkpoint

Selected controls can now follow evaluated world rotation/location through animated parents and tested rig spaces, with optional scene gravity and bounded static planar point collision. Bounce, friction, clearance, influence and priority-pose conflict behavior are explicit. The same-hash 465-test regression, 42 exact-package checks and exact-package five-event window journey pass; its 77 cooperative steps measure 27.07 ms p95 and 37.12 ms maximum. Continue toward deformable/chain dynamics, broader collision/forces and production-character review without treating this deterministic stage as learned motion or parity evidence.

## 0.36.0 procedural release checkpoint

The installable local package `releases/b4artists_ml_v0.36.0.zip` consolidates the procedural workflow surface through Breakdown Pose and Transition Timing Transfer. The frozen 54-member distributable passed 1,017 source tests across 87 curated suites and 209 exact-package feature tests across 32 suites in eight fresh Bforartists processes, with zero skips. Foreground Breakdown Pose and timing-transfer journeys pass on the exact runtime. The package is ready for local testing. Learned temporal generation, independent animator usability, clean host shutdown and Cascadeur parity remain unqualified; the full goal remains active. See `RELEASE-v0.36.0.md` and `package-test-v0.36.0.json`.

## 0.37 quick interpolation-authoring checkpoint

Development 0.37.0 adds five quick interpolation-authoring slices without changing the frozen 0.36.0 archive. Equalize Later Pose Spacing keeps a selected pivot fixed and places every later saved pose at one 0.25-through-240-frame interval without changing pose or timing payloads. The newest slice passes 8 focused tests, 113 affected tests, and a foreground dialog/operator/source-recovery journey with exactly one Undo and Redo. Learned temporal quality, independent animator review, clean host shutdown, and Cascadeur comparison remain open. See `INBETWEEN-SERIES-v1.md`, `POSE-RETIME-v1.md`, `RIPPLE-RETIME-v1.md`, `POSE-SPACING-SCALE-v1.md`, and `POSE-SPACING-EQUALIZE-v1.md`.

## 0.37 secondary external-acceleration checkpoint

Selected world-space location controls now accept one bounded animator-authored acceleration vector in addition to scene gravity. The solver preserves every captured priority pose, publishes editable linear curves, retains the existing planar collision response, keeps the zero-vector backend compatible, requires complete location curves on every selected control, and excludes ten foreign workflow owners before and during mutation. The 13-test focused suite, 91-test affected regression and foreground Bforartists lifecycle pass; the foreground run measured 10.67 ms callback p95 and 19.40 ms maximum. Continue toward per-control forces and masses, torque, broader collision, deformable chains and production-character review. This deterministic feature does not satisfy learned-motion or Cascadeur comparison gates. See `SECONDARY-EXTERNAL-ACCELERATION-v1.md`.

## 0.37 per-control force and mass checkpoint

Selected world-space location controls can now retain distinct animator-authored force and mass assignments on the armature. The host-independent conversion applies `force / mass` as control-specific acceleration while preserving the existing uniform acceleration, gravity, wind, impulse, priority, collision and recovery behavior. Strict rig-bound records, assignment/clear Undo/Redo, save/reload, BoneForge, generated default Rigify, distinct simultaneous loads, independent acceleration-composition and zero-load oracles, Pose Mode admission, stale-request rollback and exact zero-load version compatibility pass. The 14-test focused suite, 129-test affected regression and foreground Bforartists lifecycle pass; the foreground run measured 11.14 ms callback p95 and 20.29 ms maximum. Force-at-offset torque, momentum transfer, collision-derived forces, broader collision, deformable coupling, production-character review, learned motion and Cascadeur comparison remain open. See `SECONDARY-CONTROL-LOADS-v1.md`.

## 0.37 force-at-offset torque checkpoint

Selected world-space controls can now retain a local force-application offset and scalar rotational inertia with each force/mass assignment. The host-independent model rotates the offset by each authored target world orientation, evaluates `offset x force`, divides by inertia, and adds the bounded angular acceleration to the stable quaternion follower while `force / mass` drives translation. Schema-1 force-only records and exact zero-offset output remain compatible; torque uses rig-bound record schema 2 and report schema 8/backend v7. The 14-test focused suite, 143-test affected regression and foreground Bforartists lifecycle pass; the foreground run measured 11.77 ms callback p95 and 21.80 ms maximum. Coupled joint-force transfer, automatic inertia, collision-derived forces, broader collision, deformable coupling, production-character review, learned motion and Cascadeur comparison remain open. See `SECONDARY-FORCE-OFFSET-TORQUE-v1.md`.

## 0.37 secondary Load From Active checkpoint

The Secondary Motion panel can now recall the complete stored load from one assigned active selected control into Selected Force, Selected Mass, Application Offset (Local), and Rotational Inertia. Schema-1 and schema-2 assignments are supported, validation fails before property mutation, and the command leaves the stored assignment, selection and animation unchanged. The 8-test focused suite and 151-test affected regression across eleven suites pass on one frozen 44-file runtime set. Its 96-step foreground Bforartists journey also passes native recall Undo/Redo and the complete torque generation/recovery lifecycle with 10.61 ms callback p95 and 19.25 ms maximum. This is deterministic authoring convenience and does not satisfy learned-motion or Cascadeur comparison gates. See `SECONDARY-LOAD-FROM-ACTIVE-v1.md`.

## 0.37 static spherical collision checkpoint

Selected world-space location controls can now collide with one explicit static spherical exclusion volume. An unparented, unanimated, non-rigid-body scene object supplies the center and an unkeyed, undriven value supplies radius. The stable follower projects penetrated control pivots to radius plus clearance, applies radial bounce and tangential friction, rejects conflicting priority poses, detects frame-dependent center mutation, verifies evaluated published-pivot clearance to 1e-6, and leaves the legacy Planar path compatible. The 13-test focused suite and 164-test affected regression across twelve suites pass on one frozen 44-file runtime set. Its 86-step foreground Bforartists journey passes visible controls, generation, native Undo/Redo and the complete recovery lifecycle with 10.70 ms callback p95 and 19.22 ms maximum. Bone/mesh volume, multiple or moving colliders, arbitrary/deforming meshes, continuous collision, self-collision, joint impulse transfer, learned motion and Cascadeur comparison remain open. See `SECONDARY-SPHERE-COLLISION-v1.md`.

## 0.37 multiple static spheres checkpoint

Selected world-space location controls can now collide with a persistent, explicit set of up to eight static spherical exclusion volumes. Each row binds a distinct static scene object and independent radius; empty-list operation retains the earlier staged single sphere. Canonical ordering, bounded complete-set projection, duplicate/cap validation, keyed/driven radius rejection, priority conflicts, cooperative mutation cancellation, native Add Undo/Redo, save/reload persistence and evaluated published-pivot clearance pass. The 8-test focused suite and 172-test affected regression across thirteen suites use one frozen 44-file runtime set, and focused/aggregate/foreground receipts bind the complete transitive fixture chain. Its 86-step foreground Bforartists journey displays both editable rows and completes solve Undo/Redo and source recovery with 10.76 ms callback p95 and 18.26 ms maximum. Arbitrary/moving/deforming mesh collision, bone/mesh volume, continuous collision, self-collision, coupled collision forces, learned motion and Cascadeur comparison remain open. See `SECONDARY-MULTI-SPHERE-COLLISION-v1.md`.

## 0.37 moving rigid spheres checkpoint

Development 0.37 adds opt-in direct object-location animation for any row in the one-to-eight sphere set, including mixed static and moving colliders. Nine focused tests and 181 affected tests across fourteen suites pass on one frozen 44-file runtime set. Admission requires complete unmuted Location X/Y/Z curves and rejects parents, constraints, rigid bodies, drivers, NLA, curve modifiers, animated scale and delta location. The request binds the complete Action evaluation structure, and publication rechecks each live evaluated center before accepting clearance. Relative center velocity drives bounce and friction. The 86-step foreground journey passes mixed-row editing, cooperative and synchronous generation, native Undo/Redo, Restore Input, Keep and Restore Source at 11.10 ms callback p95 and 18.34 ms maximum. This remains sampled point exclusion; arbitrary or deforming geometry, parented/constrained/physics-driven centers, continuous or self-collision, coupled collision forces, learned motion and Cascadeur parity remain open. See `SECONDARY-MOVING-SPHERE-COLLISION-v1.md`.

## 0.37 animated sphere radius checkpoint

Development 0.37 adds opt-in direct uniform Scale XYZ animation to each sphere radius. The explicit radius remains the base value, each exact solve frame samples its evaluated positive uniform scale, and radial boundary velocity participates in relative bounce response. Complete unmuted Scale X/Y/Z curves are required; nonuniform, negative, incomplete, muted, modified, driven, NLA, delta-scale or post-sampling mutation rejects safely. Fifteen focused tests and 187 affected tests across fourteen suites pass on one frozen 44-file runtime set, with the existing static, moving-center, BoneForge and generated Rigify paths retained. The 86-step foreground BoneForge journey passes visible per-row controls, cooperative and synchronous solves, native Undo/Redo, Restore Input, Keep and Restore Source at 11.17 ms callback p95 and 17.44 ms maximum. This remains deterministic sampled point exclusion; arbitrary or deforming geometry, continuous or self-collision, coupled collision forces, learned motion and Cascadeur parity remain open. See `SECONDARY-ANIMATED-RADIUS-v1.md`.

## 0.37 sphere radius fit checkpoint

Development 0.37 adds a native-Undoable **Fit Radius from Bounds** action for the staged sphere and every persistent row. It snapshots a conservative origin-centered radius from eight supported object-bound corners. Static fitting includes the current world transform; Follow Radius Scale stores the local base radius so evaluated uniform scale is applied once. Float32 storage rounds upward and is rechecked for exact enclosure; missing, unavailable, degenerate or oversized bounds reject without retaining a partial value. Five focused tests and 192 affected tests across fifteen suites pass on one frozen 44-file runtime set. The 86-step foreground BoneForge journey fits two mesh bounds, displays the row controls, and passes solve Undo/Redo plus full recovery at 10.91 ms callback p95 and 23.98 ms maximum. This is a procedural setup snapshot, not arbitrary/deforming mesh collision, learned shape inference or Cascadeur parity. See `SECONDARY-SPHERE-FIT-v1.md`.
