# B4Artists Machine Learning 0.5 validation

Experimental whole-body preview milestone. The overall goal remains ACTIVE and incomplete. This adds a local contextual neural model, actual-rig fitting and a recoverable animator workflow; it does not establish Cascadeur parity.

## Implementation

The former research adapter is now b4artists_ml/body_solver.py; the old context_rig module aliases it for regression compatibility. body_model.py contains only inference and checksum-verified model decoding. Weights load from package resources, including directly from a ZIP, with no training or BVH dependency in the runtime.

body_preview.py persists source/action/slot state, normalized controls, targets, last verified preview and model request settings. The UI runs the cooperative iterator through window events, with progress and Escape cancellation. Keeping captures the verified result as an editable FK anchor and restores source controls/modes. Rigify captures now include intermediate spine controls and the default metarig neck. Mixing new and older partial capture sets may require recapturing consistent anchors.

Completed lifecycle assertions cover keep-to-interpolation/discard, full Rigify spine capture, interrupted solve rollback, save/reload, saving during a solve, animated source keys and slot preservation, invalid saved control/solver values rejected before mutation, conflicting preview workflows, and unregister cleanup across scenes.

The UI test seeds only scripted fixture/target setup in the undo stack, then uses the actual modal operator completion, a simulated Escape event, and real undo/redo. It asserts pre-solve and solved control values before keeping an anchor. This is automated window-event validation, not animator quality acceptance.

## Correctness findings fixed

- Saved input signatures now compare authored helper inputs; reconstructed hidden points can differ slightly after JSON reload and must not falsely invalidate an unchanged preview.
- The actual host Event object has no timer attribute. Modal progress now consumes timer events with monotonic throttling and removes its owned timer on every terminal path.
- Invalid saved solver quaternions and nonfinite evaluated coordinates/updates are rejected.
- Unregister restores each preview in its own scene instead of changing an unrelated active scene's frame.

## Quality and responsiveness limits

Whole-body fitting has actual-rig pin, bone-length and authored-orientation checks, but no anatomical limit, balance, collision or temporal contact model. Sparse positions are supported; requested pole/orientation targets remain missing. The neural model can degrade an already useful prior pose and was slightly worse than linear regression on fresh confirmation. See models/context_pose_mlp_v1.MODEL_CARD.md for the frozen evidence and provenance.

Large Rigify fits still take seconds. Cooperative yielding allows cancellation and redraw; it does not establish continuous live posing, a frame-time guarantee or improved animation quality. Historical dense/reuse benchmarks remain in CONTEXTUAL-RIG-OPTIMIZATION-v2.md. Current regression measurements are in training/b4artists_ml/results/context_rig_packaging_v0.5.json.

## Scope and execution

All host work uses disposable factory-startup scenes. No installed add-on or preferences were modified. The ZIP contains runtime code, maps, licenses, notices and two small weight files; it excludes training code, raw motion and test scenes.

The code router again rejected the remote /mnt/x workspace because that directory is unavailable on the execution host. No lane, policy fingerprint or patch was emitted. Local continuation followed the canonical recoverable infrastructure policy within the authorized add-on/test/documentation/package scope. No external service, credentials, Git history or Ghost/Anim Assist source was changed.

Learned temporal motion, contact intervals, physics/COM/gravity/momentum, anatomical/pole/orientation constraints, secondary motion, quadrupeds, imported-rig behavioral coverage, production meshes, the optional connector and direct comparative/animator evaluation remain unfinished. The model and passing tests do not complete the full objective.

## Final package and test evidence

106 host tests passed with zero skips: 84 loaded the ZIP (31 foundation, 18 posing, nine rig-state, 16 limb-model and 10 whole-body lifecycle), plus 12 contextual research tests and 10 actual-rig runtime-adapter tests from source. The source adapter is byte-identical to the packaged adapter. The final ZIP also passed the actual UI solve/Escape/undo/redo/keep scenario. The rendered panel and fixture screenshot were inspected; this is not a character-animation quality review.

All seven background processes completed assertion markers and then exited -1073741819 (unsigned 3221225477) with the previously isolated ucrtbase.dll shutdown access violation. The UI process also logged that shutdown violation. Passing assertions must not be described as clean host exits. Tests ran in X:/5.1.0/bforartists.exe, core 5.2.0 Alpha, build dd23ab17120d, on the recorded Windows/AMD Ryzen 7 5800XT host.

Nine dense/reuse comparisons passed unchanged pin, length, pelvis-orientation and proposal-error gates. Speedups ranged 2.31-2.84x; nominal reuse fits ranged 0.631-9.591 seconds. The default Rigify case remains a responsiveness bottleneck. These are solver timings from the regression run, not cold application startup or animator completion times.

Package: releases/b4artists_ml_v0.5.0.zip; 21 files; 192,507 bytes. SHA-256: 4e9d07ec478d6b1f6201c33be7024baae324f17e377326a2b175256b5998fa93. ZIP integrity, Python syntax and every packaged file's equality to current source passed. The 0.4 ZIP remains untouched. Current tracked and staged Git diffs are empty; ML work remains untracked, with no commits or pushes. The complete checkpoint and per-suite log hashes are in checkpoint-v0.5.0.json.
