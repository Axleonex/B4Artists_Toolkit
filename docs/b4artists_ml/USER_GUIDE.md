# B4Artists Machine Learning - experimental

The current frozen experimental package is `releases/b4artists_ml_v0.36.0.zip`. Install it through Bforartists: Edit > Preferences > Add-ons > Install from Disk. Enable B4Artists Machine Learning. Standard Blender registers only the Bforartists requirement notice. Development 0.37 source contains newer verified work, including Static Analytic Capsule Collision; the current development archive is `releases/b4artists_ml_v0.37.2-dev.zip`. Exact-package capsule binding, the affected regression and the foreground lifecycle are recorded on Bforartists 5.1.0 / Blender 5.2.0 Alpha; the host still has a known `ucrtbase.dll` shutdown fault after assertions, and the archive remains experimental.

The separate motion-label review artifact is research/evaluation tooling and is not installed with the add-on. Open `training/b4artists_ml/results/motion-label-reviewer-v2/reviewer.html` in a local browser, complete all 130 items, and use **Export completed review**. Validate the resulting JSON with `py -3 training\b4artists_ml\validate_motion_label_review_v2.py <export.json> --output-dir <new-output-directory>`. A checked box is only self-attestation; the validator does not verify identity or authorize training.

The development 0.33 source adds an opt-in **Conservative Humanoid v1** preset under Whole-Body Pose > Joint Limits, optional semantic **Chest** and **Neck** position and Rotation controls, a **Reset** action on every Pose Targets row, bidirectional hand/foot/pole helper mirroring, per-limb **Align Bend**, **Flip Side** and body-scale **Set Distance**, explicit **Rig Mapping Diagnostics**, bounded **Humanoid Mapping Corrections**, same-armature **Reusable Pose Anchors**, and a scene-local **Semantic Pose Asset** for supported humanoid adapters. These source features are not included in the 0.32.0 ZIP. See JOINT-LIMIT-PRESETS-v1.md, CHEST-TARGET-v1.md, CHEST-ORIENTATION-v1.md, NECK-TARGET-v1.md, TARGET-RESET-v1.md, TARGET-MIRROR-v1.md, POLE-ALIGN-v1.md, POLE-FLIP-v1.md, POLE-DISTANCE-v1.md, RIG-DIAGNOSTICS-v1.md, MAPPING-CORRECTIONS-v1.md, POSE-REUSE-v1.md and POSE-ASSET-v1.md.

The development 0.35 source adds a sixth, rotation-only **Head** helper, **Spine Follow** and **Neck Share** shaping, optional position-only **Pole Targets**, current-frame pole matching, per-target preview reset, bidirectional paw/pole target mirroring, per-pole **Align Bend**, **Flip Side** and body-scale **Set Distance**, and read-only procedural gait-phase review to generated Rigify cat, horse, and wolf workflows. These source features are not included in the 0.32.0 ZIP. See QUADRUPED-HEAD-v1.md, QUADRUPED-SPINE-FOLLOW-v1.md, QUADRUPED-POLES-v1.md, QUADRUPED-POLE-MATCH-v1.md, QUADRUPED-TARGET-RESET-v1.md, QUADRUPED-TARGET-MIRROR-v1.md, QUADRUPED-POLE-ALIGN-v1.md, QUADRUPED-POLE-CONTROLS-v1.md, and QUADRUPED-GAIT-PHASES-v1.md.

For the preset, start a whole-body preview, expand Joint Limits, apply it, then inspect and edit each control before solving. `Source: B4ML preset v1` identifies untouched preset values; any edit becomes `Custom override`. The ranges are animation estimates, not clinical anatomy or learned output.

## Chest and Neck orientation in development 0.33

Start Humanoid Whole-Body Pose, expand Pose Targets, enable Rotation on the Chest row or **Rot** on the Neck row, rotate its helper, and solve. Position and rotation remain independent for both targets. Rotation is evaluated on the selected semantic skeletal joint and distributed through verified writable spine controls. The shorter `Rot` label keeps the Neck controls readable in a narrow sidebar. Saved previews created before controls version 4 must be restarted before authoring Chest rotation; Neck requires a new controls-version-5 preview.

Enabled targets still form one constraint set. If a large torso or Neck turn conflicts with fixed hands, feet or head targets, the solve rejects and restores the prior pose. Release conflicting pins or use a smaller turn. This is procedural posing assistance; it is not learned orientation completion.

## Pole alignment in development 0.33

Each Hand and Foot row has **Align Bend** below its Elbow Direction or Knee Direction toggle. Click it to place the owned pole helper on the current evaluated limb bend plane. The action keeps the helper's radial distance unless it is closer than the stable 0.4-body-scale minimum, and it never changes the direction toggle. Enable the toggle when the next solve should constrain that direction.

Click **Flip Side** to place the same helper opposite the current evaluated bend. Enable the direction toggle and solve to request the other elbow or knee bend. Flip Side uses the same distance, ownership and straight-limb safeguards as Align Bend.

The number beside **Set Distance** is the last requested reach from the evaluated elbow or knee in body-scale units. Choose 0.1 to 4.0, then click Set Distance. The helper moves radially without changing its current direction. Direct dragging leaves the requested number unchanged; Align Bend and Flip Side update it to their resulting distance. Whole-body pole helpers use circular in-front displays so they remain distinct from arrow-shaped position/orientation targets.

Stop Live Solve and finish or cancel a running solve first. A straight limb has no stable bend plane; bend it slightly or move the pole manually. Invalid placement leaves the helper and rig unchanged. If the native motion layer moved since the preview began, return it to that transform or restart the preview before using Align Bend, Flip Side or Set Distance. If an enabled helper moved after the last solve, solve again before Keep. This is procedural geometry, not learned pose inference.

## Rig mapping diagnostics in development 0.33

Select an armature or its bound mesh and click **Inspect / Refresh Rig Mapping**. Expand Rig Mapping Diagnostics to see the detected profile, semantic-role coverage, mapped and directly writable control counts, excluded structural-bone categories, and which current workflow preflights pass. Pose Blending remains blocked until at least two valid, compatible anchors exist. Expand Semantic Role Mappings when you need the exact role-to-bone assignments. Missing roles and adapter blockers remain visible rather than being guessed.

The report is a read-only snapshot so ordinary panel redraws stay responsive. Click **Inspect / Refresh Rig Mapping** again after changing the rig, constraints, object transform, NLA setup, or control spaces. Inspection does not start a preview or edit the rig or animation.

## Humanoid mapping corrections in development 0.33

Use **Inspect / Refresh Rig Mapping** to identify a wrong or missing assignment on a recognized humanoid adapter. Expand **Humanoid Mapping Corrections**, choose the semantic Role, search for the intended animator Bone, and click **Apply Role**. Refresh diagnostics to inspect the resulting mappings and workflow preflights. Clear Role restores that role's detected mapping; Clear All removes every override and is also the recovery action for a corrupt or stale payload.

Corrections are stored on the selected armature object and survive `.blend` reload. They are disabled while a preview or background animation job owns the rig. Existing BoneForge, generated Rigify Basic/Default and supported imported-humanoid adapters can be refined; unknown rigs and quadrupeds cannot be promoted through this editor. Structural bone names, absent bones, duplicate final semantic assignments, changed bone names/hierarchy/classification, invalid JSON and oversized data are rejected. Applying, clearing, Undo and Redo do not move the pose or edit the action. The editor changes semantic adapter metadata rather than retargeting or rebuilding the rig.

## Reusing a pose anchor in development 0.33

Capture a pose, move the playhead to another frame, then click the duplicate icon beside that stored anchor. The source pose is copied to the current frame as another authored priority pose. Use this for a hold, repeated pose or timing change, then generate and review the ordinary Pose Blending candidate.

Reuse does not immediately apply the pose to the armature and does not create an action. If the current frame already has an anchor, that destination anchor is replaced. The operation works only within the same armature and validates the complete anchor set before changing it. Active previews, retained motion, NLA, changed controls, locks, rest data, IK/FK settings, invalid frames and oversized payloads are rejected. Use native Undo/Redo to reverse or restore the copied anchor.

## Semantic Pose Asset in development 0.33

Start a Humanoid Whole-Body Pose preview, arrange the eight semantic targets, choose which position, Rotation and elbow/knee direction requests are active, and click Solve Whole Body. After the solve succeeds and the targets have not changed, click **Save Solved Pose** under Pose Targets. The scene stores one compact semantic target asset.

Start a controls-version-5 whole-body preview on another supported humanoid in the same scene and click **Apply Pose**. The tool reconstructs target and pole changes in the destination character's verified body frame and body scale. It applies the saved pin, supported Rotation, direction and pole-distance settings to the helpers without moving the armature. Click Solve Whole Body, inspect the result, then Keep or Cancel. Apply Pose invalidates any earlier solve, so Keep remains blocked until the applied request solves successfully.

