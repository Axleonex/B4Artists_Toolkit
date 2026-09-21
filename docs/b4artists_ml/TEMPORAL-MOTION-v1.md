# Temporal motion research v1

Status: failed quality gates; research weights retained, no runtime or release promotion. The full product goal remains active and incomplete. Existing experimental release 0.10.0 is unchanged.

## Implemented experiment

An independently implemented NumPy temporal query MLP predicts residual positions and 6D orientations for 17 joints, including the hidden pelvis trajectory. Four observed poses (two anchors and optional immediately outside context), a static rest skeleton, masks, exact duration, sample interval and query time form 668 inputs. One 128-unit tanh layer predicts 153 residual values. The output is added to a linear/SLERP or positional Hermite/SLERP baseline with envelope `(4*t*(1-t))**2`. This preserves both endpoint values and the correction's zero endpoint derivative; it does not guarantee cross-window velocity continuity or rigid segment lengths.

All poses in a window use one coordinate frame defined by the known start anchor and static rest reference. No hidden pelvis coordinate system enters inference. Artificial T-pose frame zero is used only as the static rest reference and excluded from motion labels/context. Cached motion is sampled at approximately 30 fps with exact source frame IDs and effective dt retained. Gaps are 8, 16 and 32 samples (about 0.27, 0.53 and 1.07 seconds).

The pre-existing protocol was frozen before this run. Training uses 23 complete clips and 37,334 interior queries. Validation uses 6 clips / 5,664 queries including endpoints; confirmation uses 3 clips / 2,832 queries including endpoints. Files and complete clip identities cannot overlap across splits. These are clip-disjoint splits, not subject-disjoint splits. Confirmation motions were previously examined during pose research and are not newly blind data. Inputs do not include inferred or oracle contact labels, partial-body masks, style labels or multiple interior priority poses yet.

Training weights balance clip, gap and context cohorts. Statistics are fitted to training inputs only. Neural training minimizes position/6D residual loss; it currently has no explicit velocity, acceleration or kinematic-consistency objective. Ridge regression receives the same features and endpoint envelope. Model selection uses only validation position error plus 0.1 times rotation error. Confirmation labels are loaded after selection.json and selected weights are written. The saved neural model is epoch 1; later training lowered training loss while worsening validation. Ridge selected regularization 0.1.

## Results

Position, root and linear derivatives use torso-normalized distance units. Rotation is geodesic radians. Length is mean relative error against actual hidden semantic segment lengths. Each window is scored separately, then windows are averaged within clip/gap/context cohorts and cohorts are averaged equally. Derivatives never connect unrelated windows. Endpoint checks are maxima rather than averages.

| Split / model | Position error | Rotation error | Relative length error | Velocity error |
|---|---:|---:|---:|---:|
| validation / linear | 0.099178 | 0.132492 | 0.013431 | 0.619511 |
| validation / hermite | 0.110735 | 0.132492 | 0.020168 | 0.611045 |
| validation / ridge | 0.144420 | 0.161245 | 0.040116 | 0.930345 |
| validation / mlp | 0.156458 | 0.156643 | 0.047474 | 1.024370 |
| confirmation / linear | 0.727894 | 0.368793 | 0.024482 | 5.349382 |
| confirmation / hermite | 0.626986 | 0.368793 | 0.054272 | 4.871334 |
| confirmation / ridge | 0.630180 | 0.376193 | 0.071305 | 4.939953 |
| confirmation / mlp | 0.642664 | 0.385287 | 0.079411 | 5.070974 |

The MLP fails both validation and confirmation gates. Its validation position error is 57.8% worse than linear interpolation; its relative length error is 3.53 times the strongest baseline. Confirmation position error is 2.50% worse than Hermite, and length error is 3.24 times the strongest baseline. Maximum endpoint position error is zero and endpoint rotation matrix error is below 1.1e-15. No degenerate 6D output was encountered in these evaluations.

Diagnostics show that training position error improves from 0.136906 (Hermite) to 0.122015 (MLP), while validation worsens. Short contextual gaps are particularly harmed: gap-8 validation position error is 0.010881 for Hermite versus 0.084921 for the MLP. At gap 32, Hermite itself overshoots: 0.304060 versus 0.172376 for linear interpolation in the context-enabled cohort. Thus the failure includes generalization, baseline choice and unconstrained skeletal output; simply training longer or renaming the current pose model is not a supported fix.

## Verification and performance

