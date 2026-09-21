# Full-hierarchy learned sequence experiment v2

Status: structural improvement verified; learned quality gates FAILED. Research only. Release 0.10.0 and the overall product scope are unchanged; the goal remains active and incomplete.

## Change from v1

V1 predicted independent world positions and orientations, allowing stretching. V2 retains all 23 source joints needed to reconstruct the 17 semantic joints, including intermediate hip, shoulder, neck and lower-back joints. It predicts root translation and local 6D rotations and reconstructs positions/world rotations through differentiable forward kinematics. Offsets are fixed, so all retained source edges preserve their lengths. This is a property of the decoder, not a learned quality improvement or a guarantee about a future control-rig adapter.

The network receives 637 features: four observed local poses, static normalized offsets, context masks, duration and sample interval. A 128-unit tanh layer produces four coefficients for each of 141 pose components. Evaluating the coefficients with duration-squared, endpoint-zero Legendre basis functions produces a smooth, query-order-independent curve. Unlike v1's envelope, these corrections may learn nonzero endpoint derivatives. Endpoint values remain fixed; derivative continuity between separately authored windows is not guaranteed.

Training differentiates through rotation orthonormalization and the complete FK hierarchy. The whole-window objective includes semantic positions, world rotation matrices, velocity error and acceleration error, with analytic gradients verified by finite differences. Root translation/orientation remain predicted hidden variables, expressed in the known start-anchor frame. Unknown poses never supply normalization or model features. Non-root translation channels are explicitly unsupported rather than silently discarded.

The model uses the existing pinned 23 training and 6 validation clips, with 2,154 training windows and 288 validation windows. Overlapping windows and context variants do not create independent clips. The 3 previously observed confirmation clips now form 144 exploratory development windows; they are not called fresh confirmation. Source hashes and the complete protocol were frozen before training. No new data, weights, packages, services or paid compute were obtained.

## Evaluation and outcome

Baselines are world-position linear/SLERP, world-position Hermite/SLERP, full-hierarchy linear-root/local-SLERP, full-hierarchy Hermite-root/local-SLERP, and fitted ridge curve coefficients. Neural selection includes a zero-residual epoch-0 baseline. Existing position, rotation, velocity, semantic-length and cohort gates are retained; acceleration and true-edge preservation gates were added. Comparisons use the strongest baseline for each metric. Ratios use a 1e-12 denominator floor, so ratios between near-zero length errors are numerical-floor artifacts, not meaningful improvement factors.

Training ran 20 epochs. Epoch 0 won validation selection: the selected `mlp.npz` is exactly the unmodified FK interpolation baseline, not learned motion improvement. Actual trained weights remain in `last_trained.npz`, and their separate diagnostic results are retained.

| Method / split | Position error | Rotation error (rad) | Velocity error | Acceleration error |
|---|---:|---:|---:|---:|
| linear / validation | 0.099178 | 0.132492 | 0.619511 | 8.304515 |
| hermite / validation | 0.110735 | 0.132492 | 0.611045 | 8.090119 |
| fk_linear / validation | 0.100869 | 0.133288 | 0.624428 | 8.306889 |
| fk_hermite / validation | 0.122723 | 0.133288 | 0.677757 | 8.495543 |
| ridge / validation | 0.106125 | 0.140763 | 0.646249 | 8.483590 |
| mlp / validation | 0.100869 | 0.133288 | 0.624428 | 8.306889 |
| FK baseline / training | 0.152030 | 0.190339 | 1.097267 | 16.605281 |
| last trained / training | 0.095509 | 0.149693 | 0.834683 | 15.037748 |
| last trained / validation | 0.142666 | 0.171699 | 0.830845 | 10.216386 |

The final trained model reduces training position error from 0.152030 to 0.095509 (37.2%) but increases validation error from the FK baseline's 0.100869 to 0.142666 (41.4%). These observations support a generalization failure in this experiment. They do not prove that more data alone, or a particular next architecture, will solve it. Training longer is not supported by the validation trajectory.

The selected zero-residual output still fails the requested overall motion-quality gates: its validation position error is 1.7% worse than world-position linear interpolation and individual cohorts regress against their strongest baselines. On observed-development clips it is 17.5% worse than the strongest positional baseline. No selected or final-trained weights are promoted into the add-on.