The asset survives save/reload with the scene and supports BoneForge controls, generated Rigify Basic/Default, Basic/Default human metarigs and the tested Unity Humanoid convention. It is a single scene slot for sparse target requests. It is not a global library, a raw control-pose transfer, full animation retargeting, style transfer or learned inbetweening. Malformed, oversized, non-finite, stale, unsupported or replaced-helper data fails before helper or rig mutation.
## Contact review and animation cleanup in 0.32.0

Humanoid Animation Contacts and Four-Paw Contacts show compatible proposed, accepted and rejected counts. Use Previous Proposed or Next Proposed to inspect each interval at its exact start frame. Accept or reject one proposal, or apply the same decision to every compatible proposal. Bulk review leaves proposals from the other rig family unchanged.

After generating a candidate, open Animation Cleanup. Apply cleanup to Selected Controls or All Captured Controls. Smooth Curves adjusts editable handles with the chosen strength. Remove Redundant Linear Keys removes only keys whose reconstructed values remain within Key Tolerance at the original key times. You can enable either option independently.

Click Preview Cleanup and inspect the copied action. The panel reports removed keys, smoothed curves, protected contact controls, accepted-contact samples, maximum position and rotation drift, key-reduction error, derivative continuity, and safely skipped curves. Priority poses and accepted-contact dependencies remain protected. Escape cancels an active cleanup, Restore Input returns to the preceding candidate, and the normal Keep Candidate, Discard and Restore Source Animation workflow remains available. Kept cleanup survives save/reload.

Cleanup is deterministic and uses no learned motion model. It does not infer intent or replace the separate learned-inbetweening requirement. See CLEANUP-v0.32.0.md for measured coverage and limitations.

## Paw-contact suggestions in 0.31.0

On a generated Rigify cat, horse or wolf Pose Blending candidate, open Four-Paw Contacts. Select a static planar Support Surface or set the support plane. Click Suggest Paw Contacts, inspect each interval and reason, then Accept, edit or Reject before Preview Four-Paw Correction. Escape cancels scanning. Quadruped threshold units use body-to-paw distance. See PAW-SUGGESTIONS-v0.31.0.md for measured results and limits.

## Four-paw contacts in 0.30.0

Generate and select a Pose Blending candidate for a generated Rigify cat, horse or wolf with all four limbs in IK. Open **Four-Paw Contacts**, choose a paw, move to the frame where it should be planted, and click **Capture Paw Contact Here**. Set Start, End, Blend, Strength and Lock Rotation. Repeat for each required paw, then click **Preview Four-Paw Correction**.

The tool copies the candidate and writes ordinary editable linear keys for each contacted native paw IK control. Captured priority-pose frames remain unchanged. **Restore Before Paw Contacts** returns to the retained Pose Blending candidate; Discard and Restore Source use the normal candidate workflow. Escape cancels an active correction. Kept output and its source-recovery record survive save/reload.

Contact points and intervals are authored by the animator. The manual workflow does not infer footfalls or gait and does not add quadruped balance, flight, arbitrary-surface collision or learned motion.

After accepting the intended contact intervals, click **Analyze Gait Phases**. The panel divides the priority-pose range at exact contact boundaries and describes each interval as Flight, Single, Diagonal, Lateral, Fore, Hind, Triple, or Full Support. Use Previous/Next Phase to move to the interval midpoint, where the evaluated contact weights match the displayed support set. Clear Phase Report before revising the schedule. UI redraw uses lightweight validation; Analyze and navigation perform strict candidate-action and contact revalidation. Recorded generated cat/horse/wolf fixtures took about 110–112 ms to analyze, while panel display validation stayed below 6 ms.

These labels summarize an animator-accepted contact schedule. They do not recognize walk, trot, pace, canter, gallop, cadence, intent, or animation quality, and they do not generate or modify motion. See QUADRUPED-GAIT-PHASES-v1.md.

## Rigify quadruped posing from 0.29.0

Rigify cat, horse and wolf generated rigs and metarigs are recognized as quadrupeds. Inspect Rig shows the quadruped family and schema. Use Capture Pose at Current Frame on two or more frames, choose Pose Blending, and generate a reversible editable candidate. The adapter excludes generated deform, mechanism, visual-widget and tweak bones.

Generated rigs also expose **Quadruped Pose**. Put every limb in IK before starting; the tool rejects mixed or FK limb states. Set **Spine Follow** to the fraction of Head rotation that should be carried below the Head, then set **Neck Share** to divide it between Neck and Chest. Zero uses direct Head-only rotation. Click Start Quadruped Pose and move the Body and four paw helpers in Object Mode. Enable Rotation beside any helper whose corresponding native torso or paw IK control should follow its axes. The arrow-shaped **Head** helper starts with Rotation enabled and location locked. Rotate it to orient the detected Head animator control, or disable Rotation to release the Head and Spine Follow request.

Pole Targets are optional. Enable **Pole Targets** before starting the preview. If any native Rigify Pole Vector switch is Off, click **Match + Enable All Poles** to preserve the current evaluated limb pose while preparing all four controls. The one-click match works at the current frame; animated base/pole/middle controls must use Rigify's range conversion. The default keeps the six-helper schema-3 workflow. Pole Targets creates four additional position-only helpers for the fore and hind limb bends, producing a ten-helper schema-4 preview. Move those circles to direct the bends; their rotation is locked and ignored. Click **Align Bend** beside a Pole Target to place only that helper on the limb's current evaluated bend ray while preserving its distance from the middle joint. Click **Flip Side** to put the same helper on the opposite bend ray without changing its radius. Enter 0.1 to 4.0 beside **Set Distance** and click it to move the helper radially without changing its current direction. These actions require schema 4, an idle workflow, unlocked helper location and scale, and stable geometry; invalid input leaves the request and rig unchanged. Click **Reset** beside Body, a paw, Head, or a Pole Target to return only that helper to its preview-start transform. Use **Mirror L to R** or **Mirror R to L** to transfer edited fore/hind paw position and rotation requests to the opposite side; active Pole Target positions mirror with them. Mirroring preserves the source helpers and the destination Pin/Rotation options. Other helpers, options, the source action, rig pose, IK/FK state, and Pole Vector state stay unchanged. Aligning, flipping, setting distance, resetting, or mirroring after Solve clears the stale result, so solve again before Keep. Click Solve Quadruped Pose. Keep as Pose Anchor records the solved control pose and restores the source. Cancel restores the source without an anchor. A target, Rotation option, Spine Follow, Neck Share, or pole-helper change after the last solve must be solved again before Keep. Active sessions survive save/reload; schema-1 Body/paw, schema-2 direct-Head, and schema-3 Head-to-Spine sessions remain recoverable without inventing pole requests.

After a quadruped request solves, click **Save Solved Pose** to store its semantic target layout in the scene. Start a schema-3 or schema-4 preview on another generated Rigify cat, horse, or wolf with the same Pole Target mode, then click **Apply Pose**. Body, paw and Head rotation requests, optional Pole Target positions, Spine Follow and Neck Share adapt to the destination's Body frame and scale without moving the rig. Solve the applied request before Keep. The saved asset stays separate from the humanoid pose asset.

This workflow translates the native Rigify torso and four paw IK controls through a bounded deterministic solve, optionally rotates those controls, and exactly orients the semantic Head control. Schema 3 can share part of the requested Head turn through verified semantic Chest and Neck animator controls; schema 4 adds exact native pole-control positions after validating all four Pole Vector modes. Per-target Reset and bidirectional target mirroring support saved schemas 1-4. Align Bend, Flip Side and Set Distance use deterministic current-frame geometry for schema 4; Align and Flip preserve helper radii from 0.1 to 8 body scales, while Set Distance accepts 0.1 to 4 body scales. It writes only controls needed by the active request. It supports generated cat, horse and wolf rigs only. Metarigs; unsupported rig scale, shear, or reflection; locked, constrained, animated, driven, parented, or externally controlled helpers; fractional Pole Vector modes; and driven Pole Vector or IK/FK properties fail before mutation. One-click pole matching and the per-pole geometry actions do not convert animated ranges. Procedural support-phase review reads accepted contacts without changing motion. Lower-spine targets, gait recognition/generation, gait-aware physics and learned quadruped motion remain future work. Whole-Body Pose, Assisted Pose, humanoid foot-contact correction, COM flight and Whole-body Motion remain humanoid-only.

## Pose and generate motion

1. Select a humanoid armature or bound mesh. Open N-panel > B4Artists ML and Inspect Rig. Default BoneForge and Rigify humanoid IK inputs are accepted; manual mode switching or disabling native stretch is not required.

2. At the first animation frame, click Capture Pose at Current Frame, or Start Assisted Pose to adjust it using targets.

