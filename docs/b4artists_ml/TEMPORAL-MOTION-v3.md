# Motion capacity, conditioning and kernel learning v3

Status: first nonzero temporal learner to win validation selection, but full quality gates FAILED. Research only; no new runtime model or release promotion. The full product goal remains active and incomplete.

## Evidence-driven question

V2 preserved source bone lengths but learned worse validation motion than its zero-residual FK baseline. This pass first separated representation capacity from prediction quality. A clearly labelled hidden-answer diagnostic fitted the four temporal coefficients directly to ground-truth local motion. Its validation position error is 0.008351 versus the FK baseline's 0.100869; training diagnostic error is 0.016823. Thus this curve representation can express considerably better reconstructions for the tested motions. This is not a deployable predictor, a learned quality result, or a proven optimal lower bound: the diagnostic uses hidden labels and minimizes local-component residual, not the final semantic metric.

Observed-input coverage was measured independently. A 427-feature representation contains initial local pose, relative endpoint rotations, incoming/outgoing angular and root velocities, root displacement, static offsets, context masks and exact timing. It reads only serialized known observations. Validation's nearest compatible training-window standardized RMS distances have median 0.452 and maximum 7.897. These values expose uneven numerical support; they do not establish motion semantics, identity independence or calibrated confidence.

The frozen follow-up compares raw V2 pose inputs against these motion-relative inputs, and linear ridge against nonlinear RBF kernel ridge. There are 24 preregistered fits: two input variants, three linear regularizations, and three kernel widths times three kernel regularizations. No new motion data is downloaded. Normalization, centers, supervised curve targets and learned regression coefficients all use the 23 training clips only. Selection uses the same 6 validation clips; the 3 previously observed development clips are evaluated only after selection is saved.

## Model and boundaries

