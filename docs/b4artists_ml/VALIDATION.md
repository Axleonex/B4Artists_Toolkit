# B4Artists Machine Learning 0.1 validation

Current 0.31.0 evidence: PAW-SUGGESTIONS-v0.31.0.md records 17 focused source tests and 10 exact-package offline tests, including the reproduced and repaired early-input race. A later frozen-source run passed 487 tests across all 53 current factory-startup suites with no failures, errors or skips and one consistent runtime hash set. See `training/b4artists_ml/results/full-regression-031-v1.json`. Human/Cascadeur comparisons and clean Alpha-host shutdown remain unqualified.

Current experimental 0.32.0 evidence: CONTACT-REVIEW-v1.md records 30 passing affected tests for bulk/fractional contact review plus a passing two-family foreground Undo/Redo journey. CLEANUP-v1.md records five focused native cleanup workflows, 110 passing affected tests with one runtime hash set, and a passing real-window cancellation/Undo/Redo/Keep/source-recovery journey. The frozen 0.32.0 source passes 495 tests across 55 suites, and its exact archive passes 18 offline package tests with byte-for-byte source matching. See `training/b4artists_ml/results/full-regression-032-v1.json` and `CLEANUP-v0.32.0.md`.

Development 0.33 source evidence: JOINT-LIMIT-PRESETS-v1.md records the opt-in semantic limit preset. CHEST-TARGET-v1.md, CHEST-ORIENTATION-v1.md and NECK-TARGET-v1.md record optional semantic Chest/Neck position and evaluated rotation. POLE-ALIGN-v1.md, POLE-FLIP-v1.md and POLE-DISTANCE-v1.md record current/opposite-bend helper placement, circular in-front helpers and normalized radial distance. TARGET-RESET-v1.md, TARGET-MIRROR-v1.md, RIG-DIAGNOSTICS-v1.md and POSE-REUSE-v1.md record reset, mirroring, diagnostics and same-armature reuse. POSE-ASSET-v1.md records the scene-local cross-rig Semantic Pose Asset. MAPPING-CORRECTIONS-v1.md records 11/11 focused tests across BoneForge, generated Rigify Basic/Default and imported Unity Humanoid adapters, 138/138 affected tests across 11 suites with one runtime source hash set, and a passing generated-Rigify-Default foreground Apply/Undo/Redo/Clear/Solve/Escape/Keep journey. The 0.32.0 package remains unchanged; no 0.33 exact-package or full-regression claim is made yet.

Development 0.34 source evidence: CONTACT-INTERVAL-EDIT-v1.md records 6/6 focused tests across generated Rigify Default, BoneForge and generated Rigify cat contacts plus save/reload and a real-window fractional editing journey. PROP-HOLDS-v1.md records explicit humanoid hand holds on directly animated rigid props. MOVING-PLATFORMS-v1.md records humanoid foot holds on directly animated rigid planar meshes, Blender concave-mesh tessellation, a complete 706-bone generated Rigify Default solve, immutable serialized metadata, save/reload, rollback, and a real-window Bind/Clear journey. CONTACT-VISUALIZATION-v1.md records 6/6 focused and 90/90 affected tests on one final source hash set, family-aware humanoid/generated-quadruped 3D overlays, exact phase/influence, four playhead-only boundaries, save/reload, final serial-review PASS, and passing real-window evidence. No 0.34 package or milestone-wide regression claim is made yet.

