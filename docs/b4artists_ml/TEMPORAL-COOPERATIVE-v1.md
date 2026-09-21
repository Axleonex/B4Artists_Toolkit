> Performance follow-up: [selective restoration and cooperative observations](TEMPORAL-SCHEDULING-PERFORMANCE-v1.md) adds 28 passing native checks and loaded-host timing comparisons. The original evidence below remains the baseline.

# Cooperative temporal generation: research v1

The temporal research path can now pause during observation/proposal setup and existing solver checkpoints while restoring the original visible pose and playhead. A lifecycle-owned iterator cancels before save, load, undo or redo. Closing at a pause preserves newer pose/playhead edits; changed source curves, anchors, timing, transforms or rig controls reject before the next solve step. Private evaluation objects are removed before saving. Candidate publication still uses the existing workflow only after all samples pass validation.

This is a reusable research backend, not an installed operator or a qualified learned model. Callers own module unregister; product registration, disable handling and current-window interaction still require integration. Ordinary reference providers remain procedural. The original frozen v26 experiment sources, models and data, and add-on and ZIP 0.17.5 are unchanged.

## Evidence

`training/b4artists_ml/results/temporal-cooperative-verification-v1.json` consolidates 25 passing native tests: 10 cooperative/lifecycle methods and 15 existing action/recovery methods through the new generator. Eleven reference comparisons cover all eight current rig fixtures and three context-enabled cases. Generated transform components retain the 2e-6 absolute comparison tolerance; authored priority samples are exact. Tests inspect visible source pose, playhead, scene objects and source keys at pauses, then exact global resource inventories after cleanup. They cover explicit cancellation, changed-input rejection, newer-edit preservation, concurrent ownership rejection, save/reopen and loading during a paused solve, editable preview, Keep/Discard, retained source recovery and failed later-frame rollback.

The initial failed tests are retained. They compared paused global inventories including a legitimate private evaluator and used unnormalized quaternion self-dots. Corrected tests inspect the visible scene during pauses, preserve exact global cleanup assertions, and compare quaternion components at the existing tolerance. A subsequent save test reached successful cleanup but used a host library operation forbidden on the current file; the final test actually reopens the file and additionally cancels a paused job during load. Implementation and test snapshots preserve each stage.

## Remaining limits

The largest measured checkpoint is 320.22 ms. Default Rigify reaches 231.01 ms without context and 320.22 ms with context. These are diagnostic samples while two corpus-training jobs are active, not a controlled performance comparison. They exceed the existing 50 ms responsiveness target. Known-pose sampling, frame/context restoration, source validation, session preparation and final action publication still need measured optimization; cooperative scheduling alone does not qualify responsiveness.

The host retains its separately reproduced shutdown access violation after assertions. The code evaluator also returned a process access-violation status with no review output; author inspection and deterministic tests do not count as independent review. Prior 345 native runtime cases and four packaged offline cases remain applicable by unchanged byte hashes; they were not rerun here.

Learned motion quality, automatic temporal contacts, intent/style and partial-body integration, full physics/refinement, broader rigs/quadrupeds, the optional connector, independent animator assessment and equivalent Cascadeur comparison remain incomplete. The same full goal, 50-evaluation ceiling and September 9 at 19:24:05 UTC deadline remain in force.