Kernel ridge is supervised statistical learning, not a neural network. This independent NumPy implementation learns complete 23-joint temporal curve coefficients and decodes them through the existing full-hierarchy FK, preserving source offsets and priority endpoint values. The [official kernel-ridge documentation](https://scikit-learn.org/stable/modules/kernel_ridge.html) describes the nonlinear mapping and regularized closed-form fit that motivate this comparison; scikit-learn is not installed or required, and no external implementation was copied.

The new regression objective fits complete curve coefficients extracted from training labels. Unlike V2's neural objective, it does not directly optimize FK position, velocity or acceleration loss. Those metrics remain strict evaluation gates. The oracle validation diagnostic never enters model fitting or inference. A radial kernel's residual tends toward zero far from training support; returning toward a baseline does not guarantee an appropriate transition, particularly when that baseline ignores useful contextual root motion.

The selected model is `raw_pose_kernel_0.25_10.0`: 637 standardized known-pose features, RBF width 0.25, regularization 10 and 2,154 training-window centers. It produces a nonzero learned correction. Raw-pose features slightly outperform motion-relative features in the selected nonlinear comparison; the explicit motion features improve the linear comparator but do not improve overall selection. This evidence does not justify claiming that velocity inputs are inherently unhelpful.

The JSON report retains the legacy `mlp` comparison slot for the selected candidate because it shares the V2 acceptance evaluator. In this report that slot contains a kernel model, not an MLP. The saved model's `kind` is `kernel`.

## Validation results

Errors are torso-normalized distances and geodesic radians, balanced equally across clip/gap/context cohorts. Derivatives are computed within each window only. Same-input baseline reports are reproduced exactly against frozen V2 before comparisons proceed.

| Method | Position error | Rotation error (rad) |
|---|---:|---:|
| linear | 0.099178 | 0.132492 |
| hermite | 0.110735 | 0.132492 |
| fk_linear | 0.100869 | 0.133288 |
| fk_hermite | 0.122723 | 0.133288 |
| ridge | 0.106125 | 0.140763 |
| raw_pose_linear (selected within family) | 0.106125 | 0.140765 |
| raw_pose_kernel (selected within family) | 0.097331 | 0.129574 |
| motion_relative_linear (selected within family) | 0.104686 | 0.135269 |
| motion_relative_kernel (selected within family) | 0.097803 | 0.129786 |

Selected validation position error is 0.097331, a 1.86% reduction versus world-position linear interpolation. Rotation error is 2.20% lower than the strongest rotation baseline. This is a modest improvement on an already used validation split, below the preregistered 5% position requirement. The worst clip/gap/context group still has 3.17 times its strongest baseline's position error, so the cohort gate fails too.

Observed-development position error is 0.730644, 17.47% worse than its strongest baseline, and velocity is also worse. These clips were observed in prior motion experiments; this is neither fresh confirmation nor evidence of general quality superiority. Root-path prediction on poorly covered motion remains a major gap. No direct Cascadeur comparison or animator visual acceptance is available.

The selected model preserves true source edge lengths to below 8.4e-16 normalized units and priority endpoint positions to below 2.7e-15 in the recorded validation/development evaluations. Near-zero length-error ratios use the existing 1e-12 denominator floor and are not meaningful improvement factors.

## Tests and runtime evidence

- 11 new coverage/kernel tests pass. They cover hidden-label isolation, observation-only inference, suppressed missing-context velocities, rotation-log limits, explicit pair distances, training-only normalization, oracle-only target sensitivity, weighted kernel solution versus direct solve, decay outside support, saved-model equality, and hard endpoint/edge preservation.
- The previous 13 sequence and 14 temporal tests pass too: 38 standalone tests total, all with exit 0.
- Bforartists core 5.2.0 Alpha / NumPy 2.3.4 passes the 11 new tests and a selected nonzero-model inference check. The process then hits the previously observed ucrtbase.dll shutdown access violation, exit 3221225477. Passing assertions and a clean host exit remain separate facts. No real BoneForge/Rigify control-rig application or viewport workflow is verified by this test.
- Fitting/evaluation of all 24 candidates took 36.32 seconds on local CPU with four OpenBLAS threads, Python 3.14.3, NumPy 2.4.4. Selected model file size: 16,561,280 bytes.
- Fresh-process model loading: 78.07 ms. For 33 frames, first inference plus FK: 6.02 ms; warm p50/p95: 5.07/6.37 ms over 100 repeats. Peak process working set: 65,990,656 bytes. These exclude Bforartists, control-rig fitting and viewport rendering.

## Reproduction and source evidence

```powershell
# [PowerShell]
$env:OPENBLAS_NUM_THREADS='4'
python -B tests/test_b4artists_ml_motion_coverage.py
python -B tests/test_b4artists_ml_sequence.py
python -B tests/test_b4artists_ml_temporal.py
python -B -u training/b4artists_ml/train_kernel_motion.py --output kernel_motion_reproduction
```

Use a new output name; existing result directories are rejected. Results live under `training/b4artists_ml/results/kernel_motion_v3/`, with `selection.json`, `report.json`, selected/family model files, host records, inference-benchmark.json and reproducibility.json. The separately labelled capacity audit lives under `results/motion_coverage_v3/`. Source and manifest checksums are recorded before fitting; repeated evaluation is replication, not a new blind experiment.

This pass uses only the existing pinned CMU conversion cache. No raw files, models, dependencies, subscriptions or paid compute are newly downloaded or purchased. Existing provenance and CMU/NSF acknowledgment requirements remain in effect. The direct CMU publisher page was retried on 2026-09-06 and still timed out; this is recorded as unavailable, not as a successful license recheck. The conversion notice and earlier provenance are documented in TEMPORAL-MOTION-v1.md. No new weights are bundled or published.

## Next work without narrowing the product

1. Use the retained cohort and input-support evidence to design a bounded training/augmentation expansion and a genuinely untouched motion evaluation split. Do not reuse old confirmation as fresh proof or broaden a dataset indiscriminately.
2. Address root-context behavior and input ambiguity with controlled experiments while retaining the full articulated predictor, exact priorities and FK constraints. The selected model's small validation gain does not resolve poorly covered development motion.
3. Establish canonical cross-rig motion encoding and test retargeting through actual BoneForge/Rigify rigs and bound meshes. This source-BVH model cannot be advertised as general character-rig compatibility.
4. Deliver a qualifying multi-anchor learned preview workflow with contacts, partial edits, style control, cancellation, editable output, source recovery and save/reload. These requirements are still open, as are balance/COM, gravity, momentum, secondary motion, quadrupeds, the separate connector, production coverage and equivalent Cascadeur/animator comparisons.


## Verified gravity-conditioning gap

The constructed diagnostic `results/motion_coverage_v3/gravity-alias.json` rotates an entire observed motion 90 degrees while keeping a supplied world-gravity direction fixed. Raw pose inputs remain equal within 8.9e-16 and motion-relative inputs within 6.7e-15, while the gravity direction in anchor coordinates changes by 1.414 in Euclidean vector norm. Current normalization therefore erases a distinction required by gravity-aware prediction. This does not establish the cause of every validation regression or measured CMU gravity; the supplied direction is explicitly a fixed reference-up assumption.

The next conditioning change should preserve explicit scene gravity/support context under coordinate transforms, distinguish physical tilt from a change of coordinate system, and test this on real rig adapters. Do not silently assume gravity follows the character's initial pelvis frame. Retain all quality gates and the complete articulated predictor while addressing this gap.

An independent repeat exited 0 and reproduced byte-identical selected and all four family-best model files, with identical validation/development reports. This is reproducibility evidence, not new blind confirmation.