Development 0.35 source evidence: QUADRUPED-HEAD-v1.md records the semantic Head target. QUADRUPED-SPINE-FOLLOW-v1.md records schema-3 distribution through semantic Chest and Neck controls. QUADRUPED-POLES-v1.md records opt-in schema-4 fore/hind Pole Targets. QUADRUPED-POLE-MATCH-v1.md records current-frame **Match + Enable All Poles** through generated Rigify's pose-preserving operator with 8/8 focused and 93/93 affected tests on its 43-file runtime set. QUADRUPED-GAIT-PHASES-v1.md records procedural support-phase review from animator-accepted contacts with 5/5 focused and 98/98 affected tests across 13 suites on a 44-file runtime set. QUADRUPED-TARGET-RESET-v1.md records schema-1-4 per-target preview-start Reset with 9/9 focused and 107/107 affected tests across 14 suites. QUADRUPED-TARGET-MIRROR-v1.md records bidirectional paw/pole request mirroring with 8/8 focused and 115/115 affected tests across 15 suites. QUADRUPED-POSE-ASSET-v1.md records normalized Body-frame request reuse across generated Rigify cat, horse, and wolf with 7/7 focused and 122/122 affected tests across 16 suites. QUADRUPED-POLE-ALIGN-v1.md records schema-4 current-bend alignment with 6/6 focused and 128/128 affected tests across 17 suites. QUADRUPED-POLE-CONTROLS-v1.md records per-pole Flip Side and normalized Set Distance with 8/8 focused and 136/136 affected tests across 18 suites on one frozen 44-file runtime set. Cat/horse/wolf limb oracles, strict hostile scale/range handling, helper locks, save/reload, complete Action/slot/pose/mode preservation, stale-solve invalidation, busy and dependency-handler rejection, parent-space transform rollback, foreground Flip/Distance/Undo/Redo evidence, and final serial-review PASS are covered. Learned gait recognition/generation, imported/custom adapters, learned quadruped motion, packaging, milestone-wide validation, human review, and Cascadeur comparison remain open. Every Bforartists subprocess completed assertions before a known non-clean shutdown path; clean process exit is not claimed.

Development 0.36 source evidence: TIMING-CONTROLS-v1.md records Uniform, Ease In / Out, Ease In and Ease Out plus a bounded global Breakdown Bias. TRANSITION-TIMING-v1.md records destination-owned per-transition overrides, global fallback, projection separation, hostile-data bounds, recapture/reuse semantics, and foreground native Undo/Redo. TRANSITION-WINDOW-v1.md records normalized Departure/Arrival holds, a 10% active-motion floor, legacy schema upgrade, and first-anchor normalization after removal or earlier insertion. BREAKDOWN-POSE-v1.md records full-body and selected-control editable priority-pose insertion, exact effective-timing preservation for untouched controls, rotation-mode storage, save/reload, and foreground dialog/native Undo/Redo. TRANSITION-TIMING-TRANSFER-v1.md records rig-local Copy/Paste, stable global snapshots, destination-only mutation, hostile clipboard bounds, save/reload, and Whole-body rejection. The newest focused suite passes 6/6, and the affected regression passes 176/176 across 23 suites on one frozen 44-file runtime set. The foreground journey verifies visible Copy/Paste controls, frame 11 to frame 21 transfer, native Undo/Redo, identical interval behavior, and bounded source Action structure recovery. No complete-Action-state, 0.36 package, learned timing, independent usability, or Cascadeur-comparison claim is made.

Historical record. Current status: REQUIREMENTS.md, SECONDARY-CHAIN-v0.26.0.md, SECONDARY-WORLD-DYNAMICS-v0.25.0.md and HUMANOID-REVIEW-AND-CORRECTION-v13.md. The original 0.1 evidence below remains historical.

## Result

All 31 tests in `tests/test_b4artists_ml.py` passed in Bforartists when loading the add-on directly from `releases/b4artists_ml_v0.1.0.zip`: 9 kernel/mapping checks and 22 runtime checks. No runtime skips in the packaged run. Plain Python runs the 9 kernel checks and explicitly skips the 22 tests requiring the host.

The existing combined Ghost Tool / Anim Assist smoke script also passed with the packaged B4Artists ML add-on registered. The import path printed by that process confirms execution from the ZIP.

## What was exercised

- Bforartists host detection and simulated standard-Blender notice-only registration.

- BoneForge FK/IK vs deform/mechanism names; exact upstream map semantics; MMD Japanese and VRoid mappings.

- Actual Rigify Basic/basic_human and default human metarig creation, real rig generation, capture, candidate generation, expected midpoint movement and discard.

- Original action key coordinates, handles, interpolation metadata and original slot preserved after preview/discard.

- Keep preserves the source action using a fake user and retains a separate candidate action.

- New animation with no original action, failed generation after candidate creation, fake-user candidate cleanup and independent armature state.

