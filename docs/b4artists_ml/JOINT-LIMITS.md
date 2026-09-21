# Experimental 0.7.0 - configurable whole-body control limits

The complete product goal remains active and incomplete. This milestone adds artist-defined swing/twist bounds to the existing learned-proposal/geometric-fit workflow. No model was trained or replaced. It does not establish anatomical correctness, learned temporal motion, production readiness or Cascadeur parity.

## Control and coordinate contract

Each enabled entry names a writable control from the verified whole-body adapter. Generated ORG/MCH/DEF bones cannot be configured as output controls. Swing is the circular cone angle from the control's rest-local Y axis; twist is a signed rotation about that axis. Bounds refer to the actual control rotation in its rest/parent space, not a world-space Euler angle or a clinical body measurement.

The local-space interpretation follows Blender's [PoseBone matrix_basis documentation](https://docs.blender.org/api/5.2/bpy.types.PoseBone.html): its transform is relative to the parent and the bone's rest transform. The implementation uses quaternion swing/twist decomposition rather than installing native Euler Limit Rotation constraints. Control-follow mechanisms still matter: a root-follow head can be independent of neck rotation. We preserve that rig choice instead of changing it to make a constraint pass.

The pure NumPy/math module accepts wxyz unit quaternions and validates finite ranges. It measures swing as 2*atan2(hypot(x,z),hypot(w,y)) and twist as the wrapped 2*atan2(y,w). Residuals are swing excess and the shortest signed angular correction to the permitted twist interval. Sign-negated quaternions produce equivalent residuals, including the shared -pi/+pi boundary.

At 180-degree swing, longitudinal twist is undefined. Restricted twist therefore requires a swing maximum below 180 degrees. Inputs round-tripped through RNA float32 have an endpoint tolerance of 2e-7 radians, followed by clamping to the exact mathematical endpoints. This tolerance does not expand the accepted solve error.

## Fitting and acceptance

Limit residuals participate in the same bounded least-squares fit as position pins, pelvis orientation and pole directions. For head/hands/feet with a desired final orientation, the residual evaluates that future orientation in the current parent's local space during fitting. This lets available parent controls absorb rotation where the rig permits it. Merely checking limits after applying effector orientations would fail that workflow.

After the final pose and effector orientations are applied, limits are recomputed on the original rig. Maximum accepted violation is 0.001 radians, alongside unchanged pin (2e-4 torso units), orientation (0.001 radians), pole direction (0.01 radians) and relative bone-length (0.002) gates. Conflicting requests or failed convergence restore the preceding preview. Diagnostics identify the worst violating control; they do not claim mathematical proof that every rejected target is unreachable.

No control constraint, rest pose, source action or authored follow setting is rewritten. The private evaluation copy uses the same limit code and original-rig final verification. Cancellation removes the copy and restores the previous preview.

## Animator workflow

Joint Limits is a collapsible section in Whole-Body Pose. Choose a control using the searchable selector, enable Limit This Control and edit Swing/Twist Min/Twist Max. All entries start disabled; 175-degree swing and unrestricted twist are editing defaults, not anatomical presets. The panel shows the active-entry count.

Settings persist across previews and .blend reload. Stale controls are removed when a new preview creates its adapter list. Enabled limits enter the immutable solve signature, so editing them invalidates Keep and a result computed from earlier settings. Changes during a solve restore the preceding verified preview. The existing target-strength control blends targets; it does not relax limits. Disabled limits do not change historical preview signatures.

Limits apply only to whole-body pose solves. Interpolation candidates are not yet validated against limits between anchors. Hinge-plane restrictions, asymmetric anatomical swing regions, evaluated joint frames independent of control-follow spaces, calibrated character presets and temporal enforcement remain unfinished.

## Regressions and failed experiments

The first development run executed eight tests and reported three errors. Active swing caps and feasible pins passed, but UI defaults exceeded exact +/-pi by float32 rounding. Boundary validation was fixed and tested through saved RNA settings.

