# B4Artists Machine Learning 0.2 validation

Historical record. Current checkpoint: [0.3 validation](VALIDATION-0.3.md).
The ZIP passed all 49 automated tests with zero host skips: 18 posing tests plus the existing 31 interpolation/mapping/lifecycle tests. Plain Python separately passed 11 mathematical/mapping tests and correctly skipped 38 host-dependent tests. The actual full Rigify generator was used; fast substitute fixtures were disabled. See `tests/test_b4artists_ml_posing.py` and `posing-benchmark-v0.2.0.json`.

Covered workflows include BoneForge FK, Rigify basic/full generated FK, basic/full metarig FK, rigid Rigify IK, positional poles, world rotation/translation/uniform scale, reach clamping, pelvis displacement with pins, target strength, selective pins, repeated solves, rollback after partial mutation, source-action preservation through anchor/candidate use, helper selection, bound-mesh evaluation, guarded incompatible rigs, undo/redo and saving/reopening a pending session.

BoneForge was built from the adjacent reference checkout using its actual builder. Rigify fixtures came from the host's bundled Rigify. Neither is imported by the distributed add-on. IK fixtures explicitly disable native IK constraint stretch; unmodified default IK is not reported as supported. Default IK rejection and unchanged pose data were tested. Native constraints and IK/FK properties are never altered by the add-on.

## Accuracy and timing

There are 15 recorded scenario samples in the JSON. Reachable targets had maximum normalized position error below 2.70e-7 of the head-tail to ankle-midpoint reference span. FK BoneForge pelvis lowering placed the initially straight arms beyond their reach by about 0.00332 world units; this was correctly clamped and reported, while reachable feet remained pinned. It is not counted as accurate preservation of an unreachable hand pin.

Sample solve times range from approximately 27 to 132 ms including scene evaluation. Multiple generated test rigs coexist in that scene. These are individual synchronous solve samples, not viewport FPS, statistically established cold/warm distributions, or interactive usability measurements. CPU identifier: AMD64 Family 25 Model 33 Stepping 2, AuthenticAMD. No learned-model inference or direct Cascadeur benchmark was run. Peak memory and manual visual assessment are still missing.

## Runtime qualification

Executable: X:/5.1.0/bforartists.exe; host core 5.2.0 Alpha, build dd23ab17120d. The previously isolated host shutdown access violation still occurs after successful assertions, including in baseline processes without this add-on. `B4ML_POSING_RESULT: PASS` establishes assertion results; the process exit is not clean. The parent log runner's successful exit is not being substituted for the child process result.

## Package

Version 0.2.0 experimental; 27,329 bytes. SHA-256: `585f8ef8a10d1b33b603f92edb3c42609d6783f49c2ef2ab816024c55b9273c3`. The ZIP contains only source, mapping data, license and attribution. It includes no weights, external runtime, assets, network client or embedded credential. All 12 archive members passed ZIP integrity checks and byte-for-byte comparison with the source set. Eight Python source/test files passed parsing and whitespace checks. The old mesh-selection test fixture was updated to include the active view layer required by the new selection boundary.

## Scope and remaining work

The full product goal and phase 2 remain incomplete. See REQUIREMENTS.md for every requirement and ROADMAP.md for next steps. This checkpoint implements an end-to-end geometric subset and is not AutoPosing, learned animation or physics parity.

The mandatory router preflight reported OMP READY and a missing remote X: workspace, without execution lanes or a remote patch. Native continuation used the canonical recovery policy. Changed scope: b4artists_ml, its two test modules, docs/b4artists_ml and the 0.2 ZIP. No commits, pushes, installed addon modifications, paid services or model/dataset downloads.