3. For assisted posing, move the hand/foot spheres and pole hints in Object Mode. Selecting a helper keeps the rig panel available. Uncheck a limb to release its position pin, set Pelvis Offset in world axes, and adjust Target Strength or Maximum Bend. Optionally check Learn Bend for individual limbs, then adjust Learned Bend Influence. With it off, that limb uses your pole. Click Solve Pose.

4. Inspect the pose and reported target error. Unreachable targets are clamped and reported; this does not count as meeting the requested pin. Keep as Pose Anchor saves the result. Cancel removes helpers and restores the input. With converted IK input, keeping also restores the input rig; the solved result is stored in the anchor for motion generation.

5. Move to another frame and capture/keep another pose. To shape an interval, use **Create Breakdown Pose** or **Procedural Inbetween Series**. Use the clock to move one saved pose, the right arrow to translate that pose and every later pose, or the outward-arrow scale button to proportionally compress or expand every later pose around a fixed pivot. Full-body captures on known generated rigs use a consistent FK representation, including when the input action switches IK/FK.

6. Choose Pose Blending for deterministic timing controls, or Whole-body Motion for a procedural trajectory through full-body captures. For Pose Blending, select Uniform, Ease In / Out, Ease In, or Ease Out. Move **Breakdown Bias** toward negative values for later arrival or positive values for earlier arrival. Use a saved pose's **Timing** button to override only the transition arriving at that pose. Set **Departure Hold** to delay motion from the prior pose and **Arrival Hold** to reach the destination early; at least 10% of the interval remains available for motion. Captured pose frames remain exact. Whole-body generation keeps supported work on a temporary rig; source edits or cancellation stop the pending job safely. Whole-body Motion offers Smooth Transitions to reduce abrupt speed changes while preserving authored poses. Generate the preview, scrub it, and apply captured contact correction where needed. Output remains editable FK animation with explicit IK/FK mode keys.

## Interpolation timing controls in development 0.36

Use the Timing menu and Breakdown Bias only with **Pose Blending**. The four timing shapes and signed bias apply to location, scale, and shortest-path rotation. They do not move captured poses or change their frame numbers. For a local change, click **Timing** beside a destination pose and enable **Override Global Timing**. A `Timing*` label marks an active override. Departure Hold preserves the prior pose at the start of that interval; Arrival Hold preserves the destination at its end. Both use normalized interval fractions and their sum may not exceed 90%. The first pose has no button because it has no incoming transition. Discard returns to the original source Action; Keep retains the candidate with inspectable timing metadata.

Intervals without an override use the global controls and a full motion window. Recapturing a destination pose keeps its override; reusing that pose at a new frame copies only the pose. Removing the first pose clears timing from the new first pose. Saved files with a dormant first-pose record are normalized when an earlier pose is captured or reused.

To insert an editable priority pose, place the playhead strictly between two saved poses and click **Create Breakdown Pose**. The dialog begins at the playhead's natural fraction. Set **Pose Blend** to choose the exact prior-to-following blend. With **Selected Controls Only**, selected captured controls use that blend while untouched controls retain their pre-insertion preview under the current global timing or destination override. The following pose keeps its timing record; the new anchor starts without an inherited incoming override. Native Undo/Redo and save/reload preserve the operation. See `BREAKDOWN-POSE-v1.md`.

To reuse an interval's complete timing, click the Copy icon beside its destination pose, then click the Paste icon beside another destination. Copy includes easing, bias, Departure Hold, and Arrival Hold. An interval using global timing is copied as a stable snapshot of the current global easing and bias with zero holds. Paste creates an explicit override only on the chosen destination. The rig-local clipboard survives save/reload, and native Undo/Redo applies to the pasted override. See `TRANSITION-TIMING-TRANSFER-v1.md`.

These controls do not learn motion style, infer intent, or remap Whole-body Motion and projected samples. See `TIMING-CONTROLS-v1.md`, `TRANSITION-TIMING-v1.md`, and `TRANSITION-WINDOW-v1.md`.

## Procedural Inbetween Series in development 0.37

Use **Pose Blending**, place the playhead strictly between two saved poses, and click **Procedural Inbetween Series**. Choose one to eight inbetweens. The tool divides the selected interval evenly and samples the timing that existed before insertion, including its destination easing, Breakdown Bias, Departure Hold, and Arrival Hold.

The new poses are ordinary editable priority anchors. The two endpoint anchors and every other existing anchor remain unchanged, and the source Action is not edited. Each new pose starts without an incoming timing override; use its Timing control afterward when that new transition needs a local shape. Native Undo removes the complete series together, and Redo restores it.

Very narrow or very large absolute frame ranges can lose even spacing in Blender's stored frame precision. The operation rejects those ranges before adding anything. Finish other animation jobs, restore a kept Native Motion Layer, and remove or mute NLA strips before creating a series. See `INBETWEEN-SERIES-v1.md`.

To retime one saved pose, move the playhead to its new frame and click the clock beside that pose. Confirm the source and destination in the **Priority Pose Retime** dialog. The move preserves the exact saved pose and its incoming transition timing. It also preserves the following pose's timing and the source Action. A middle pose must stay between its current neighbors; first and last poses may move outward within the 240-frame span. One native Undo reverses the complete move, and one Redo restores it. See `POSE-RETIME-v1.md`.

To move a pose and the complete later sequence, place the playhead at the clicked pose's new frame and click the right-arrow beside it. **Ripple Pose Retime** shifts that pose and every later pose by the same requested delta. Their saved poses, incoming timing, descriptive name suffixes, and storage order stay exact; their internal intervals stay within one percent after Blender float rounding. Only the gap from the prior unmoved pose to the clicked pose changes. The dialog reports how many poses will move. One Undo reverses the entire ripple and one Redo restores it. Use the clock for an isolated move and the right arrow for a sequence move. See `RIPPLE-RETIME-v1.md`.

To change the duration of every later interval, click the outward-arrow scale button beside the fixed pivot. Choose 0.25x through 4x. Values below one compress later frames and values above one expand them. Pose data, easing, bias, holds, name suffixes, source animation, and the pivot frame remain exact. One Undo/Redo covers the complete scale. See `POSE-SPACING-SCALE-v1.md`.

To turn irregular later pose timing into a constant beat, click the `=` button beside the fixed pivot. **Equalize Later Pose Spacing** starts with the next pose's current interval; enter the desired number of frames between every later priority pose. The pivot, saved poses, per-transition timing, descriptive suffixes, and source animation remain exact. One Undo/Redo covers the complete change. See `POSE-SPACING-EQUALIZE-v1.md`.

## Secondary Motion

1. Generate or reopen an animation candidate, then select one or more pose controls on the armature. Secondary Motion uses the explicit selection; it does not guess which controls represent hair, cloth, tails, flesh or props.

2. Open Secondary Motion. Choose Local to follow authored channels or World to follow evaluated controls through their parent and constraint spaces. Enable Rotation and/or Location. Response Frequency controls how quickly the result follows the input; lower values create more lag. Damping reduces oscillation, Air Friction damps velocity relative to still air or the World-space Wind Velocity, Influence blends the result, and Boundary Blend returns smoothly to each captured priority pose.

3. To couple rotational follow-through, choose Local, enable Rotation and enable Couple Selected Chain. You can select one direct, unbranched parent-child control chain manually. You can also make one intended pose control active, choose Toward Children or Toward Parents, set Maximum Controls from 2 to 32, and click Select Direct Chain. The helper accepts recognized rig controls and custom non-deforming controls present in every captured pose with complete editable rotation curves. Child branches, topology gaps, structural controls, unrecognized deform bones, locks and drivers are rejected. Swap Previous Selection restores the replaced selection and active control; click it again to reapply the chain. A prior valid chain mode is restored, while an invalid one-control chain is restored with coupling Off. Chain Propagation zero matches independent followers, and chain coupling affects rotation only.