- 14 standalone Python tests pass with exit 0. Coverage includes hidden-position/orientation contamination, absent-context isolation, known-frame inversion, rigid-transform/scale invariance, quaternion/6D reconstruction, half turns, explicit degenerate rotation handling, source-frame timing, endpoint envelope, split identity rejection, cohort weights, finite-difference loss gradients and window-isolated metrics.
- The same 14 tests and a saved-weight inference/endpoints check pass in Bforartists 5.2.0 Alpha (host core), NumPy 2.3.4. The host subsequently reports the previously observed ucrtbase.dll access violation at shutdown. The PowerShell invocation reports exit 1; this is not a clean host exit. Scope is research math/model compatibility, not an integrated animation workflow or rig/mesh validation.
- Training/evaluation took 18.83 seconds on local CPU, Python 3.14.3, NumPy 2.4.4, four OpenBLAS threads. Explicit training arrays occupy 145,751,936 bytes; this is not peak training memory.
- In a fresh standalone process, model loading took 13.13 ms, BVH decoding 12.72 ms, and 33-frame feature encoding 0.708 ms. First inference was 0.375 ms; warm p50/p95 were 0.150/0.204 ms over 100 repeats. Peak process working set was 34,590,720 bytes. These exclude Bforartists, rig projection and viewport evaluation.

## Provenance and reproduction

All source BVHs are the existing pinned CMU conversion cache. No new data, model, dependency or paid compute was downloaded or purchased. Manifest SHA256 values, individual motion SHA256 values, protocol and implementation SHA256 values are recorded in the experiment. The models are locally trained research artifacts under training/, not new bundled release assets.

Sources rechecked on 2026-09-06:

- [Robust Motion In-betweening](https://arxiv.org/abs/2102.04942): establishes temporal transition generation as a distinct learning task and evaluates temporally sparse keyframe constraints. This experiment is an independent compact baseline, not an implementation of that recurrent/adversarial model or a reproduction of its results.
- [On the Continuity of Rotation Representations in Neural Networks](https://arxiv.org/abs/1812.07035): rotation representation reference. No paper code or weights were copied.
- [Pinned CMU conversion notice](https://raw.githubusercontent.com/una-dinosauria/cmu-mocap/09a07f54f3bbb58797325f009282d0b2048a2871/READMEFIRST.txt): documents frame-zero initialization, conversion limitations, and the reproduced research/commercial use permission. Current direct publisher recheck was unavailable in the preceding research attempt; this notice remains accessible. Retain the existing CMU/NSF acknowledgment in distribution documentation and complete current distribution review before bundling any new weights. The converted motions are imperfect anatomical ground truth.

From the repository root, PowerShell:

```powershell
# [PowerShell]
$env:OPENBLAS_NUM_THREADS='4'
python -B tests/test_b4artists_ml_temporal.py
python -B -u training/b4artists_ml/train_temporal_motion.py --output temporal_query_reproduction
```

Use a new output name; an existing result directory is rejected to preserve evidence. Protocol/source/manifest hashes must match for exact reproduction. Results: `training/b4artists_ml/results/temporal_query_v1/` contains report.json, selection.json, diagnostics.json, inference-benchmark.json, host-validation.json and the selected model files. `reproducibility.json` confirms a fresh repeat exited 0 and reproduced byte-identical model files and identical validation/confirmation metrics.

## Next coherent work

1. Replace independent point residuals with a sequence-aware, kinematically consistent representation that separates pelvis trajectory from articulated motion and reconstructs the actual skeletal hierarchy. The current 17-joint collapsed BVH mapping skips intermediate bones; its world rotations alone cannot reconstruct every semantic offset. Address this explicitly before using FK as a guarantee.
2. Include temporal derivative/continuity objectives, bounded context behavior and short-gap identity behavior in a newly frozen experiment. Tune on training/validation only; these confirmation clips are now observed motion-development data. A new untouched evaluation corpus is needed before a fresh generalization claim.
3. Compare against the current strong baselines and preserve all failed runs. Do not promote a weaker neural result merely to add an ML button.
4. Integrate a qualifying backend into the actual Bforartists preview workflow with multi-pose preservation, partial edits, contacts, rig fitting, cancellation, recovery and mesh validation. This research backend alone does not meet that requirement.

COM/support, gravity, momentum, secondary motion, quadrupeds, the optional connector, production rig coverage and equivalent animator/Cascadeur comparisons remain required. No parity or superiority claim is supported.
