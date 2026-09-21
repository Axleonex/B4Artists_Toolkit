# B4Artists Machine Learning

Experimental 0.31.0 adds provisional four-paw contact suggestions for generated Rigify cat, horse and wolf candidates, using evaluated motion and an explicit plane or static planar mesh. Review and accept suggestions before the existing copied-action correction. Early frame-rate, priority-pose and rig-transform changes now cancel scanning; fractional priorities are sampled. The focused source passes 17 tests, the exact archive passes 10 offline checks, and the frozen current source passes the complete 53-suite/487-test regression. See PAW-SUGGESTIONS-v0.31.0.md. These are heuristic suggestions; learned gait, learned temporal motion, human usability and Cascadeur parity remain unqualified.

Development 0.35 now has ten verified quadruped workflow slices. Generated Rigify cat, horse, and wolf retain the six-helper Body, four-paw, and semantic Head preview; schema 3 adds Spine Follow plus Neck Share; opt-in schema 4 adds four position-only Pole Targets; **Match + Enable All Poles** uses the generated rig's pose-preserving Toggle Pole operator at the current frame; Procedural Gait Phases classifies support sets from animator-accepted contacts without changing motion; per-target Reset returns one helper to its preview-start transform; bidirectional target mirroring transfers fore/hind paw and optional Pole Target edits; a scene-local pose-request asset transfers verified sparse targets between cat, horse, and wolf in normalized Body coordinates; per-limb **Align Bend** places one Pole Target on its current evaluated bend ray; and **Flip Side** plus body-scale **Set Distance** provide guarded per-pole shaping. The newest suite passes 8/8 focused and 136/136 affected tests across 18 suites on one frozen 44-file runtime hash set, plus foreground Flip/Distance/Undo/Redo evidence and final serial-review PASS. See QUADRUPED-HEAD-v1.md, QUADRUPED-SPINE-FOLLOW-v1.md, QUADRUPED-POLES-v1.md, QUADRUPED-POLE-MATCH-v1.md, QUADRUPED-GAIT-PHASES-v1.md, QUADRUPED-TARGET-RESET-v1.md, QUADRUPED-TARGET-MIRROR-v1.md, QUADRUPED-POSE-ASSET-v1.md, QUADRUPED-POLE-ALIGN-v1.md, and QUADRUPED-POLE-CONTROLS-v1.md. Learned gait recognition/generation, imported/custom quadruped adapters, human review, packaging, and Cascadeur comparison remain open.

Development 0.36 adds deterministic interpolation timing controls to Pose Blending: Uniform, Ease In / Out, Ease In, Ease Out, a bounded global Breakdown Bias, and destination-owned easing, bias, Departure Hold, and Arrival Hold for individual incoming transitions without moving captured pose frames. At least 10% of every interval remains active. Legacy timing records and first-pose ownership are repaired without touching the source Action. **Create Breakdown Pose** inserts a normal editable anchor at the playhead using a direct prior-to-following blend; selected-control mode keeps all unselected controls at the exact effective-timing preview. A rig-local Copy/Paste clipboard transfers the complete timing setup between destination intervals; global intervals copy as stable explicit snapshots. The newest slice passes 6/6 focused and 176/176 affected tests across 23 suites on one frozen 44-file runtime set, a foreground Copy/Paste/operator/Undo/Redo journey, and bounded Action structure recovery checks. Learned timing, animator comparison, packaging, and Cascadeur comparison remain open. See `TIMING-CONTROLS-v1.md`, `TRANSITION-TIMING-v1.md`, `TRANSITION-WINDOW-v1.md`, `BREAKDOWN-POSE-v1.md`, and `TRANSITION-TIMING-TRANSFER-v1.md`.

## Product scope

A separate, locally operating, Bforartists-exclusive add-on. No runtime dependency on Ghost Tool, Anim Assist, BoneForge, Rigify, Cascadeur, an online account or a paid API. Humanoids are first and quadrupeds second. The original Ghost Tool and Anim Assist source remain untouched.

The target is complete sparse-input posing, intelligent learned inbetweening, contacts, balance, physics and refinement, supported by reproducible quality/performance comparisons. See REQUIREMENTS.md for the full scope, ROADMAP.md for execution history, DELIVERY-ORDER-v1.md for the active achievable-first build sequence, ARCHITECTURE-DECISION-v3.md for the product-first hybrid decision and ARCHITECTURE-REVIEW-v4.md for the retained architecture and evidence rules. Completing the current deterministic subset does not complete the goal.

## Working workflows

- Inspect supported humanoid and generated Rigify quadruped conventions through a read-only mapping snapshot. The development 0.33 panel distinguishes mapped and directly writable animator controls from deform, mechanism, organization, widget and tweak bones; reports missing semantic roles and adapter warnings; and shows current capture, blending, or whole-body preflight results. See `RIG-DIAGNOSTICS-v1.md`.
- Correct one or more detected humanoid semantic roles on an individual armature object through a bounded Role/Bone editor. Development 0.33 binds the exact payload to its adapter and bone-name/hierarchy signature, feeds validated roles into capture/posing/cleanup/diagnostics, preserves pose and animation, and rejects stale, structural, duplicate, corrupt, unknown-family and quadruped input. See `MAPPING-CORRECTIONS-v1.md`.

- Inspect Rigify cat, horse and wolf as quadrupeds, then capture full poses and generate reversible Pose Blending candidates without writing generated mechanism bones.