4. With World and Location enabled, Gravity Influence applies scene gravity. External Acceleration adds a uniform scene-space vector in scene units per second squared; zero disables it. Wind Velocity sets uniform scene-space air motion in scene units per second; Air Friction must be above zero and damps the selected controls toward that velocity. Velocity Impulse applies one scene-space velocity change at Impulse Frame and affects following samples; a fractional frame is sampled exactly. To give controls distinct constant loads, set Selected Force and Selected Mass. A zero Application Offset (Local) applies only `force / mass` translation. For torque, also enable Rotation, enter the force point relative to the control pivot in the control's local scene units, and set scalar Rotational Inertia. Assign Load stores the complete setup on the selected controls; select other controls and repeat, or use Clear Load. To inspect, edit, or transfer an existing setup, make one assigned selected control active and click Load From Active; all four stored values return to the visible fields without changing the assignment or animation. The solver rotates the local offset by the target world orientation, applies `offset x force / inertia` as angular acceleration, and applies `force / mass` as linear acceleration. Assignments survive save/reload and support native Undo/Redo. Enable Collision and choose a Shape. **Planar** uses the Support Plane or chosen static planar Contact Surface. **Sphere** uses an unparented, non-rigid-body scene object's world origin as its center plus an explicit base radius; object geometry does not set the collision volume. The staged field is **Sphere Center / Bounds Source**. For mesh, curve, surface, metaball or text objects, **Fit New Radius from Bounds** snapshots a conservative origin-centered radius before adding the row; each existing row has **Fit Radius from Bounds**. Fitting uses current world bounds for a static radius and local bounds for Follow Radius Scale. When an object's origin is not the desired center, click **Create Bounds Proxy** instead: it snapshots the current world bounds, creates and adds a separate unparented Empty sphere at the eight-corner center, and leaves the source geometry unchanged. The proxy is static by default and can be edited like any other Empty. Both setup actions support native Undo/Redo and do not make the object's faces into a collision surface. To use direct object-location animation, enable **Follow Center Animation** before adding the staged sphere, or toggle **Follow Animation** on its row. Moving centers require complete unmuted Location X/Y/Z curves. To multiply the base radius by direct uniform object-scale animation, enable **Follow Radius Scale** before adding the staged sphere or on its row. Scale following requires complete unmuted Scale X/Y/Z curves that remain finite, positive and uniform. Both animation options reject parents, constraints, rigid bodies, drivers, NLA, curve modifiers and animated delta transforms. The staged fields work directly while the set is empty. Click Add Sphere to Set to copy them into a persistent list, or use Create Bounds Proxy to create and add a row in one action, then repeat for up to eight mixed static, moving-center or changing-radius colliders. Each row exposes its own center, radius, fit action and animation toggles; Remove deletes one row, and Clear Sphere Set returns to direct staged-sphere use. The list survives save/reload and Add supports native Undo/Redo. Clearance expands every excluded pivot distance. Bounce and Friction act on control velocity relative to center motion and radial boundary expansion or contraction. Conflicting priority poses are rejected. World acceleration, control loads, torque, wind, impulse, and collision do not apply to a coupled chain. For arbitrary geometry, choose **Mesh** for sampled nearest-triangle contact or **Closed Volume** for a finite spherical selected-control volume. Enable **Continuous-Time Sweep** only on a closed mesh. Static Closed Volume uses the exact schema-21 swept-sphere path; direct moving or deforming Closed Volume uses the explicitly bounded schema-22 interpolated-volume path.

5. Click Preview Secondary and scrub the result. The input candidate remains retained. Escape cancels a running solve. Restore Input returns to the retained input so settings can be changed without stacking results.

6. The result contains ordinary editable linear keys. Keep Candidate, Discard and Restore Source use the same workflow as interpolation, contacts and flight.

This is deterministic selected-control physics. Direct-chain selection follows topology and editable curves; it does not infer which controls are hair, cloth, tails, flesh or props. Bforartists does not restore pose-bone selection through native Redo in the tested host, so the explicit two-way Swap Previous Selection action is the qualified reversible path during the current editing session. Saving keeps that live swap available; loading a file, Undo, or Redo clears it because its exact Action/slot ownership is runtime-bound. The chain option is a bounded rotational follower, not deformable simulation. External Acceleration, Wind Velocity, and Velocity Impulse are uniform controls; Force/Mass, local application offset, and scalar inertia are assigned per control. Load From Active explicitly recalls a stored assignment and does not infer or simulate one. The torque model follows the authored target orientation and does not infer joint coupling, anatomy, mass, inertia, or collision impulses. Sphere collision excludes sampled control pivots from one to eight direct rigid spheres with optional center and uniform-radius animation; radius fitting and proxy creation snapshot explicit bounds and do not use faces as collision geometry or follow later deformation. Mesh and Closed Volume collision are explicit deterministic triangle-mesh paths; moving/deforming finite-volume sweep remains bounded at interpolated states and is not a globally exact moving-surface solver. Learned secondary behavior remains unqualified. See SECONDARY-CHAIN-v0.26.0.md, SECONDARY-WORLD-DYNAMICS-v0.25.0.md, SECONDARY-CHAIN-SELECTION-v1.md, SECONDARY-EXTERNAL-ACCELERATION-v1.md, SECONDARY-WIND-VELOCITY-v1.md, SECONDARY-VELOCITY-IMPULSE-v1.md, SECONDARY-CONTROL-LOADS-v1.md, SECONDARY-FORCE-OFFSET-TORQUE-v1.md, SECONDARY-LOAD-FROM-ACTIVE-v1.md, SECONDARY-SPHERE-COLLISION-v1.md, SECONDARY-MULTI-SPHERE-COLLISION-v1.md, SECONDARY-MOVING-SPHERE-COLLISION-v1.md, SECONDARY-ANIMATED-RADIUS-v1.md, SECONDARY-SPHERE-FIT-v1.md, SECONDARY-SPHERE-PROXY-v1.md, SECONDARY-MESH-COLLISION-v1.md, SECONDARY-CONTINUOUS-MESH-COLLISION-v1.md, SECONDARY-EXACT-SWEPT-VOLUME-v1.md and SECONDARY-BOUNDED-MOVING-VOLUME-v1.md.

7. Discard restores the input action and modes. Keep Candidate retains the new action. After keeping, Restore Source Animation returns to the input action, slot, transforms and original mode state; the candidate remains available. Use this button rather than relying solely on the action dropdown, which cannot restore unkeyed rig properties.

Anchors, active posing sessions, candidates and the latest source-recovery record persist in the blend file. Undo/redo and save/reload have automated tests. If a saved source action re-evaluates its IK modes during loading, explicit Solve re-enters the saved FK working state at the original frame. Cancel remains available.

## Experimental whole-body posing

1. Select a supported BoneForge, Rigify or validated imported FK humanoid and click Start Whole-Body Pose. This creates pelvis, chest, neck, head, hand and foot position targets and matches supported IK inputs onto FK controls.

2. Move the axis targets in Object Mode. Keep the pelvis position pinned; uncheck other position pins to release those joints. Chest and Neck position and rotation start unchecked, and each option can be enabled independently. Enable Rotation on pelvis, Chest, head, hands or feet, or **Rot** on Neck, to use those target axes. Use Align Bend or Flip Side to place an elbow/knee helper along or opposite the current evaluated bend plane, optionally set its normalized radial distance, then enable Elbow Direction or Knee Direction when that pole should constrain the next solve. Click Reset on one row to return that target, its supported orientation and its elbow/knee helper to the preview-start transform. Use Mirror L to R or Mirror R to L to copy both hand and foot changes, including their direction helpers, through the semantic body plane. Mirroring keeps source helpers, destination toggles and the current rig pose unchanged. Align, Flip, Set Distance, Reset and mirroring require Live Solve to be stopped.

3. Set Target Strength to blend target displacement. Set Learned Influence to blend the frozen local neural suggestion; zero fits the starting pose geometrically. A learned suggestion can worsen an already useful pose, so inspect it before keeping.

4. Click Solve Whole Body for a single fit, or Start Live Solve for automatic updates after you edit targets or settings. Live Solve waits 150 ms for edits to settle, cancels outdated work, and fits the newest request. Stop Live Solve or Escape cancels an unfinished fit and retains the preceding successful preview. Larger Rigify fits still take seconds; live updating does not make them instantaneous. Calling the single-solve operator through EXEC_DEFAULT runs synchronously for scripts.

5. Keep as Pose Anchor stores editable FK control values and restores the original source rig. A changed or reset target must finish solving before it can be kept. Stop Live Solve before using Reset. Cancel Preview restores the source without an anchor. Author another anchor and use the existing interpolation preview workflow to review the resulting motion.

Live Solve starts off. Save, reload, undo/redo, finishing the preview, changing scene/frame, or disabling the add-on stops automatic work. Live mode never resumes from a saved or undone scene. Editing rig controls directly stops Live Solve and preserves those edits; solve again to verify the pose before keeping it.

Targets and the last verified preview survive saving and reopening the blend file. Saving during a solve cancels the unfinished solve and saves the preceding preview. Undo/redo restores the pre-solve and solved control states. After reopening, Keep or Solve restores the saved FK preview before using it; source action keys and the action slot remain intact. Restore the original frame, action, rig properties and object transform if a diagnostic requests it. Changed/deleted controls or helpers are rejected instead of applying incompatible results.

Whole-body fixtures currently cover BoneForge controls, basic/default generated Rigify humans and basic/default human metarigs. Validated plain-FK Mocap, Unity and Unreal conventions now have FBX/weighted-mesh behavioral tests; other variants need adapters. Whole-body anchor capture now includes the intermediate Rigify spine controls and default metarig neck; recapture a consistent set when mixing older captures with new anchors.

## Important scope

This version combines experimental learned whole-body suggestions, geometric limb posing, an optional learned limb bend prior and deterministic interpolation. The old limb prior still falls back to authored poles for default BoneForge/Rigify arm proportions. The separate contextual network works through a full-body rig fit, but has mixed reconstruction evidence and no demonstrated visual or production advantage. Neither model learns motion between frames.

