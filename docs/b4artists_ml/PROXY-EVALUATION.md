# Whole-body evaluation optimization: 0.5.1

The full goal remains ACTIVE and incomplete. This milestone reduces host evaluation work for the existing contextual pose objective. It adds no training data, model weights, pose-quality claim or physics capability.

## Architecture and correctness

For eligible rigs with at least 128 bones, the solver builds a temporary copied armature in a private scene. A conservative dependency traversal retains required landmarks, writable controls, measured bone lengths, parents, constraint targets, IK chains (including ancestor writes), B-bone handles and object/armature driver dependencies. Unneeded bones, constraints and drivers are removed only from the copy. Source actions, meshes, bones and constraints are not edited by this optimization.

The copy keeps the source frame/subframe and frame rate. Driver targets that refer to the source rig or armature are remapped to their copies. External constraints, parented rigs, opaque/self/context-dependent drivers and unsupported dependencies use the full-rig path in automatic mode. The copy must match source matrices at setup within 2e-5; a mismatch removes it before full-rig fallback. These guards are conservative eligibility rules, not general certification of arbitrary custom rigs.

Finite-difference probes run in the copy. Cooperative checkpoints apply only the accepted iterate to the visible rig. Final output is applied and verified on the original rig using the existing pin, length and pelvis-orientation gates, with authored head/hand/foot orientations retained. Failure or iterator closure restores the preceding preview. Save-time cancellation removes the temporary scene before serialization. Source Object/Pose Mode and active scene/selection are preserved during private Edit Mode construction.

The explicit host and proxy backends remain available for differential tests. Automatic mode keeps the original path for small rigs where setup overhead offers little benefit. Continuous live posing is still unfinished.

## Experiment history

The first conservative attempt rejected Rigify's armature-data B-bone drivers; its failure is retained in proxy-evaluation-v1.json and the matching log. The next iteration included those dependencies and matched full matrices, but muting constraints without removing unused bones gave limited benefit. A private scene with dependency-closed bone removal produced exact measured matrices over 125 randomized poses on five real rigs.

Complete solves on transformed BoneForge, Rigify basic/default and basic/default metarigs then matched full-rig joint coordinates exactly in the tested cases, with unchanged pin and proposal-error gates. The recorded pre-package default Rigify solve fell from about 7.2 seconds to 1.6-1.7 seconds, including copy setup. Small rig timings remain noisy and do not establish universal speedups.

The first frame-driver fixture accidentally introduced a descendant-to-ancestor cycle and failed differential comparison. Its failed record is retained. The corrected acyclic fixture verifies an actual frame-driven constraint at frame 8.5 without loosening tolerances. A separate injected baseline mismatch verifies that automatic mode discards an incompatible copy and falls back.

## Validation scope

Dedicated tests cover random full matrices, complete transformed-rig solves, generator-close cleanup, source Pose Mode, external-dependency fallback, injected failure rollback, save/reload during a proxy-backed preview, frame-dependent constraints and baseline-mismatch fallback. The packaged workflow and actual UI event-loop tests remain required release gates. See checkpoint-v0.5.1.json for final counts, paths, hashes and host exit status.

Historical files are not overwritten: each experiment result has its own name and log. The original experiment JSON files were recovered from their original PROXY_RESULT log records after correcting a result-path bug in the test runner. Existing 0.5 binaries and checkpoint evidence remain available.

## Remaining requirements

This changes evaluation cost, not learned quality. Prior-pose regressions, anatomical/pole/orientation constraints, balance and contacts, learned temporal motion, gravity/COM/momentum, secondary motion, quadrupeds, imported/production rigs, the optional connector and equivalent Cascadeur/animator comparisons remain open. Next prioritize authored pole/orientation and anatomical constraints alongside further responsiveness work; do not treat this performance checkpoint as complete animation quality.

## Final packaged evidence

104 host tests passed with zero skips: 93 from the ZIP, 10 source adapter regressions, and one additional default-Rigify progress measurement test. The 12 unchanged contextual training/data tests were not rerun for this runtime-only optimization. All eight background processes passed assertions and then hit the previously isolated ucrtbase.dll shutdown access violation (-1073741819 / 3221225477). The actual UI process also logged the shutdown violation; these are not clean host exits.

The final packaged UI explicitly exercised proxy-backed default Rigify solving, Escape cancellation, undo/redo and keeping an anchor, checking that temporary scenes were absent after terminal operations. Its rendered panel and rig fixture screenshot were inspected. This is not animator visual-quality acceptance.

| Transformed fixture | Full rig ms | Proxy ms | Maximum joint difference |
|---|---:|---:|---:|
| boneforge | 687.06 | 710.21 | 0 |
| rigify_basic | 2147.81 | 1473.11 | 0 |
| rigify_default | 6366.46 | 1710.87 | 0 |
| metarig_basic | 552.23 | 551.79 | 0 |
| metarig_default | 1032.10 | 566.54 | 0 |

Default Rigify cooperative measurements: 150 checkpoints; median 28.69 ms, p95 34.70 ms, maximum 189.60 ms. The longest checkpoint remains a noticeable pause; the first checkpoint also includes copy setup. Synchronous solve 1905.69 ms; cooperative solve 4385.58 ms; identical final joint coordinates. These are local measurements on the existing Windows/AMD Ryzen 7 5800XT host (Bforartists core 5.2.0 Alpha, dd23ab17120d), not hardware-wide guarantees.

Package: releases\b4artists_ml_v0.5.1.zip; 22 files; 195,220 bytes; SHA-256 9c1cec4df70fd7df0832467817222828306b837536a784b6fdf56b17f2f7d2d8. ZIP integrity, syntax and source equality passed. Weights and prior packages are unchanged. No tracked Ghost/Anim Assist changes, commits or pushes.

The required router again could not access the remote /mnt/x workspace and emitted no lane, fingerprint or patch. Local work continued under the canonical recoverable infrastructure policy within this authorized runtime, test, documentation and packaging milestone.