- Pose generated Rigify cat, horse and wolf rigs with a Body target, four independent paw targets, and a rotation-only semantic Head target while preserving their existing native IK setup. Body and paw helpers can optionally author native control world rotations. Spine Follow and Neck Share distribute a bounded part of the Head turn through semantic Chest and Neck controls before Head is corrected to its exact target. Opt-in Pole Targets move four source-bound native Rigify pole controls and prove evaluated bend response while paw pins remain bounded. **Match + Enable All Poles** prepares dormant poles with Rigify's generated current-frame pose matcher while preserving the action and Auto Key. Solve remains deterministic, bounded to eight position-residual passes, and reversible; it does not infer gait or natural motion. See QUADRUPED-HEAD-v1.md, QUADRUPED-SPINE-FOLLOW-v1.md, QUADRUPED-POLES-v1.md, and QUADRUPED-POLE-MATCH-v1.md.

- Capture four-paw contact points and time intervals on a generated Rigify cat, horse or wolf Pose Blending candidate. Preview writes ordinary linear location/rotation keys to a copied action at quarter-frame samples and checks them at eighth-frame samples. Captured priority poses remain unchanged; no contact or gait is inferred.

- Review humanoid and quadruped contact suggestions with compatible-family counts, bulk accept/reject and fractional previous/next interval navigation. Review changes no action curves.

- Classify the accepted generated-Rigify quadruped contact schedule into conservative Flight, Single, Diagonal, Lateral, Fore, Hind, Triple, and Full Support intervals. Previous/Next navigation uses interval midpoints and strictly revalidates the candidate action and contacts without editing animation. See `QUADRUPED-GAIT-PHASES-v1.md`.
- Reset one active generated-Rigify quadruped Body, paw, Head, or optional Pole helper to its preview-start transform without changing other helpers, rig pose, source animation, or native rig modes. Saved schemas 1-4 and foreground Undo/Redo are covered. See `QUADRUPED-TARGET-RESET-v1.md`.
- Mirror generated-Rigify quadruped fore/hind paw position and orientation edits from left to right or right to left, including position-only Pole Targets when active. Source helpers, destination options, rig pose, source animation, saved schemas 1-4, and foreground Undo/Redo are covered. See `QUADRUPED-TARGET-MIRROR-v1.md`.
- Align one schema-4 quadruped Pole Target to its current evaluated limb bend ray while preserving its middle-joint radius. The operation leaves the rig, source animation, native modes, other helpers and request options unchanged, and invalidates the stale solve until the animator solves again. See `QUADRUPED-POLE-ALIGN-v1.md`.
- Flip one schema-4 quadruped Pole Target across the current limb bend or set its normalized radial distance while preserving the source Action, rig pose, modes, other helpers and request options. See `QUADRUPED-POLE-CONTROLS-v1.md`.

- Inspect exact contact boundaries with Go Start/Go End and atomically set Start/End from a fractional playhead for humanoid and generated Rigify quadruped contacts. Development 0.34 validates candidate bounds and same-limb overlap before mutation, supports Undo/Redo and save/reload, and preserves animation and rig state. See `CONTACT-INTERVAL-EDIT-v1.md`.

- Bind an accepted humanoid hand contact explicitly to a directly animated rigid prop. Development 0.34 stores the captured relationship in prop-local position and rotation, follows the evaluated prop transform through the interval, preserves the source and prop actions, rejects unsupported ownership or animation changes, and supports Undo plus save/reload. See `PROP-HOLDS-v1.md`.

- Bind an accepted humanoid foot contact explicitly to a directly animated rigid planar mesh. Development 0.34 follows the platform's evaluated per-frame transform, verifies Blender-tessellated surface containment, preserves both actions, fails closed on geometry or animation changes, and supports Undo plus save/reload. See `MOVING-PLATFORMS-v1.md`.

- Review humanoid and generated Rigify quadruped contacts directly in the 3D View. Development 0.34 draws the selected or compatible targets and evaluated-limb separation, reports the exact correction phase/influence, and navigates Blend In, Hold Start, Hold End and Blend Out without editing animation. See `CONTACT-VISUALIZATION-v1.md`.

- Shape Pose Blending timing with Uniform, Ease In / Out, Ease In, or Ease Out and move the breakdown earlier or later with a bounded global bias. Captured pose frames stay exact, each adjacent interval is remapped independently, and Discard returns to the original source Action. See `TIMING-CONTROLS-v1.md`.

- Preview deterministic smoothing and conservative redundant-key removal on selected or all captured controls in a copied candidate. Priority poses, accepted-contact dependencies and the retained input are protected; Escape, Undo/Redo, Keep, Restore Input, save/reload and Restore Source Animation are covered by native workflows. This procedural workflow is packaged in experimental 0.32.0 and remains explicitly non-learned.
- Apply an opt-in conservative humanoid joint-limit preset to verified semantic controls during whole-body posing. The development 0.33 source displays preset provenance, preserves per-character overrides, leaves unmapped controls unchanged, and passes BoneForge, Rigify basic/default, metarig, and imported Unity coverage. See `JOINT-LIMIT-PRESETS-v1.md`.