Whole-body head/spine compensation and selected-control damped secondary motion are implemented for the tested humanoid rigs. Development 0.37 also includes explicit selected-control force-at-offset torque with authored scalar inertia, active-control load recall, and up to eight direct rigid spherical selected-control colliders with optional center/uniform-radius animation, conservative bounds-to-radius fitting, and unparented proxy creation from current world bounds. It additionally includes a procedural Static Capsule collider: choose two distinct unparented static endpoint objects and a radius in the Secondary Motion panel to keep selected control pivots outside a finite segment with spherical end caps. Exact-package capsule binding, the affected secondary-motion regression and the foreground recovery journey pass on Bforartists 5.1.0 / Blender 5.2.0 Alpha; the host retains the known `ucrtbase.dll` shutdown fault after assertions. Calibrated anatomical presets, dynamic balance, coupled joint torques, general rigid-body dynamics, arbitrary/deforming environment collision, continuous/self-collision, learned inbetweening, deformable or inferred secondary dynamics and the optional Cascadeur connector remain unfinished. Version 0.25.0 added evaluated world-space follow, selected-control scene gravity and static planar point collision; 0.26.0 adds explicit local rotation-chain propagation; development 0.37 adds uniform external acceleration, wind-relative drag, one frame-authored velocity impulse, persistent per-control force/mass acceleration, force-at-local-offset torque, Load From Active and bounded direct sphere point exclusion with optional center/uniform-radius animation, radius fitting, bounds-centered proxy creation, and static capsule point exclusion; 0.28.0 adds limited deterministic quadruped position posing; 0.29.0 adds optional quadruped target rotation. These quadruped controls are deterministic and do not use the unchanged humanoid learned model; see BODY-CONTROLS.md for the humanoid controls.

Native IK constraints remain unchanged. Input poses are matched through evaluated joint transforms, with rollback if the conversion cannot satisfy positions, orientation, scale or control locks. Imported naming conventions are recognized but need wider behavioral tests. Arbitrary parent-space switching, driven/constrained writable controls and nonuniform/reflected object scale remain limited.

Selected Controls Only keeps the previous direct-control capture workflow. Use consistent selected controls and rig settings; do not mix those anchors with normalized whole-body anchors. Old anchors remain readable, but mixing capture formats requires recapturing a consistent set.

Legacy limb solving updates on button press; whole-body posing also has optional Live Solve. For legacy limb posing, Target Strength zero restores the starting pose. In whole-body posing, Target Strength blends control requests; Learned Influence independently affects unconstrained joints. Maximum Bend is an elbow/knee flexion cap, not a full anatomical model. Keep clips within the 240-frame span and 128-anchor limits. Original action data stays intact; candidate key insertion can affect neighboring handles and mode boundaries use one-frame samples.

The limb model (34,920 bytes) and contextual model (109,583 bytes) are bundled and use host NumPy. There are no automatic downloads. Missing/corrupt model data causes the solve to fail and restore the preceding pose. See the bundled `models/MODEL_CARD.md` and `models/context_pose_mlp_v1.MODEL_CARD.md` for provenance, measured scope and limitations.

## Faster evaluation in 0.5.1

Larger eligible rigs use a temporary simplified copy for internal evaluations. The final pose is checked on your original rig. Unsupported dependencies use the original evaluation path; no rig conversion or extra installation is required. Cancel, save and completed solves remove the temporary copy. Large solves still take seconds, and model-quality limitations are unchanged. See PROXY-EVALUATION.md for measured scope.

## Saved previews from earlier versions

Existing 0.5.1 whole-body previews can still be kept or cancelled. Start a new preview to obtain initialized rotation/pole helpers. Source actions remain preserved. BODY-CONTROLS.md explains control selection, strength and error tolerances.

## Whole-body joint limits in 0.7.0

Open Joint Limits during a whole-body preview. Choose a control, enable Limit This Control, and set Swing, Twist Min and Twist Max. Angles are displayed in the scene's angle units. Limits start disabled and retain your settings between previews and across save/reload. Only supported writable controls are offered.

Swing measures departure from the control's rest-local Y axis; twist rotates around that axis. These settings limit the actual control rotation relative to its rest/parent space. They are not anatomical measurements or human range-of-motion presets. Different control-follow spaces can produce different relationships to the character's physical joint. Rigify's default root-follow head consumes head-control rotation even when the neck turns; the solver preserves that choice. To author a different follow space, end the preview, adjust the rig, and begin again.

Limits participate in fitting alongside pins, poles and requested rotations. Final limits are checked on the original rig, including head, hands and feet after their orientations are applied. A conflicting request or unsuccessful fit restores the preceding preview and names the worst violating control. Adjust the targets or limits and solve again. Changing an enabled limit invalidates Keep until another solve succeeds. Target Strength does not soften these bounds.

Twist intervals must have Min <= Max within -180 to +180 degrees. With restricted twist, Swing must be below 180 degrees because longitudinal twist is undefined at an exactly reversed bone axis. Accepted numerical limit error is at most 0.001 radians (about 0.057 degrees).

These limits apply to whole-body pose solves. They are not enforced continuously along interpolation candidates, and they do not prevent mesh collision or provide balance. Version 0.9 adds optional directional bend bounds as described below. Anatomical presets and temporal limit enforcement remain required work. See JOINT-LIMITS.md for implementation and validation evidence.

## Skeletal-joint measurement in 0.8.0

For supported joints, Joint Limits now offers a Measure selector. Control Rotation retains the 0.7 behavior. Skeletal Joint instead measures the evaluated bone relative to its actual skeletal parent, corrected for their rest relationship. This can constrain the head relative to the neck even when the head's animator control follows the root.

Both modes write only supported animator controls. The fitting process evaluates requested head/hand/foot rotations before measuring skeletal limits, including generated dependencies such as Rigify's distributed neck. The original rig is the final acceptance authority. Follow properties and native constraints remain unchanged.

Skeletal Joint is available for mapped limb joints and the head on the tested generated rigs, and for eligible direct deform/FK chains on BoneForge and metarigs. Unsupported controls show Control space only. End an older preview and start a new one to populate the new capability selector; existing 0.7 control-limit previews remain keepable. Measurement-space changes invalidate a solved preview until it is solved again.

This is a rest-corrected skeletal rotation bound, not a calibrated anatomical preset. Version 0.9 adds artist-defined directional bend regions. Anatomical joint surfaces, mesh collision, and limits throughout interpolated motion remain unimplemented. See JOINT-FRAMES.md for coordinate definitions, tests and current latency.

## Directional bend limits and calibration in 0.9.0

During a whole-body preview, open Joint Limits, select an elbow/knee control, enable its limit, and choose Control Rotation or the supported Skeletal Joint measurement. Enable Limit Bend Direction to add a forward bend interval and a sideways allowance to the existing swing/twist bounds. Collapse Pose Targets when you need more space for these settings.

To establish the forward direction, pose the selected joint with a clear bend of at least 5 degrees in the intended direction, then click Use Current Bend as Forward. This reads the current evaluated pose in the selected measurement space and changes only Forward Axis. It does not change the pose, infer anatomical ranges, redefine the rest pose, or automatically enable a limit. Straight and fully reversed axes cannot provide reliable calibration and are rejected. Calibration is unavailable during a solve.

Set Bend Min and Bend Max for permitted signed forward bending and Sideways Swing for the permitted off-plane component. Negative forward values allow bending in the opposite direction. These values are components of the twist-free swing rotation, not clinical flexion measurements or Euler angles. The initial 0-to-160-degree forward interval and 5-degree sideways allowance are editing defaults; adjust them for the character. The total Swing cap also applies, so contradictory bounds can make a request unsolvable.

Click Solve Whole Body and inspect the preview. Enabled bounds remain firm when Target Strength changes. Changing an enabled direction or range requires solving again before Keep. Limits and calibration survive saving/reopening and new previews; older saved previews leave the new directional option disabled. Keep, Cancel and source recovery retain their existing behavior.

Directional fitting uses more rig evaluations and can take substantially longer on generated rigs. It remains a cancellable button-triggered workflow. Anatomical presets, temporal enforcement, contacts, balance, learned motion and physics remain separate unfinished requirements. See BEND-LIMITS.md for measured evidence and limitations.

## Foot-contact suggestions in 0.20.0

Generate and select an interpolation candidate, then open Animation Contacts. Leave Support Surface empty to use the authored support plane, or choose an unparented static planar mesh without modifiers or constraints. Adjust Maximum Surface Distance, Maximum Foot Speed, Minimum Hold Frames and Bridge Gap Frames, then click **Suggest Foot Contacts**. The scan is cancellable and does not change animation.

Review every provisional row. Confidence is heuristic evidence, not ground truth. Click **Accept** to make the selected interval available to contact correction, or **Reject** to keep it excluded. You can edit an accepted interval before previewing correction. Re-running the scan replaces only unaccepted proposals and preserves manual or previously accepted contacts. Suggested state and evidence survive save/reload.