True-edge length error remains below 1.4e-15 normalized units for the final trained model's tested training/validation windows. The semantic segment lengths in this pinned hierarchy are also preserved to numerical precision. Priority endpoint reconstruction error is below 3.6e-15 normalized distance. This resolves the first experiment's stretching mechanism in the research representation while leaving motion plausibility, style, contacts and real-rig application unproven.

## Tests, host and performance

13 new tests cover full-chain source reconstruction, fixed edge lengths under perturbed learned rotations, rotation/FK gradients, complete sequence-loss/network gradients, observed-input isolation, absent-context isolation, local-baseline endpoints, continuous queries, duration scaling, global rigid/scale invariance, rejection of animated non-root translations, and strongest-baseline gates. These and the prior 14 temporal tests pass in standalone Python with exit 0.

The 13 new tests and a nonzero final-trained-model inference check pass in Bforartists core 5.2.0 Alpha, NumPy 2.3.4. The tested host then hits the previously observed ucrtbase.dll shutdown access violation, actual exit 3221225477. This is not a clean host exit. No BoneForge/Rigify control application, bound mesh, action preview or animator evaluation is established by these research tests.

Training and all recorded split evaluations took 38.22 seconds using four OpenBLAS threads, Python 3.14.3 and NumPy 2.4.4. The network has 154,420 parameters. A fresh standalone inference process using the actual nonzero trained weights measured:

- Model loading: 14.25 ms; source BVH decode: 18.36 ms; observed feature construction: 1.31 ms.
- 33-frame curve inference plus 23-joint FK: first call 0.595 ms; warm p50/p95 0.440/0.561 ms over 100 repeats.
- Peak process working set: 35,590,144 bytes, including Python/NumPy, the model and one motion clip. This excludes Bforartists, control-rig fitting and viewport rendering.

## Reproduction and provenance

All experiment artifacts live under `training/b4artists_ml/results/sequence_motion_v2/`. `selection.json` records source/protocol/model hashes and topology; `report.json` records every cohort and gate; `diagnostics.json` separates final-trained and selected-baseline behavior; `host-validation.json` and `host-process.json` separate passing assertions from the crashing host exit. `reproducibility.json` confirms a fresh repeat exited 0 with byte-identical selected, ridge and nonzero final-trained weights, plus identical validation and observed-development metrics.

```powershell
# [PowerShell]
$env:OPENBLAS_NUM_THREADS='4'
python -B tests/test_b4artists_ml_sequence.py
python -B tests/test_b4artists_ml_temporal.py
python -B -u training/b4artists_ml/train_sequence_motion.py --output sequence_motion_reproduction
```

Use a new output name; existing results are preserved by rejecting overwrite. The source/data provenance and distribution caveats in TEMPORAL-MOTION-v1.md still apply. In particular, the [pinned CMU conversion notice](https://raw.githubusercontent.com/una-dinosauria/cmu-mocap/09a07f54f3bbb58797325f009282d0b2048a2871/READMEFIRST.txt) documents initialization and conversion limitations. Existing CMU/NSF acknowledgment must be retained. No new model distribution has been approved or performed. The curve model and NumPy analytic gradients are independent implementations; no Cascadeur code or weights are used.

## Next work toward the actual product

The decoder and temporal objective now provide a tested foundation for further learning. Before another candidate is promoted:

1. Audit motion coverage and conditioning against the failing validation cohorts. Develop a bounded, documented corpus/augmentation strategy and a genuinely untouched evaluation split; avoid repeatedly treating the already observed clips as independent confirmation.
2. Evaluate motion-relative conditioning and appropriate sequence capacity against this frozen experiment. Preserve short/static transitions and useful local motion while learning larger transitions. Separate training fit, domain coverage and ambiguous multi-modal motion rather than assuming a larger network is sufficient.
3. Retain the tested full hierarchy, FK gradients, exact endpoint controls and strong baselines. Investigate temporal representation limits and contextual derivative behavior with controlled ablations.
4. Integrate a qualifying learned backend into actual multi-anchor Bforartists workflows with partial edits, contacts, rig/mesh projection, cancellation, source recovery, save/reload and editable output. A fast research decoder is not a finished animation tool.

Balance/COM, gravity, momentum, secondary motion, humanoid production coverage, quadrupeds, the separate entitlement-aware connector and equivalent Cascadeur/animator comparisons remain required. No parity, superiority or production-readiness claim is made.
