# Experimental 0.8.0 - evaluated skeletal joint frames

The full product goal remains active and incomplete. This milestone adds a skeletal-joint measurement mode to the 0.7 limit workflow. No model weights, training data, Ghost Tool or Anim Assist code changed. It does not establish calibrated anatomy, learned motion, production readiness or Cascadeur parity.

## Coordinate contract and adapters

Control Rotation retains the existing rest-local animator-control semantics. Skeletal Joint reads the evaluated skeletal bone and its actual skeletal parent, then removes their rest relationship. The same skeletal pose therefore has the same measurement regardless of the animator control's follow space.

For child and parent orientation quaternions C and P, rest orientations C0 and P0, the measured rotation is:

    R0 = inverse(P0) * C0
    Q = inverse(R0) * inverse(P) * C

Swing/twist is then measured in the child's rest-local axes. Object translation, rotation and positive uniform scale do not enter this armature-space relative orientation. The 0.7 signed twist interval, quaternion-sign equivalence, singularity rules and acceptance thresholds remain in effect.

This uses the documented evaluated [PoseBone.matrix](https://docs.blender.org/api/5.2/bpy.types.PoseBone.html) and rest [Bone.matrix_local](https://docs.blender.org/api/4.3/bpy.types.Bone.html) transforms. The former includes constraints/drivers; the latter is the rest bone transform in armature space. Data is read from generated skeletons, while all writes continue to target verified animator controls.

The adapter maps the 12 limb controls onto their actual existing joint chains, plus the generated Rigify head onto its ORG head/neck chain. Eligible direct deform/FK bones on BoneForge and metarigs also have parent-relative frames. A generated mechanism is never guessed to be an anatomical parent. Unsupported controls offer only Control Rotation. The generated neck control governs a distributed chain, so this release does not invent a single neck joint for that control.

Frame pairs and rest offsets are computed per solve request; the existing immutable rest-structure and rig-property guards remain active. The private evaluation copy explicitly retains measured children and parents and is still validated against the original rig. Persistent settings store only the selected measurement mode and bounds. A new preview populates capability flags for its current adapter.

## Distributed dependencies and numerical fitting

A joint's evaluated parent may itself depend on the requested effector. For skeletal requests, fitting now applies all requested/preserved head, hand and foot orientations before reading the evaluated graph. Quaternion assignments are batched and followed by an update. Progress yields also expose the accepted full pose. Final limit, position, orientation, pole and bone-length gates run on the original rig.

This matters on Rigify: the installed super_head.py at lines 294-295 distributes the head control's LOCAL rotation across neck mechanisms. Changing head-follow can therefore change the physical neck even if the head orientation alone is held fixed. Preserving a child-to-control offset while ignoring that parent dependency was insufficient.

Skeletal requests use a normalized finite-difference step of 1e-4, while existing control-space requests retain 1e-3. The larger step stalled close to tight inequality boundaries in reference fixtures, even with fresh derivatives. The finer step passed the unchanged pin tolerance. No acceptance threshold was loosened. Some accepted head fixtures remain close to the pin threshold; this is limited regression evidence, not proof of robust convergence for every reachable pose.

## Development evidence and corrections

- joint-frames-v1.json: six tests; one failure and two errors. Predicting only the final head rotation missed the distributed parent change. The initial invariance fixture also held only the head fixed while the actual neck differed.
- joint-frames-v2.json: actual final effector evaluation fixed the generated Rigify head bound, but coarse derivatives stalled on three pin fixtures. The invariance fixture still needed an actual parent match.
- joint-frames-dense-v3.json: refreshing every derivative at the same coarse step did not resolve three pin errors. The single-fixture trace in diagnose-joint-fit.log confirms the error was present in accepted solver steps, not introduced solely by final application.
- joint-frames-v4.json: six tests passed with the finer step and a genuinely matched child/parent fixture. The test authors the neck control to match its evaluated skeletal orientation across follow settings; it does not overwrite mechanism bones.
- joint-frames-package-v0.8.0.json: eight packaged tests passed, including a bound-mesh sample and an actual retained 0.7 preview.

All artifacts above are under training/b4artists_ml/results, with command logs under training/b4artists_ml/cache. Failed experiments remain available rather than being overwritten by successful results.

## Coverage

The new suite covers rest-frame consistency across all five humanoid fixtures, matched skeletal measurements across Rigify follow settings despite differing control rotations, active limb bounds on three rig families, and tight head limits on all five fixtures without changing authored follow values. It also covers unsupported spaces before mutation, active preview cancellation, save/reload, changed measurement-space rejection before Keep, and source restoration.

The default generated Rigify bound-head sample moved 0.03694 rig units and agreed with its evaluated deform-bone transform to 4.66e-8 units. This is one weighted reference sample, not production character-mesh acceptance.

The legacy fixture was created through the actual unchanged 0.7.0 ZIP and saved with enabled control limits. The 0.8 runtime retains Control Rotation as the default for absent measurement-space properties, and successfully keeps that saved preview as an anchor. Older preview signatures are not rewritten to opt into new behavior.

## Actual UI and performance

The exact 0.8.0 ZIP passed the established real event-loop workflow on default generated Rigify with 13 skeletal limits, six rotation targets and four poles. Timer-driven solving, simulated Escape, undo, redo and Keep all passed. The native screenshot was inspected; the selected Skeletal Joint mode is visible. The expanded sidebar still requires scrolling to lower controls/actions at the recorded window size.

The UI solve took 15,406.44 ms, 75 iterations and 1,552 evaluations. Limit violation was zero; pin error was 2.0887e-6 torso units; orientation error was 7.4822e-7 radians. Total scenario time was 17.31 seconds. This does not establish continuous responsive posing, a performance improvement over the differently configured 0.7 scenario, or animator quality acceptance.

The eight new packaged background tests passed before the known shutdown access violation, and the UI likewise logged EXCEPTION_ACCESS_VIOLATION in ucrtbase.dll after its passing marker. These are not clean application exits. All 128 regression tests passed with zero skips: the eight new skeletal-frame tests and all 120 established regressions. There are 118 package-entry tests and 10 source-adapter tests whose runtime is byte-identical to the ZIP. Twelve unchanged contextual training/data tests were not rerun; model weights and data code did not change.

All ten background processes completed passing assertion markers and then exited with the known shutdown violation (signed -1073741819 / unsigned 3221225477). UI stderr separately records the same shutdown problem; its launcher did not capture a numeric exit code. Per-suite hashes and outcomes are in checkpoint-joint-frames-v1.json.

Package: releases/b4artists_ml_v0.8.0.zip, 24 runtime files, 201,906 bytes. SHA-256: 81efd39adbaba205cc6f38ef3993f3f2bbc8c503e5a4fd37319d2d164f2757d9. ZIP integrity, Python syntax and source-byte equality pass. The 0.7 release is unchanged.

The required execution router stopped before host application because its remote /mnt/x workspace was unavailable. It emitted no lane, policy fingerprint or patch. Native continuation followed the canonical recoverable-infrastructure policy within the declared source/test/documentation/package scope. No commit, push, installed-add-on update, credential change, Ghost Tool edit or Anim Assist edit occurred. Tracked and staged Git diffs remain empty; the ML work is still untracked.

## Remaining scope

The implemented frame is a rest-corrected bone-pair rotation, not a calibrated anatomical joint model. Directional hinge/swing regions, asymmetry, character presets, joint surfaces, temporal limit enforcement, contacts and balance remain incomplete. Generated torso/neck mechanisms need further explicit anatomical adapters where a control affects multiple physical segments.

Learned temporal motion, gravity/momentum/secondary motion, continuous interaction, production rigs and meshes, imported rigs, quadrupeds, an optional entitlement-aware connector, blind animator evaluation and equivalent direct Cascadeur comparisons remain required. The existing contextual model's prior-pose quality regression remains unresolved.