The automatic detector covers feet against static planar surfaces. Use explicit manual capture and binding for hands, props, and moving planar platforms. Automatic moving-platform inference, arbitrary nonplanar collision and automatic training labels remain unsupported.

## Animation contacts in 0.10.0

1. Capture compatible full-body poses, then Generate Interpolation Preview. Start with a short clip; the current correction uses normalized FK controls.

2. Open Animation Contacts near the top of the panel. At a pose where the hand or foot should stay, choose Capture Limb and click Capture Contact Here. Set Hold From and Hold To inside the candidate's anchor span.

In development 0.34, enable **Show Contact Overlay** to draw the selected target and its evaluated limb separation in the 3D View; **Show All Contacts** adds every compatible interval. Green, amber and red indicate accepted, proposed and rejected review states. The row reports the current phase and exact effective influence. Use **Blend In**, **Hold Start**, **Hold End**, or **Blend Out** to inspect all four boundaries, including subframes. These buttons move only the playhead. Move the playhead and click **Set Start** or **Set End** to trim the selected interval. The edit validates the candidate range and all enabled same-limb hold/blend regions before changing the boundary. Invalid edits leave the interval unchanged. The same review controls appear for generated Rigify paw contacts; preferences and fractional boundaries survive save/reload. See `CONTACT-INTERVAL-EDIT-v1.md` and `CONTACT-VISUALIZATION-v1.md`.

3. Set Blend Frames for smooth entry/exit outside the hold interval, positive Strength up to 1, and Hold Rotation if the captured orientation should stay. Each contact has an Enabled checkbox; use the Contact index to select another captured interval. Same-limb hold/blend regions must not overlap, except at a shared zero-influence boundary.

4. Contact Point Settings exposes a local offset when the sole or palm differs from the joint origin. Set Capture Local Offset before capture; the selected interval's world point and offset can also be edited deliberately. By default, a contact is a static world point.

For a humanoid hand that should follow a directly animated rigid prop, choose the object under **Hand-to-Prop Hold** and click **Bind to Prop**. Binding stores the captured hand relationship in the prop's local position and rotation; the correction follows the prop's evaluated transform over the interval. The line **Following _object_** identifies the committed target. Changing the selection field alone does not retarget it. Click **Clear** to turn the relationship back into a fixed world-space target. Bind and Clear support Undo, and the relationship survives save/reload.

The prop must be an unparented object in the same scene and visible active view layer. This version rejects constrained, driven, NLA, rigid-body, animated-scale, reflected, sheared, or curve-modified props and any prop-animation change during correction. A prop-bound hand cannot be a support patch. It does not infer a grasp, pose fingers, detect the prop, or support constrained/parented/physics-driven motion. See `PROP-HOLDS-v1.md`.

For a humanoid foot on a directly animated rigid platform, choose a mesh under **Foot-to-Moving-Platform** and click **Bind to Platform**. The captured foot point must lie on the mesh within Contact Tolerance and inside Blender's tessellated face bounds. Correction then follows the platform's evaluated object position and rotation. **Following _object_** identifies the committed platform; changing the selector alone does not retarget it. **Clear** fixes the current target in world space. Bind/Clear support Undo, and the binding survives save/reload.

The platform must be a finite, unparented planar base mesh in the same scene and active view layer. Modifiers, shape keys, mesh animation, constraints, drivers, NLA, rigid bodies, animated scale, reflection, shear, and curve modifiers are rejected. The foot must remain reachable without moving the body. Platform-bound contacts cannot be support patches, so current COM/support analysis does not move with them. This first workflow is humanoid-only and kinematic; it does not simulate the platform or collide the rest of the character. See `MOVING-PLATFORMS-v1.md`.

5. Click Preview Contact Correction. The modal operation checks authored samples and intermediate times, adds local samples when needed, and allows Escape cancellation. A contact that conflicts with a priority pose or is unreachable with the existing body path is rejected. Original poses and limb lengths are preserved within the documented numerical tolerances.

6. Scrub the candidate and inspect contact drift. Adjust settings and preview again; corrections regenerate from the retained input rather than accumulating. Restore Before Contacts returns to the interpolation candidate. Keep Candidate, Discard and Restore Source Animation retain their existing meanings.

Contact settings, the corrected candidate and its retained input survive save/reload. Saving during processing cancels the unfinished correction. Action curves outside the selected limbs/intervals are preserved within the documented coverage; custom Bezier boundary behavior still requires wider validation. The input candidate is retained as an editable alternative action.

This is geometric contact correction around existing interpolation. It does not learn motion, infer balance, collide with a floor, follow moving support surfaces, enforce all anatomical limits through time or generate root motion to reach an impossible contact. Explicit directly animated rigid-prop hand holds are supported within the contract above. See CONTACTS.md and `PROP-HOLDS-v1.md` for sampling, accuracy, preservation, performance and limitations.

## COM and support analysis in 0.11.0

Open Center of Mass / Support and initialize the editable mass model. Review segment weights and center fractions under Mass Model. In Animation Contacts, capture explicit sole/palm centers, enable Use as Support Patch, and set width, length and heading. Configure the support plane and tolerances, then Analyze Current Pose. The result is a saved static estimate; reanalyze after edits or frame changes. Undo/Redo and save/reload preserve the workflow.

The estimate uses evaluated rig joints and scene gravity, preserving the animation. Foot/hand drift, changed orientation, off-plane contacts, partial strength and times outside the hold interval exclude support patches. The default mass distribution and rectangular patches are artist-authored approximations. Inside Support does not prove dynamic balance; inclined planes are labelled geometry-only. No balance correction, collision detection or new learned animation is added. [SUPPORT.md](SUPPORT.md) explains units, assumptions, report data and verification.

## Static balance assistance in 0.12.0

After authoring mass and support patches, start a whole-body pose preview and enable Assist Static Balance. Choose Balance Strength and Support Inset. Allow Pelvis Translation explicitly releases the pelvis position; supporting hand/foot captures and other animator pins remain constrained. Solve Whole Body previews the correction, Escape restores the preceding pose, and Keep as Pose Anchor retains editable animation while restoring the source rig. Repeated strength adjustments use the original reference.

Use [BALANCE.md](BALANCE.md) for the complete workflow, conflicts, units, compatibility and measured limits. Old 0.11 previews remain usable with balance disabled; start a new preview to initialize their missing balance reference. This is current-pose static assistance and does not enforce physics through interpolated motion or prove dynamic stability.

## Airborne motion

Generate an interpolation candidate, open Airborne Motion, and initialize its mass model. Add an interval between authored Takeoff and Landing poses, set Gravity Influence and click Preview COM Flight. The tool fits the authored COM to scene gravity while preserving the relative pose. Intermediate conflicting priority poses and overlapping contact influence are rejected.

Escape cancels the solve. Restore Before Flight recovers its input; Keep/Discard and Restore Source Animation retain ordinary recovery. Apply contacts after flight and restore any contact correction before changing flight. The displayed speed jump is an estimate of boundary discontinuity, not a solved transition. See FLIGHT.md for units, mass assumptions, frame limits and current physics limitations.

## Regenerating flight previews in 0.13.1

Preview COM Flight replaces its prior unmodified generated result. The tool removes that superseded action only when it has no remaining users and still matches its recorded generated name and curve fingerprint. Edited animation curves, renamed alternatives, fake-user actions, shared actions and asset-marked results are retained; an otherwise unused edited/renamed or legacy result receives a fake user so it survives saving. Retained input animation and Keep/Discard recovery are unchanged. Undo/Redo also applies to replacement.

Long default Rigify flights can currently reject because small facial-bone transforms exceed the preservation tolerance. This is a known compatibility limitation; the tested failure restores the candidate and permits Discard back to source. No tolerance was loosened. See FLIGHT-OPTIMIZATION.md for measured performance limits.

## Native Motion Layer

After generating an interpolation preview and authoring COM Flight intervals, choose **Native Motion Layer** as the flight method. Click **Preview COM Flight**, inspect the result, then Keep or Discard. Escape cancels generation. **Restore Before Flight** removes the current native correction while retaining the interpolation candidate.

The method moves a native collection instance containing the source rig and its bound meshes. The rig's original animation channels stay in their original coordinate system. The instance's residual, translation, optional quaternion and COM-pivot curves provide the editable flight trajectory; the source pose action remains independently editable. Playback of a saved result uses Bforartists' native data and does not require the add-on to be loaded.

After Keep, **Restore Source Animation** stores an independent complete motion alternative under **Saved Motion Results** before restoring the original animation. Click an alternative's preview button to reopen a separate candidate; editing or discarding that candidate preserves the stored alternative.

