# Contextual pose completion V1 research checkpoint

Status: research backend verified; full product goal ACTIVE and incomplete. The released add-on remains 0.4.0 with its original limb model. No contextual model is installed or packaged.

## Implemented pipeline

`context_data.py` produces 17 synchronized semantic landmarks: pelvis, spine, chest, neck, head, shoulders, elbows, wrists, hips, knees and ankles. Coordinates use an explicitly supplied pelvis pose and a rest-derived anatomical frame, normalized by torso length. Current pelvis rotation comes from decoded transforms; hidden current torso positions do not define the input frame.

Inputs contain reference geometry, the animator's starting pose, visible target positions and a visibility mask (170 values). The model predicts a 51-value pose residual. Unknown target values are removed before inference, including NaNs. Training never exposes hidden elbows or knees. Starting poses are a neutral reference or strictly earlier sampled motion frames. Three geometry variants preserve segment directions while changing upper/lower limb proportions; these are synthetic stresses, not proof of compatibility with real generated rigs.

`context_network.py` implements an independent NumPy tanh network trained with Adam. No Cascadeur or restricted research implementation/weights were copied. A trained linear model and a controlled own-effector linear ablation provide comparisons. The ablation retains the complete starting pose; it only removes other observed targets when predicting elbows/knees, so it does not isolate all possible sources of body context.

`context_pipeline.complete_pose` loads frozen weights with checksum validation, blends learned influence and projects onto reference segment lengths while copying explicit pins exactly. Failed convergence raises an error without mutating inputs. Influence zero uses geometric projection of the starting pose. The damped least-squares projector improves convergence over the retained initial position-based projector. It enforces lengths and pins only: anatomical angles, twist, balance, collision and effector orientations remain unimplemented.

## Quality evidence and counterevidence

All errors below are mean hidden-joint distances in reference torso-length units, averaged equally across clips. Each method uses the same length/pin projection. Validation projection samples at most 64 examples per clip; confirmation uses every example. These are single-frame reconstruction results, not animation or visual acceptance.

| Set / starting pose | Geometric starting pose | Linear model | Neural model |
|---|---:|---:|---:|
| Validation / neutral | 0.20065 | 0.12603 | 0.10493 |
| Validation / earlier pose | 0.08045 | 0.10186 | 0.09190 |
| Fresh confirmation / neutral | 0.21984 | 0.09676 | 0.10089 |
| Fresh confirmation / earlier pose | 0.13031 | 0.10024 | 0.10088 |

The model and projector were frozen before fetching three subject-number 75 run/jump clips. Both predeclared confirmation modes passed: neutral reconstruction improved by at least 10% over geometric adjustment, prior-pose reconstruction did not deteriorate in aggregate, no clip exceeded its deterioration cap, pins were exact and all tested projected poses converged within 0.1% maximum relative edge-length error. The confirmation set contains only one subject number and is now diagnostic for future design decisions.

The linear model was slightly better on fresh confirmation. On earlier-pose validation, both learned methods were worse than geometric adjustment. This prevents a claim that the neural model consistently preserves animator intent or improves existing poses. A quality-aware selection method or better training must be evaluated without tuning against this confirmation set. The contextual experiment is not a replacement release for the failed V3/V4 models or a demonstration of Cascadeur parity.

## Reproducibility and provenance

The exact V4 training manifest supplies 23 training clips and six validation clips; no confirmation motion values enter training. The model uses 18,561 augmented training examples, 128 hidden units, seed 20260906 and selected epoch 85. Re-running training reproduced both neural and linear weight files byte for byte. The repeat took 21.15 seconds on the measured machine.

Neural weights: `training/b4artists_ml/results/context_pose_mlp_v1.npz`, 109,583 bytes; SHA-256 `919de9c772a521d6531f692b8903d0392fb981bf79896f40a8ff893d746a6f96`. Decompressed model arrays total 116,588 bytes. Code and project-created weights are GPL-2.0-or-later; underlying motion data retains its publisher's terms. The existing CMU/converter provenance and notices in `b4artists_ml/models/MODEL_CARD.md` apply to the source family. No raw motion is redistributed in an add-on.

Five pinned manifests now describe 48 cached clips and 59,385,308 raw bytes, within the established 60 MB cumulative budget. CMU subject numbers do not guarantee different people. No new network downloads were performed during this verification checkpoint.

## Runtime evidence

Twelve contextual tests passed inside Bforartists with zero skips, including actual imported landmarks and pelvis orientation, missing-input isolation, numerical gradient checks, impossible-pin failure, and the frozen callable model. The two imported clips each checked 119 joint samples; maximum position discrepancy was 6.41e-6 source units. All 16 existing learned-model tests also passed in the host, including actual BoneForge/Rigify fixtures and the expanded 48-clip integrity check. Those rig fixtures exercise the released limb workflow; they do not prove contextual whole-body rig support.

Bforartists executable: `X:/5.1.0/bforartists.exe`, core 5.2.0 Alpha, build `dd23ab17120d`, Python 3.13.9, NumPy 2.3.4. CPU: AMD Ryzen 7 5800XT, eight cores / 16 logical processors. Windows 11 build 26200.

A separate host run measured all 468 confirmation examples as individual callable solves: median 6.27 ms, p95 8.79 ms, maximum 31.23 ms, no failures. Model read/check/decode took 6.70 ms; the first solve after imports and data preparation took 6.45 ms. All pins remained exact and maximum length error was 0.000999853.

Host working set rose from 183,369,728 bytes before model load to a sampled maximum of 184,922,112 bytes (increase 1,552,384 bytes). Private commit rose from 256,057,344 to 273,129,472 bytes. These OS measurements include allocator/runtime effects. The process peak includes host and data preparation; the sampled working-set difference is not a precise allocation peak. Rig extraction, control application, dependency graph evaluation, viewport, application cold startup and hardware variants remain unmeasured.

All three host runs completed assertions/measurements and then hit the previously isolated `ucrtbase.dll` shutdown access violation, exit -1073741819 (unsigned 3221225477). Do not report a clean process exit.

## Visual review and next integration

`write_context_preview.py` generates `training/b4artists_ml/cache/context-preview.html`, showing recorded, geometrically adjusted and neural poses with frame/case/view controls. Browser policy blocked opening its local URL, so the artifact has not received rendered visual inspection or animator acceptance. It uses independent single-frame solves; playback does not establish temporal coherence. Keep the derived motion preview in ignored cache.

Next, implement and test a real-rig adapter. Inspect actual evaluated joints and complete parent paths for BoneForge and Rigify basic/default rigs. The canonical 17-edge skeleton is not their bone hierarchy; missing intermediate spine/clavicle joints cannot be treated as rigid bones. Establish reference normalization, control-space kinematics, explicit pelvis/head/pole/orientation semantics and domain checks before writing output. Validate source/mode rollback, pinned evaluated endpoints, lengths and bound-mesh behavior on the actual rigs. Keep learned participation distinct from fallback.

Head/spine application, anatomical limits, contacts, balance/physics, learned temporal motion, secondary motion, quadrupeds, production interactions and the optional connector remain required work. See REQUIREMENTS.md for the full unchanged goal.