- Multiple pose anchors, locked axes, changed locks, NaN input, frame budget, changing IK/FK properties, NLA/driver rejection and unexpected active-action changes.

- Quaternion sign continuity and Euler wrap across 180 degrees.

- Saving and reopening a .blend containing a pending candidate, then restoring the original action.

- UI operator invocation and register/unregister lifecycle. This is not a manual visual UI review.

## Timing samples

The packaged run generated an 11-frame candidate for 32 mapped body controls in 45.48 ms on the basic Rigify human and 110.50 ms on the full default human. Earlier source runs measured 38.04 ms and 82.20 ms respectively. These are single-run wall-clock samples including local candidate creation and host evaluation, not a statistically established performance guarantee or viewport FPS. Rigify's own rig generation time is excluded from these preview timings.

## Runtime limitation

Test executable: `X:/5.1.0/bforartists.exe`, distributed as Bforartists 5.1.0, with Blender 5.2.0 Alpha core, hash dd23ab17120d. This installed build has the previously isolated ucrtbase.dll shutdown crash even without an add-on. Tests print `B4ML_RESULT: PASS` and finish assertions before that crash. Exit code is not being described as clean.

Other Bforartists versions, actual production BoneForge/MMD/VRM characters, complex constrained rigs, manual mouse/keyboard use, GPU drawing and natural-motion quality remain unverified. No AutoPosing, physics or learned-motion parity claim is made.

## Package

- Version: 0.1.0 (experimental)

- Files: 11

- Size: 20,799 bytes

- SHA-256: cb05db7416c48a94bf6e17a86773e75e4c45f0b59a607fe7b72a4a0a76017134

- ZIP integrity and every packaged file's bytes checked against source.

- The four bundled BoneForge mapping tables match the GitHub blob hashes read from the upstream repository.

- Source syntax and new-file trailing whitespace checked. Existing tracked source files remain unchanged.

## Execution record

Scope: `b4artists_ml`, `tests/test_b4artists_ml.py`, `docs/b4artists_ml`, and `releases/b4artists_ml_v0.1.0.zip`. The mandatory coding-router preflight ran through the approved remote execution route. It reported OMP READY and workspace BLOCKED; that executor does not expose this repository's local X: workspace. No execution lanes were emitted and no remote patch was applied. Work continued within scope under the canonical automatic native continuation policy for recoverable infrastructure failures.

One file-write approval review timed out. Its permitted retry succeeded; no task work remains blocked by that timeout.

No commits, pushes, external publication, paid APIs, trained weights or dataset downloads. No existing add-on source, installed add-on copy, or saved application preferences were updated. Rigify was enabled only inside disposable factory-startup test processes.

## Prospective Cascadeur comparison validation

`check_cascadeur_comparison_protocol_v1.py` passes and writes `results/cascadeur-comparison-protocol-validation-v1.json`. It binds the comparison to the exact procedural v12 aggregate SHA-256 `25e4284d5490263014975d6e4885fc627a5cb9d426e640143228645b954edb95` and protocol SHA-256 `18a1d76a3836aa852d00a6c0bf904ea1a837b763a9ecae6bb6c847913aa311e4`. The frozen comparison protocol SHA-256 is `5fedbc2cef2f6048e13e57622e9e44396d1623890ce12477e13892ac69632a4e`.

This validates protocol completeness and claim boundaries only. Results are absent; parity, superiority and full-goal completion remain false.

## 0.36.0 package consolidation

The installable local package `releases/b4artists_ml_v0.36.0.zip` consolidates the procedural workflow surface through Breakdown Pose and Transition Timing Transfer. The frozen 54-member distributable passed 1,017 source tests across 87 curated suites and 209 exact-package feature tests across 32 suites in eight fresh Bforartists processes, with zero skips. Foreground Breakdown Pose and timing-transfer journeys pass on the exact runtime. The package is ready for local testing. Learned temporal generation, independent animator usability, clean host shutdown and Cascadeur parity remain unqualified; the full goal remains active. See `RELEASE-v0.36.0.md` and `package-test-v0.36.0.json`.