Keep a candidate before starting whole-body or limb posing. Select the displayed instance or its posing helper to use the existing tools. Helpers, contact capture and COM/support analysis follow the displayed rigid transform. Restore the kept source before generating another interpolation candidate. Apply source object scale before creating the motion layer; native motion permits its generated rotation but rejects scale, shear, reflection and parenting.

Near-converged plain whole-body poses may receive one additional fit attempt. The pin tolerance is unchanged and Escape still cancels. This can add a few seconds for difficult targets; ordinary successful requests use the existing budget. Conflicting limits, invalid inputs and large accuracy failures still reject and restore the preceding preview.

Native flight currently has real-rig acceptance for the documented BoneForge and default Rigify cases, including a 60-frame default Rigify interval. Native COM velocity/C2 acceleration transitions, finite rigid-segment airborne angular refinement, sampled static planar collision response and a separate selected-control secondary stage are available as described below. Learned inbetweening, joint/external force solving, arbitrary/deforming collision and advanced secondary dynamics remain unfinished. See NATIVE-FLIGHT.md, PLANAR-COLLISION-RESPONSE-v0.23.0.md and SECONDARY-MOTION-v0.24.0.md for measured scope and the known host shutdown issue.

## Multiple airborne intervals in 0.14.1

Author each airborne interval between two priority poses. Up to sixteen non-overlapping intervals can share the native motion layer. Each interval has its own Gravity Influence. Keep, Restore Before Flight, source restoration and saved alternatives use the same workflow as a single interval. The generated native driver structure expands automatically when a formula would exceed the host's length limit.

The tested five- and sixteen-interval cases use repeated poses to verify generation and recovery. Long or physically conflicting intervals can still fail the unchanged accuracy checks and restore their input. Takeoff/landing momentum, collision response and naturalness still require animator judgment and further development.

## Native sampling maintenance in 0.14.2

Native COM flight avoids repeated rig mapping and unnecessary deformation-matrix collection during fitting. Counterbalanced 60-frame BoneForge/default Rigify checks produced identical native curves and drivers, with about 5% lower mean solve time. The acceleration threshold is unchanged; tested 240-frame flights still reject and restore their source. See NATIVE-SAMPLING-0.14.2.md for evidence and the 32-bit position diagnostic. No new temporal model is bundled.

## Live Solve performance

The five humanoid fixtures take roughly 1-6 seconds per complete fit. The 0.15.1 optimization approximately halves measured idle scheduling on BoneForge and default Rigify; default Rigify now measures about 10 ms in the paired idle test. Fit steps can still exceed 100 ms. Automatic updates are experimental and the full responsiveness goal is not met. See LIVE-POSE-v1.md and LIVE-REQUEST-PERFORMANCE-v1.md for exact measurements and lifecycle coverage.

## Imported FK humanoids

Import your rig using the host, then select its armature or bound mesh. The Mocap (mixamorig), Unity and Unreal adapters check actual spine, shoulder and limb parents. A connected pelvis uses its first unconnected ancestor for translation. Root ancestors join full-pose anchors and candidate interpolation; source animation remains recoverable. Nonstandard topology may still use ordinary Capture Pose even when whole-body posing is unavailable. Driven/constrained dependencies, mechanism ancestors and nonuniform bone scale need a dedicated adapter. No rest bones or connections are changed. Legacy FK assisted-pose Keep leaves the solved pose visible; Cancel restores its captured input. Whole-body Keep saves the anchor and restores the original pose. These are tested synthetic FBX conventions, not a guarantee for every production file.

0.16.1 preserves the existing animator workflow. Interpolation in the panel is still procedural; a qualified learned-motion model is not yet enabled. Source recovery and existing posing remain covered by the current package checks in package-test-v0.16.1.json.

## Native velocity transitions in 0.17.1

Choose Native Motion Layer in Airborne Motion. Under Transition frames, set Before takeoff and After landing to at least one frame for the joins you want to smooth; zero disables a join. Spans must stay inside the candidate and between authored poses. Contacts and overlapping flight/transition regions are rejected. The transition preserves its endpoint poses and smooths COM velocity using an editable native cubic curve. Restore Before Flight before changing an existing result, then preview again. Keep, Discard, Restore Source and archived results work as before.

Gravity Influence controls the airborne arc. Transition frames independently enable velocity matching, including existing source corners when Gravity Influence is zero. Inspect the displacement before keeping. This is procedural COM velocity matching; planted-foot transitions and secondary gravity remain unfinished. Contacts and selected-control Secondary Motion can refine the resulting candidate. Saved native results retain their own timing even if the panel settings are later edited. See MOMENTUM-TRANSITIONS-v1.md and NATIVE-CONTACT-COMPOSITION-v1.md.

## Presentation patch 0.17.2

The transition frame controls now fit in the tested narrow sidebar. Animation behavior is unchanged from 0.17.1. Exact-package window checks pass; prior behavioral and offline evidence is retained after an exact source audit. See package-test-v0.17.2.json. Independent animator usability and the known host shutdown failure remain unqualified.

## Experimental 0.17.3: cancellable preparation

The 0.17.3 ZIP adds staged preparation of temporary evaluation rigs. Default Rigify first active ticks averaged 146.6 ms before and 39.5 ms after in the final headless comparison; worst ticks averaged 95.6 ms after, and total active work increased 9.1%. Full responsiveness remains unqualified. 321 fresh regression cases and four exact-package offline live/Keep/Discard cases pass. Current-package UI interaction and independent animator usability remain unverified; the known host shutdown crash persists. See COOPERATIVE-PREPARATION-v1.md and package-test-v0.17.3.json.

For manual motion inspection, motion-review-v1/index.html contains 96 fixed examples with recorded motion, procedural control and two learned candidates. Data and JavaScript syntax pass static checks; browser policy blocked local-file interaction verification. No reviewer ratings were supplied, and no temporal candidate is qualified or included in the addon. See MOTION-REVIEW-v1.md. All original learned-motion, physics/refinement, rig coverage, optional connector and equivalent Cascadeur comparison requirements remain.

## Experimental 0.17.4: finalization and recovery

The 0.17.4 ZIP reduces finishing pauses, reads structural signatures more efficiently without caching them, and restores the verified preview if the public record is damaged during completion. The released/current fault comparison confirms the recovery fix on BoneForge and default Rigify. All 330 regression cases and four exact-package offline live/Keep/Discard cases pass. Default Rigify finishing ticks averaged 77.99 ms before and 48.03 ms after; worst-tick averages fell 28% and total active work fell 8%, with identical poses and solver metrics across five profiles. The first candidate missed its worst-tick gate and remains recorded as a failure.

Full responsiveness remains incomplete: worst ticks still exceed 50 ms and solves take seconds. Current-package UI interaction, independent animator assessment and equivalent Cascadeur comparison remain unverified; the known host shutdown crash persists. No temporal model is qualified or bundled. All original learned-motion, physics/refinement, rig/quadruped, connector and distribution requirements remain. See FINALIZATION-PERFORMANCE-v1.md and package-test-v0.17.4.json.

## Shape-aware Rigify correction in 0.20.2

Large Rigify candidates using procedural shape smoothing now keep contact fitting on the dependency-closed evaluator through publication. The 32-case procedural humanoid packet passes on BoneForge, generated Rigify basic/default and an imported Unity-style hierarchy. Three exact-package actual-window foot-contact journeys remain below 50 ms per callback and below 8 seconds total. This improves correction speed; full-action generation can still take tens of seconds. See PROCEDURAL-VERTICAL-SLICE-v12.md and PROCEDURAL-PROXY-PERFORMANCE-v0.20.2.md.

## Independent procedural-slice evaluation

These tools are evaluation aids outside the installed add-on. Open `training/b4artists_ml/results/procedural-vertical-slice-reviewer-v2/reviewer.html` in a local browser to assess the exact 0.25.0 32-case procedural slice. Play both anonymized candidates, switch among front, side and oblique views, and inspect priority ghosts, pelvis trails, contacts and the floor. Complete both candidates' naturalness, contact, continuity, intent, acceptability, correction and interaction fields, choose an overall preference, add visible-failure tags and lock the case. Method identity and automated measurements appear only after locking.

The browser stores progress locally and sends nothing. Enter a reviewer ID or anonymous code and experience category after all 32 cases are locked, then export the JSON. Check it with `py -3 training\b4artists_ml\check_procedural_vertical_slice_human_review_v2.py <exported-review.json>`.

For actual correction effort, launch a frozen candidate in Bforartists with `py -3 training\b4artists_ml\launch_correction_trial_v1.py --reviewer <code> --case boneforge/reach --side A --output training\b4artists_ml\results\hands-on-correction-trials-v1`. The separate `B4ML Study` panel tracks active time and action-key edits, excludes pauses, and leaves the source scene unchanged. Validate its export with `py -3 training\b4artists_ml\validate_correction_trial_v1.py <exported-trial.json>`. Automated smoke exports are marked synthetic and cannot pass as human evidence. The reviewer uses joint centers and cannot show skin deformation, axial twist or mesh collisions. See HUMANOID-REVIEW-AND-CORRECTION-v13.md.