- Enable optional semantic Chest and Neck position and Rotation constraints during whole-body posing. They start released, map joints 2 and 3 of the existing 17-joint representation through each verified adapter, evaluate the selected skeletal orientation, and distribute rotation through verified writable spine controls. See `CHEST-TARGET-v1.md`, `CHEST-ORIENTATION-v1.md` and `NECK-TARGET-v1.md`.

- Reset one whole-body target to its preview-start transform while preserving its position/rotation/pole toggles and current rig pose. Hand and foot resets include their owned elbow or knee direction helper; stale results must solve again before Keep. See TARGET-RESET-v1.md.

- Mirror authored hand, foot, elbow-direction and knee-direction helper deltas from left to right or right to left through the verified semantic body frame. The operation preserves source helpers, destination toggles, rig pose and source animation. See TARGET-MIRROR-v1.md.

- Align an owned elbow or knee direction helper to the current evaluated limb bend without changing its toggle, rig pose or source animation. Straight limbs and unsupported helper state fail atomically. See POLE-ALIGN-v1.md.

- Flip an owned elbow or knee helper opposite the current evaluated bend plane to request the alternative bend direction. Distance is preserved or raised to the documented stability minimum; toggle, rig pose and source animation remain unchanged. See POLE-FLIP-v1.md.

- Capture multiple pose anchors and generate editable, separate action candidates using deterministic shortest-path quaternion interpolation and optional smoothstep timing.

- Duplicate a validated pose anchor to the current frame as a same-armature authored priority pose for holds or repetition. Development 0.33 preserves the rig and source action, supports overwrite, Undo/Redo and save/reload, and fails closed on stale or malformed anchor sets. See `POSE-REUSE-v1.md`.
- Place elbow/knee helpers along or opposite the evaluated bend, then set their radial reach in body-scale units without changing direction. Development 0.33 uses circular in-front pole displays and preserves the rig pose, source animation, toggles and preview lifecycle. See `POLE-ALIGN-v1.md`, `POLE-FLIP-v1.md` and `POLE-DISTANCE-v1.md`.
- Save one verified eight-target whole-body request into the scene and apply it to another supported humanoid adapter in normalized body coordinates. Development 0.33 preserves the destination rig pose until Solve, carries position/rotation/pole requests, invalidates stale solves and survives save/reload. See `POSE-ASSET-v1.md`.

- Select pose controls and preview deterministic local or evaluated-world rotation/location follow-through, optional scene gravity and bounded planar collision on a copied candidate, with exact captured priority poses and Restore Input. In Local rotation mode, an explicitly selected direct chain can propagate bounded parent lag into its children.

- Pose from hand/foot targets, pole hints, explicit world-space pelvis displacement, target strength and a geometric elbow/knee bend cap. Keep as an anchor or cancel the session.

- Accept default BoneForge and Rigify IK inputs by matching their evaluated joints onto FK controls. Native IK constraints are not edited. Generated motion uses FK; this is explicit in the panel.

- Store canonical rig modes with normalized anchors. Candidate actions key the required IK/FK modes inside the authored interval and return to sampled input values outside it. Discard restores the original action, slot, transforms and mode values.

- After keeping a candidate, **Restore Source Animation** returns to its input action and mode state. The candidate remains available as an action. The recovery record survives save/reload.

- Restore the source setup after saving an anchor from a converted IK posing session. The animator can inspect the solved pose before keeping, and see the saved result again in an interpolation candidate.

- Opt into a trained local elbow/knee bend prior per limb, blend its influence, and retain authored poles when inputs fall outside training bounds. Model errors roll the pose back. Default BoneForge/Rigify arms currently fall back because their proportions are outside this first model's domain.

## Compatibility evidence