A requested head rotation on default Rigify could not be absorbed by its neck. Inspection of the real generated chain found head -> MCH-ROT-head -> neck with the generated copy-rotation mechanism and torso head_follow=0.0. The test now covers both authored spaces: root-follow rejects the conflicting head-control twist bound without changing that property; a separate fixture authored with head_follow=1.0 successfully fits through its parent. BoneForge and metarig parent-compensation cases also pass. This is an explicit compatibility distinction, not a silently relaxed assertion.

Development artifacts remain under training/b4artists_ml/results/joint-limits-v1.json (failed) and joint-limits-v2.json (nine tests passed). Final ZIP-specific results are joint-limits-package-v0.7.0.json. Assertions cover quaternion decomposition/sign/wrap behavior, invalid requests before mutation, feasible pins on five transformed rigs, active swing limits on three rig families, head twist/parent interaction, incompatible requests, source restoration, save/reload, retained settings, stale requests and cooperative cancellation.

The active-limit fixture deliberately uses a 0.025-radian cap to demonstrate enforcement against a differing learned proposal; it is not a suggested human elbow or knee range. Observed unconstrained swing ranges exceeded the cap, while the constrained poses remained inside it and preserved the pinned pelvis.

## Actual UI evidence

The exact 0.7.0 ZIP passed the real event-loop scenario on default generated Rigify with 22 enabled control limits, six rotation targets and four poles. Timer-driven completion, simulated Escape cancellation, undo, redo and Keep were exercised. The native screenshot was inspected: the joint selector and angle controls render correctly; the expanded sidebar requires scrolling to lower actions at this window height. This is automated workflow validation, not an animator naturalness assessment.

The recorded solve took 15,123.18 ms, with 1,657 evaluations and 80 iterations. Maximum limit violation was zero; pin error was 1.9129e-6 torso units. Total UI scenario time was 17.07 seconds. Do not substitute background solver times for interactive latency. Continuous responsive posing remains a major gap.

The UI logged the previously isolated ucrtbase.dll shutdown access violation after its passing assertion marker. Background test processes also show that host shutdown problem. Passing assertions do not imply clean application exits. The UI launcher did not capture a numeric exit code; the stderr crash marker is the authoritative UI shutdown evidence.

All 120 regression tests passed with zero skips: 110 package-entry tests and 10 actual-rig source-adapter tests whose runtime is byte-identical to the ZIP. This comprises the nine new limit tests and all 111 established 0.6 regressions. The existing actual 0.5.1 saved-preview compatibility test still passes. Twelve unchanged contextual training/data tests were not rerun; no training/data code or weights changed.

The nine background processes completed assertions and exited with the known shutdown access violation (signed -1073741819 / unsigned 3221225477). Per-suite logs, hashes, UI evidence and source/package equality are recorded in checkpoint-joint-limits-v1.json.

The package contains 23 runtime files, 200,297 bytes; SHA-256 26077afff1e89422de4ad9c9aaa0bc2efa680740d484e9c4626f8a3f825dd891. ZIP integrity, source-byte equality and Python syntax pass. The prior 0.6.0 ZIP is unchanged.

The required execution router was called for implementation and packaging scopes. Both attempts stopped before host application because the remote /mnt/x workspace was unavailable. No lane, policy fingerprint or patch was emitted. Native continuation followed the canonical recoverable infrastructure policy within the declared project scope. No commit, push, installed-add-on update, credential change, Ghost Tool edit or Anim Assist edit occurred. Tracked and staged Git diffs remain empty; this ML work is still untracked.

## Remaining product scope

Anatomical limits, contacts and balance require further integration. Learned motion, physics/gravity/momentum, secondary motion, production rig and mesh coverage, imported rigs, quadrupeds, optional entitlement-aware Cascadeur integration and direct comparative animator evaluation remain open. The bundled contextual model's prior-pose regression remains documented and unresolved.