## Experimental 0.17.5: bounded record reconstruction

The local experimental 0.17.5 package integrates bounded record reconstruction. All 345 native regression cases and four exact-package offline live/Keep/Discard cases pass. Default Rigify idle p95 improves 44.4%, total active work 14.3%, and worst-tick averages 13.3%, with exact five-profile poses, signatures and solver metrics. Each read returns an independent mutable tree; source validation remains unchanged. Cache keys/blobs stay within 4 MiB plus bounded container overhead and are released at preview/lifecycle boundaries. Worst ticks still exceed 50 ms. Current UI interaction, independent animator assessment, full learned motion and Cascadeur parity remain unverified; the known host shutdown crash persists. See RECORD-CACHE-PRODUCTION-v1.md and package-test-v0.17.5.json. The original goal remains active and incomplete.

## Match COM acceleration in 0.20.3

For a Native Motion Layer airborne interval with takeoff or landing transition frames, enable **Match COM Acceleration** before **Preview COM Flight**. The option smooths both COM speed and acceleration into and out of the flight while preserving authored boundary poses and the untouched outer edges. It is off by default. The result remains an editable native motion layer and supports the same Cancel, Restore Before Flight, Keep, Restore Source and Discard workflow. This is linear COM refinement; selected-control secondary motion is a later candidate stage, while general forces remain future work. See COM-ACCELERATION-TRANSITIONS-v0.20.3.md.

## Airborne angular momentum in 0.21.0

Choose **Native Motion Layer** and raise **Angular Momentum** for a free-flight interval before running **Preview COM Flight**. Zero keeps the original character orientation. One applies the full bounded correction; intermediate values blend it. The correction uses the editable mass model and reduces variation in segment-center point-mass angular momentum while keeping the takeoff/landing orientations and COM trajectory fixed. It can run with transition frames and **Match COM Acceleration**.

The generated result contains editable quaternion and COM-pivot curves on the native motion instance. Restore Before Flight, Escape, Keep, Restore Source, reopen and Discard retain their ordinary meanings. Split an interval at any additional priority pose. A nonzero angular setting with Root Curves is rejected. This flight stage excludes joint torques, collision impulses and air drag; selected-control Secondary Motion is applied separately. Inspect the result before keeping it. See ANGULAR-MOMENTUM-v0.21.0.md.

## Rigid-segment inertia in 0.22.1

The current **Angular Momentum** option extends the 0.21 workflow to include intrinsic segment spin. Under Center of Mass / Support, select a mass segment and adjust **Inertia Radius** when its default ellipsoid thickness does not fit the character. This radius is relative to the evaluated segment length and survives save/reload. Changing it during a running correction cancels safely rather than mixing settings.

The result still uses editable motion-layer quaternion and COM-pivot curves with exact takeoff and landing orientation. The panel reports total rigid-segment variation reduction. Defaults are artist estimates, so inspect the motion and tune mass, center fraction, radius and strength together. Joint torque, external forces, general mesh collision and drag are not yet solved; selected-control Secondary Motion is a separate refinement. See RIGID-SEGMENT-INERTIA-v0.22.1.md.

## Static planar collision response in 0.23.0

Choose **Native Motion Layer** and raise **Collision Response** for an airborne interval. Set **Collision Clearance** as a fraction of evaluated trunk length. The tool uses the explicit support plane under Center of Mass / Support, or the optional static planar mesh selected as the contact surface. The plane normal defines the allowed side; static mesh normals are oriented against scene gravity. Root Curves rejects this option.

The response treats the 17 mass segments as finite ellipsoids using their editable **Inertia Radius** values. It moves the complete displayed character along the plane normal and publishes separate editable linear curves. It can run with Gravity Influence, Angular Momentum, transition frames and Match COM Acceleration. Authored takeoff and landing poses remain unchanged; a plane that would require moving either pose is rejected with an edit instruction.

Zero disables the feature. Partial strength intentionally leaves a measured portion of penetration. Inspect the panel's post-response penetration readout before keeping. Escape, Restore Before Flight, Undo/Redo, Keep, Restore Source, reopen and Discard work as for other native results.

This first adapter handles one static infinite plane or bounded planar mesh. It samples segment-center participation and verifies clearance at quarter-frame-or-finer keys plus a shifted phase. It does not provide arbitrary mesh or self-collision, moving/deforming surfaces, collision impulses, friction, torque, deformation-volume contact or a continuous-time guarantee. See PLANAR-COLLISION-RESPONSE-v0.23.0.md.

The user authorized 20 additional hours starting September 8 at 23:24:05 UTC, ending September 9 at 19:24:05 UTC. The same goal and 50-evaluation ceiling remain in force; no criteria or history were reset.

## Experimental 0.18.0: authored whole-body motion

The local0.18.0 experimental archive includes a procedural Whole-body Motion option. All 369 native regression cases and seven exact-package offline workflows pass. This build is available for local testing; current modal viewport usability and animator quality remain unverified.

1. Capture at least two full humanoid poses. Add a middle pose to define a crouch, reach or recovery. Keep Selected Controls Only off for this method; existing Pose Blending still supports selective captures.

2. Under Generate and Review, set Method to Whole-body Motion and click Generate Whole-body Preview. The original source pose stays visible while the result is generated. Escape or Cancel stops the job; orbit controls remain available in the modal operator. Saving, loading, undo/redo or disabling the addon cancels unfinished generation.

3. Scrub the completed candidate. Use Animation Contacts to capture and apply explicit foot or hand holds, then review the correction. Keep Candidate and Discard retain their existing behavior; Restore Source Animation remains available after keeping.

This method interpolates authored body positions and endpoint orientations, then fits the actual rig. It is procedural, requires no training files or downloads, and does not provide learned temporal motion. Authored-only observation reads match the validated research result exactly on the three controlled crouch/recover fixtures. The original pose-blending method remains the default.

Motion quality and responsiveness remain limited: SLERP plus baked FK curves can change velocity abruptly at priorities, and complete fits take seconds. Contact correction improves the measured crouch rotation transition but does not establish smooth animation generally. Independent animator assessment and current modal viewport interaction remain unverified.

## Installing the local experimental 0.36.0 package

In Bforartists, open **Edit > Preferences > Add-ons**, choose **Install from Disk**, and select `releases/b4artists_ml_v0.36.0.zip`. Enable **B4Artists Machine Learning**, then use **View3D > Sidebar > B4Artists ML**. This package is Bforartists-only and intended for local testing. The release does not claim learned temporal generation or Cascadeur parity; see `RELEASE-v0.36.0.md` for the measured scope.

### Closed Volume mesh collision

In Secondary Motion, choose World and Location, enable Collision, and choose
**Closed Volume**. Select one unparented triangle mesh with closed topology,
enable **Follow Shape-Key Deformation** only when the mesh uses a direct
shape-key Action, and set **Control Volume Radius**. The solver treats each
selected control as a finite spherical volume and keeps its radius plus
Clearance outside the nearest evaluated mesh triangle. Open meshes, moving
object transforms, modifiers, drivers, NLA and rigid-body state are rejected;
use **Mesh** instead when you need the existing sampled surface behavior.

The result remains an ordinary editable candidate. Inspect the reported target
space (`closed evaluated triangle volume`) and final penetration before keeping
it. With a static closed mesh and **Continuous-Time Sweep**, the target space
becomes `exact swept-sphere closed evaluated triangle volume`: the solver uses
exact segment-to-filled-triangle distance for the authored finite radius and
catches near-face or rounded-edge contact even when the centerline misses. This
exact path is static-only; moving/deforming trajectories retain their bounded
interpolation contract. Self-collision, coupled collision forces, learned
motion and Cascadeur parity remain separate unfinished capabilities.

For static closed meshes, enable **Continuous-Time Sweep** below the mesh
binding. This catches segment crossings between solver samples and is useful
when a fast control would otherwise tunnel through the mesh. It cannot be
combined with Follow Shape-Key Deformation; open meshes and moving collision
objects are rejected for this option.

## Portable matched-comparison characters

The developer evaluation folder `training/b4artists_ml/reference-assets-v1` contains three exact neutral FBX files and matching Bforartists source scenes: standard, tall/long-limbed and short/broad. Use the same frozen FBX bytes for each B4ML/Cascadeur matched pair; do not re-export one side. Their common Unity-style skeleton and project-owned block mesh keep rig and appearance variables explicit. These are evaluation assets outside the installed add-on.

The source files and fresh Bforartists FBX imports pass hierarchy, binding, topology, weighting, proportion and external-data checks. The bounded Cascadeur disposable import audit also passes for all three assets, but conversion, mapping, matched animation and parity remain unverified. See `PORTABLE-COMPARISON-CHARACTERS-v1.md` before using them; no comparison outcome or parity claim exists.