Reference: [BoneForge B4Artists](https://github.com/Axleonex/BoneForge_B4Artists). Its original mocap, Unity, Unreal and Rigify deform JSON maps remain bundled unchanged under GPL terms. Additional naming recognition covers legacy/metarig skeletons, generated Rigify controls, VRoid/VRM and MMD. These names are not a substitute for behavioral tests.

Runtime fixtures use the actual BoneForge builder and Rigify basic/default human generators. Default IK inputs, FK posing, animated IK/FK source properties, source restoration and evaluated mesh samples are tested. Basic/default metarigs have FK workflow tests. BoneForge's IK switch direction is opposite to Rigify's; the adapter records this explicitly.

Mocap, Unity and Unreal plain-FK conventions now have independently authored FBX skeleton/weighted-mesh workflow tests, including root ancestry and transformed proportions. Other import variants, arbitrary parent spaces and production characters still need wider coverage. No asset/file importer or character model is bundled. Use the host/BoneForge to import assets and select the resulting rig or bound mesh.

## Boundaries

This combines geometric limb solving, optional learned bend directions, deterministic local transform interpolation and selected-control local/world secondary motion with optional gravity and planar point collision. Local rotation mode can couple one explicitly selected direct chain; location remains independent and chains do not use world gravity/collision. The contextual model adds head/pelvis targets and automatic spine/body fitting on tested humanoids; development 0.33 adds opt-in Chest/Neck constraints, Reset, pole placement/distance and a scene-local cross-rig semantic target-pose asset. Development 0.34 adds explicit local-transform holds from humanoid hands to directly animated rigid props, from humanoid feet to directly animated rigid planar meshes, and read-only contact target/separation overlays with exact blend-boundary review. Development 0.35 adds direct semantic Head orientation, adjustable Head-to-Spine follow, opt-in native fore/hind Pole Targets, current-frame pole matching, per-target preview reset, bidirectional paw/pole target mirroring, per-pole current-bend alignment, per-pole side flipping and normalized distance control, and read-only support-phase review from accepted contacts to the generated-Rigify quadruped workflow. The asset transfers sparse requests rather than raw controls or animation. Lower-spine target shaping, animated-range quadruped pole conversion, a pose library, production-character retargeting, learned pole/orientation conditioning, automatic contacts, gait recognition/generation, moving-surface COM/support analysis, constrained, deforming or physics-driven target holds, arbitrary mesh/self-collision, dynamic/temporal balance, joint torque, broad external-force solving, deformable or automatically inferred secondary dynamics and learned motion remain unfinished. Native free flight includes artist-mass finite ellipsoid angular refinement and a sampled static plane response. The older limb prior predicts only a bend direction. Maximum Bend is only an elbow/knee flexion cap. Targets refer to wrists/ankles, not full collision volumes.

Default whole-body capture normalizes known generated rigs to FK. Selected Controls Only retains its existing direct-control semantics and requires consistent rig settings. Mixing legacy/native and normalized anchors is rejected with a recapture instruction. Full IK-to-FK matching verifies joint position, orientation and scale; unsupported matches roll back.

Positive uniform object scale and ordinary writable controls are supported. Nonuniform/reflected object transforms, arbitrary constraints/drivers on writable FK controls, incompatible locked channels, unsupported NLA/action layering and animated non-mode rig properties require future adapters. Native IK output, mixed output modes and arbitrary space changes are not implemented.

Whole-body solves are cooperative in the UI, with a single-solve button or opt-in Live Solve after target edits settle. Escape, Keep/Cancel, undo/redo and save/reload stop unfinished work safely. Live mode never resumes from a restored scene. Legacy limb solves and scripted EXEC calls are synchronous. Measured default Rigify scheduling and fit latency still miss the full responsiveness goal. Candidate limits remain 240-frame span, 128 anchors and a conservative 200,000-key budget, including mode keys. Full revolutions need intermediate anchors.

The original action data is never rewritten. Candidate copies replace captured channels in the interval; inserting keys can affect neighboring automatic handles. Mode keys add one-frame boundary samples, so adjacent subframe behavior may change in the candidate. Use Restore Source Animation rather than only selecting the source in the action dropdown: selecting an action alone cannot restore unkeyed input rig properties. Only the most recent kept candidate has this object-local recovery record.

## Publication and references

Author and committer must both be axlbot <axleonex@gmail.com>; GitHub authentication must be Axleonex. No ML commits or pushes have been made. Publication requires the repository review and explicit confirmation.

Behavioral targets: [AutoPosing](https://cascadeur.com/help/tools/animation_tools/autoposing), [Inbetweening](https://cascadeur.com/help/category/278), [AutoPhysics](https://cascadeur.com/help/tools/physics_tools/autophysics), and [Cascadeur 2026.2](https://cascadeur.com/help/category/319). These references provide neither proprietary algorithms nor model weights, and do not establish parity.

## Subsequent model research

Proportion-augmented V3 and expanded-data V4 candidates failed their release gates. The 0.4 model remains installed in the package; see MODEL-RESEARCH-0.4-followup.md and CONTEXTUAL-POSE-EXPERIMENT.md. The arm compatibility gap remains open.

## Historical contextual research checkpoint (before 0.5)

A frozen 17-joint learned completion backend now has host decoder/math tests, reproducible weights and CPU measurements. It is outside the released add-on and has no full-body BoneForge/Rigify control adapter. Fresh confirmation passed its gates, but the linear baseline was slightly better, and prior-pose validation favors geometric adjustment. See CONTEXTUAL-POSE-RESULTS-v1.md and checkpoint-context-pose-v1.json. The 0.4 package and complete product requirements remain unchanged.

## Current whole-body integration

Version 0.5 integrates the frozen contextual model with actual-rig fitting, six positional targets, persistent modal previews and editable anchors. See USER_GUIDE.md, VALIDATION-0.5.md and PROXY-EVALUATION.md. The prior research evidence remains historical; linear confirmation superiority and prior-pose neural regressions remain unresolved. No parity or visual-quality claim is made.

## Explicit control update in 0.6.0

Optional world-space rotation targets and elbow/knee pole directions now participate in whole-body previews, with persistent settings, original-rig verification and editable anchors. They geometrically constrain the existing learned suggestion; the model itself is unchanged. BODY-CONTROLS.md records the measured scope, saved-preview compatibility and remaining requirements.

## 0.7.0 configurable limits

Whole-body previews include persistent per-control rest-local swing and twist bounds, integrated fitting and original-rig acceptance. Defaults are disabled for deliberate opt-in. The UI uses a control selector and shows the selected control's settings. JOINT-LIMITS.md records active-limit and recovery tests. This advances the joint-limit requirement, but does not complete anatomical modeling, hinge-plane restrictions, temporal enforcement or production quality.

## 0.8.0 evaluated skeletal limits

Selected joint limits can now measure evaluated skeletal child/parent rotations independently of animator control-follow spaces. Actual effector and distributed-neck dependencies participate in fitting. This advances anatomical frame support, while calibrated presets, directional hinge/swing regions, temporal enforcement, balance and the remaining learned-motion/physics requirements stay open. See JOINT-FRAMES.md.

## 0.9.0 directional bend bounds

Whole-body previews now support artist-defined signed forward bend intervals, sideways allowances, and pose-based calibration of the forward axis. The settings use either existing control or supported skeletal frames, persist across preview/reload, and participate in original-rig acceptance. This advances directional limit support; it does not provide anatomical range presets, new neural weights, learned temporal motion or Cascadeur parity. See BEND-LIMITS.md for package validation and measured UI cost.

## 0.10.0 temporal contact correction

Explicit hand/foot hold intervals now feed a geometric correction of isolated FK animation candidates. Static world contacts support local sole/palm offsets, held rotations, transition blending, selective strength, preserved priority poses and cancellation. Intermediate checks trigger bounded local key refinement. Repeated previews use the retained uncorrected input, with Restore Before Contacts and save/reload recovery. This does not complete learned motion, support/balance, collision or physics requirements. CONTACTS.md records the exact evidence and limitations.

## Temporal research checkpoint

The first actual temporal query model and reproducible evaluation pipeline are implemented outside the add-on. Both validation and confirmation quality gates fail; no new motion model is promoted into release 0.10.0. TEMPORAL-MOTION-v1.md records 14 leakage/math tests, host inference checks, frozen results and the sequence/kinematic changes required next. Learned-motion product acceptance remains incomplete.

## Full-hierarchy sequence research checkpoint

TEMPORAL-MOTION-v2.md records a 23-joint differentiable FK decoder, smooth learned curve coefficients and velocity/acceleration training. Source-edge stretching is eliminated in tested research outputs; learned validation quality still regresses and the zero-residual baseline wins selection. No model or runtime release is promoted. 13 new tests, prior temporal regressions and nonzero-model host inference cover the research layer only. Learned-animation, real-rig workflow and full product acceptance remain open.

## Motion capacity and kernel research checkpoint

TEMPORAL-MOTION-v3.md records a hidden-answer capacity diagnostic and controlled observed-input/learner comparisons. A nonzero kernel model wins validation selection with 1.86% lower average position error than linear interpolation, but fails the 5% improvement, cohort and observed-development gates. It remains research-only. 38 standalone tests and selected-model host inference pass; the host still crashes at shutdown. Runtime 0.10.0 and the full remaining product scope are unchanged.

## Explicit physical-context checkpoint

GRAVITY-CONTEXT-v4.md records gravity/support encoding, a read-only scene adapter and an analytical free-point helper. Physical tilt is now distinguishable from coordinate changes. The direction-conditioned learner improves validation only marginally and still fails full quality gates. 52 standalone tests and actual scene-context checks pass, followed by the known host shutdown crash. No runtime release is promoted; actual-rig COM/support and full learned-motion/physics acceptance remain open.

## 0.11.0 explicit COM/support diagnostic

An editable 17-segment mass model now drives current-pose COM/support snapshots on the verified BoneForge and Rigify adapters. Authored static support patches are screened against evaluated contact positions/orientations, hold timing and a world-space plane. The workflow preserves native IK and animation, supports saved settings and UI Undo/Redo, and reports geometric limitations explicitly. SUPPORT.md records implementation and evidence. This advances COM/support analysis; automatic balance, gravity trajectory application, momentum, learned temporal quality, quadrupeds, connector and comparative acceptance remain open.

## 0.12.0 static balance correction

Whole-body previews now fit the authored COM projection toward a support inset, with explicit strength and optional pelvis translation. Supporting hand/foot positions and orientations, animator pins and enabled joint limits remain acceptance constraints on the original rig. Cancellation, Keep, Undo/Redo, source recovery and saved previews retain the existing workflow. BALANCE.md records real-rig evidence and the helper-transform correctness fix. Static geometry is not dynamic balance: applied gravity/momentum across motion, learned temporal quality, production/other rig coverage, quadrupeds, connector and comparative acceptance remain open.

## 0.13.0 authored COM flight

Explicit airborne intervals now fit editable master-root curves to constant scene gravity, with retained input, adjustable influence, priority preservation, contact-order validation, adaptive sampling and boundary-velocity diagnostics. This is procedural physics assistance; learned temporal acceptance, full angular momentum, secondary motion, production/other rig coverage, quadrupeds, connector and comparative quality remain open. See FLIGHT.md and the shared goalposts ledger for evidence and acceptance status.

## Flight performance maintenance in 0.13.1

Indexed key lookup and bulk curve fingerprints reduce measured long-clip stalls. Regenerating flight removes only an unchanged, unreferenced prior result owned by that preview. Edited, renamed, shared, fake-user, asset-marked and legacy results are preserved. Refinement passes now reject changed playhead/object space at the pass boundary. Source actions and the retained flight input remain recoverable.

See FLIGHT-OPTIMIZATION.md for current validation and timing receipts. Long default Rigify flights still reject when facial-bone basis error exceeds the unchanged tolerance; a rollback regression covers the observed 60-frame case. Full performance, host lifecycle, animator usability and the original learned-motion/Cascadeur objective remain incomplete.

## 0.14.0 native motion integration

Native Motion Layer adds a separate editable translation trajectory to COM flight. The source rig evaluates at its original coordinates, avoiding the facial-bone precision rejection observed with long default Rigify root-curve corrections. The tested native 60-frame default Rigify flight meets the same COM, relative-bone and acceleration gates. Keep/Discard, complete saved motion alternatives, source restoration, displayed pose helpers and contact/support coordinates now participate in the workflow. Native playback survives reopening without the add-on or script execution.

This is procedural gravity assistance. The two bundled learned pose models are unchanged; learned temporal motion, momentum transitions, secondary motion, full rig coverage and independent animator/Cascadeur acceptance remain unfinished. NATIVE-FLIGHT.md documents limits, tests and the bounded near-convergence retry for whole-body posing. No source animation, Ghost Tool, Anim Assist or Git history is changed by this milestone.

## Qualification after native integration

The 60-frame BoneForge/default Rigify native benchmarks meet their frozen engineering budgets; both tested 240-frame intervals reject at the unchanged acceleration gate. NATIVE-FLIGHT-PERFORMANCE-v1.md records the distinction. REPRODUCIBILITY-0.14.md records fresh byte-identical training and confirmation for both shipped pose models with the original default 16-thread BLAS environment. Learned temporal quality, full performance, independent usability and full product acceptance remain open.

## 0.14.1 multiple native flights

Long flight expressions now use a native driver per interval plus a final sum. Zero/partial strength and up to sixteen intervals pass the documented transformed-rig fixtures, including complete result recovery and add-on-free saved playback. NATIVE-MULTI-FLIGHT-0.14.1.md records the bounded coverage; learned temporal, physics breadth, production rigs and independent comparative acceptance remain incomplete.

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

0.15.1 scopes repeated preview decoding to one live tick. Paired idle p95 drops

about 53% on BoneForge/default Rigify with exact five-profile pose parity.

124 fresh regression cases, explicitly retained independent coverage, 83 fresh

offline cases and the packaged actual-window journey pass. Full quality gates

remain open; the next original-scope work is behavioral imported-humanoid

adapters under IMPORTED-HUMANOIDS-PLAN-v1.md.

## Imported FK humanoids in 0.16.0

Whole-body and live posing, anchors, interpolation, limits, contacts, support and native flight now operate on the validated plain-FK Mocap/Unity/Unreal fixtures. Connected pelvis roots use an editable ancestor; root ancestry is captured and reinterpolated inside the candidate interval. Original actions and rest/mesh data remain intact. Ordinary partial/nonstandard-rig capture retains its earlier availability. See IMPORTED-HUMANOIDS-v1.md for all 257 regression cases, final correction provenance, 95 offline cases and three packaged native UI journeys. This is measured synthetic-fixture support, not complete production compatibility or new learned-motion quality.

## Temporal projection integration in 0.16.1

TEMPORAL-PROJECTION-v1.md records the shared-observation to real-rig and editable-action path, with all 17 orientations, exact priorities, source preservation and failure recovery. The runtime interfaces are packaged; temporal orchestration and its procedural provider remain research code. No learned temporal model or new interpolation panel control is promoted. Current-source 303-case regression, 110 offline cases and actual-window Rigify/imported recovery checks pass; host shutdown and full-goal quality remain unqualified.

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

The user authorized 20 additional hours starting September 8 at 23:24:05 UTC, ending September 9 at 19:24:05 UTC. The same goal now has a user-authorized ceiling of 75 total evaluations; the September 9, 19:24:05 UTC deadline and original criteria/history remain unchanged.

## Projected-risk selector preparation v26

The training-only proposal pool contains a hidden-label position oracle with 10.3% average improvement across the first window of each of 466 training cohorts. The existing position-plus-0.1-rotation oracle also passes the diagnostic gates. These are upper-bound coverage diagnostics, not deployable model quality or a release claim. Eighteen proposal/selector checks pass, including exact stationary preservation after a retained one-ULP pre-fit correction.

One configuration is frozen before corpus fitting: 596 observed inputs, 32 hidden units, 12 whole-interval choices, 60 epochs and the unchanged projection/gates. Projected costs and model fitting completed for all 7358 training windows. The fixed candidate passes average position improvement and the other aggregate checks, but fails the 1.10 worst-cohort limit in three of 96 development groups (worst 2.90). Sixteen moving-rig, sixteen stationary-rig, fifteen action/recovery and twenty-five cooperative/lifecycle methods pass. The independent run produced identical frozen weights; complete reproduction of development reports remains pending. A separate 1728-edit raw-proposal diagnostic finds discrete-selection jumps. See PROJECTED-SELECTOR-v26.md; the model remains unqualified. Procedural choices remain labelled procedural; selected v20 components use frozen learned residuals. Runtime/package 0.17.5 and its prior 345-case/four-offline-check evidence remain unchanged. Fresh confirmation stays absent. See PROJECTED-SELECTOR-PLAN-v26.md.

The complete original goal, 50-evaluation ceiling and September 9 at 19:24:05 UTC deadline remain unchanged.

## Cooperative temporal research v1

TEMPORAL-SCHEDULING-PERFORMANCE-v1.md records selective restoration and per-known-pose pauses, with 28 passing native methods and two 24-run counterbalanced comparisons. Exact source, reference samples and cleanup are preserved; total work increases modestly for finer cancellation. Worst steps still exceed the original 50 ms target. Trained-provider cooperative validation passes 25 methods; production UI/disable integration remains pending. No model or runtime package is promoted. Runtime and ZIP 0.17.5, and prior 345 native/four offline evidence remain unchanged. The original endpoint, 50-evaluation ceiling and September 9 at 19:24:05 UTC deadline remain unchanged.

## Latest research: soft readout v27

Experimental and unqualified. The same frozen v26 learned weights use temperature-one probability marginals over position and rotation experts. No refit, new data or production change occurred. Rotations use hemisphere-aligned normalized quaternion blending; it is only locally continuous away from hemisphere boundaries and rejects a near-zero mixture.

Two complete evaluations reproduce identical model, protocol, probabilities and normalized reports. The original gates, projection and matched controls remain unchanged. Confirmation is sealed. It passes the newer development partition but fails two of 96 total cohorts. Native checks and reproduction pass; small-edit sensitivity remains mixed. See SOFT-SELECTOR-v27.md. The full goal remains active and incomplete.

## Latest research: training tail-risk v28

The fixed training objective improves in-sample risk but fails three of 96 development cohorts, adding a new regression. Exact reproduction, 72 native assertions and matched edit probes complete; no temporal model is qualified or promoted. See TAIL-RISK-SELECTOR-v28.md. The full original goal remains incomplete.

## Historical evaluation-limit checkpoint

The original goal remains incomplete. Development has reached the authorized 50-evaluation ceiling; the extended time allowance does not raise that ceiling. All tracked jobs are terminal. Experimental 0.17.5 remains the local test build; no temporal research candidate is promoted. See EVALUATION-LIMIT-HANDOFF.md for the full endpoint audit, exact evidence and resumption boundaries.

## Current authored-motion integration

The user resumed development to75 total evaluations. Evaluation52 passed a procedural crouch/recover workflow on BoneForge and basic/default Rigify, with save/reload and source recovery. The next worktree revision integrates that authored-only trajectory into the addon as a cancellable preview option. All 369 native regression cases, including 24 new math/lifecycle/operator checks, and seven exact-package offline workflows pass. The archive matches the worktree and is available for local testing; no installation or publication was performed. No temporal weights are promoted. Deferred quadrupeds, optional connector, advanced momentum, secondary motion and broad rig coverage remain part of the unchanged full goal.

## Full-hierarchy weak motion labels

MOTION-LABEL-PROPOSALS-v1.md records a frozen train-only geometry pass over 1,392 eligible clips and all 68 future-training subjects. It produces compact foot-contact, takeoff, landing and static proposals plus a reproducible 130-item review queue. Every item is explicitly heuristic, capped at 0.35 confidence and unreviewed. All 17 future-development subjects remain excluded from pose-array reads. Scene geometry, hand contacts, naturalness and intent remain missing evidence. No model or runtime is promoted; the full goal and its 100-evaluation ceiling remain unchanged.

## Current learned-motion result

The repaired full-hierarchy TCN and the distinct diffusion family are both rejected. The four TCN fits preserve complete priority poses and bone lengths but fail the frozen unseen-subject motion gates. The four diffusion fits were evaluated at 4, 8 and 12 deterministic DDIM steps; all twelve comparisons regress against the procedural floor in aggregate position, rotation, velocity, acceleration, jerk and foot velocity. No temporal checkpoint is bundled or promoted. FULL-HIERARCHY-TCN-v2.md, FULL-HIERARCHY-DIFFUSION-v1.md and ARCHITECTURE-DECISION-v3.md record the evidence and the product-first pivot. The full goal remains active and incomplete.

## Current real-rig task packet

REAL-RIG-TASK-PACKET-v1.md establishes a 17-joint semantic local hierarchy as the product-facing humanoid inference boundary. Fifteen assertions pass across eight BoneForge, Rigify and imported-rig fixtures after a measured proper-rotation correction. The maximum fixed-offset reconstruction residual is `8.77e-7` body scales. Richer source hierarchies remain training and adapter detail. Production rigs, twist distribution, mixed IK/FK output, nonuniform scale, fingers and quadrupeds remain unqualified.

## Current action evidence

ACTION-EVIDENCE-AUDIT-v1.md shows that the subject-disjoint development set contains 1,824 windows with task labels seen during training and 82 novel-label windows: 42 aerial and 40 recovery. Landing has only an indirect heuristic label, difficult transitions are not reviewed, and crouch/turn training coverage spans only three subjects each. Future motion evaluation must separate seen-action, held-out-action and real-rig transfer. No model outcome or motion array was read for this audit.

## Current review workflow

MOTION-LABEL-REVIEWER-v1.md provides an offline visual reviewer for all 130 weak contact, takeoff, landing and static candidates. It embeds 7,163 finite skeleton frames, front/side playback, corrected boundaries, intent and notes, persistent progress and checksum-bound JSON export. Structural/data validation and JavaScript compilation pass; rendered-browser use and human decisions remain unverified, so reviewed ground truth remains zero.


## Scene-aware foot-contact suggestions in 0.20.0

CONTACT-SUGGESTIONS-v0.20.0.md records provisional static-plane/planar-mesh detection, explicit accept/reject, source-safe cancellation and reload, a passing actual-window journey and exact-archive tests. Suggestions use evaluated motion and matching priority-pose evidence but remain heuristics, not learned motion or training truth. Moving surfaces, collision, hand/object detection, broad action coverage and independent usability remain open.

## Contact workflow performance in 0.20.1

CONTACT-PERFORMANCE-v0.20.1.md records the qualified default-Rigify foot-contact latency reduction, exact-package event trials and remaining limits. It supplies the interaction baseline retained by the completed v12 procedural slice below.

## Procedural humanoid vertical slice v12

PROCEDURAL-VERTICAL-SLICE-v12.md records 32/32 passing Bforartists cases across BoneForge, generated Rigify basic/default and an FBX roundtrip Unity-style rig. Reach, crouch, walk, run, jump, land, turn and difficult transition all pass the frozen mathematical, contact, lifecycle and source-preservation gates. PROCEDURAL-PROXY-PERFORMANCE-v0.20.2.md records the optimized Rigify path, 430-test regression and exact-package checks. This completes the automated procedural floor. It does not qualify learned motion, appearance, human usability, clean host shutdown, quadrupeds or Cascadeur parity. The next product evidence is reviewed motion labels and an independent animator pass; broader end-to-end latency remains a measured optimization gap.

## Current-release humanoid review evidence v13

HUMANOID-REVIEW-AND-CORRECTION-v13.md reruns the unchanged four-rig/eight-task protocol against the exact 0.25.0 source and passes 32/32 cases. The refreshed balanced reviewer contains 3,136 frames and passes static plus Edge interaction validation. The separate Bforartists correction tracker copies the candidate action, excludes paused time, measures action edits and restores the source on cancel; its synthetic smoke is explicitly rejected as human evidence. No independent review has been submitted, so visual quality and human correction effort remain unqualified. Runtime and package bytes are unchanged.

## Prospective matched Cascadeur comparison

CASCADEUR-COMPARISON-PROTOCOL-v1.md freezes the future matched comparison before results exist. It requires three hash-frozen proportion-varied humanoids, eight equivalent task families, 24 cases per animator, at least three independent animators, matched automated and human measures, and predeclared parity/superiority gates. The validator passes against the exact v12 aggregate and protocol identities. No Cascadeur run, parity result or superiority result exists; portable assets, recorded Cascadeur entitlement/settings, the animator panel and an accepted B4ML learned temporal runtime remain missing.

## COM acceleration refinement in 0.20.3

COM-ACCELERATION-TRANSITIONS-v0.20.3.md records the optional C2 takeoff/landing transition, its editable native curves, source recovery, 432-test regression, exact-archive offline checks and real-window lifecycle. The acceleration option is off by default. The exact-package UI journey remains above the broad sub-50 ms callback target, and angular momentum, forces, collision and secondary motion remain open.

## Airborne angular momentum in 0.21.0

ANGULAR-MOMENTUM-v0.21.0.md records the opt-in normalized-segment point-mass solver, bounded rigid correction, COM-pivot compensation, C2 composition, editable quaternion/pivot curves, source recovery, same-hash regression and visible-window lifecycle. BoneForge and Rigify-default fixtures reduce measured angular variation by more than 87% while retaining authored boundary poses. Full segment inertia, forces, collision, secondary motion, independent animator review and Cascadeur comparison remain open.

## Rigid-segment angular inertia in 0.22.1

RIGID-SEGMENT-INERTIA-v0.22.1.md records the finite solid-ellipsoid segment tensors, evaluated roll and axial spin, editable per-segment inertia radii, vectorized rotation logs, real-rig measurements, exact-package checks and visible lifecycle. The release preserves the 0.21 bounded motion-layer workflow while closing its point-mass-only limitation. Default body dimensions remain artist estimates; torques, external forces, collision and secondary motion remain open.

## Static planar collision response in 0.23.0

PLANAR-COLLISION-RESPONSE-v0.23.0.md records the opt-in whole-character plane-normal response, finite ellipsoid extents, priority-pose conflicts, editable linear publication, shifted clearance verification, C2/angular composition, source recovery, same-hash regression and exact-package lifecycle. It closes one bounded static-plane collision slice. Arbitrary mesh/self-collision, moving/deforming surfaces, impulses, friction, torques, secondary motion, continuous-time guarantees and human/Cascadeur comparisons remain open.

## Selected-control secondary motion in 0.24.0

SECONDARY-MOTION-v0.24.0.md records the deterministic implicit spring solver, quaternion-safe rotation, selected location, exact priority envelopes, editable action publication, modal cancellation, stale-input guards, flight composition, save/reload, Undo/Redo, Keep/Discard and source recovery. Per-control gravity, global-space follow, automatic secondary-part detection, deformable/self/arbitrary collision and learned secondary motion remain open.

## World-space secondary dynamics in 0.25.0

SECONDARY-WORLD-DYNAMICS-v0.25.0.md records evaluated local/world conversion through animated parents and tested rig spaces, selected-control scene gravity, bounded static planar point collision, bounce/friction, exact priority conflict handling, editable publication and full recovery. Automatic secondary-part detection, deformable/chain dynamics, control volume/self/arbitrary collision, moving surfaces, learned secondary motion and human comparison remain open.

## Local experimental 0.36.0 package

The installable local package `releases/b4artists_ml_v0.36.0.zip` consolidates the procedural workflow surface through Breakdown Pose and Transition Timing Transfer. The frozen 54-member distributable passed 1,017 source tests across 87 curated suites and 209 exact-package feature tests across 32 suites in eight fresh Bforartists processes, with zero skips. Foreground Breakdown Pose and timing-transfer journeys pass on the exact runtime. The package is ready for local testing. Learned temporal generation, independent animator usability, clean host shutdown and Cascadeur parity remain unqualified; the full goal remains active. See `RELEASE-v0.36.0.md` and `package-test-v0.36.0.json`.
